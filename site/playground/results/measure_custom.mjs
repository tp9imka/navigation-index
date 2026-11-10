// loop-75: browser = native for custom vehicles and sensors in the run message (cfg.vehicle, cfg.sensor).
// loop-75b: cfg.yaw, vehicle radius in the planners, and the page's "Advanced: your drone" panel.
// Cases: native_parity_custom.json (depth_cam_87 as a cfg.sensor dict with and without cfg.yaw, vehicle radius
// 0.25 and 0.35 m on narrow_gap_0 with mppi_astar and astar_unknown). Also checks: the ready env lists the 5
// presets, the result carries the vehicle, sensor, yaw and inflation flown (= native), an unknown key is refused
// with its name, a non-object cfg.sensor and an unknown cfg.yaw are refused; then index.html: the sensor select
// offers the 5 presets, the drone panel feeds readCfg (PG.config) and the copied link, and the link restores it.
// Pattern of measure_loop73b.mjs (not imported), but it talks to worker.js directly: playground.js builds
// its run configs from the form, which has no vehicle / sensor fields yet. The worker is started from a
// same-origin page (manifest.json) with a fresh ?v= so no cached worker.js is used.
// Run from the repo root (Node 22+, no npm packages), after
//   samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py
//   node site/playground/results/measure_custom.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network access to cdn.jsdelivr.net.
// Writes site/playground/results/playground_custom.json and playground_custom.md.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8778, DBG = 9346, DESK = { width: 1280, height: 900 };
const READY_TIMEOUT_S = 600;
const EXPECT_PRESETS = ["ideal", "crazyflie", "crazyflie_bright", "depth_cam_87", "lidar_2d"];
const sleep = t => new Promise(r => setTimeout(r, t));
const write = (name, data) => fs.writeFileSync(path.join(HERE, name), typeof data === "string" ? data : JSON.stringify(data, null, 1) + "\n");
const NATIVE = JSON.parse(fs.readFileSync(path.join(HERE, "native_parity_custom.json"), "utf8"));
const KEYS = NATIVE.keys;

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
        } else if (m.method === "Runtime.exceptionThrown") {
          this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 600));
        } else if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type)) {
          this.log.push(m.params.type + ": " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 600));
        }
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

const pick = s => Object.fromEntries(KEYS.map(k => [k, s[k]]));
const same = (a, b) => KEYS.every(k => a[k] === b[k]);
const sameJson = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// In the page: one worker, a promise per run id.
const BOOT = `(() => {
  window.PEND = new Map(); let n = 0;
  window.W = new Worker("worker.js?v=loop75b-" + Date.now() + "&pyodide=cdn", { type: "module" });
  window.WREADY = new Promise((ok, fail) => {
    W.onmessage = ev => {
      const m = ev.data;
      if (m.type === "ready") ok(m.env);
      else if (m.type === "error" && m.fatal) fail(new Error(m.message));
      else if (m.type === "result" || m.type === "error") {
        const p = PEND.get(m.id); if (!p) return; PEND.delete(m.id);
        p(m.type === "result" ? { ok: true, result: m.result } : { ok: false, message: m.message });
      }
    };
    W.onerror = ev => fail(new Error("worker error: " + (ev.message || "?")));
  });
  window.RUN = async (worldName, cfg) => {
    const world = await (await fetch("presets/" + worldName + ".json", { cache: "no-cache" })).json();
    const id = ++n;
    return new Promise(ok => { PEND.set(id, ok); W.postMessage({ type: "run", id, world, cfg }); });
  };
  return true;
})()`;

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "pg75-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  let chrome = null;
  const out = { date: new Date().toISOString(), input: "synthetic", page: `http://127.0.0.1:${PORT}/site/playground/manifest.json`,
    worker: "site/playground/worker.js (direct postMessage)", native: "native_parity_custom.json",
    host: { cpus: os.cpus().length, loadavg: os.loadavg().map(x => Math.round(x * 10) / 10) } };
  try {
    chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
      "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
    { stdio: ["ignore", "ignore", "pipe"] });
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    out.chrome = version.Browser;
    await cdp.send("Page.navigate", { url: out.page });
    await sleep(800);
    await cdp.eval(BOOT);
    const t0 = Date.now();
    const env = await cdp.eval(`Promise.race([WREADY, new Promise((_, f) => setTimeout(() => f(new Error("ready timeout")), ${READY_TIMEOUT_S * 1000}))])`);
    out.ready_s = Math.round((Date.now() - t0) / 100) / 10;
    out.env = { pyodide: env.pyodide, python: env.python, numpy: env.numpy, scipy: env.scipy, presets: env.presets,
      load_errors: env.load_errors, arena_files: env.arena_files };
    out.presets_ok = sameJson(env.presets, EXPECT_PRESETS);
    console.log("ready in", out.ready_s, "s; presets", JSON.stringify(env.presets));
    out.parity = [];
    for (const c of NATIVE.cases) {
      const cfg = { planner: c.planner, preset: c.preset, fault: c.fault, filter: c.filter, seed: c.seed };
      if (c.sensor) cfg.sensor = c.sensor;
      if (c.vehicle) cfg.vehicle = c.vehicle;
      if (c.yaw) cfg.yaw = c.yaw;
      const r = await cdp.eval(`RUN(${JSON.stringify(c.world)}, ${JSON.stringify(cfg)}).then(x => x.ok ? {ok: true, score: x.result.score, wall_s: x.result.wall_s, sim_s: x.result.sim_s, worker_ms: x.result.worker_ms, vehicle: x.result.vehicle, sensor: x.result.sensor, radius: x.result.radius, yaw: x.result.yaw, inflation: x.result.inflation, n_beams: x.result.scan_angles.length, max_range: x.result.max_range, frames: x.result.frames.length} : x)`);
      if (!r.ok) throw new Error("run failed for " + JSON.stringify(c) + ": " + r.message);
      const flown = { vehicle: r.vehicle, sensor: r.sensor, radius: r.radius, yaw: r.yaw, n_beams: r.n_beams, max_range: r.max_range };
      const row = { world: c.world, planner: c.planner, custom: c.sensor ? "sensor" : "vehicle", browser: pick(r.score), native: c.score,
        before: c.before || null, free_path: c.free_path,
        same: same(r.score, c.score), flown_same: sameJson(flown, c.flown) && sameJson(r.inflation, c.inflation), frames: { browser: r.frames, native: c.frames },
        flown, browser_wall_s: r.wall_s, worker_ms: r.worker_ms, native_wall_s: c.native_wall_s, sim_s: r.sim_s };
      out.parity.push(row);
      console.log(c.world, row.custom, row.same ? "same" : "DIFF", row.flown_same ? "flown same" : "flown DIFF", r.wall_s, "s browser,", c.native_wall_s, "s native");
    }
    // refusals
    const cam = NATIVE.cases[0].sensor;
    const bad1 = await cdp.eval(`RUN("random_0", ${JSON.stringify({ planner: "straight", sensor: { ...cam, fov: 90 } })})`);
    const bad2 = await cdp.eval(`RUN("random_0", ${JSON.stringify({ planner: "straight", sensor: [1, 2] })})`);
    const bad3 = await cdp.eval(`RUN("random_0", ${JSON.stringify({ planner: "straight", vehicle: { radius_m: 0.2 } })})`);
    const bad4 = await cdp.eval(`RUN("random_0", ${JSON.stringify({ planner: "straight", yaw: "spin" })})`);
    out.refusals = [
      { case: "sensor with unknown key fov", ok: !bad1.ok && /unknown sensor keys: fov/.test(bad1.message), message: bad1.message || null },
      { case: "sensor is an array", ok: !bad2.ok && /cfg\.sensor must be an object/.test(bad2.message), message: bad2.message || null },
      { case: "vehicle missing 3 keys", ok: !bad3.ok && /missing vehicle keys: v_max, a_max, tau/.test(bad3.message), message: bad3.message || null },
      { case: "cfg.yaw spin", ok: !bad4.ok && /cfg\.yaw must be fixed or look_where_you_go/.test(bad4.message), message: bad4.message || null },
    ];
    // index.html: sensor select, drone panel => PG.config and the link, link => panel (no Python needed)
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/playground/index.html?pyodide=cdn` });
    await sleep(800);
    await cdp.eval(`new Promise(ok => { const t = setInterval(() => { if (window.PG) { clearInterval(t); PG.started.then(() => ok(true)); } }, 100); })`);
    const ui = await cdp.eval(`(async () => {
      const opts = Array.from(document.querySelector("#A_preset").options).map(o => o.value);
      const def = PG.config().a;
      const link0 = await PG.shareUrl();
      document.querySelector("#drRadius").value = "0.25"; document.querySelector("#drVmax").value = "1.5";
      document.querySelector("#drYaw").value = "look_where_you_go";
      const set = PG.config().a, link = await PG.shareUrl();
      document.querySelector("#drRadius").value = "9";      // out of range => clamped to 0.6 in readCfg
      const clamped = PG.config().a.vehicle;
      return { opts, def, link0, set, link, clamped };
    })()`);
    await cdp.send("Page.navigate", { url: ui.link });
    await sleep(800);
    await cdp.eval(`new Promise(ok => { const t = setInterval(() => { if (window.PG) { clearInterval(t); PG.started.then(() => ok(true)); } }, 100); })`);
    const back = await cdp.eval(`({ cfg: PG.config().a, open: document.querySelector("#droneBox").open, msg: document.querySelector("#worldMsg").textContent })`);
    const q = new URL(ui.link).searchParams, q0 = new URL(ui.link0).searchParams;
    const wantVeh = { radius_m: 0.25, v_max: 1.5, a_max: 3, tau: 0.15 };
    out.ui = { sensor_options: ui.opts, default_cfg: ui.def, set_cfg: ui.set, link_params: Object.fromEntries(q), restored: back, clamped: ui.clamped };
    out.ui_checks = [
      { check: "sensor select offers the 5 presets", ok: sameJson(ui.opts, EXPECT_PRESETS) },
      { check: "default drone: no vehicle / yaw in readCfg or the link", ok: !("vehicle" in ui.def) && !("yaw" in ui.def) && !q0.has("radius") && !q0.has("yaw") },
      { check: "drone panel => readCfg vehicle + yaw", ok: sameJson(ui.set.vehicle, wantVeh) && ui.set.yaw === "look_where_you_go" },
      { check: "link carries radius, v_max, yaw", ok: q.get("radius") === "0.25" && q.get("v_max") === "1.5" && q.get("yaw") === "look_where_you_go" },
      { check: "link restores the drone panel (open, same readCfg)", ok: back.open && sameJson(back.cfg.vehicle, wantVeh) && back.cfg.yaw === "look_where_you_go" },
      { check: "radius 9 m clamped to 0.6 m in readCfg", ok: ui.clamped && ui.clamped.radius_m === 0.6 },
    ];
    out.console = cdp.log;
  } finally {
    if (chrome) chrome.kill();
    server.kill();
  }
  const n = out.parity.filter(r => r.same).length;
  out.summary = `${n}/${out.parity.length} cases identical (browser = native)`;
  out.flown_ok = out.parity.every(r => r.flown_same);
  out.refusals_ok = out.refusals.every(r => r.ok);
  out.ui_ok = out.ui_checks.every(r => r.ok);
  write("playground_custom.json", out);
  const f = v => (v == null ? "-" : v);
  const md = [`# Playground loop-75 / 75b: custom vehicle, sensor and yaw in the run message, browser vs native`, "",
    `\`node site/playground/results/measure_custom.mjs\`, ${out.date}. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, truth pose, no filter).`,
    `Browser: ${out.chrome}, Pyodide ${out.env.pyodide} (Python ${out.env.python}, numpy ${out.env.numpy}, scipy ${out.env.scipy}), worker.js driven directly by postMessage. Native: ${NATIVE.native_env.python}, numpy ${NATIVE.native_env.numpy}, scipy ${NATIVE.native_env.scipy} ([native_parity_custom.json](native_parity_custom.json)).`,
    `Host: ${out.host.cpus} CPUs, load average ${out.host.loadavg.join(" / ")} at start. Worker ready in ${out.ready_s} s. Load errors in the worker: ${JSON.stringify(out.env.load_errors)}.`, "",
    `**${out.summary}.** Vehicle and sensor flown (result "vehicle", "sensor", radius, beams, max range) = native: ${out.flown_ok ? "yes, every case" : "NO"}. ` +
    `Ready env presets = ${JSON.stringify(EXPECT_PRESETS)}: ${out.presets_ok ? "yes" : "NO " + JSON.stringify(out.env.presets)}. Refusals as expected: ${out.refusals.filter(r => r.ok).length}/${out.refusals.length}.`, "",
    "| world | planner | custom | sensor / yaw | vehicle radius m | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |",
    "|---|---|---|---|---|---|---|---|---|---|",
    ...out.parity.map(r => `| ${r.world} | ${r.planner} | ${r.custom} | ${r.flown.sensor.name} / ${r.flown.yaw} | ${r.flown.radius} | ${r.browser.outcome} / ${f(r.browser.time_to_goal_s)} / ${r.browser.min_clearance_m} / ${r.browser.path_length_m} | ${r.native.outcome} / ${f(r.native.time_to_goal_s)} / ${r.native.min_clearance_m} / ${r.native.path_length_m} | ${r.same ? "yes" : "NO"} | ${r.browser_wall_s} | ${r.native_wall_s} |`),
    "", "Vehicle radius in the planners (loop-75b). Before = the same run with the planners at the shipped 0.15 m (native only, `inflate=False`). Free path = BFS on the true grid inflated by the radius.", "",
    "| world | planner | radius m | free path | before: outcome / time to goal s / min clearance m / path m | after (browser = native) |", "|---|---|---|---|---|---|",
    ...out.parity.filter(r => r.before).map(r => `| ${r.world} | ${r.planner} | ${r.flown.radius} | ${r.free_path ? "yes" : "no"} | ${r.before.outcome} / ${f(r.before.time_to_goal_s)} / ${r.before.min_clearance_m} / ${r.before.path_length_m} | ${r.browser.outcome} / ${f(r.browser.time_to_goal_s)} / ${r.browser.min_clearance_m} / ${r.browser.path_length_m} |`),
    "", "| refusal case | as expected | worker message |", "|---|---|---|",
    ...out.refusals.map(r => `| ${r.case} | ${r.ok ? "yes" : "NO"} | ${String(r.message).replace(/\|/g, "/").replace(/\n/g, " ")} |`),
    "", `Page checks (index.html, no Python run): ${out.ui_checks.filter(r => r.ok).length}/${out.ui_checks.length}.`, "",
    "| page check | ok |", "|---|---|", ...out.ui_checks.map(r => `| ${r.check} | ${r.ok ? "yes" : "NO"} |`),
    "", `Console errors / warnings: ${out.console.length}`, ...out.console.map(x => "- " + x), ""];
  write("playground_custom.md", md.join("\n"));
  console.log(out.summary, "flown", out.flown_ok, "presets", out.presets_ok, "refusals", out.refusals_ok, "ui", out.ui_ok);
}

main().catch(err => { console.error(err); process.exit(1); });
