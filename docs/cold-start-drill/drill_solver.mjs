// 2026-11-10 cold-start drill: drive the Solver like a team would, in headless Chrome (no browser installed).
// Copied from site/solver/results/measure_recommend.mjs (server, CDP client, Chrome flags).
// Usage (from the hub clone root): node drill_solver.mjs <world.json> <outdir>
// Clicks: Import world JSON (file input), Your drone (radius 0.2, v_max 1.5, depth_cam_87), Quick,
// read headline + Pareto, Recommend (real button, downloads allowed into <outdir>/dl).
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const ROOT = process.cwd();
const WORLD = path.resolve(process.argv[2]);
const OUT = path.resolve(process.argv[3]);
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8792, DBG = 9392, DESK = { width: 1280, height: 900 };
const sleep = t => new Promise(r => setTimeout(r, t));
const T0 = Date.now(), stamp = () => ((Date.now() - T0) / 1000).toFixed(1);

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
  fs.mkdirSync(path.join(OUT, "dl"), { recursive: true });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "drill-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", world_file: path.basename(WORLD),
    host: `${os.cpus()[0].model}, ${os.cpus().length} cores, load ${os.loadavg().map(v => v.toFixed(1)).join(" ")}`, t: {} };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser; out.t.chrome_up = stamp();
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable"); await cdp.send("DOM.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: path.join(OUT, "dl") });
    const tNav = Date.now();
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/solver/` });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
    out.python_ready_s = (Date.now() - tNav) / 1000; out.t.ready = stamp();
    out.K = await cdp.eval("SOLVER.K");
    // 1. Import world JSON: set the hidden file input like a user picking the file
    const { root } = await cdp.send("DOM.getDocument");
    const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: "#fileIn" });
    await cdp.send("DOM.setFileInputFiles", { nodeId, files: [WORLD] });
    for (let i = 0; i < 50; i++) { await sleep(100); if (await cdp.eval("!!(SOLVER.S.doc && SOLVER.S.doc.obstacles && SOLVER.S.worldName === null)")) break; }
    out.import_msg = await cdp.eval("(document.querySelector('#worldMsg') || {}).textContent || ''");
    out.world_loaded = await cdp.eval("({ name: SOLVER.S.worldName, obstacles: SOLVER.S.doc.obstacles.length, a: SOLVER.S.doc.a, b: SOLVER.S.doc.b, family: SOLVER.S.doc.family, radius: SOLVER.S.doc.radius })");
    out.t.imported = stamp();
    // 2. Your drone: open the panel, type radius and v_max, pick depth_cam_87
    await cdp.eval(`(() => { document.querySelector('#droneBox').open = true;
      for (const [sel, v] of [['#vehR', '0.2'], ['#vehV', '1.5']]) { const e = document.querySelector(sel); e.value = v; e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('change')); }
      const s = document.querySelector('#droneSensor'); s.value = 'depth_cam_87'; s.dispatchEvent(new Event('change')); return true; })()`);
    out.drone_options = await cdp.eval("[...document.querySelectorAll('#droneSensor option')].map(o => o.value)");
    out.drone_summary = await cdp.eval("document.querySelector('#droneSum').textContent");
    out.t.drone_set = stamp();
    // 3. Quick: click the button, wait for the sweep to finish
    const tq = Date.now();
    await cdp.eval("document.querySelector('#quickBtn').click(), true");
    for (let i = 0; i < 1800; i++) {
      await sleep(1000);
      const st = await cdp.eval("SOLVER.S.sweep ? { running: SOLVER.S.sweep.running, done: SOLVER.S.sweep.done, total: SOLVER.S.sweep.total } : null");
      if (st && !st.running && st.done > 0) { out.sweep = st; break; }
    }
    out.quick_wall_s = (Date.now() - tq) / 1000; out.t.quick_done = stamp();
    out.headline = await cdp.eval("document.querySelector('#headline').textContent");
    out.limit_line = await cdp.eval("(document.querySelector('#limitLine') || {}).textContent || ''");
    // 4. Pareto view
    out.pareto = await cdp.eval("(() => { const p = SOLVER.pareto(); if (!p) return null; return { key: p.key, front: p.par && p.par.map ? p.par.map(r => r.planner || r.id || r) : p.par, rows: p.rows }; })()");
    out.pareto_text = await cdp.eval("(document.querySelector('#paretoBox') || {}).innerText || ''");
    fs.writeFileSync(path.join(OUT, "quick_export.json"), await cdp.eval("SOLVER.exportJSON()"));
    // 5. Recommend: click the real button (downloads), then the same function for the record
    out.rec_enabled = await cdp.eval("!document.querySelector('#recBtn').disabled");
    await cdp.eval("document.querySelector('#recBtn').click(), true");
    await sleep(3000);
    out.downloads = fs.readdirSync(path.join(OUT, "dl"));
    out.share_msg = await cdp.eval("document.querySelector('#shareMsg').textContent");
    const r = await cdp.eval("SOLVER.recommend()");
    fs.writeFileSync(path.join(OUT, "recommend_api.md"), r.md);
    fs.writeFileSync(path.join(OUT, "recommend_api.json"), r.json);
    const j = JSON.parse(r.json);
    out.rec = { headline: j.headline && j.headline.text, kind: j.kind, tied_n: j.tied_n, command: j.fly ? j.fly.command : null,
      arm: j.fly ? j.fly.arm : null, passage_m: j.passage && j.passage.passage_m, advisor: r.advisor };
    out.t.recommended = stamp();
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(OUT, "solver_check.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify({ ...out, pareto: out.pareto ? { key: out.pareto.key, front: out.pareto.front } : null }, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
