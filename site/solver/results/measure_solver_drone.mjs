// Copy of measure_solver_maze.mjs: "Your drone" panel. One Quick sweep on office_0 with the drone's
// sensor set to depth_cam_87 in the panel (Quick = 3 seeds, the drone's sensor only, truth pose, every planner,
// jitter on 0.5 m), a 390 px phone check with the panel open on Custom, and a share link round trip of
// vehicle, custom sensor and yaw (no sweep after the reload).
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_solver_drone.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network for cdn.jsdelivr.net.
// Writes into site/solver/results/: quick_office_0_depth_cam.json (SOLVER.exportJSON()), solver_check_drone.json
// and solver_drone_390.png (390 x 844 at 2x, viewport only).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8783, DBG = 9353, DESK = { width: 1280, height: 900 };
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
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-drone-chrome-"));
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
    out.page = `http://127.0.0.1:${PORT}/site/solver/index.html?map=office_0`;
    const t0 = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.ready.then(() => true)");
    out.python_ready_s = (Date.now() - t0) / 1000;
    out.planners = await cdp.eval("SOLVER.S.env.planners");
    // the panel: drone sensor = depth_cam_87 (a preset choice checks that preset; Quick then flies it alone)
    out.drone_options = await cdp.eval("[...document.querySelectorAll('#droneSensor option')].map(o => o.value)");
    out.preset_boxes = await cdp.eval("[...document.querySelectorAll('#presetList input')].map(i => i.value)");
    await cdp.eval("(() => { const s = document.querySelector('#droneSensor'); s.value = 'depth_cam_87'; s.dispatchEvent(new Event('change')); return true; })()");
    out.drone_summary = await cdp.eval("document.querySelector('#droneSum').textContent");
    out.count_msg_before = await cdp.eval("document.querySelector('#countMsg').textContent");
    const t1 = Date.now();
    out.sweep = await cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, workers_ready: SOLVER.S.readyCount, K: SOLVER.K }))");
    out.sweep.wall_s_from_click = (Date.now() - t1) / 1000;
    out.limit_line = await cdp.eval("document.querySelector('#limitLine').textContent");
    out.time_limit_select = await cdp.eval("document.querySelector('#tlimSel').value");
    const json = await cdp.eval("SOLVER.exportJSON()");
    fs.writeFileSync(path.join(HERE, "quick_office_0_depth_cam.json"), json);
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
    out.spec = doc.spec;
    out.drone = doc.drone;
    out.presets_flown = [...new Set(doc.records.map(r => r.preset))];
    out.count_msg_after = await cdp.eval("document.querySelector('#countMsg').textContent");
    out.csv_head = (await cdp.eval("SOLVER.csv()")).split("\n")[0];

    // phone 390 px: panel open, Custom chosen (fields shown), no horizontal scroll
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await cdp.eval("(() => { document.querySelector('#droneBox').open = true; const s = document.querySelector('#droneSensor'); s.value = 'custom'; s.dispatchEvent(new Event('change')); return true; })()");
    await sleep(600);
    out.phone = await cdp.eval("({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, bodyScrollWidth: document.body.scrollWidth, customShown: !document.querySelector('#customBox').hidden, count: document.querySelector('#countMsg').textContent })");
    out.phone.no_horizontal_scroll = out.phone.scrollWidth <= out.phone.innerWidth && out.phone.bodyScrollWidth <= out.phone.innerWidth;
    await cdp.eval(scrollTo("#droneBox"));
    await sleep(400);
    out.shot_phone = await shot(cdp, "solver_drone_390.png");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });

    // share link round trip: vehicle radius 0.25, v_max 1.5, custom 24 beams 120 deg 4 m, yaw look_where_you_go
    await cdp.eval(`(() => { const set = (s, v) => { const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event("input")); e.dispatchEvent(new Event("change")); };
      set("#vehR", "0.25"); set("#vehV", "1.5"); set("#csBeams", "24"); set("#csFov", "120"); set("#csMax", "4"); set("#yawSel", "look_where_you_go"); return true; })()`);
    const link = await cdp.eval("SOLVER.shareUrl()");
    await cdp.send("Page.navigate", { url: link });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
    out.share = { query: link.split("#")[0].split("?")[1], back: await cdp.eval(`({ open: document.querySelector('#droneBox').open,
      r: document.querySelector('#vehR').value, v: document.querySelector('#vehV').value, a: document.querySelector('#vehA').value,
      sensor: document.querySelector('#droneSensor').value, beams: document.querySelector('#csBeams').value, fov: document.querySelector('#csFov').value,
      max: document.querySelector('#csMax').value, yaw: document.querySelector('#yawSel').value, summary: document.querySelector('#droneSum').textContent,
      count: document.querySelector('#countMsg').textContent })`) };
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "solver_check_drone.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify(out, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
