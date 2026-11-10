// Playground worker (loop-48b, ES module worker): runs the hub's real close-area arena (samples/close-area-arena) under
// Pyodide in a Web Worker, so the page never freezes while Python computes a run.
// Protocol (postMessage):
//   page => worker  {type: "run", id, world: <close-area-world/1 dict>, cfg: {planner, preset, fault, filter, seed,
//                   recovery, max_time_s, vehicle, sensor}}   max_time_s optional: run time limit override in s,
//                   clamped 10-300; without it the limit comes from world.family (LONG_FAMILIES in DRIVER_PY, as bench.py)
//                   vehicle optional (loop-75): {radius_m, v_max, a_max, tau}, all four, each clamped to VEHICLE_CLAMP;
//                   without it run.DEFAULTS["vehicle"]. sensor optional: {beams, fov_deg, max_range_m, min_range_m,
//                   noise_sigma_m, cone_deg?, dropout?}, clamped to SENSOR_CLAMP; it replaces cfg.preset (which
//                   is then reported as "custom"). Unknown or missing keys => error naming them
//                   (samples/close-area-arena/presets.py). The result carries "vehicle" and "sensor" as flown
//                   (after clamping, with a "clamped" list).
//                   loop-75b: cfg.yaw optional, "fixed" (default, every sensor) | "look_where_you_go"; the result
//                   carries it as "yaw" (and config.yaw). Every planner inflates obstacles by the flown
//                   vehicle radius_m for that run (radius_override in DRIVER_PY, restored after the run); the
//                   result's "inflation" lists the constants set and the planners that have no radius term.
//                   astar_unknown is geofenced (map corner on the area bounds - 2 m), as close-area-benchmark.
//   worker => page  {type: "progress", stage, step, steps, mb, mb_expected}
//                   {type: "retry", step, attempt, attempts, wait_s, error}   (a load step failed, retrying)
//                   {type: "ready", env, planners, timings}
//                   {type: "result", id, result}  |  {type: "error", id, message}
// Pyodide version, package list and the Python files come from manifest.json (same pin as the spike).
// results/native_parity.mjs extracts DRIVER_PY and runs it under native CPython, so browser and
// native execute the same driver. Keep DRIVER_PY free of backticks and dollar-brace.

const DRIVER_PY = String.raw`
import copy, importlib, json, math, sys, time
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

class GeofencedAStar(astar.AStarESDF):
    """close-area-benchmark bench.py GeofencedAStar (loop-75b): astar_esdf(known_map=False) with its
    log-odds map corner on the area bounds minus 2 m (same 24 m size), instead of the shipped fixed
    corner at (-2.5, -2.5), which left office_0's B outside the map. Subclass built here, sample not edited."""

    def __init__(self, bounds, margin=2.0):
        self.bounds, self.margin = bounds, margin
        super().__init__(known_map=False)

    def reset(self):
        super().reset()
        if self.map is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin


PLANNERS = {
    "straight": lambda: straight.make(),
    "freest_beam": lambda: run_faults.FreestBeam(),
    "astar_known": lambda: astar.make(known_map=True),
    "astar_unknown": lambda w: GeofencedAStar(_bounds(w)),
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
WORLD_PLANNERS = {"astar_unknown"}
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


# Sensor presets offered by the page (loop-75 adds the two team-facing ones from presets.SENSOR_SPECS).
PG_PRESETS = ("ideal", "crazyflie", "crazyflie_bright", "depth_cam_87", "lidar_2d")
# Custom vehicle / sensor from a run message (loop-75): sane ranges, values outside are clamped and
# listed in the result's "clamped". presets.py then checks the clamped dict (keys, types, min < max).
VEHICLE_CLAMP = {"radius_m": (0.05, 0.6), "v_max": (0.1, 5.0), "a_max": (0.5, 20.0), "tau": (0.02, 1.0)}
SENSOR_CLAMP = {"beams": (1, 360), "fov_deg": (1.0, 360.0), "max_range_m": (0.5, 30.0), "min_range_m": (0.0, 5.0),
                "noise_sigma_m": (0.0, 0.5), "cone_deg": (0.0, 30.0), "dropout": (0.0, 0.5)}
MIN_RANGE_GAP_M = 0.1         # min_range_m is clamped to at most max_range_m - 0.1
# Look-where-you-go yaw (loop-75). The range fan is body frame and the planners command yaw_rate 0, so a
# forward-only sensor would stare at the initial goal bearing all run. With cfg.yaw = "look_where_you_go"
# the driver sets the setpoint's yaw rate: face the commanded velocity, or the goal when slower than
# YAW_SLOW_MPS, proportional with YAW_GAIN, capped at YAW_RATE_CAP. loop-75b: opt-in for every sensor (it was
# on by default for fov < 360 deg in loop-75); fixed yaw was faster in 4 of 4 office_0 / maze_0 runs
# (samples/close-area-arena/results/custom_sensor_0.md).
YAW_RATE_CAP = 1.0            # rad/s (57 deg/s) [proposal], half of vehicle.Vehicle yaw_rate_max 2.0
YAW_GAIN = 2.0                # 1/s, yaw rate per rad of heading error [proposal]
YAW_SLOW_MPS = 0.2            # m/s, below this commanded speed face the goal [proposal]
FULL_FOV = 2 * math.pi - 1e-9
YAW_OPTIONS = ("fixed", "look_where_you_go")   # cfg.yaw (loop-75b), default "fixed" for every sensor

# Vehicle radius in the planners (loop-75b). The planner samples hardcode the 0.15 m arena radius as module
# constants (or constructor defaults). When a run flies another radius_m, every planner below inflates by it:
# each constant is set to radius_m + (its shipped value - 0.15 m), so the planner's own margins on top of the
# radius stay as shipped, for that run only, and restored after it (radius_override). At 0.15 m nothing is touched.
RADIUS_DEFAULT = float(run_mod.DEFAULTS["vehicle"]["radius"])
RADIUS_CONSTS = [                # (module global name in this driver, attribute, what it is)
    ("astar", "RADIUS", "A* known / unknown map, D* Lite, Theta*, Lazy Theta*, MPPI-A* guide, relocalization arms: inflation"),
    ("astar", "CARROT_CLEAR_M", "astar_esdf carrot chord clearance, RADIUS + TRACK_MARGIN at import"),
    ("_ha", "RADIUS", "Hybrid A*: inflation (copied from astar_esdf at import)"),
    ("_rrt", "RADIUS", "Informed RRT*: inflation (copied from astar_esdf at import)"),
    ("_mppi", "R_COLL", "MPPI: collision distance (astar_esdf.RADIUS at import)"),
    ("_mppi", "D_SAFE", "MPPI: distance where the obstacle cost starts (0.25 m beyond the radius as shipped)"),
    ("_dwa", "RADIUS", "DWA, DWA + memory: rollout clearance"),
    ("_bug", "RADIUS", "Bug2, TangentBug: wall distance, hit and free-segment tests"),
]
RADIUS_NOT_REACHED = {
    "straight": "flies the straight line to B, has no obstacle model",
    "freest_beam": "fixed 1.0 m free-beam and 0.6 m repulsion thresholds, no radius term",
}


def _radius_table():
    """[(module, attr, offset, note)] for the loaded modules, deduplicated by module identity."""
    out, seen = [], set()
    g = globals()
    for name, attr, note in RADIUS_CONSTS:
        mod = g.get(name)
        if mod is None or not hasattr(mod, attr) or (id(mod), attr) in seen:
            continue
        seen.add((id(mod), attr))
        out.append((mod, attr, float(getattr(mod, attr)) - RADIUS_DEFAULT, name.lstrip("_") + "." + attr))
    return out


RADIUS_TABLE = _radius_table()


class radius_override:
    """with radius_override(r): the RADIUS_TABLE constants = r + offset; restored on exit, also after an error."""

    def __init__(self, r):
        self.r, self.saved = float(r), []

    def __enter__(self):
        if self.r != RADIUS_DEFAULT:
            self.saved = [(m, a, getattr(m, a)) for m, a, _, _ in RADIUS_TABLE]
            for m, a, off, _ in RADIUS_TABLE:
                setattr(m, a, round(self.r + off, 9))
        return self

    def __exit__(self, *exc):
        for m, a, v in self.saved:
            setattr(m, a, v)
        self.saved = []
        return False

    def record(self):
        if self.r == RADIUS_DEFAULT:
            return {"radius_m": self.r, "set": {}, "instance": {}, "not_reached": dict(RADIUS_NOT_REACHED)}
        return {"radius_m": self.r, "set": {lbl: round(self.r + off, 9) for _, _, off, lbl in RADIUS_TABLE},
                "instance": {"apf": "APF.radius = radius_m", "vfh_plus": "VFHPlus.r_rs = radius_m + d_s (0.1 m)"},
                "not_reached": dict(RADIUS_NOT_REACHED)}


def build_planner(planner, w, r=RADIUS_DEFAULT):
    """PLANNERS[planner] for world w; inside radius_override(r) for a non-default radius. APF and VFH+ keep the
    radius on the instance (constructor default 0.15 m), so they are set here, per run."""
    pl = PLANNERS[planner](w) if planner in WORLD_PLANNERS else PLANNERS[planner]()
    if r != RADIUS_DEFAULT:
        if planner == "apf":
            pl.radius = r
        elif planner == "vfh_plus":
            pl.r_rs = round(pl.r_rs - RADIUS_DEFAULT + r, 9)
    return pl


def _clamp_spec(spec, required, defaults, ranges, what):
    """(clamped dict with defaults filled, list of {key, asked, flown}) for a run-message dict."""
    presets.check_keys(spec, required, defaults, what)
    s = dict(defaults, **spec)
    out, changed = {}, []
    for k, v in s.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError(what + " " + k + " must be a finite number, got " + repr(v))
        lo, hi = ranges[k]
        c = min(max(v, lo), hi)
        if k == "beams":
            c = int(round(c))
        if c != v:
            changed.append({"key": k, "asked": v, "flown": c})
        out[k] = c
    if "min_range_m" in out and out["min_range_m"] > out["max_range_m"] - MIN_RANGE_GAP_M:
        c = round(out["max_range_m"] - MIN_RANGE_GAP_M, 6)
        changed = [x for x in changed if x["key"] != "min_range_m"]
        changed.append({"key": "min_range_m", "asked": s["min_range_m"], "flown": c})
        out["min_range_m"] = c
    return out, changed


def clamp_vehicle(spec):
    return _clamp_spec(spec, presets.VEHICLE_SPEC_KEYS, {}, VEHICLE_CLAMP, "vehicle")


def clamp_sensor(spec):
    return _clamp_spec(spec, presets.SENSOR_SPEC_REQUIRED, presets.SENSOR_SPEC_DEFAULTS, SENSOR_CLAMP, "sensor")


def look_where_you_go(sp, pose, goal):
    """Yaw rate (rad/s) toward the commanded velocity, or the goal when slow, from the pose the planner saw."""
    if math.hypot(sp.vx, sp.vy) >= YAW_SLOW_MPS:
        target = math.atan2(sp.vy, sp.vx)
    else:
        target = math.atan2(goal[1] - pose.y, goal[0] - pose.x)
    err = (target - pose.yaw + math.pi) % (2 * math.pi) - math.pi
    return max(-YAW_RATE_CAP, min(YAW_RATE_CAP, YAW_GAIN * err))


def env_json():
    import platform, scipy
    return json.dumps({"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                       "machine": platform.machine(), "system": platform.system(), "imports_ms": IMPORT_MS,
                       "planners": list(PLANNERS), "presets": [k for k in PG_PRESETS],
                       "faults": ["truth", "none", "jump", "bias", "dropout"],
                       "filters": ["none"] + (["F2"] if filters is not None else []),
                       "yaw": list(YAW_OPTIONS), "radius_consts": [lbl for _, _, _, lbl in RADIUS_TABLE],
                       "recovery": list(pg_reloc.ARMS) if pg_reloc is not None else ["none"],
                       "load_errors": LOAD_ERRORS})


def _r(v, n=3):
    return None if v is None or not math.isfinite(v) else round(float(v), n)


def simulate(doc, planner="astar_known", preset="ideal", fault="truth", filt="none", seed=0, cfg=None,
             recovery="none", max_time_s=None, vehicle=None, sensor=None, yaw="fixed", yaw_policy=None, inflate=True):
    """_simulate inside radius_override(vehicle radius_m): the planners inflate by the flown radius for this
    run only. inflate=False (native before/after comparison only, the run message has no such field) keeps
    the shipped 0.15 m constants, as before loop-75b."""
    r = clamp_vehicle(vehicle)[0]["radius_m"] if vehicle is not None else RADIUS_DEFAULT
    ov = radius_override(r if inflate else RADIUS_DEFAULT)
    with ov:
        out = _simulate(doc, planner, preset, fault, filt, seed, cfg, recovery, max_time_s, vehicle, sensor,
                        yaw, yaw_policy, ov.r)
    out["inflation"] = ov.record()
    return out


def _simulate(doc, planner="astar_known", preset="ideal", fault="truth", filt="none", seed=0, cfg=None,
              recovery="none", max_time_s=None, vehicle=None, sensor=None, yaw="fixed", yaw_policy=None,
              plan_radius=RADIUS_DEFAULT):
    """Fly one world. Same loop as run.run_one (filter off) or run_kill.run_one (F2 on), with the
    sensor preset and pose source as arguments. Scored by scorer.score on truth.
    fault: "truth" = no estimator (planner sees truth); else estimator.py VIO EKF with dark zones and
    faults.py case fault ("none" = no fault).
    recovery (pg_reloc.ARMS): with fault jump or dropout, wrap the estimator in a relocalization arm
    of samples/close-area-relocalize; the arm brings its own planner (A* known map behind the hover
    gate), so planner must be astar_known and the filter none.
    max_time_s: None = by world family (max_time_for), else the run time limit in s (clamped 10-300).
    vehicle / sensor (loop-75): None, or a team-facing dict (presets.py schema), clamped by clamp_vehicle /
    clamp_sensor; sensor replaces preset. yaw (loop-75b, run message cfg.yaw): "fixed" (default, every sensor)
    = yaw rate 0 from the driver, the vehicle keeps its initial bearing to B; "look_where_you_go" = the
    look_where_you_go policy below, for any sensor. yaw_policy (loop-75, native scripts only, overrides yaw when
    given): "auto" = look_where_you_go when the sensor fov < 360 deg, "off" = fixed.
    plan_radius: the radius the planners were set to by simulate (radius_override), for the APF / VFH+ instances."""
    cfg = cfg or run_mod.DEFAULTS
    t_max, t_max_src = max_time_for(doc, max_time_s)
    veh_rec = dict(presets.vehicle_spec({"radius_m": cfg["vehicle"]["radius"], "v_max": cfg["vehicle"]["v_max"],
                                         "a_max": cfg["vehicle"]["a_max"], "tau": cfg["vehicle"]["tau"]}),
                   source="default", clamped=[])
    if vehicle is not None:
        vs, vch = clamp_vehicle(vehicle)
        cfg = dict(cfg, vehicle=presets.vehicle_kwargs(vs))
        veh_rec = dict(presets.vehicle_spec(vs), source="cfg", clamped=vch)
    if sensor is not None:
        ss, sch = clamp_sensor(sensor)
        sens = presets.sensor_spec(ss)
        preset = "custom"
        sens_rec = dict(presets.describe_sensor(sens), clamped=sch)
    else:
        sens = preset
        sens_rec = dict(presets.describe_sensor(preset), clamped=[])
    if yaw_policy is not None:
        if yaw_policy not in ("auto", "off"):
            raise ValueError("yaw_policy must be auto or off")
        yaw_on = yaw_policy == "auto" and presets.sensor_fov(sens) < FULL_FOV
    else:
        if yaw not in YAW_OPTIONS:
            raise ValueError("cfg.yaw must be fixed or look_where_you_go, got " + repr(yaw))
        yaw_on = yaw == "look_where_you_go"
    yaw_flown = "look_where_you_go" if yaw_on else "fixed"
    sens_rec["yaw_policy"] = "look_where_you_go" if yaw_on else "off"
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
    sensor = presets.make_sensor(sens, np.random.default_rng([seed, index, 7]))   # run.py noise stream
    est = None
    if fault != "truth":
        est = estimator.make_pose_source_factory(fault, dark=True)(w, seed, index)
    src, trace = est, None
    if recovery != "none":
        src, pl = pg_reloc.build(recovery, w, est, seed, index)
        trace = pg_reloc.Trace(recovery, src)
    else:
        pl = build_planner(planner, w, plan_radius)
        if pg_reloc is not None and fault in pg_reloc.FAULTS and filt == "none":
            trace = pg_reloc.Trace("none", est)      # verdict strip only: lost while quality is 0
    ad = adapter_mod.SimAdapter(w, veh, sensor, pose_source=src)
    pl.reset()
    f = None
    if filt == "F2":
        if filters is None:
            raise RuntimeError("safety filter did not load: " + LOAD_ERRORS.get("safety_filter", "?"))
        f = filters.make("F2")
        fsensor = presets.make_sensor(sens, np.random.default_rng([seed, index, 8]))   # run_kill.py filter stream
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
            if yaw_on:                          # copy: planners may keep the setpoint they returned
                sp_nom = copy.copy(sp_nom)
                sp_nom.yaw_rate = look_where_you_go(sp_nom, pose, goal)
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
                   "recovery": recovery, "yaw": yaw_flown},
        "yaw": yaw_flown,
        "reloc": trace.result(res, est) if trace is not None else None,
        "vehicle": veh_rec, "sensor": sens_rec,
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
                   recovery=c.get("recovery", "none"), max_time_s=c.get("max_time_s"),
                   vehicle=c.get("vehicle"), sensor=c.get("sensor"), yaw=c.get("yaw", "fixed"))
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

// cfg.vehicle / cfg.sensor (loop-75) must be plain objects when present; DRIVER_PY checks keys and clamps values.
function checkCfg(cfg) {
  for (const k of ["vehicle", "sensor"]) {
    const v = cfg[k];
    if (v !== undefined && v !== null && (typeof v !== "object" || Array.isArray(v)))
      throw new Error(`cfg.${k} must be an object, got ${Array.isArray(v) ? "array" : typeof v}`);
  }
}

function runOne(msg) {
  const t0 = performance.now();
  try {
    checkCfg(msg.cfg || {});
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
