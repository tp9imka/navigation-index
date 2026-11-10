// Run the Solver page in headless Chrome and record one real Quick sweep on random_0 (start/goal
// jitter ON, the default 0.5 m: seed 0 = exact map, seeds 1 and 2 move A and B).
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_solver.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network for cdn.jsdelivr.net.
// Writes into site/solver/results/: quick_random_0.json (SOLVER.exportJSON(), the function behind the
// Export JSON button), solver_check.json and viewport screenshots (never full page):
// solver_matrix_desktop.png (1280 x 900, light), solver_race_mid.png (1280 x 900, light),
// solver_phone_390.png (390 x 844 at 2x, dark).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8781, DBG = 9351, DESK = { width: 1280, height: 900 };
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
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-chrome-"));
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
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });

    out.page = `http://127.0.0.1:${PORT}/site/solver/index.html?map=random_0`;
    const t0 = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.ready.then(() => true)");
    out.python_ready_s = (Date.now() - t0) / 1000;
    out.count_msg_before = await cdp.eval("document.querySelector('#countMsg').textContent");

    // Quick sweep (3 seeds, ideal, truth pose, every planner the worker lists)
    const t1 = Date.now();
    out.sweep = await cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, workers_ready: SOLVER.S.readyCount, K: SOLVER.K }))");
    out.sweep.wall_s_from_click = (Date.now() - t1) / 1000;
    const json = await cdp.eval("SOLVER.exportJSON()");
    fs.writeFileSync(path.join(HERE, "quick_random_0.json"), json);
    const doc = JSON.parse(json);
    out.headline = doc.headline.text;
    out.outcomes = doc.records.reduce((a, r) => ((a[r.outcome] = (a[r.outcome] || 0) + 1), a), {});
    out.jitter = doc.jitter;
    out.distinct = Object.fromEntries(doc.ranking.map(r => [r.planner, { n: r.n, n_distinct: r.n_distinct, reached: r.reached,
      ci: [+(r.success.lo * 100).toFixed(1), +(r.success.hi * 100).toFixed(1)], median_time_s: r.median_time_s }]));
    out.ranking = doc.ranking.map(r => r.planner);
    // seed 0 is the exact map: A* known map should match the playground's random_0 seed 0 run
    const ak0 = doc.records.find(r => r.planner === "astar_known" && r.seed === 0);
    out.seed0_astar_known = ak0 ? { time_to_goal_s: ak0.time_to_goal_s, min_clearance_m: ak0.min_clearance_m, a: ak0.a, b: ak0.b } : null;
    out.jitter_controls = await cdp.eval("({ on: document.querySelector('#jitterOn').checked, radius: document.querySelector('#jitterR').value })");
    out.count_msg_after = await cdp.eval("document.querySelector('#countMsg').textContent");

    // 1. desktop result matrix, with one cell clicked (detail panel)
    await cdp.eval("document.querySelector('#matrix button.cell').click(), true");
    await sleep(300);
    await cdp.eval(scrollTo("#headline"));
    await sleep(300);
    out.shot_matrix = await shot(cdp, "solver_matrix_desktop.png");

    // 2. race mid-animation: variation ideal|truth, seed 1 (jittered A and B), paused at half of the longest run
    out.anim = await cdp.eval("(() => { SOLVER.animate('ideal|truth', 1); const A = SOLVER.S.anim; SOLVER.setT(A.tmax / 2); return { seed: A.seed, runs: A.runs.length, tmax: A.tmax, t: A.t }; })()");
    await cdp.eval(scrollTo(".race h2"));
    await sleep(400);
    out.shot_race = await shot(cdp, "solver_race_mid.png");

    // 3. phone 390 px, dark theme: no horizontal scroll
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
    await sleep(600);
    out.phone = await cdp.eval("({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, bodyScrollWidth: document.body.scrollWidth })");
    out.phone.no_horizontal_scroll = out.phone.scrollWidth <= out.phone.innerWidth && out.phone.bodyScrollWidth <= out.phone.innerWidth;
    await cdp.eval(scrollTo("#ranking li:nth-last-child(2)"));
    await sleep(400);
    out.shot_phone = await shot(cdp, "solver_phone_390.png");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });

    // 4. share link round trip: world + sweep spec restored in a reload
    const link = await cdp.eval("SOLVER.shareUrl()");
    const world0 = JSON.stringify(doc.world);
    await cdp.send("Page.navigate", { url: link });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
    const back = await cdp.eval("({ world: JSON.stringify(SOLVER.S.doc), name: SOLVER.S.worldName, planners: document.querySelectorAll('input[name=planner]:checked').length, seeds: document.querySelector('#seedsIn').value, presets: [...document.querySelectorAll('input[name=preset]:checked')].map(i => i.value), jitterOn: document.querySelector('#jitterOn').checked, jitterR: document.querySelector('#jitterR').value })");
    out.share = { length: link.length, world_same: back.world === world0, name: back.name, planners_checked: back.planners, seeds: back.seeds, presets: back.presets,
      jitter_on: back.jitterOn, jitter_radius: back.jitterR };

    // 5. cancel: start a sweep, cancel after the first result, check the counts
    out.cancel = await cdp.eval(`(async () => {
      SOLVER.run();
      for (let i = 0; i < 600 && SOLVER.S.sweep.done < 1; i++) await new Promise(r => setTimeout(r, 100));
      SOLVER.cancel();
      const sw = SOLVER.S.sweep;
      return { total: sw.total, done: sw.done, cancelled: sw.cancelled, text: document.querySelector('#sweepText').textContent };
    })()`);
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    fs.writeFileSync(path.join(HERE, "solver_check.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify(out, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
