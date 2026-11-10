// loop-93: scripted pass over the Day-1 Solver path that no script had clicked before, in headless Chrome:
// Import world JSON (samples/close-area-arena/rooms/hall_8x6.world.json, CDP DOM.setFileInputFiles) => Quick
// (real mouse click) => Export CSV, Export JSON and Recommend (real mouse clicks; downloads captured with CDP
// Browser.setDownloadBehavior) => check every file exists and parses => Thorough with 2 planners (wiring check)
// => free_path parity: 10 `straight` runs on small worlds, worker free_path vs the page's SW.hasFreePath.
// Copied from measure_recommend.mjs (server, CDP client, Chrome flags) and rooms/shot_solver.mjs (file import).
// Run from the repo root (Node 22+, no npm packages): node site/solver/results/measure_import.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network for cdn.jsdelivr.net.
// CPU: the page's pool (K = min(4, cores - 1)); 90 + 40 + 10 = 140 runs.
// Writes site/solver/results/measure_import.json and the downloads under results/import_hall_8x6/.
// node site/solver/results/measure_import.mjs --check-only re-checks the saved downloads (no browser, no runs).
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8803, DBG = 9373, DESK = { width: 1280, height: 900 };
const WORLD = path.join(ROOT, "samples/close-area-arena/rooms/hall_8x6.world.json");
const DL = path.join(HERE, "import_hall_8x6"), DL_T = path.join(DL, "thorough");
const THOROUGH_PLANNERS = ["astar_known", "dstar_lite"];
const sleep = t => new Promise(r => setTimeout(r, t));

class CDP {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); this.log = []; this.events = []; }
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
        else if (m.method) this.events.push(m);
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

// A real mouse click (Input.dispatchMouseEvent) at the centre of the element: a user gesture, as a person's click.
async function click(cdp, sel) {
  const r = await cdp.eval(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null;
    e.scrollIntoView({ block: "center", behavior: "instant" }); const b = e.getBoundingClientRect();
    return { x: b.left + b.width / 2, y: b.top + b.height / 2, disabled: !!e.disabled }; })()`);
  if (!r) throw new Error("no element " + sel);
  await sleep(150);
  for (const type of ["mouseMoved", "mousePressed", "mouseReleased"])
    await cdp.send("Input.dispatchMouseEvent", { type, x: r.x, y: r.y, button: "left", clickCount: type === "mouseMoved" ? 0 : 1 });
  return r;
}

async function importFile(cdp, file) {
  const { root } = await cdp.send("DOM.getDocument", { depth: -1 });
  const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: "#fileIn" });
  await cdp.send("DOM.setFileInputFiles", { nodeId, files: [file] });
  for (let i = 0; i < 40; i++) {
    await sleep(250);
    const msg = await cdp.eval(`document.querySelector("#worldMsg").textContent`);
    if (msg.includes(path.basename(file))) return msg;
  }
  return await cdp.eval(`document.querySelector("#worldMsg").textContent`);
}

// Wait for n more completed downloads on the browser session (Browser.downloadProgress state completed / canceled).
async function downloads(bcdp, from, n, ms = 20000) {
  const t0 = Date.now();
  for (;;) {
    const ev = bcdp.events.slice(from);
    const begin = ev.filter(e => e.method === "Browser.downloadWillBegin").map(e => e.params);
    const done = ev.filter(e => e.method === "Browser.downloadProgress" && ["completed", "canceled"].includes(e.params.state)).map(e => e.params);
    if (done.length >= n || Date.now() - t0 > ms)
      return begin.map(b => ({ file: b.suggestedFilename, state: (done.find(d => d.guid === b.guid) || { state: "not finished" }).state }));
    await sleep(200);
  }
}

async function waitSweep(cdp, label, maxMin = 45) {
  for (let i = 0; i < maxMin * 30; i++) {
    await sleep(2000);
    const s = await cdp.eval("(() => { const sw = SOLVER.S.sweep; return sw ? { running: sw.running, done: sw.done, total: sw.total } : null; })()");
    if (s && !s.running) return s;
    if (i % 30 === 0) console.error(label, JSON.stringify(s));
  }
  throw new Error(label + ": sweep did not finish");
}

// RFC 4180 CSV (quoted fields, "" inside quotes), as sweep.js toCSV writes it. Rows of strings.
function parseCSV(text) {
  const rows = []; let row = [], f = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"' && text[i + 1] === '"') { f += '"'; i++; } else if (c === '"') q = false; else f += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
    else if (c !== "\r") f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  if (q) throw new Error("unterminated quote");
  return rows;
}

function checkFile(file, kind) {
  const out = { file: path.relative(HERE, file), exists: fs.existsSync(file) };
  if (!out.exists) return out;
  const text = fs.readFileSync(file, "utf8");
  out.bytes = Buffer.byteLength(text);
  try {
    if (kind === "csv") {
      const rows = parseCSV(text), head = rows[0];
      out.rows = rows.length - 1; out.columns = head.length;
      out.has_free_path_col = head.includes("free_path");
      out.rows_same_width = rows.every(r => r.length === head.length);
      out.free_path_values = [...new Set(rows.slice(1).map(r => r[head.indexOf("free_path")]))];
      out.outcomes = rows.slice(1).reduce((a, r) => (a[r[head.indexOf("outcome")]] = (a[r[head.indexOf("outcome")]] || 0) + 1, a), {});
      out.parses = out.rows > 0 && out.rows_same_width;
    } else if (kind === "json") { const j = JSON.parse(text); out.schema = j.schema; out.parses = true; out.json = j; }
    else { out.parses = text.startsWith("# Recommend") && !/[\u2013\u2014]/.test(text); out.first_line = text.split("\n")[0]; }
  } catch (err) { out.parses = false; out.error = String(err.message); }
  return out;
}

// Parity worlds: the worker's free_path (world_json.from_json + worlds_complex.has_free_path) vs SW.hasFreePath.
const OPEN = { schema: "close-area-world/1", family: "custom", bounds: [-2, -2, 18, 18], a: [0, 0], b: [15, 15], radius: 0.15, obstacles: [] };
const WALL_GAP = g => ({ ...OPEN, obstacles: [
  { type: "box", cx: (-2 + 10 - g / 2) / 2, cy: 10, hx: (10 - g / 2 + 2) / 2, hy: 0.15 },
  { type: "box", cx: (10 + g / 2 + 18) / 2, cy: 10, hx: (18 - 10 - g / 2) / 2, hy: 0.15 }].filter(o => o.hx > 0) });
const wallT = (x0, y0, x1, y1) => ({ type: "wall", x0, y0, x1, y1, thickness: 0.1 });
const POCKET = b => ({ ...OPEN, b, obstacles: [wallT(15.2, 14.4, 15.2, 15.6), wallT(16.4, 14.4, 16.4, 15.6), wallT(15.2, 14.4, 16.4, 14.4), wallT(15.2, 15.6, 16.4, 15.6)] });
function parityCases(hall) {
  return [["open", OPEN, 0.15], ["wall_gap_0", WALL_GAP(0), 0.15], ["wall_gap_0.30", WALL_GAP(0.3), 0.15], ["wall_gap_0.35", WALL_GAP(0.35), 0.15],
    ["wall_gap_0.40", WALL_GAP(0.4), 0.15], ["wall_gap_0.80", WALL_GAP(0.8), 0.15], ["pocket_b_inside", POCKET([15.8, 15]), 0.15],
    ["pocket_b_outside", POCKET([14.8, 15]), 0.15], ["hall_8x6_r0.15", hall, 0.15], ["hall_8x6_r0.30", hall, 0.3]]
    .map(([name, world, radius_m]) => ({ name, world, radius_m }));
}

// --check-only: re-check the saved downloads without a browser or a sweep (updates measure_import.json).
function checkOnly() {
  const f = path.join(HERE, "measure_import.json"), out = JSON.parse(fs.readFileSync(f, "utf8"));
  const strip = c => { const x = { ...c }; delete x.json; return x; };
  out.steps.downloads.files = { csv: checkFile(path.join(DL, "solver_custom.csv"), "csv"), json: strip(checkFile(path.join(DL, "solver_custom.json"), "json")),
    recommend_md: checkFile(path.join(DL, "recommend.md"), "md"), recommend_json: strip(checkFile(path.join(DL, "recommend.json"), "json")) };
  out.steps.thorough.json_file = strip(checkFile(path.join(DL_T, "solver_custom.json"), "json"));
  out.files_rechecked = { date: new Date().toISOString(), command: "node site/solver/results/measure_import.mjs --check-only" };
  fs.writeFileSync(f, JSON.stringify(out, null, 1) + "\n");
  console.log(JSON.stringify(out.steps.downloads.files, null, 1));
}

async function main() {
  if (process.argv.includes("--check-only")) return checkOnly();
  fs.mkdirSync(DL_T, { recursive: true });
  for (const d of [DL, DL_T]) for (const f of fs.readdirSync(d)) if (fs.statSync(path.join(d, f)).isFile()) fs.rmSync(path.join(d, f));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "solver-import-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", note: "SYNTHETIC SIMULATION, 2.5D point mass, scored on truth. Not a flight result.",
    host: `${os.cpus()[0].model}, ${os.cpus().length} cores, load ${os.loadavg().map(v => v.toFixed(1)).join(" ")}`,
    page: `http://127.0.0.1:${PORT}/site/solver/index.html`, world_file: path.relative(ROOT, WORLD), steps: {} };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const bcdp = new CDP(version.webSocketDebuggerUrl);
    await bcdp.open();
    await bcdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: DL, eventsEnabled: true });
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable"); await cdp.send("DOM.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    const t0 = Date.now();
    await cdp.send("Page.navigate", { url: out.page });
    for (let i = 0; i < 100; i++) { await sleep(200); if (await cdp.eval("typeof SOLVER === 'object'").catch(() => false)) break; }
    await cdp.eval("SOLVER.started.then(() => SOLVER.ready).then(() => true)");
    out.python_ready_s = (Date.now() - t0) / 1000;

    // 1. Import world JSON
    const msg = await importFile(cdp, WORLD);
    const st = out.steps.import = { message: msg, ok: msg.startsWith("Imported") && (await cdp.eval(`document.querySelector("#worldMsg").className`)).includes("ok"),
      world_name: await cdp.eval("SOLVER.S.worldName"), obstacles: await cdp.eval("SOLVER.S.doc.obstacles.length"),
      bounds: await cdp.eval("SOLVER.S.doc.bounds") };
    if (!st.ok) throw new Error("import failed: " + msg);

    // 2. Quick (real click), every planner the worker lists
    const t1 = Date.now();
    await click(cdp, "#quickBtn");
    await sleep(1000);
    const q = out.steps.quick = { spec: await cdp.eval("SOLVER.S.sweep && SOLVER.S.sweep.spec") };
    q.end = await waitSweep(cdp, "quick");
    q.wall_s_from_click = (Date.now() - t1) / 1000;
    Object.assign(q, await cdp.eval(`(() => { const sw = SOLVER.S.sweep, recs = sw.records.filter(Boolean);
      const by = k => recs.reduce((a, r) => (a[r[k]] = (a[r[k]] || 0) + 1, a), {});
      return { elapsed_s: sw.elapsed_s, K: SOLVER.K, records: recs.length, outcomes: by("outcome"),
        free_path: by("free_path"), free_path_pred: by("free_path_pred"),
        pred_mismatch: recs.filter(r => r.free_path != null && r.free_path !== r.free_path_pred).length,
        jitters: sw.jitters, headline: document.querySelector("#headline").textContent,
        no_path_cells: [...document.querySelectorAll("#matrix td")].filter(td => /no path/.test(td.textContent)).length,
        buttons_enabled: ["#csvBtn", "#jsonBtn", "#recBtn"].map(s => !document.querySelector(s).disabled) }; })()`));

    // 3. CSV, JSON, Recommend buttons (real clicks), downloads into DL
    const dl = out.steps.downloads = {};
    for (const [sel, n] of [["#csvBtn", 1], ["#jsonBtn", 1], ["#recBtn", 2]]) {
      const from = bcdp.events.length;
      await click(cdp, sel);
      dl[sel] = await downloads(bcdp, from, n);
    }
    dl.share_msg = await cdp.eval(`document.querySelector("#shareMsg").textContent`);
    const csv = checkFile(path.join(DL, "solver_custom.csv"), "csv"), js = checkFile(path.join(DL, "solver_custom.json"), "json");
    const rmd = checkFile(path.join(DL, "recommend.md"), "md"), rjs = checkFile(path.join(DL, "recommend.json"), "json");
    const sweepDoc = js.json, recDoc = rjs.json;
    delete js.json; delete rjs.json;
    dl.files = { csv, json: js, recommend_md: rmd, recommend_json: rjs };
    if (sweepDoc) Object.assign(q, { export_headline: sweepDoc.headline.text, export_no_path: sweepDoc.no_path,
      ranking_top: sweepDoc.ranking.slice(0, 5).map(r => ({ planner: r.planner, reached: r.reached, n: r.n, no_path: r.no_path,
        wilson: [r.success.lo, r.success.hi].map(v => Math.round(v * 1000) / 1000), median_time_s: r.median_time_s })),
      reached_planners_5of5: sweepDoc.ranking.filter(r => r.reached === r.n && r.n === 5).length,
      csv_rows_match_records: csv.rows === sweepDoc.records_n });
    if (recDoc) Object.assign(q, { recommend_kind: recDoc.kind, recommend_no_path: recDoc.no_path,
      recommend_command: recDoc.fly && recDoc.fly.command, recommend_arm: recDoc.fly && recDoc.fly.arm, passage_m: recDoc.passage.passage_m,
      tied_n: recDoc.tied_n, clearly_worse: recDoc.clearly_worse.map(r => r.planner) });

    // 4. Thorough wiring, 2 planners (real clicks on None, two planner boxes, Thorough)
    await bcdp.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: DL_T, eventsEnabled: true });
    await click(cdp, "#noneBtn");
    for (const p of THOROUGH_PLANNERS) await click(cdp, `#plannerList input[value="${p}"]`);
    const th = out.steps.thorough = { count_msg: await cdp.eval(`document.querySelector("#countMsg").textContent`) };
    const t2 = Date.now();
    await click(cdp, "#thoroughBtn");
    await sleep(1000);
    th.spec = await cdp.eval("SOLVER.S.sweep && SOLVER.S.sweep.spec");
    th.end = await waitSweep(cdp, "thorough");
    th.wall_s_from_click = (Date.now() - t2) / 1000;
    Object.assign(th, await cdp.eval(`(() => { const sw = SOLVER.S.sweep, recs = sw.records.filter(Boolean);
      const by = k => recs.reduce((a, r) => (a[r[k]] = (a[r[k]] || 0) + 1, a), {});
      return { elapsed_s: sw.elapsed_s, records: recs.length, outcomes: by("outcome"), free_path: by("free_path"),
        variations: [...document.querySelectorAll("#matrix thead th")].slice(1).map(e => e.textContent),
        headline: document.querySelector("#headline").textContent }; })()`));
    { const from = bcdp.events.length; await click(cdp, "#jsonBtn"); th.download = await downloads(bcdp, from, 1); }
    const tj = checkFile(path.join(DL_T, "solver_custom.json"), "json");
    th.json_file = { ...tj, json: undefined };
    if (tj.json) Object.assign(th, { export_seeds: tj.json.spec.seeds, export_presets: tj.json.spec.presets, export_planners: tj.json.spec.planners,
      export_records: tj.json.records_n, ranking: tj.json.ranking.map(r => ({ planner: r.planner, reached: r.reached, n: r.n, no_path: r.no_path,
        wilson: [r.success.lo, r.success.hi].map(v => Math.round(v * 1000) / 1000), median_time_s: r.median_time_s })) });

    // 5. free_path parity on the page's pool (its onDone wrapped for these jobs only)
    const hall = JSON.parse(fs.readFileSync(WORLD, "utf8"));
    const cases = parityCases(hall);
    out.steps.parity = await cdp.eval(`(async () => {
      const SW = await import("./sweep.js?v=20261110g");
      const cases = ${JSON.stringify(cases)}, pool = SOLVER.S.pool, orig = pool.cb.onDone, got = {};
      const all = new Promise(ok => { pool.cb.onDone = (job, res, err) => {
        if (!job.parity) return orig(job, res, err);
        got[job.name] = { worker: res ? res.free_path : null, outcome: res && res.score ? res.score.outcome : null, error: err || null };
        if (Object.keys(got).length === cases.length) ok();
      }; });
      pool.add(cases.map(c => ({ parity: true, name: c.name, world: c.world,
        cfg: { planner: "straight", preset: "ideal", fault: "truth", filter: "none", seed: 0,
          ...(c.radius_m !== 0.15 ? { vehicle: { ...SW.VEHICLE_DEFAULT, radius_m: c.radius_m } } : {}) } })));
      await all;
      pool.cb.onDone = orig;
      return cases.map(c => ({ name: c.name, radius_m: c.radius_m, page: SW.hasFreePath(c.world, c.world.a, c.world.b, c.radius_m), ...got[c.name] }));
    })()`);
    out.parity_agree = out.steps.parity.filter(p => p.worker === p.page).length + "/" + out.steps.parity.length;
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    await sleep(1500);
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch { /* temp dir */ }
    fs.writeFileSync(path.join(HERE, "measure_import.json"), JSON.stringify(out, null, 1) + "\n");
    console.log(JSON.stringify({ ...out, steps: Object.keys(out.steps) }, null, 1));
  }
}
main().catch(err => { console.error(err); process.exit(1); });
