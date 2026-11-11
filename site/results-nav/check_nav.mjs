// Nav check and screenshots for the shared site nav. Run from the repo root: node site/results-nav/check_nav.mjs
// - spawns `python3 -m http.server` on the repo root (base "/") and a tiny node server that serves the
//   repo under "/navigation-index/" (the GitHub Pages layout),
// - opens every page in the machine's headless Chrome (CDP over Node's built-in WebSocket),
//   reads the nav as rendered by nav.js (hrefs, aria-current, horizontal overflow at 390 px),
// - fetches every nav and brand link and records the HTTP status,
// - saves viewport screenshots (never taller than the viewport) and link_check.json here.
import { spawn } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PY_PORT = 8765, PREFIX_PORT = 8766, CDP_PORT = 9333;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const PAGES = ["index.html", "site/index.html", "site/showcase.html", "site/solver/index.html",
  "site/playground/index.html", "graph/index.html"];
const ALIASES = ["", "site/", "site/solver/", "site/playground/", "graph/"];

// GitHub Pages layout: /navigation-index/<path> => <repo>/<path>.
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".png": "image/png", ".txt": "text/plain", ".md": "text/markdown", ".py": "text/plain" };
function prefixServer() {
  return http.createServer((req, res) => {
    const u = new URL(req.url, "http://x");
    if (!u.pathname.startsWith("/navigation-index/")) { res.writeHead(404); return res.end(); }
    let p = path.join(ROOT, decodeURIComponent(u.pathname.slice("/navigation-index/".length)));
    if (!p.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, "index.html");
    if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" });
    fs.createReadStream(p).pipe(res);
  }).listen(PREFIX_PORT, "127.0.0.1");
}

async function waitHttp(url, tries = 150) {
  for (let i = 0; i < tries; i++) { try { await fetch(url); return; } catch { await sleep(200); } }
  throw new Error("not up: " + url);
}

class Page {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); this.waiters = [];
    ws.onmessage = ev => { const m = JSON.parse(ev.data);
      if (m.id && this.pending.has(m.id)) { const { ok, err } = this.pending.get(m.id); this.pending.delete(m.id); m.error ? err(new Error(m.error.message)) : ok(m.result); }
      else if (m.method) this.waiters = this.waiters.filter(w => !(w.method === m.method && (w.ok(m.params), true))); }; }
  send(method, params = {}) { const id = ++this.id; this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((ok, err) => this.pending.set(id, { ok, err })); }
  once(method, ms = 15000) { return new Promise(ok => { const w = { method, ok }; this.waiters.push(w);
    setTimeout(() => { this.waiters = this.waiters.filter(x => x !== w); ok(null); }, ms); }); }
  async eval(expr) { const r = await this.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }); return r.result.value; }
  async open(url, width, height, dark = false) {
    await this.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 500 });
    await this.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }] });
    const loaded = this.once("Page.loadEventFired");
    await this.send("Page.navigate", { url });
    await loaded; await sleep(900);
  }
  async shot(file) { const r = await this.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(HERE, file), Buffer.from(r.data, "base64")); return file; }
}

const READ_NAV = `(() => {
  const nav = document.getElementById("siteNav");
  const brand = document.querySelector(".top .brand");
  const links = nav ? [...nav.querySelectorAll(".nav-list a")].map(a => ({ label: a.textContent.trim(), href: a.getAttribute("href"), url: a.href, current: a.getAttribute("aria-current") })) : [];
  return { js: !!(nav && nav.classList.contains("nav-js")), brand: brand ? { href: brand.getAttribute("href"), url: brand.href } : null, links,
    scrollWidth: document.documentElement.scrollWidth, innerWidth: innerWidth };
})()`;

async function main() {
  fs.mkdirSync(HERE, { recursive: true });
  const py = spawn("python3", ["-m", "http.server", String(PY_PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const ps = prefixServer();
  const prof = fs.mkdtempSync(path.join(os.tmpdir(), "navchk-"));
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${prof}`,
    "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
  const out = { generated: new Date().toISOString(), server: `python3 -m http.server ${PY_PORT} (repo root)`,
    prefix_server: `node static server, repo under /navigation-index/ on ${PREFIX_PORT}`, chrome: CHROME, pages: [], links: [], summary: {} };
  try {
    await waitHttp(`http://127.0.0.1:${PY_PORT}/`);
    await waitHttp(`http://127.0.0.1:${CDP_PORT}/json/version`);
    const t = await (await fetch(`http://127.0.0.1:${CDP_PORT}/json/new?about:blank`, { method: "PUT" })).json();
    const ws = new WebSocket(t.webSocketDebuggerUrl);
    await new Promise((ok, err) => { ws.onopen = ok; ws.onerror = err; });
    const page = new Page(ws);
    await page.send("Page.enable"); await page.send("Runtime.enable");

    const status = new Map();
    async function code(url) {
      if (!status.has(url)) { try { status.set(url, (await fetch(url, { redirect: "manual" })).status); } catch (e) { status.set(url, "error: " + e.message); } }
      return status.get(url);
    }

    const origins = [[`http://127.0.0.1:${PY_PORT}/`, "/"], [`http://127.0.0.1:${PREFIX_PORT}/navigation-index/`, "/navigation-index/"]];
    for (const [origin, base] of origins) {
      for (const p of [...PAGES, ...ALIASES]) {
        const url = origin + p;
        for (const width of [1280, 390]) {
          await page.open(url, width, 800);
          const nav = await page.eval(READ_NAV);
          const current = nav.links.filter(l => l.current === "page").map(l => l.label);
          out.pages.push({ base, page: "/" + p, width, nav_js: nav.js, current, overflow_x: nav.scrollWidth > nav.innerWidth,
            scroll_width: nav.scrollWidth, links: nav.links.map(l => l.href), brand: nav.brand && nav.brand.href });
          if (width !== 1280) continue;
          for (const l of [...nav.links, ...(nav.brand ? [{ label: "brand", href: nav.brand.href, url: nav.brand.url }] : [])]) {
            const external = !l.url.startsWith("http://127.0.0.1");
            out.links.push({ base, from: "/" + p, label: l.label, href: l.href, url: l.url,
              status: external ? "external, not fetched" : await code(l.url) });
          }
        }
      }
    }

    // Screenshots (viewport only).
    const py0 = origins[0][0];
    const shots = [];
    await page.open(py0, 1280, 860); shots.push(await page.shot("home-desktop.png"));
    await page.open(py0, 390, 844); shots.push(await page.shot("home-390.png"));
    await page.open(py0, 390, 844, true);
    await page.eval(`document.querySelector("#siteNav .nav-toggle").click()`); await sleep(200);
    shots.push(await page.shot("home-390-menu-dark.png"));
    await page.open(py0 + "site/solver/", 1280, 860); shots.push(await page.shot("solver-nav-desktop.png"));
    await page.open(py0 + "site/", 1280, 860); shots.push(await page.shot("search-nav-desktop.png"));
    await page.open(py0 + "site/", 390, 844, true);
    await page.eval(`document.querySelector("#siteNav .nav-toggle").click()`); await sleep(200);
    shots.push(await page.shot("search-390-menu-dark.png"));
    await page.open(py0 + "site/showcase.html", 390, 844); shots.push(await page.shot("showcase-390.png"));
    await page.open(py0 + "graph/", 1280, 860); await sleep(1500); shots.push(await page.shot("graph-nav-desktop.png"));
    // Search page round trip: Home => Search card => brand => Home.
    await page.open(py0, 1280, 860);
    const loaded1 = page.once("Page.loadEventFired");
    await page.eval(`document.querySelector('.tile[href="site/"]').click()`); await loaded1; await sleep(1500);
    const onSearch = await page.eval(`({ path: location.pathname, results: document.querySelectorAll("#results .card, .card").length, current: document.querySelector('#siteNav [aria-current="page"]')?.textContent })`);
    const loaded2 = page.once("Page.loadEventFired");
    await page.eval(`document.querySelector(".top .brand").click()`); await loaded2; await sleep(400);
    const backHome = await page.eval(`({ path: location.pathname, current: document.querySelector('#siteNav [aria-current="page"]')?.textContent })`);
    out.round_trip = { home_to_search: onSearch, brand_back: backHome };
    out.screenshots = shots;
    ws.close();
  } finally {
    chrome.kill(); py.kill(); ps.close();
  }
  const local = out.links.filter(l => typeof l.status === "number");
  out.summary = {
    pages_checked: out.pages.length,
    links_fetched: local.length,
    links_200: local.filter(l => l.status === 200).length,
    links_not_200: local.filter(l => l.status !== 200).map(l => `${l.base} ${l.from} => ${l.href} ${l.status}`),
    pages_without_js_nav: out.pages.filter(p => !p.nav_js).map(p => `${p.base}${p.page.slice(1)} @${p.width}`),
    pages_with_overflow_x: out.pages.filter(p => p.overflow_x).map(p => `${p.base}${p.page.slice(1)} @${p.width} (${p.scroll_width})`),
    pages_with_wrong_current: out.pages.filter(p => p.current.length !== 1).map(p => `${p.base}${p.page.slice(1)}: ${p.current.join(",")}`),
  };
  fs.writeFileSync(path.join(HERE, "link_check.json"), JSON.stringify(out, null, 2) + "\n");
  console.log(JSON.stringify(out.summary, null, 2));
  console.log(JSON.stringify(out.round_trip));
}
main().catch(e => { console.error(e); process.exit(1); });
