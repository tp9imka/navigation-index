// Verify the playground in headless Chrome against the native CPython reference.
// Run from the repo root (Node 22+, no npm packages), after native_parity.py:
//   samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py
//   node site/playground/results/measure_playground.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...), network access to cdn.jsdelivr.net,
// and the arena venv (for the native run of the hand-drawn world).
// Writes into site/playground/results/: playground_check.json, playground_check.md, custom_world.json and
// viewport screenshots pg_*.png (1280 x 900 desktop, 390 x 844 phone at 2x).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8766, DBG = 9334, DESK = { width: 1280, height: 900 };
const sleep = t => new Promise(r => setTimeout(r, t));
const write = (name, data) => fs.writeFileSync(path.join(HERE, name), typeof data === "string" ? data : JSON.stringify(data, null, 1) + "\n");
const NATIVE = JSON.parse(fs.readFileSync(path.join(HERE, "native_parity.json"), "utf8"));
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

async function shot(cdp, name) {
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  fs.writeFileSync(path.join(HERE, name), Buffer.from(data, "base64"));
  const h = spawnSync("sips", ["-g", "pixelHeight", "-g", "pixelWidth", path.join(HERE, name)], { encoding: "utf8" }).stdout;
  const ph = +(h.match(/pixelHeight: (\d+)/) || [])[1], pw = +(h.match(/pixelWidth: (\d+)/) || [])[1];
  if (!(ph <= 4000)) throw new Error(`${name} is ${ph} px tall`);
  return { file: name, width: pw, height: ph };
}

const pick = s => Object.fromEntries(KEYS.map(k => [k, s[k]]));
const same = (a, b) => KEYS.every(k => a[k] === b[k]);

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "pg-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", page: `http://127.0.0.1:${PORT}/site/playground/index.html`, steps: [] };
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

    // 1. cold load (fresh profile)
    const tNav = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    await sleep(800);
    out.loading_shot = await shot(cdp, "pg_loading.png");
    await cdp.eval("PG.ready.then(() => true)");
    out.load = await cdp.eval("({ready_ms: PG_STATE.readyMs, mb: PG_STATE.loadMb, worker: PG_STATE.loadTimings, env: PG_STATE.env})");
    out.load.wall_since_navigate_s = (Date.now() - tNav) / 1e3;
    console.log("ready", out.load.ready_ms, "ms", out.load.mb, "MB");

    // 2. every native reference case, browser vs native
    out.parity = [];
    for (const c of NATIVE.cases) {
      await cdp.eval(`PG.loadPreset(${JSON.stringify(c.world)})`);
      const cfg = { planner: c.planner, preset: c.preset, fault: c.fault, filter: c.filter, seed: 0 };
      const r = await cdp.eval(`PG.run([${JSON.stringify(cfg)}]).then(x => x && x.map(y => ({score: y.score, wall_s: y.wall_s, sim_s: y.sim_s, worker_ms: y.worker_ms})))`);
      if (!r) throw new Error("run failed for " + JSON.stringify(c) + " " + await cdp.eval("document.querySelector('#runMsg').textContent"));
      const b = r[0];
      const row = { ...c, browser: pick(b.score), native: c.score, same: same(b.score, c.score), browser_wall_s: b.wall_s, sim_s: b.sim_s };
      delete row.score;
      out.parity.push(row);
      console.log(c.world, c.planner, c.preset, c.fault, c.filter, row.same ? "same" : "DIFF", b.wall_s, "s");
    }

    // 3. compare mode on a preset: A* known map vs freest_beam, end of replay
    await cdp.eval("PG.loadPreset('random_0')");
    await cdp.eval("PG.setCompare(true)");
    const cmp = await cdp.eval(`PG.run([{planner:'astar_known',preset:'ideal',fault:'truth',filter:'none',seed:0},{planner:'freest_beam',preset:'ideal',fault:'truth',filter:'none',seed:0}]).then(x => x.map(y => y.score))`);
    await cdp.eval("PG.seek(PG.duration())");
    await sleep(300);
    out.compare = { world: "random_0", a: pick(cmp[0]), b: pick(cmp[1]), parity_text: await cdp.eval("document.querySelector('#parityMsg').textContent") };
    out.compare.shot = await shot(cdp, "pg_compare_random0.png");

    // 4. draw one obstacle with real pointer events on an empty world, then run A* and freest_beam on it
    await cdp.eval("document.querySelector('#newBtn').click(); PG.setTool('box'); true");
    const rect = await cdp.eval("(() => { const b = document.querySelector('#arena').getBoundingClientRect(); return {x: b.left, y: b.top, w: b.width, h: b.height}; })()");
    const W = await cdp.eval("PG.world().bounds");
    const toPx = (x, y) => {          // same transform as playground.js view(): pad 0.4 m
      const pad = 0.4, s = Math.min(rect.w / (W[2] - W[0] + 2 * pad), rect.h / (W[3] - W[1] + 2 * pad));
      return [rect.x + (x - W[0] + pad) * s, rect.y + (W[3] + pad - y) * s];
    };
    const mouse = async (type, [x, y]) => cdp.send("Input.dispatchMouseEvent", { type, x, y, button: "left", buttons: type === "mouseReleased" ? 0 : 1, clickCount: 1, pointerType: "mouse" });
    const p0 = toPx(7, 7), p1 = toPx(13, 12);
    await mouse("mousePressed", p0);
    for (let k = 1; k <= 8; k++) await mouse("mouseMoved", [p0[0] + (p1[0] - p0[0]) * k / 8, p0[1] + (p1[1] - p0[1]) * k / 8]);
    await mouse("mouseReleased", p1);
    await sleep(200);
    const drawn = await cdp.eval("PG.world()");
    out.drawn = { obstacles: drawn.obstacles };
    if (drawn.obstacles.length !== 1) throw new Error("pointer drawing did not add one box: " + JSON.stringify(drawn.obstacles));
    write("custom_world.json", drawn);
    const cust = await cdp.eval(`PG.run([{planner:'astar_known',preset:'ideal',fault:'truth',filter:'none',seed:0},{planner:'freest_beam',preset:'ideal',fault:'truth',filter:'none',seed:0}]).then(x => x.map(y => ({score: y.score, wall_s: y.wall_s, free_path: y.free_path})))`);
    await cdp.eval("PG.seek(PG.duration() * 0.55)");
    await sleep(300);
    out.custom = { a: pick(cust[0].score), b: pick(cust[1].score), free_path: cust[0].free_path };
    out.custom.shot = await shot(cdp, "pg_custom_drawn.png");

    // 5. fault + filter, mid-replay, dark theme; and the main thread during a slow run
    await cdp.eval("PG.loadPreset('random_0')");
    await cdp.eval(`(() => { window.__gaps = []; let last = performance.now(); window.__rafOn = true;
      const f = now => { window.__gaps.push(now - last); last = now; if (window.__rafOn) requestAnimationFrame(f); }; requestAnimationFrame(f); return true; })()`);
    const slow = await cdp.eval(`PG.run([{planner:'astar_unknown',preset:'ideal',fault:'truth',filter:'none',seed:0}]).then(x => x[0].wall_s)`);
    const gaps = await cdp.eval("(() => { window.__rafOn = false; const g = window.__gaps.slice(2); return {frames: g.length, max_ms: Math.round(Math.max(...g)), median_ms: Math.round(g.sort((a,b)=>a-b)[g.length>>1])}; })()");
    out.responsive = { run: "astar_unknown on random_0", python_wall_s: slow, ...gaps };
    console.log("responsive", out.responsive);
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
    const ff = await cdp.eval(`PG.run([{planner:'astar_known',preset:'ideal',fault:'jump',filter:'none',seed:0},{planner:'astar_known',preset:'ideal',fault:'jump',filter:'F2',seed:0}]).then(x => x.map(y => ({score: y.score, fault_log: y.fault_log})))`);
    await cdp.eval("PG.seek(14.3)");
    await sleep(300);
    out.fault_filter = { a: { ...pick(ff[0].score), fault_log: ff[0].fault_log }, b: { ...pick(ff[1].score), intervention_frac: ff[1].score.intervention_frac } };
    out.fault_filter.shot = await shot(cdp, "pg_jump_f2_dark.png");
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });

    // 6. phone width: no horizontal scroll, run still works
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await cdp.send("Page.reload", {});
    await sleep(500);
    await cdp.eval("PG.ready.then(() => true)");
    await cdp.eval("PG.loadPreset('office_0')");
    const ph = await cdp.eval(`PG.run([{planner:'astar_known',preset:'ideal',fault:'truth',filter:'none',seed:0}]).then(x => x[0].score)`);
    await cdp.eval("PG.seek(PG.duration())");
    await sleep(300);
    out.phone = { viewport: "390 x 844 @2x", scroll_width: await cdp.eval("document.documentElement.scrollWidth"),
      body_scroll_width: await cdp.eval("document.body.scrollWidth"), score: pick(ph) };
    out.phone.no_horizontal_scroll = out.phone.scroll_width <= 390 && out.phone.body_scroll_width <= 390;
    await cdp.eval("document.querySelector('#arena').scrollIntoView({block: 'start'}); window.scrollBy(0, -60); true");
    await sleep(200);
    out.phone.shot = await shot(cdp, "pg_phone_390.png");
    // the new 'Playground' nav link must not push the other pages' top bar wider than 390 px
    out.nav_390 = {};
    for (const pg of ["showcase.html", "index.html"]) {
      await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/${pg}` });
      await sleep(2500);
      out.nav_390[pg] = await cdp.eval(`(() => { const n = document.querySelector('.topnav'), a = [...n.querySelectorAll('a')].find(x => x.getAttribute('href') === 'playground/index.html');
        const r = a && a.getBoundingClientRect();
        return {scroll_width: document.documentElement.scrollWidth, link_visible: !!(r && r.width > 0 && r.right <= 390), link_right_px: r ? Math.round(r.right) : null, topnav_right_px: Math.round(n.getBoundingClientRect().right)}; })()`);
    }
    out.console = cdp.log.splice(0);
    cdp.ws.close();
  } finally {
    chrome.kill(); server.kill();
    await sleep(1500);
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 }); } catch (err) { /* temp dir */ }
  }

  // 7. native run of the hand-drawn world with the same driver
  const py = path.join(ROOT, "samples/close-area-arena/.venv/bin/python");
  const code = `
import json, sys
sys.argv = ["x"]
sys.path.insert(0, ${JSON.stringify(HERE)})
import native_parity as NP
NP.load_arena()
ns = NP.driver_ns()
doc = json.load(open(${JSON.stringify(path.join(HERE, "custom_world.json"))}))
print(json.dumps([ns["simulate"](doc, p, "ideal", "truth", "none", 0)["score"] for p in ("astar_known", "freest_beam")]))
`;
  const p = spawnSync(py, ["-c", code], { encoding: "utf8", maxBuffer: 64 << 20 });
  if (p.status !== 0) throw new Error(p.stderr);
  const nat = JSON.parse(p.stdout.trim().split("\n").pop());
  out.custom.native_a = pick(nat[0]); out.custom.native_b = pick(nat[1]);
  out.custom.same_a = same(out.custom.a, nat[0]); out.custom.same_b = same(out.custom.b, nat[1]);
  write("playground_check.json", out);
  write("playground_check.md", report(out));
  console.log(report(out));
}

function report(o) {
  const L = [], f = s => KEYS.map(k => s[k] == null ? "-" : s[k]).join(" / ");
  const nSame = o.parity.filter(r => r.same).length;
  L.push("# Playground check: headless Chrome vs native CPython", "");
  L.push(`Written by \`node site/playground/results/measure_playground.mjs\` on ${o.date.slice(0, 10)}. Input: synthetic ` +
    "(simulated layouts, vehicle, range sensors and VIO from samples/close-area-arena). Raw data: [playground_check.json](playground_check.json). " +
    "Native reference: [native_parity.json](native_parity.json) from `native_parity.py`, which runs the same `DRIVER_PY` string from worker.js.", "");
  L.push(`Browser: ${o.chrome} headless, Pyodide ${o.load.env.pyodide} (Python ${o.load.env.python}, numpy ${o.load.env.numpy}, scipy ${o.load.env.scipy}). ` +
    `Native: CPython ${NATIVE.native_env.python}, numpy ${NATIVE.native_env.numpy}, scipy ${NATIVE.native_env.scipy}, ${NATIVE.native_env.machine}.`, "");
  L.push("## Load (fresh Chrome profile, cold HTTP cache)", "");
  L.push(`- Python ready ${o.load.ready_ms} ms after the page script started; ${o.load.mb} MB downloaded (Resource Timing in the worker).`);
  L.push(`- Worker steps: Pyodide runtime ${o.load.worker.pyodide_ms} ms, numpy + scipy + ${o.load.env.arena_files} hub files ${o.load.worker.packages_ms} ms, imports ${o.load.worker.import_ms} ms ` +
    `(scipy.ndimage ${o.load.env.imports_ms.scipy_ndimage}, arena ${o.load.env.imports_ms.arena}, reactive ${o.load.env.imports_ms.reactive}, safety filter ${o.load.env.imports_ms.safety_filter} ms).`);
  L.push(`- Planners loaded: ${o.load.env.planners.join(", ")}. Filters: ${o.load.env.filters.join(", ")}. Load errors: ${JSON.stringify(o.load.env.load_errors)}.`, "");
  L.push(`## Browser score = native score on the preset worlds: ${nSame}/${o.parity.length}`, "");
  L.push(`Fields: ${KEYS.join(", ")}. Seed 0.`, "");
  L.push(`| world | planner | sensor | VIO fault | filter | browser: ${KEYS.join(" / ")} | same as native | browser Python s | native Python s |`, "|---|---|---|---|---|---|---|---|---|");
  for (const r of o.parity) L.push(`| ${r.world} | ${r.planner} | ${r.preset} | ${r.fault} | ${r.filter} | ${f(r.browser)} | ${r.same ? "yes" : "NO: native " + f(r.native)} | ${r.browser_wall_s} | ${r.native_wall_s} |`);
  L.push("", "## Hand-drawn world (box drawn with pointer events)", "");
  L.push(`One box from (7, 7) to (13, 12) on an empty 20 x 20 m area, A (1.5, 1.5), B (18.5, 18.5): ${JSON.stringify(o.drawn.obstacles[0])}. BFS free path: ${o.custom.free_path ? "yes" : "no"}. Saved as [custom_world.json](custom_world.json).`, "");
  L.push(`| planner | browser: ${KEYS.join(" / ")} | native: same? |`, "|---|---|---|");
  L.push(`| astar_known | ${f(o.custom.a)} | ${o.custom.same_a ? "yes" : "NO: " + f(o.custom.native_a)} |`);
  L.push(`| freest_beam | ${f(o.custom.b)} | ${o.custom.same_b ? "yes" : "NO: " + f(o.custom.native_b)} |`);
  L.push("", "## Page stays responsive while Python runs", "");
  L.push(`During ${o.responsive.run} (${o.responsive.python_wall_s} s of Python in the worker) the page drew ${o.responsive.frames} animation frames; ` +
    `longest gap between frames ${o.responsive.max_ms} ms, median ${o.responsive.median_ms} ms.`, "");
  L.push("## Other runs shown in the screenshots", "");
  L.push(`- Compare, random_0: A astar_known ${f(o.compare.a)}; B freest_beam ${f(o.compare.b)}. Page note: "${o.compare.parity_text}"`);
  L.push(`- VIO jump on random_0, astar_known: no filter ${f(o.fault_filter.a)} (jump fired at ${o.fault_filter.a.fault_log && o.fault_filter.a.fault_log.fired_t} s); ` +
    `F2 ${f(o.fault_filter.b)}, F2 intervened on ${(100 * o.fault_filter.b.intervention_frac).toFixed(1)} % of 50 Hz steps.`);
  L.push(`- Phone ${o.phone.viewport}: office_0 astar_known ${f(o.phone.score)}; document scroll width ${o.phone.scroll_width} px, body ${o.phone.body_scroll_width} px => ` +
    `${o.phone.no_horizontal_scroll ? "no horizontal scroll" : "HORIZONTAL SCROLL"}.`, "");
  L.push("- Nav link at 390 px: " + Object.entries(o.nav_390).map(([p, v]) => `site/${p} scroll width ${v.scroll_width} px, Playground link ${v.link_visible ? "visible" : "NOT fully visible"} (right edge ${v.link_right_px} px)`).join("; ") + ".", "");
  const shots = [o.loading_shot, o.compare.shot, o.custom.shot, o.fault_filter.shot, o.phone.shot];
  L.push("Viewport screenshots (checked with `sips -g pixelHeight`): " + shots.map(s => `[${s.file}](${s.file}) ${s.width} x ${s.height}`).join(", ") + ".", "");
  L.push(`Console errors / warnings / exceptions: ${o.console.length}${o.console.length ? ": " + o.console.join(" | ") : ""}.`, "");
  return L.join("\n");
}

main().catch(err => { console.error(err); process.exit(1); });
