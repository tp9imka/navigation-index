// Record one Stress sweep on random_0 in headless Chrome and the Pareto view on a 390 px phone.
// Copied from measure_recommend.mjs (same server, CDP client and Chrome flags).
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_stress.mjs [map]
// Default map: random_0. Needs Google Chrome at the macOS default path (or CHROME=...) and network for
// cdn.jsdelivr.net. Writes into site/solver/results/:
// stress_<map>.json (SOLVER.exportJSON() of the Stress sweep), recommend_<map>_stress.md and .json
// (SOLVER.recommend(), the function behind the Recommend button), stress_check.json (tie sizes vs the
// recorded Quick file recommend_<map>.json, Pareto sets per variation, theme and phone checks) and
// solver_pareto.png (390 x 844 at 2x, viewport only, scrolled to the Pareto view).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8784, DBG = 9354, DESK = { width: 1280, height: 900 };
const MAP = process.argv[2] || "random_0";
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
        } else if (m.method === "Runtime.exceptionThrown") this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 600));
        else if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type))
          this.log.push(m.params.type + ": " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 600));
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
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 600));
    return r.result.value;
  }
}
async function shot(cdp, name) {
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  fs.writeFileSync(path.join(HERE, name), Buffer.from(data, "base64"));
  const h = spawnSync("sips", ["-g", "pixelHeight", "-g", "pixelWidth", path.join(HERE, name)], { encoding: "utf8" }).stdout;
  return { file: name, width: +(h.match(/pixelWidth: (\d+)/) || [])[1], height: +(h.match(/pixelHeight: (\d+)/) || [])[1] };
}
// canvas: CSS size, backing size, and the colour at its top-left corner (the background) and theme
const canvasState = `(() => { const c = document.querySelector("#pareto"), d = c.getContext("2d").getImageData(2, 2, 1, 1).data;
  return { css_w: c.clientWidth, css_h: c.clientHeight, w: c.width, h: c.height, corner_rgb: [d[0], d[1], d[2]],
    theme: document.documentElement.dataset.theme || "system", panel: getComputedStyle(document.documentElement).getPropertyValue("--panel").trim() }; })()`;

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-stress-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", host: `${os.cpus()[0].model}, ${os.cpus().length} cores, load ${os.loadavg().map(v => v.toFixed(1)).join(" ")}`, map: MAP };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    out.page = `http://127.0.0.1:${PORT}/site/solver/index.html?map=${MAP}`;
    const t0 = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
    out.python_ready_s = (Date.now() - t0) / 1000;
    out.world = await cdp.eval("SOLVER.S.worldName");
    out.stress_title = await cdp.eval("document.querySelector('#stressBtn').title");
    const t1 = Date.now();
    out.sweep = await cdp.eval("SOLVER.stress().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, K: SOLVER.K }))");
    out.sweep.wall_s_from_click = (Date.now() - t1) / 1000;
    out.count_msg = await cdp.eval("document.querySelector('#countMsg').textContent");
    const ex = await cdp.eval("SOLVER.exportJSON()");
    fs.writeFileSync(path.join(HERE, `stress_${MAP}.json`), ex);
    const doc = JSON.parse(ex);
    out.spec = doc.spec;
    out.outcomes = doc.records.reduce((a, r) => ((a[r.outcome] = (a[r.outcome] || 0) + 1), a), {});
    out.errors = doc.records.filter(r => r.outcome === "error").map(r => [r.planner, r.preset, r.fault, r.seed, r.error]);
    const r = await cdp.eval("SOLVER.recommend()");
    fs.writeFileSync(path.join(HERE, `recommend_${MAP}_stress.md`), r.md);
    fs.writeFileSync(path.join(HERE, `recommend_${MAP}_stress.json`), r.json);
    const j = JSON.parse(r.json);
    const q = JSON.parse(fs.readFileSync(path.join(HERE, `recommend_${MAP}.json`), "utf8"));
    const tied = x => (x.kind === "tie" ? x.pick.map(p => p.planner) : x.pick.slice(0, 1).map(p => p.planner));
    out.stress = { headline: j.headline.text, kind: j.kind, tied_n: j.tied_n, tied: tied(j), clearly_worse: j.clearly_worse.map(p => p.planner),
      pareto: j.pareto.front.map(p => p.planner) };
    out.quick = { source: `site/solver/results/recommend_${MAP}.json`, headline: q.headline.text, kind: q.kind, tied_n: q.tied_n, tied: tied(q) };
    out.left_the_tie = out.quick.tied.filter(p => !out.stress.tied.includes(p));
    // Pareto view per variation, read back from the page (SOLVER.pareto() after each select change)
    const vars = await cdp.eval("[...document.querySelectorAll('#paretoVar option')].map(o => o.value)");
    out.pareto_view = {};
    for (const v of vars) {
      out.pareto_view[v || "pooled"] = await cdp.eval(`(async () => { const s = document.querySelector("#paretoVar"); s.value = ${JSON.stringify(v)};
        s.dispatchEvent(new Event("change")); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        const p = SOLVER.pareto().par; return { group_n: p.group.length, front: p.front, excluded: p.excluded,
          rows_n: SOLVER.pareto().rows.length, text: document.querySelector("#paretoList").textContent }; })()`);
    }
    await cdp.eval(`(async () => { const s = document.querySelector("#paretoVar"); s.value = ""; s.dispatchEvent(new Event("change"));
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); return true; })()`);
    out.canvas_light = await cdp.eval(canvasState);
    await cdp.eval("document.querySelector('#themeBtn').click(), true");
    await sleep(300);
    out.canvas_dark = await cdp.eval(canvasState);
    await cdp.eval("document.querySelector('#themeBtn').click(), true");
    // phone 390 px: Pareto view, no horizontal scroll
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await sleep(600);
    await cdp.eval(`(() => { const e = document.querySelector("#paretoBox"); window.scrollTo({ top: e.getBoundingClientRect().top + window.scrollY - 8, behavior: "instant" }); return true; })()`);
    await sleep(500);
    out.phone = await cdp.eval("({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth })");
    out.phone.no_horizontal_scroll = out.phone.scrollWidth <= out.phone.innerWidth;
    out.phone.canvas = await cdp.eval(canvasState);
    out.shot = await shot(cdp, "solver_pareto.png");
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "stress_check.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify(out, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
