"use strict";
// Feasibility spike (loop-48a): run the hub's real close-area arena (samples/close-area-arena)
// in the browser with Pyodide, time it, stream positions back and draw them.
// No build step. Files to copy into Pyodide come from manifest.json.
//   spike.html            => 2 cases (straight, astar_esdf known map), 1 run each, animated
//   spike.html?bench=1    => 6 cases x (3 streamed runs + 1 run without streaming), for results/measure.mjs
// window.SPIKE_RESULT holds every measurement; window.SPIKE_DONE turns true at the end.

const qs = new URLSearchParams(location.search);
const BENCH = qs.has("bench");
const REPS = Math.max(1, Math.min(10, parseInt(qs.get("reps") || (BENCH ? "3" : "1"), 10) || 1));
const TARGET_RUN_S = 30, TARGET_WALL_S = 15;    // brief: a 30 s run finishes in under ~15 s after load
const CASES = BENCH ? [
  ["straight", "random", 0], ["astar_esdf_known", "random", 0], ["astar_esdf_unknown", "random", 0],
  ["straight", "u_trap", 1], ["astar_esdf_known", "u_trap", 1], ["astar_esdf_unknown", "u_trap", 1],
] : [["straight", "random", 0], ["astar_esdf_known", "random", 0]];

const $ = s => document.querySelector(s);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const nextFrame = () => new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)));
const ms = (a, b) => Math.round((b - a) * 10) / 10;

const R = { page: location.href, ua: navigator.userAgent, started: new Date().toISOString(),
  bench: BENCH, reps: REPS, t: {}, imports: null, env: null, cases: [], memory: [], resources: [], errors: [] };
window.SPIKE_RESULT = R;
window.SPIKE_DONE = false;
window.addEventListener("error", e => R.errors.push(String(e.message || e)));
window.addEventListener("unhandledrejection", e => R.errors.push(String(e.reason && e.reason.stack || e.reason)));

function status(msg) { $("#status").textContent = msg; }

// ---------- Python driver: the only Python in the spike, the rest is the arena itself ----------
// results/measure.mjs extracts this string and runs it under native CPython for the baseline,
// so browser and native time the same calls. Keep it free of backticks and dollar-brace.
const DRIVER_PY = String.raw`
import importlib, json, time
_t0 = time.perf_counter()
import numpy as np
import scipy.ndimage
_t1 = time.perf_counter()
arena_run = importlib.import_module("close_area_arena.run")
world_mod = importlib.import_module("close_area_arena.world")
straight = importlib.import_module("close_area_arena.planners.straight")
astar = importlib.import_module("close_area_arena.planners.astar_esdf")
_t2 = time.perf_counter()
IMPORT_TIMES = {"numpy_scipy_import_ms": round((_t1 - _t0) * 1e3, 1),
                "arena_import_ms": round((_t2 - _t1) * 1e3, 1)}

PLANNERS = {
    "straight": lambda: straight.make(),
    "astar_esdf_known": lambda: astar.make(known_map=True),
    "astar_esdf_unknown": lambda: astar.make(known_map=False),
}


class Tap:
    """pose_source hook (CONTRACT.md): returns truth unchanged, streams (t, x, y) out at planner rate."""
    def __init__(self, emit):
        self.emit = emit
        self.n = 0

    def __call__(self, truth):
        self.emit(truth.t, truth.x, truth.y)
        self.n += 1
        return truth


def env_json():
    import platform, sys, scipy
    return json.dumps({"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                       "machine": platform.machine(), "system": platform.system(), "imports": IMPORT_TIMES})


def bench_case(planner, family, index, seed=0, emit=None):
    cfg = arena_run.DEFAULTS
    t0 = time.perf_counter()
    w = world_mod.make_world(family, seed, index, radius=cfg["vehicle"]["radius"])
    t1 = time.perf_counter()
    p = PLANNERS[planner]()
    tap = Tap(emit) if emit is not None else None
    row, ts, xy = arena_run.run_one(p, w, seed, index, cfg, tap)
    t2 = time.perf_counter()
    sim_s = float(ts[-1])
    run_s = t2 - t1
    path = getattr(p, "path_xy", None)
    replans = getattr(p, "replan_ms", None)
    return json.dumps({
        "planner": planner, "family": family, "seed": seed, "index": index,
        "world_ms": round((t1 - t0) * 1e3, 1), "run_s": round(run_s, 3), "sim_s": round(sim_s, 2),
        "wall_per_sim_s": round(run_s / sim_s, 4) if sim_s > 0 else None,
        "steps_50hz": int(len(ts) - 1), "streamed": tap.n if tap else 0,
        "replans": len(replans) if replans is not None else 0,
        "replan_ms_median": round(float(np.median(replans)), 2) if replans else None,
        "row": row, "world": w.to_dict(),
        "trace": np.round(xy[::5], 3).tolist(),
        "path": None if path is None else np.round(path, 3).tolist(),
    })
`;

// ---------- drawing ----------
function drawCase(cv, c, upto) {
  const g = cv.getContext("2d"), W = cv.width, H = cv.height, w = c.world;
  const [x0, y0, x1, y1] = w.area, s = Math.min(W / (x1 - x0), H / (y1 - y0));
  const X = x => (x - x0) * s, Y = y => H - (y - y0) * s;
  g.fillStyle = css("--panel"); g.fillRect(0, 0, W, H);
  g.strokeStyle = css("--obst"); g.lineWidth = 2; g.strokeRect(1, 1, W - 2, H - 2);
  g.fillStyle = css("--obst");
  for (const [cx, cy, hx, hy] of w.boxes) g.fillRect(X(cx - hx), Y(cy + hy), 2 * hx * s, 2 * hy * s);
  for (const [cx, cy, r] of w.cylinders) { g.beginPath(); g.arc(X(cx), Y(cy), r * s, 0, 2 * Math.PI); g.fill(); }
  if (c.path && c.path.length > 1) {
    g.strokeStyle = css("--ok"); g.setLineDash([4, 4]); g.lineWidth = 1.5; g.beginPath();
    c.path.forEach(([x, y], i) => (i ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y)))); g.stroke(); g.setLineDash([]);
  }
  const pts = c.stream.length ? c.stream : c.trace;   // positions streamed during the run (10 Hz)
  const n = upto == null ? pts.length : Math.min(upto, pts.length);
  g.strokeStyle = css("--accent"); g.lineWidth = 2; g.beginPath();
  for (let i = 0; i < n; i++) { const [x, y] = pts[i]; i ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y)); }
  g.stroke();
  const dot = (x, y, col, r) => { g.fillStyle = col; g.beginPath(); g.arc(X(x), Y(y), r, 0, 2 * Math.PI); g.fill(); };
  dot(0, 0, css("--ok"), 6); dot(w.goal[0], w.goal[1], css("--bad"), 6);
  if (n) dot(pts[n - 1][0], pts[n - 1][1], css("--est"), 4);
}

function animate(cv, c) {
  const n = c.stream.length, speed = 4, t0 = performance.now(), dur = (c.sim_s / speed) * 1e3;
  const frame = now => {
    const k = Math.max(1, Math.round(n * Math.min(1, (now - t0) / dur)));
    drawCase(cv, c, k);
    if (k < n) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}

function addCard(c) {
  const el = document.createElement("figure");
  el.className = "card";
  el.innerHTML = `<canvas width="320" height="320" aria-label="Top-down path of ${esc(c.planner)} on ${esc(c.family)} layout ${c.index}"></canvas>
    <figcaption><b>${esc(c.planner)}</b> on ${esc(c.family)}/${c.index}: ${esc(c.row.outcome)} at ${c.sim_s} s simulated,
    ${c.run_s} s wall (${c.wall_per_sim_s} s per simulated s). ${c.streamed} positions streamed.</figcaption>`;
  $("#cards").appendChild(el);
  const cv = el.querySelector("canvas");
  if (BENCH) drawCase(cv, c); else animate(cv, c);
}

function addRow(c) {
  const tr = document.createElement("tr");
  const proj = c.wall_per_sim_s == null ? "-" : (c.wall_per_sim_s * TARGET_RUN_S).toFixed(2);
  tr.innerHTML = `<td>${esc(c.planner)}</td><td>${esc(c.family)}/${c.index}</td><td>${c.rep}</td><td>${c.stream_on ? "yes" : "no"}</td>
    <td>${esc(c.row.outcome)}</td><td>${c.sim_s}</td><td>${c.run_s}</td><td>${c.wall_per_sim_s}</td><td>${proj}</td><td>${c.world_ms}</td>`;
  $("#rows").appendChild(tr);
}

// ---------- memory and downloads (Chrome only fields are optional) ----------
function memory(label, py) {
  const m = { label };
  try {
    const mod = py && (py._module || (py._api && py._api._module));
    const buf = mod && (mod.HEAP8 || mod.HEAPU8);
    if (buf) m.wasm_heap_mb = Math.round(buf.buffer.byteLength / 1048576);
  } catch (err) { /* private API moved */ }
  if (performance.memory) m.js_heap_used_mb = Math.round(performance.memory.usedJSHeapSize / 1048576);
  R.memory.push(m);
}

function resources() {
  return performance.getEntriesByType("resource")
    .filter(e => /pyodide|\.whl|\.py$|\.zip|\.wasm/.test(e.name))
    .map(e => ({ name: e.name.replace(/^https?:\/\/[^/]+/, ""), host: new URL(e.name).host,
      transfer_kb: Math.round(e.transferSize / 1024), encoded_kb: Math.round(e.encodedBodySize / 1024),
      decoded_kb: Math.round(e.decodedBodySize / 1024), ms: Math.round(e.duration) }));
}

function loadScript(src) {
  return new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = src; s.crossOrigin = "anonymous"; s.onload = ok; s.onerror = () => fail(new Error("could not load " + src));
    document.head.appendChild(s);
  });
}

function summarize() {
  const by = {};
  for (const c of R.cases) {
    const k = `${c.planner} ${c.family}/${c.index}`;
    (by[k] = by[k] || { streamed: [], plain: [] })[c.stream_on ? "streamed" : "plain"].push(c);
  }
  const med = a => { const s = [...a].sort((p, q) => p - q); return s.length ? s[(s.length - 1) >> 1] : null; };
  R.summary = Object.entries(by).map(([k, v]) => {
    const wps = med(v.streamed.map(c => c.wall_per_sim_s));
    const proj = wps == null ? null : Math.round(wps * TARGET_RUN_S * 100) / 100;
    return { case: k, sim_s: v.streamed[0] && v.streamed[0].sim_s, first_run_s: v.streamed[0] && v.streamed[0].run_s,
      median_run_s: med(v.streamed.map(c => c.run_s)), median_wall_per_sim_s: wps,
      no_stream_run_s: v.plain[0] ? v.plain[0].run_s : null,
      projected_30s_run_wall_s: proj, verdict: proj == null ? "n/a" : (proj < TARGET_WALL_S ? "PASS" : "FAIL") };
  });
  const lines = R.summary.map(s => `${s.case}: 30 s run => ${s.projected_30s_run_wall_s} s wall (${s.verdict})`);
  $("#verdict").textContent = `Ready ${R.t.ready_ms} ms after navigation. ` + lines.join("; ");
}

// ---------- main ----------
async function main() {
  const t = R.t;
  status("fetching manifest.json");
  const mUrl = new URL("manifest.json", location.href);
  const m = await (await fetch(mUrl)).json();
  R.pyodide_version = m.pyodide;
  $("#ver").textContent = m.pyodide;

  status(`loading Pyodide ${m.pyodide} from cdn.jsdelivr.net`);
  const a = performance.now();
  await loadScript(m.pyodide_base + "pyodide.js");
  const b = performance.now();
  const py = await loadPyodide({ indexURL: m.pyodide_base });
  const c = performance.now();
  t.pyodide_script_ms = ms(a, b); t.pyodide_init_ms = ms(b, c);
  memory("after loadPyodide", py);

  status("loading numpy + scipy, fetching arena files");
  const fetchFiles = Promise.all(m.files.map(async f => {
    const r = await fetch(new URL(f.src, mUrl));
    if (!r.ok) throw new Error(`${r.status} ${f.src}`);
    return [f.dst, await r.text()];
  }));
  const pk = py.loadPackage(m.packages, { messageCallback: () => {} }).then(() => (t.packages_ms = ms(c, performance.now())));
  const fl = fetchFiles.then(v => ((t.arena_fetch_ms = ms(c, performance.now())), v));
  const [, files] = await Promise.all([pk, fl]);
  const home = "/home/pyodide/";
  for (const [dst, text] of files) {
    py.FS.mkdirTree(home + dst.slice(0, dst.lastIndexOf("/")));
    py.FS.writeFile(home + dst, text);
  }
  R.arena_files = files.length;
  R.arena_bytes = files.reduce((n, [, s]) => n + s.length, 0);
  const d = performance.now();
  t.load_total_ms = ms(a, d);
  memory("after numpy + scipy", py);

  status("importing the arena");
  py.runPython(`import sys\nif "${home}" not in sys.path: sys.path.insert(0, "${home}")`);
  py.runPython(DRIVER_PY);
  const e = performance.now();
  t.import_ms = ms(d, e);
  R.env = JSON.parse(py.globals.get("env_json")());
  t.ready_ms = Math.round(e);            // since navigation start
  memory("after arena import", py);

  const bench = py.globals.get("bench_case");
  const plan = [];
  for (const cs of CASES) {
    for (let r = 1; r <= REPS; r++) plan.push([...cs, r, true]);
    if (BENCH) plan.push([...cs, REPS + 1, false]);
  }
  const first = new Set();
  for (const [planner, family, index, rep, streamOn] of plan) {
    status(`running ${planner} on ${family}/${index} (run ${rep}); the page is frozen while Python runs`);
    await nextFrame();
    const stream = [];
    // undefined => Python None (Pyodide 314 turns JS null into JsNull, which is not None)
    const emit = streamOn ? (tt, x, y) => { stream.push([x, y]); } : undefined;
    const res = JSON.parse(bench(planner, family, index, 0, emit));
    res.rep = rep; res.stream_on = streamOn; res.stream = stream;
    const { stream: _s, trace: _t, path: _p, world: _w, ...slim } = res;
    slim.stream_n = stream.length;
    R.cases.push(slim);
    addRow(res);
    const key = planner + family + index;
    if (!first.has(key) && streamOn) { first.add(key); addCard(res); }
    memory(`after ${planner} ${family}/${index} run ${rep}`, py);
  }
  bench.destroy();
  R.resources = resources();
  summarize();
  status("done");
}

main().catch(err => {
  R.errors.push(String(err && err.stack || err));
  status("failed: " + (err && err.message || err));
}).finally(() => { R.finished = new Date().toISOString(); window.SPIKE_DONE = true; });
