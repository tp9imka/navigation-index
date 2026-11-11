// Capture the per-planner paths of one real Solver Quick sweep for the Home page race replay.
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/capture_race.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network for cdn.jsdelivr.net.
// Drives site/solver/index.html?map=glass_office_0 in headless Chrome, presses Quick (SOLVER.quick():
// your drone's sensor = ideal, truth pose, the worker's planner list, Solver pool K = min(4, cores - 1)),
// then keeps the seed 0 trajectories (seed 0 = the exact preset map, A and B not jittered) from
// SOLVER.S.sweep.traj, thinned to 10 Hz, plus the outcome and time to B of each run from SOLVER.exportJSON().
// Writes site/solver/results/race_glass_office_0.json. Input: synthetic (2.5D point mass, scored on truth).
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8783, DBG = 9353, MAP = "glass_office_0", HZ = 10;
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
        } else if (m.method === "Runtime.exceptionThrown") this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
        else if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error")
          this.log.push("error: " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 400));
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
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 400));
    return r.result.value;
  }
}

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "race-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", "--window-size=1280,900", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/solver/index.html?map=${MAP}` });
    for (let i = 0; i < 150; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.ready.then(() => true)");
    const t0 = Date.now();
    const sweep = await cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, cancelled: sw.cancelled, K: SOLVER.K, spec: sw.spec }))");
    const wall = (Date.now() - t0) / 1000;
    if (sweep.K > 4) throw new Error(`pool K = ${sweep.K} > 4`);
    const doc = JSON.parse(await cdp.eval("SOLVER.exportJSON()"));
    const traj = await cdp.eval("SOLVER.S.sweep.traj.filter(t => t.seed === 0).map(t => ({ planner: t.planner, key: t.key, outcome: t.outcome, pts: t.pts }))");
    // labels as the Solver shows them (SW.plannerLabel), read from the planner checkboxes
    const label = await cdp.eval("Object.fromEntries([...document.querySelectorAll('#plannerList label')].map(l => [l.querySelector('input').value, l.querySelector('span').textContent]))");
    const rec0 = Object.fromEntries(doc.records.filter(r => r.seed === 0).map(r => [r.planner, r]));
    const r2 = v => Math.round(v * 100) / 100;
    const paths = traj.map(t => {
      const thin = []; let next = 0;
      for (const p of t.pts) if (p[0] >= next - 1e-9) { thin.push([r2(p[0]), r2(p[1]), r2(p[2])]); next = p[0] + 1 / HZ; }
      const last = t.pts[t.pts.length - 1];
      if (thin[thin.length - 1][0] !== r2(last[0])) thin.push([r2(last[0]), r2(last[1]), r2(last[2])]);
      const r = rec0[t.planner] || {};
      return { planner: t.planner, label: label[t.planner] || t.planner, outcome: t.outcome,
        time_to_goal_s: r.time_to_goal_s ?? null, min_clearance_m: r.min_clearance_m ?? null, pts: thin };
    }).sort((a, b) => a.planner.localeCompare(b.planner));
    const out = {
      schema: "navidx-race-paths/1",
      input: "synthetic",
      note: "Seed 0 (exact preset map) of one Solver Quick sweep. 2.5D point mass, simulated range sensor, scored on truth. Not a flight result.",
      command: "node site/solver/results/capture_race.mjs",
      page: `site/solver/index.html?map=${MAP}`,
      map: MAP,
      world: `site/playground/presets/${MAP}.json`,
      date: new Date().toISOString(),
      chrome: version.Browser,
      host: `${os.cpus()[0].model}, ${os.cpus().length} cores`,
      pool_workers: sweep.K,
      sweep: { done: sweep.done, total: sweep.total, cancelled: sweep.cancelled, wall_s: wall, seeds: doc.spec ? doc.spec.seeds : null,
        variations: doc.spec ? doc.spec.variations || null : null, headline: doc.headline ? doc.headline.text : null },
      hz: HZ,
      planners: paths.length,
      outcomes: paths.reduce((a, p) => ((a[p.outcome] = (a[p.outcome] || 0) + 1), a), {}),
      paths,
      console: cdp.log,
    };
    fs.writeFileSync(path.join(HERE, `race_${MAP}.json`), JSON.stringify(out) + "\n");
    console.log(JSON.stringify({ ...out, paths: paths.map(p => `${p.planner} ${p.outcome} ${p.pts.length}`) }, null, 1));
  } finally {
    chrome.kill(); server.kill();
  }
}
main().catch(err => { console.error(err); process.exit(1); });
