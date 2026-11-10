// loop-73 copy of measure_solver.mjs: one real Quick sweep on maze_0 only (start/goal jitter ON, the
// default 0.5 m: seed 0 = exact map, seeds 1 and 2 move A and B). No screenshots, share or cancel steps.
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_solver_maze.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network for cdn.jsdelivr.net.
// loop-73b: run time limit Auto (maze => 120 s, as the benchmark); records limit_line (the result header).
// Writes into site/solver/results/: quick_maze_0.json (SOLVER.exportJSON(), the function behind the
// Export JSON button) and solver_check_maze_0.json.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8782, DBG = 9352, DESK = { width: 1280, height: 900 };
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
  const ph = +(h.match(/pixelHeight: (\d+)/) || [])[1], pw = +(h.match(/pixelWidth: (\d+)/) || [])[1];
  if (!(ph <= 4000)) throw new Error(`${name} is ${ph} px tall`);
  return { file: name, width: pw, height: ph };
}
const scrollTo = sel => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); window.scrollTo({ top: e.getBoundingClientRect().top + window.scrollY - 56, behavior: "instant" }); return true; })()`;

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-maze-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", host: `${os.cpus()[0].model}, ${os.cpus().length} cores, load ${os.loadavg().map(v => v.toFixed(1)).join(" ")}` };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    out.page = `http://127.0.0.1:${PORT}/site/solver/index.html?map=maze_0`;
    const t0 = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.ready.then(() => true)");
    out.python_ready_s = (Date.now() - t0) / 1000;
    out.planners = await cdp.eval("SOLVER.S.env.planners");
    out.count_msg_before = await cdp.eval("document.querySelector('#countMsg').textContent");
    const t1 = Date.now();
    out.sweep = await cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, workers_ready: SOLVER.S.readyCount, K: SOLVER.K }))");
    out.sweep.wall_s_from_click = (Date.now() - t1) / 1000;
    out.limit_line = await cdp.eval("document.querySelector('#limitLine').textContent");     // loop-73b: limit in the result header
    out.time_limit_select = await cdp.eval("document.querySelector('#tlimSel').value");
    const json = await cdp.eval("SOLVER.exportJSON()");
    fs.writeFileSync(path.join(HERE, "quick_maze_0.json"), json);
    const doc = JSON.parse(json);
    out.world = doc.world && doc.world.family;
    out.headline = doc.headline.text;
    out.outcomes = doc.records.reduce((a, r) => ((a[r.outcome] = (a[r.outcome] || 0) + 1), a), {});
    out.errors = doc.records.filter(r => r.outcome === "error").map(r => [r.planner, r.seed, r.error]);
    out.ranking = doc.ranking.map(r => ({ planner: r.planner, n: r.n, n_distinct: r.n_distinct, reached: r.reached,
      ci: [+(r.success.lo * 100).toFixed(1), +(r.success.hi * 100).toFixed(1)], median_time_s: r.median_time_s }));
    const wall = {};
    for (const r of doc.records) (wall[r.planner] = wall[r.planner] || []).push(r.wall_s);
    out.max_wall_s = Object.fromEntries(Object.entries(wall).map(([p, v]) => [p, Math.max(...v.filter(x => x != null))]));
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "solver_check_maze_0.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify(out, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
