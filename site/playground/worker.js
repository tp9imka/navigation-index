// Playground worker (loop-48b, ES module worker): runs the hub's real close-area arena (samples/close-area-arena) under
// Pyodide in a Web Worker, so the page never freezes while Python computes a run.
// Protocol (postMessage):
//   page => worker  {type: "run", id, world: <close-area-world/1 dict>, cfg: {planner, preset, fault, filter, seed,
//                   recovery, max_time_s}}   max_time_s optional: run time limit override in s, clamped 10-300;
//                   without it the limit comes from world.family (LONG_FAMILIES in DRIVER_PY, as bench.py)
//   worker => page  {type: "progress", stage, step, steps, mb, mb_expected}
//                   {type: "retry", step, attempt, attempts, wait_s, error}   (a load step failed, retrying)
//                   {type: "ready", env, planners, timings}
//                   {type: "result", id, result}  |  {type: "error", id, message}
// Pyodide version, package list and the Python files come from manifest.json (same pin as the spike).
// results/native_parity.mjs extracts DRIVER_PY and runs it under native CPython, so browser and
// native execute the same driver. Keep DRIVER_PY free of backticks and dollar-brace.

const DRIVER_PY = String.raw`
import importlib, json, math, sys, time
import numpy as np

_t0 = time.perf_counter()
import scipy.ndimage
_t1 = time.perf_counter()
P = "close_area_arena."
run_mod = importlib.import_module(P + "run")
WJ = importlib.import_module(P + "world_json")
WC = importlib.import_module(P + "worlds_complex")
presets = importlib.import_module(P + "presets")
estimator = importlib.import_module(P + "estimator")
scorer = importlib.import_module(P + "scorer")
vehicle_mod = importlib.import_module(P + "vehicle")
adapter_mod = importlib.import_module(P + "adapter")
straight = importlib.import_module(P + "planners.straight")
astar = importlib.import_module(P + "planners.astar_esdf")
run_faults = importlib.import_module(P + "run_faults")
_t2 = time.perf_counter()

PLANNERS = {
    "straight": lambda: straight.make(),
    "freest_beam": lambda: run_faults.FreestBeam(),
    "astar_known": lambda: astar.make(known_map=True),
    "astar_unknown": lambda: astar.make(known_map=False),
}
LOAD_ERRORS = {}

# APF and VFH+ (samples/close-area-planner-reactive): offered only if their files import cleanly.
try:
    if REACTIVE_DIR not in sys.path:
        sys.path.insert(0, REACTIVE_DIR)
    _apf = importlib.import_module("apf")
    _vfh = importlib.import_module("vfh_plus")
    PLANNERS["apf"] = lambda: _apf.make()
    PLANNERS["vfh_plus"] = lambda: _vfh.make()
except Exception as e:                       # noqa: BLE001 - report, do not crash the page
    LOAD_ERRORS["reactive"] = repr(e)
_t3 = time.perf_counter()


def _load_sample(folder, names):
    """Import modules of a sample that does "import arena" (each sample has its own arena.py).
    Same recipe as samples/close-area-benchmark/bench.py _load_sample: the folder goes on sys.path
    only while importing, and the short names leave sys.modules afterwards (the objects stay alive).
    The reactive sample's "arena" module is put back, so APF and VFH+ are untouched."""
    short = ["arena"] + list(names)
    saved = {n: sys.modules.pop(n) for n in short if n in sys.modules}
    sys.path.insert(0, folder)
    try:
        return {n: importlib.import_module(n) for n in names}
    finally:
        sys.path.remove(folder)
        for n in short:
            sys.modules.pop(n, None)
        sys.modules.update(saved)


DWA_MEM_S = 3.0                # s of remembered returns, as close-area-benchmark/bench.py
RRT_ITERS = 5000               # Informed RRT* budget, as close-area-benchmark/bench.py


def _bounds(w):
    return (w.xmin, w.ymin, w.xmax, w.ymax)


def _geofenced_dstar(bounds, margin=2.0):
    """bench.py geofenced_dstar: GridReplanner(backend="dstar") with its log-odds map corner on the
    area bounds minus 2 m (same 24 m size), instead of the shipped fixed corner at (-2.5, -2.5)."""
    base_cls = _dsl.GridReplanner

    class GeofencedDStar(base_cls):
        def reset(self):
            super().reset()
            if self.map is not None:
                self.map.x0 = bounds[0] - margin
                self.map.y0 = bounds[1] - margin

    return GeofencedDStar(backend="dstar")


# Planners that need the world (geofence) take it as an argument; the rest ignore it.
WORLD_PLANNERS = set()
# DWA, DWA + 3 s memory, Bug2, TangentBug (samples/close-area-planner-dwa-bug)
try:
    _m = _load_sample(DWABUG_DIR, ["dwa", "bug"])
    _dwa, _bug = _m["dwa"], _m["bug"]
    PLANNERS["dwa"] = lambda: _dwa.make()
    PLANNERS["dwa_mem"] = lambda: _dwa.make(memory_s=DWA_MEM_S)
    PLANNERS["bug2"] = lambda: _bug.make("bug2")
    PLANNERS["tangent_bug"] = lambda: _bug.make("tangent_bug")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["dwa_bug"] = repr(e)
# D* Lite, unknown map, geofenced as in the benchmark (samples/close-area-planner-dstar)
try:
    _dsl = _load_sample(DSTAR_DIR, ["dstar_lite"])["dstar_lite"]
    PLANNERS["dstar_lite"] = lambda w: _geofenced_dstar(_bounds(w))
    WORLD_PLANNERS.add("dstar_lite")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["dstar"] = repr(e)
# Informed RRT*, 5000 samples, known map (samples/close-area-planner-sampling)
try:
    _rrt = _load_sample(SAMPLING_DIR, ["rrt_star"])["rrt_star"]
    PLANNERS["informed_rrt_star"] = lambda: _rrt.make(iters=RRT_ITERS, informed=True, seed=0)
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["sampling"] = repr(e)
# Theta* and Lazy Theta* (samples/close-area-planner-thetastar). Unknown map offered as Lazy only:
# plain Theta* unknown-map replans were 1.88 s p95 in CPython (its README).
try:
    _theta = _load_sample(THETASTAR_DIR, ["thetastar"])["thetastar"]
    PLANNERS["thetastar_known"] = lambda: _theta.make(known_map=True)
    PLANNERS["lazy_thetastar_known"] = lambda: _theta.make(known_map=True, lazy=True)
    PLANNERS["lazy_thetastar_unknown"] = lambda w: _theta.make(known_map=False, lazy=True, bounds=_bounds(w))
    WORLD_PLANNERS.add("lazy_thetastar_unknown")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["thetastar"] = repr(e)
# MPPI, unknown map, geofenced as in the benchmark (samples/close-area-planner-mppi)
try:
    _mppi = _load_sample(MPPI_DIR, ["mppi"])["mppi"]
    PLANNERS["mppi"] = lambda w: _mppi.make(guide="none", bounds=_bounds(w))
    PLANNERS["mppi_astar"] = lambda w: _mppi.make(guide="astar", bounds=_bounds(w))
    WORLD_PLANNERS.update(("mppi", "mppi_astar"))
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["mppi"] = repr(e)
# Hybrid A*, unknown map, geofenced as in the benchmark (samples/close-area-planner-hybrid-astar)
try:
    _ha = _load_sample(HYBRID_DIR, ["hybrid_astar"])["hybrid_astar"]
    PLANNERS["hybrid_astar"] = lambda w: _ha.make(bounds=_bounds(w))
    WORLD_PLANNERS.add("hybrid_astar")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["hybrid_astar"] = repr(e)
# A* + MPC (close-area-planner-mpc) is not offered: it imports osqp, and Pyodide 314.0.7 ships no osqp wheel.
# VIO loss recovery arms (samples/close-area-relocalize, built by pg_reloc.py the run_disambiguate.py way)
pg_reloc = None
try:
    pg_reloc = importlib.import_module("pg_reloc")
    pg_reloc.load(RELOC_DIR, _load_sample)
except Exception as e:                       # noqa: BLE001
    pg_reloc = None
    LOAD_ERRORS["relocalize"] = repr(e)
_t3b = time.perf_counter()

# F2 safety filter (samples/close-area-safety-filter/filters.py, imports scipy.optimize)
filters = None
try:
    if FILTER_DIR not in sys.path:
        sys.path.append(FILTER_DIR)
    filters = importlib.import_module("filters")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["safety_filter"] = repr(e)
_t4 = time.perf_counter()

IMPORT_MS = {"scipy_ndimage": round((_t1 - _t0) * 1e3, 1), "arena": round((_t2 - _t1) * 1e3, 1),
             "reactive": round((_t3 - _t2) * 1e3, 1),
             "sample_planners": round((_t3b - _t3) * 1e3, 1), "safety_filter": round((_t4 - _t3b) * 1e3, 1)}
FILTER_SCAN_EVERY = 3        # physics steps, as close-area-safety-filter/run_kill.py (16.7 Hz filter scan)
# Run time limit (loop-73b): the same table as close-area-benchmark/bench.py LONG_FAMILIES, so a preset
# world gets the limit its benchmark row had. Other families, and worlds without a family, keep
# run.DEFAULTS max_time_s (60 s). A run message may override it with cfg.max_time_s, clamped.
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}
MAX_TIME_CLAMP_S = (10.0, 300.0)


def max_time_for(doc, override=None):
    """(limit s, source) for one run: source "cfg" (override, clamped to MAX_TIME_CLAMP_S),
    "family" (doc["family"] in LONG_FAMILIES) or "default" (run.DEFAULTS)."""
    if override is not None:
        if isinstance(override, bool) or not isinstance(override, (int, float)) or not math.isfinite(override):
            raise ValueError("max_time_s must be a number of seconds")
        lo, hi = MAX_TIME_CLAMP_S
        return min(max(float(override), lo), hi), "cfg"
    fam = doc.get("family")
    if isinstance(fam, str) and fam in LONG_FAMILIES:
        return LONG_FAMILIES[fam], "family"
    return float(run_mod.DEFAULTS["max_time_s"]), "default"


def env_json():
    import platform, scipy
    return json.dumps({"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                       "machine": platform.machine(), "system": platform.system(), "imports_ms": IMPORT_MS,
                       "planners": list(PLANNERS), "presets": [k for k in ("ideal", "crazyflie", "crazyflie_bright")],
                       "faults": ["truth", "none", "jump", "bias", "dropout"],
                       "filters": ["none"] + (["F2"] if filters is not None else []),
                       "recovery": list(pg_reloc.ARMS) if pg_reloc is not None else ["none"],
                       "load_errors": LOAD_ERRORS})


def _r(v, n=3):
    return None if v is None or not math.isfinite(v) else round(float(v), n)


def simulate(doc, planner="astar_known", preset="ideal", fault="truth", filt="none", seed=0, cfg=None,
             recovery="none", max_time_s=None):
    """Fly one world. Same loop as run.run_one (filter off) or run_kill.run_one (F2 on), with the
    sensor preset and pose source as arguments. Scored by scorer.score on truth.
    fault: "truth" = no estimator (planner sees truth); else estimator.py VIO EKF with dark zones and
    faults.py case fault ("none" = no fault).
    recovery (pg_reloc.ARMS): with fault jump or dropout, wrap the estimator in a relocalization arm
    of samples/close-area-relocalize; the arm brings its own planner (A* known map behind the hover
    gate), so planner must be astar_known and the filter none.
    max_time_s: None = by world family (max_time_for), else the run time limit in s (clamped 10-300)."""
    cfg = cfg or run_mod.DEFAULTS
    t_max, t_max_src = max_time_for(doc, max_time_s)
    if recovery != "none":
        if pg_reloc is None:
            raise RuntimeError("relocalization did not load: " + LOAD_ERRORS.get("relocalize", "?"))
        if fault not in pg_reloc.FAULTS:
            raise ValueError("VIO loss recovery needs the jump or dropout fault")
        if planner != "astar_known" or filt != "none":
            raise ValueError("VIO loss recovery flies A* known map without a filter (as run_disambiguate.py)")
    t_start = time.perf_counter()
    w = WJ.from_json(doc)
    idx = doc.get("index")
    index = idx if isinstance(idx, int) and not isinstance(idx, bool) else 0
    radius = cfg["vehicle"]["radius"]
    free = bool(WC.has_free_path(w, radius))
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    veh = vehicle_mod.Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **cfg["vehicle"])
    sensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 7]))   # run.py noise stream
    est = None
    if fault != "truth":
        est = estimator.make_pose_source_factory(fault, dark=True)(w, seed, index)
    src, trace = est, None
    if recovery != "none":
        src, pl = pg_reloc.build(recovery, w, est, seed, index)
        trace = pg_reloc.Trace(recovery, src)
    else:
        pl = PLANNERS[planner](w) if planner in WORLD_PLANNERS else PLANNERS[planner]()
        if pg_reloc is not None and fault in pg_reloc.FAULTS and filt == "none":
            trace = pg_reloc.Trace("none", est)      # verdict strip only: lost while quality is 0
    ad = adapter_mod.SimAdapter(w, veh, sensor, pose_source=src)
    pl.reset()
    f = None
    if filt == "F2":
        if filters is None:
            raise RuntimeError("safety filter did not load: " + LOAD_ERRORS.get("safety_filter", "?"))
        f = filters.make("F2")
        fsensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 8]))   # run_kill.py filter stream
    elif filt != "none":
        raise ValueError("filter must be none or F2")
    HZ, DT = vehicle_mod.HZ, vehicle_mod.DT
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(t_max * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    grid = w.grid if getattr(pl, "uses_grid", False) else None
    ts, xy = [0.0], [(0.0, 0.0)]
    frames, paths = [], []
    last_path = None
    sp_nom, fscan, scan = None, None, None
    n_int = n_f = 0
    iv_window = 0
    max_err = 0.0
    errs = []
    pose = tr = None
    for k in range(n_steps):
        if f is not None:                       # run_kill.py: estimate every physics step
            pose = ad.pose()
            tr = ad.truth()
            max_err = max(max_err, math.hypot(pose.x - tr.x, pose.y - tr.y))
        if k % ratio == 0:
            if f is None:                       # run.py: estimate at planner steps
                pose = ad.pose()
                tr = ad.truth()
                max_err = max(max_err, math.hypot(pose.x - tr.x, pose.y - tr.y))
                if trace is not None:
                    trace.frame(pose, tr.t)
            scan = ad.ranges()
            sp_nom = pl.step(pose, scan, goal, grid, pdt)
            if f is None:
                ad.send_setpoint(sp_nom)
            e = math.hypot(pose.x - tr.x, pose.y - tr.y)
            errs.append(e)
            frames.append([round(tr.t, 3), round(tr.x, 3), round(tr.y, 3), round(tr.yaw, 3),
                           round(pose.x, 3), round(pose.y, 3), _r(pose.sigma_xy, 3), int(pose.quality),
                           iv_window, [_r(d, 2) for d in scan.distances]])
            iv_window = 0
            pth = getattr(pl, "path_xy", None)
            if pth is not None and pth is not last_path:
                paths.append([round(tr.t, 3), np.round(pth, 2).tolist()])
            elif pth is None and last_path is not None:
                paths.append([round(tr.t, 3), None])
            last_path = pth
        if f is not None:
            if k % FILTER_SCAN_EVERY == 0:
                fscan = fsensor.scan(w, veh.p[0], veh.p[1], veh.yaw, veh.t)
            health = {"t": pose.t, "quality": pose.quality, "reset_counter": pose.reset_counter,
                      "sigma_xy": pose.sigma_xy, "belief": est.belief() if est is not None else None, "uwb": None}
            sp, intervened = f.filter(sp_nom, pose, fscan, w, health, DT)
            n_f += 1
            n_int += int(intervened)
            iv_window += int(intervened)
            ad.send_setpoint(sp)
        ad.tick()
        px, py = float(veh.p[0]), float(veh.p[1])
        ts.append(veh.t)
        xy.append((px, py))
        if math.hypot(px - goal[0], py - goal[1]) <= scorer.GOAL_TOL:
            break
        if w.clearance(px, py) < radius:
            break
        if len(xy) > lag and math.hypot(px - xy[-1 - lag][0], py - xy[-1 - lag][1]) < scorer.STUCK_DIST:
            break
    res = scorer.score(ts, xy, w, goal, radius)
    res.update({"index": index, "n_obstacles": len(w.boxes) + len(w.cylinders),
                "goal": [round(goal[0], 3), round(goal[1], 3)], "max_pose_error_m": round(max_err, 4)})
    if errs:
        res["est_err_median_m"] = round(float(np.median(errs)), 4)
    if f is not None:
        res["intervention_frac"] = round(n_int / max(n_f, 1), 4)
    xy_a = np.asarray(xy)
    clr = w.sdf(xy_a[::ratio])                 # truth clearance at planner rate, for the sparkline
    return {
        "config": {"planner": planner, "preset": preset, "fault": fault, "filter": filt, "seed": seed, "index": index,
                   "recovery": recovery},
        "reloc": trace.result(res, est) if trace is not None else None,
        "score": res, "free_path": free,
        "wall_s": round(time.perf_counter() - t_start, 3), "sim_s": round(float(ts[-1]), 2),
        "max_time_s": t_max, "max_time_source": t_max_src,
        "hz": cfg["plan_hz"], "radius": radius, "goal_tol_m": scorer.GOAL_TOL,
        "offset": [float(-w.xmin + doc["bounds"][0]), float(-w.ymin + doc["bounds"][1])],
        "scan_angles": [round(a, 4) for a in scan.angles] if scan is not None else [],
        "max_range": float(scan.max_range) if scan is not None else None,
        "frames": frames,
        "end": [round(float(ts[-1]), 3), round(float(xy_a[-1, 0]), 3), round(float(xy_a[-1, 1]), 3)],
        "clearance": [round(float(c), 3) for c in clr],
        "paths": paths,
        "dark_zones": [z.to_list() for z in est.zones] if est is not None else [],
        "fault_log": est.fault.log if est is not None and est.fault is not None else None,
    }


def play(doc_json, cfg_json):
    c = json.loads(cfg_json)
    out = simulate(json.loads(doc_json), c.get("planner", "astar_known"), c.get("preset", "ideal"),
                   c.get("fault", "truth"), c.get("filter", "none"), int(c.get("seed", 0)),
                   recovery=c.get("recovery", "none"), max_time_s=c.get("max_time_s"))
    return json.dumps(out, allow_nan=False)
`;

const HOME = "/home/pyodide/";
let py = null, play = null, ready = null;
let mbDone = 0;

function progress(stage, step, steps, extra) { postMessage({ type: "progress", stage, step, steps, mb: Math.round(mbDone * 10) / 10, ...extra }); }

function watchDownloads(expected) {
  try {
    new PerformanceObserver(list => {
      for (const e of list.getEntries()) mbDone += (e.transferSize || e.encodedBodySize || 0) / 1048576;
      progress(null, null, null, { mb_expected: expected });
    }).observe({ type: "resource", buffered: true });
  } catch (err) { /* no PerformanceObserver in this worker: stage progress only */ }
}

// Load retries (loop-63, dry-run blocker 7: one cold load stalled 122 s, then "Failed to fetch").
// Every load step is named and gets ATTEMPTS tries, with BACKOFF_S waits between them. A step that
// does not finish within TIMEOUT_S counts as a failed attempt. After the last attempt the page shows
// a Retry button, which starts a new worker (that also drops any fetch that still hangs).
const ATTEMPTS = 3, BACKOFF_S = [2, 6];
const TIMEOUT_S = { manifest: 20, source: 10, runtime: 120, files: 30, packages: 180 };
const attemptsLog = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const errText = err => String(err && err.message || err);

function withTimeout(p, s, name) {
  let timer;
  return Promise.race([p, new Promise((_, fail) => { timer = setTimeout(() => fail(new Error(`${name} timed out after ${s} s`)), s * 1000); })])
    .finally(() => clearTimeout(timer));
}

async function step(name, key, fn) {
  for (let i = 1; ; i++) {
    const t0 = performance.now();
    try {
      const out = await withTimeout(fn(i), TIMEOUT_S[key], name);
      attemptsLog.push({ step: name, attempt: i, ok: true, ms: Math.round(performance.now() - t0) });
      return out;
    } catch (err) {
      const msg = errText(err);
      attemptsLog.push({ step: name, attempt: i, ok: false, ms: Math.round(performance.now() - t0), error: msg });
      if (i >= ATTEMPTS) throw new Error(`${name}: ${i} of ${ATTEMPTS} attempts failed, last error: ${msg}`);
      const wait = BACKOFF_S[i - 1];
      postMessage({ type: "retry", step: name, attempt: i, attempts: ATTEMPTS, wait_s: wait, error: msg });
      await sleep(wait * 1000);
    }
  }
}

async function fetchT(url, s, opts) {         // fetch with a real abort after s seconds
  const ac = new AbortController(), timer = setTimeout(() => ac.abort(new Error(`timed out after ${s} s`)), s * 1000);
  try {
    const r = await fetch(url, { cache: "no-cache", ...opts, signal: ac.signal });
    if (!r.ok) throw new Error(`HTTP ${r.status} ${url}`);
    return r;
  } finally { clearTimeout(timer); }
}

// Where Pyodide comes from. manifest.json "pyodide_source": "cdn" (pyodide_base), "local" (pyodide_local,
// relative to the manifest) or "auto" (local when <pyodide_local>pyodide.mjs answers, else cdn).
// The page URL can override it: ?pyodide=cdn|local|auto (playground.js passes it to the worker).
async function pickSource(m, mUrl) {
  const want = new URL(self.location.href).searchParams.get("pyodide") || m.pyodide_source || "cdn";
  const local = m.pyodide_local ? new URL(m.pyodide_local, mUrl).href : null;
  if (want === "local" || want === "auto") {
    let found = false;
    if (local) {
      try { await fetchT(local + "pyodide.mjs", TIMEOUT_S.source, { method: "HEAD" }); found = true; } catch (err) { /* not vendored */ }
    }
    if (found) return { source: "local", base: local };
    if (want === "local") throw new Error(`pyodide_source is local, but ${local}pyodide.mjs is missing (README: Offline / blocked CDN)`);
  }
  return { source: "cdn", base: m.pyodide_base };
}

async function init() {
  const t = {}, T0 = performance.now(), ms = a => Math.round(performance.now() - a);
  const mUrl = new URL("manifest.json", self.location.href);
  const STEPS = 4;
  // revalidate: a cached manifest or .py from an older deploy breaks imports silently
  const m = await step("manifest.json", "manifest", async () => (await fetchT(mUrl, TIMEOUT_S.manifest)).json());
  const exp = m.expected_download_mb;
  watchDownloads(exp);
  const src = await pickSource(m, mUrl);
  const where = src.source === "local" ? "local folder " + m.pyodide_local : "cdn.jsdelivr.net";
  progress(`Pyodide ${m.pyodide} runtime (wasm + Python stdlib, about 6 MB) from ${where}`, 1, STEPS, { mb_expected: exp });
  // Module worker: importScripts of the CDN pyodide.js failed in Chrome 140 (NetworkError), and
  // pyodide.mjs refuses classic workers, so worker.js is started with {type: "module"}.
  // A retry imports pyodide.mjs with ?attempt=N: a failed module import can stay cached under its URL.
  const runtime = async i => {
    const { loadPyodide } = await import(src.base + "pyodide.mjs" + (i > 1 ? `?attempt=${i}` : ""));
    return loadPyodide({ indexURL: src.base });
  };
  py = await step("Pyodide runtime", "runtime", runtime);
  t.pyodide_ms = ms(T0);
  progress(`numpy + scipy wheels (about 16 MB) from ${where}, and the hub .py files`, 2, STEPS, { mb_expected: exp });
  const a = performance.now();
  const texts = new Map();
  await step("hub .py files", "files", () => Promise.all(m.files.filter(f => !texts.has(f.dst)).map(async f => {
    texts.set(f.dst, await (await fetchT(new URL(f.src, mUrl), TIMEOUT_S.files)).text());
  })));
  let timedOut = false;
  await step("numpy + scipy wheels", "packages", async i => {
    // a timed-out loadPackage may still hold Pyodide's package lock: start a fresh runtime first
    if (i > 1 && timedOut) py = await runtime(i);
    timedOut = true;
    const errs = [];
    await py.loadPackage(m.packages, { messageCallback: () => {}, errorCallback: e => errs.push(String(e)) });
    timedOut = false;
    const missing = m.packages.filter(p => !(p in py.loadedPackages));
    if (missing.length) throw new Error(`not loaded: ${missing.join(", ")}${errs.length ? " (" + errs.slice(-2).join("; ") + ")" : ""}`);
  });
  for (const f of m.files) {
    py.FS.mkdirTree(HOME + f.dst.slice(0, f.dst.lastIndexOf("/") + 1));
    py.FS.writeFile(HOME + f.dst, texts.get(f.dst));
  }
  t.packages_ms = ms(a);
  progress("importing the arena, planners, safety filter and relocalizer", 3, STEPS, { mb_expected: exp });
  const b = performance.now();
  py.runPython(`import sys\nif "${HOME}" not in sys.path: sys.path.insert(0, "${HOME}")\n` +
    `REACTIVE_DIR = "${HOME}reactive"\nFILTER_DIR = "${HOME}safety_filter"\n` +
    `DWABUG_DIR = "${HOME}dwa_bug"\nDSTAR_DIR = "${HOME}dstar"\nSAMPLING_DIR = "${HOME}sampling"\nRELOC_DIR = "${HOME}reloc"\n` +
    `THETASTAR_DIR = "${HOME}thetastar"\nMPPI_DIR = "${HOME}mppi"\nHYBRID_DIR = "${HOME}hybrid_astar"`);
  py.runPython(DRIVER_PY);
  t.import_ms = ms(b);
  t.ready_ms = ms(T0);
  play = py.globals.get("play");
  const env = JSON.parse(py.globals.get("env_json")());
  env.pyodide = m.pyodide;
  env.pyodide_source = src.source;
  env.pyodide_base = src.base;
  env.arena_files = m.files.length;
  env.load_attempts = attemptsLog;
  progress("ready", STEPS, STEPS, { mb_expected: exp });
  postMessage({ type: "ready", env, timings: t, mb: Math.round(mbDone * 10) / 10 });
}

function runOne(msg) {
  const t0 = performance.now();
  try {
    const out = JSON.parse(play(JSON.stringify(msg.world), JSON.stringify(msg.cfg || {})));
    out.worker_ms = Math.round(performance.now() - t0);
    postMessage({ type: "result", id: msg.id, result: out });
  } catch (err) {
    const text = String(err && err.message || err);
    postMessage({ type: "error", id: msg.id, message: text.split("\n").filter(Boolean).slice(-3).join("\n") });
  }
}

ready = init().catch(err => {
  postMessage({ type: "error", id: null, fatal: true, message: "load failed: " + errText(err), attempts: attemptsLog });
  throw err;
});

self.onmessage = async ev => {
  const msg = ev.data || {};
  if (msg.type !== "run") return;
  try { await ready; } catch (err) { return; }
  runOne(msg);
};
