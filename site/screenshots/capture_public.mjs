// Screenshots and the 390 px overflow check for the public pages (wave 3 site design).
// Run from the repo root (Node 22+, no npm packages): node site/screenshots/capture_public.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...). Serves the repo root with
// python3 -m http.server, then for every page x width (1280, 390) x theme (light, dark):
// records document scrollWidth vs innerWidth, console errors, exceptions and failed requests,
// and writes a viewport screenshot site/screenshots/public-<page>-<width>-<theme>.png (graph: no
// screenshot, only the overflow check). Summary: site/screenshots/public-check.json.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8785, DBG = 9355;
const PAGES = [
  ["home", "/"], ["results", "/site/results.html"], ["learn", "/site/learn.html"], ["solver", "/site/solver/"],
  ["playground", "/site/playground/"], ["search", "/site/"], ["graph", "/graph/", false],
];
const SIZES = [[1280, 900, 1], [390, 844, 2]];
const THEMES = ["light", "dark"];
const sleep = t => new Promise(r => setTimeout(r, t));

class CDP {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); this.log = []; }
  open() {
    return new Promise((ok, fail) => {
      this.ws.onopen = ok; this.ws.onerror = fail;
      this.ws.onmessage = ev => {
        const m = JSON.parse(ev.data);
        if (m.id && this.pending.has(m.id)) {
          const [res, rej] = this.pending.get(m.id); this.pending.delete(m.id);
          m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
        } else if (m.method === "Runtime.exceptionThrown") this.log.push("exception: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text).slice(0, 300));
        else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error")
          this.log.push("console.error: " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 300));
        else if (m.method === "Log.entryAdded" && m.params.entry.level === "error")
          this.log.push("log: " + m.params.entry.text.slice(0, 200) + " " + (m.params.entry.url || ""));
      };
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((res, rej) => this.pending.set(id, [res, rej]));
  }
  async eval(expr) {
    const r = await this.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  }
}

// widest elements past the right edge, to point at the cause of a horizontal scroll
const OFFENDERS = `(() => { const W = innerWidth, out = [];
  for (const el of document.querySelectorAll("body *")) { const r = el.getBoundingClientRect();
    if (r.right > W + 1 && r.width > 0 && getComputedStyle(el).position !== "fixed") out.push([Math.round(r.right), el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\\s+/).join(".") : "")]); }
  return out.sort((a, b) => b[0] - a[0]).slice(0, 5); })()`;

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "public-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--window-size=1280,900", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), rows: [] };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable"); await cdp.send("Log.enable");
    for (const [name, url, shoot = true] of PAGES) {
      for (const [w, h, dpr] of SIZES) {
        for (const theme of THEMES) {
          await cdp.send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile: w < 600 });
          await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: theme }] });
          cdp.log = [];
          await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}${url}` });
          await sleep(500);
          await cdp.eval("(() => { try { localStorage.removeItem('navidx-theme'); } catch (e) {} delete document.documentElement.dataset.theme; return true; })()");
          await sleep(name === "solver" || name === "playground" ? 3500 : 2500);
          const m = await cdp.eval("({ scrollWidth: document.documentElement.scrollWidth, bodyScrollWidth: document.body.scrollWidth, innerWidth: innerWidth, dark: getComputedStyle(document.documentElement).colorScheme })");
          const row = { page: name, url, width: w, theme, ...m, horizontal_scroll: Math.max(m.scrollWidth, m.bodyScrollWidth) > m.innerWidth };
          if (row.horizontal_scroll) row.offenders = await cdp.eval(OFFENDERS);
          row.errors = cdp.log.filter(l => !/favicon/.test(l));
          if (shoot) {
            const file = `public-${name}-${w}-${theme}.png`;
            const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
            fs.writeFileSync(path.join(HERE, file), Buffer.from(data, "base64"));
            row.screenshot = file;
          }
          out.rows.push(row);
          console.log(`${name} ${w} ${theme}: scrollWidth ${m.scrollWidth}/${m.innerWidth}${row.horizontal_scroll ? " OVERFLOW " + JSON.stringify(row.offenders) : ""} errors ${row.errors.length}`);
          for (const e of row.errors) console.log("   " + e);
        }
      }
    }
    // Search: sample rows carry their input badge (kind facet = sample)
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/#kind=sample` });
    await sleep(2500);
    out.search_sample_badges = await cdp.eval(`(() => { const rows = [...document.querySelectorAll("#results .card")];
      const withBadge = rows.filter(r => r.querySelector('.meta .badge[class*="b-"]'));
      const tally = {}; withBadge.forEach(r => { const t = r.querySelector('.meta .badge[class*="b-"]').textContent; tally[t] = (tally[t] || 0) + 1; });
      return { rows: rows.length, with_input_badge: withBadge.length, labels: tally, fit_facet: [...document.querySelectorAll("#facets h3, #facets .facet-title")].map(h => h.textContent).filter(t => /fit/i.test(t)) }; })()`);
    console.log("search sample badges", JSON.stringify(out.search_sample_badges));
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "public-check.json"), JSON.stringify(out, null, 1) + "\n");
  }
}
main().catch(err => { console.error(err); process.exit(1); });
