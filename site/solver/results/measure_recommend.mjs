// Record the Recommend export (first recorded 2026-11-10; re-recorded with Quick = 5 seeds) from real Quick sweeps in
// headless Chrome, one per map.
// Copied from measure_solver.mjs (same server, CDP client and Chrome flags), screenshots dropped.
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_recommend.mjs [map ...]
// Default maps: narrow_gap_0 random_0. Needs Google Chrome at the macOS default path (or CHROME=...)
// and network for cdn.jsdelivr.net. Writes into site/solver/results/ per map:
// recommend_<map>.md and recommend_<map>.json (SOLVER.recommend(), the function behind the Recommend button),
// quick_<map>_<TAG>.json (SOLVER.exportJSON(), the sweep they came from; TAG = loop87, the first-recording files are
// kept), and recommend_check.json.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8783, DBG = 9353, DESK = { width: 1280, height: 900 };
const MAPS = process.argv.slice(2).length ? process.argv.slice(2) : ["narrow_gap_0", "random_0"];
const TAG = "loop87";
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

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", host: `${os.cpus()[0].model}, ${os.cpus().length} cores, load ${os.loadavg().map(v => v.toFixed(1)).join(" ")}`, maps: {} };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    for (const map of MAPS) {
      const m = out.maps[map] = { page: `http://127.0.0.1:${PORT}/site/solver/index.html?map=${map}` };
      const t0 = Date.now();
      await cdp.send("Page.navigate", { url: m.page });
      for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
      await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
      m.python_ready_s = (Date.now() - t0) / 1000;
      m.world = await cdp.eval("SOLVER.S.worldName");
      const t1 = Date.now();
      m.sweep = await cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, K: SOLVER.K }))");
      m.sweep.wall_s_from_click = (Date.now() - t1) / 1000;
      fs.writeFileSync(path.join(HERE, `quick_${map}_${TAG}.json`), await cdp.eval("SOLVER.exportJSON()"));
      m.button_enabled = await cdp.eval("!document.querySelector('#recBtn').disabled");
      const r = await cdp.eval("SOLVER.recommend()");
      fs.writeFileSync(path.join(HERE, `recommend_${map}.md`), r.md);
      fs.writeFileSync(path.join(HERE, `recommend_${map}.json`), r.json);
      const j = JSON.parse(r.json);
      m.advisor_loaded = r.advisor;
      m.headline = j.headline.text;
      m.kind = j.kind;
      m.seeds = j.flown.seeds;
      m.tied_n = j.tied_n;
      m.clearly_worse_n = j.clearly_worse.length;
      m.more_seeds = j.more_seeds;
      m.command = j.fly ? j.fly.command : null;
      m.arm = j.fly ? j.fly.arm : null;
      m.passage_m = j.passage.passage_m;
    }
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "recommend_check.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify(out, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
