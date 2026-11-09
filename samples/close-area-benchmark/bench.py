"""Benchmark matrix: every close-area planner in the hub x every arena family x two sensor presets.

.venv/bin/python bench.py --layouts 20 --seed 0 --workers 14     # full matrix, results/matrix_0.*

Planners (imported by path from their samples, nothing edited there):
  straight            close-area-arena planners/straight.py (floor)
  freest_beam         close-area-arena run_faults.FreestBeam (CONTRACT.md example)
  apf_escape          close-area-planner-reactive apf.make() (APF + wall-follow escape)
  vfh_plus            close-area-planner-reactive vfh_plus.make()
  astar_known         close-area-arena planners/astar_esdf.make(known_map=True)
  astar_unknown       astar_esdf known_map=False, map prior moved to the area geofence (see below)
  informed_rrt_star   close-area-planner-sampling rrt_star.make(iters=5000, informed=True), known map
  astar_mpc           close-area-planner-mpc mpc.AStarMPC(known_map=True), corridor MPC follower
  astar_unknown_f2    astar_unknown with the F2 (PX4-CBF as shipped) filter from close-area-safety-filter
                      on every 50 Hz physics step, fed by its own scan every 3 steps (as run_kill.py)
  dwa                 close-area-planner-dwa-bug dwa.make()
  dwa_mem             dwa.make(memory_s=3.0), 3 s of remembered returns (as that sample's bench.py)
  bug2, tangent_bug   close-area-planner-dwa-bug bug.make("bug2") / bug.make("tangent_bug")
  dstar_lite          close-area-planner-dstar GridReplanner(backend="dstar"), unknown map, same geofence
                      as astar_unknown (subclass built here, sample not edited)
Diagnostic only (--planners astar_unknown_prior): astar_esdf known_map=False exactly as shipped.

Adding rows to an existing matrix without re-running the old ones (loop-46c):
  .venv/bin/python bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite \
      --recheck vfh_plus,astar_unknown --workers 14     # merge + run-by-run check of 2 old rows
  .venv/bin/python bench.py --cross-check matrix_0      # DWA/Bug rows vs the dwa-bug sample's own run

Geofence: the shipped unknown-map A* keeps a fixed 24 m log-odds map from (-2.5, -2.5) in the A
frame, so a B that lies at negative x or y (office rooms, glass_office) is clamped to the map
edge. astar_unknown gets the area bounds as an operator geofence instead (map corner = area
corner - 2 m, same 24 m size). It still learns every obstacle from range hits only.

Families: random, u_trap, narrow_gap (world.py), office, warehouse, forest, maze, glass_office
(worlds_complex.py), all built through world_glass.make_any_world so glass_office keeps glass.
Presets: ideal (72 rays, 6 m) and crazyflie (4 cone beams, 3 m, glass invisible), presets.py.
Run time limit: 60 s, raised to 120 s for maze and warehouse (A* known needs 41-44 s median there
in results/worlds_sanity_0.md of the arena; the unknown-map variants explore and need more).
The loop, stop conditions and scorer are run.run_one's (as run_sensors.run_one); scored on truth.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.normpath(os.path.join(HERE, ".."))
ARENA = os.path.join(SAMPLES, "close-area-arena")
RESULTS = os.path.join(HERE, "results")


def _load_arena():
    if "close_area_arena" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "close_area_arena", os.path.join(ARENA, "__init__.py"), submodule_search_locations=[ARENA])
        pkg = importlib.util.module_from_spec(spec)
        sys.modules["close_area_arena"] = pkg
        spec.loader.exec_module(pkg)


_load_arena()
A = lambda m: importlib.import_module(f"close_area_arena.{m}")   # noqa: E731
run, scorer, world_glass, presets = A("run"), A("scorer"), A("world_glass"), A("presets")
adapter, vehicle, astar_esdf = A("adapter"), A("vehicle"), A("planners.astar_esdf")
straight, run_faults = A("planners.straight"), A("run_faults")


def _load_sample(folder: str, names: list[str]) -> dict:
    """Import modules from a sibling sample that use `import arena` / `from arena import ...`.
    Each sample has its own arena.py, so the folder goes on sys.path only while importing, and the
    short module names are dropped from sys.modules afterwards (the module objects stay alive)."""
    path = os.path.join(SAMPLES, folder)
    if not os.path.isdir(path):
        return {}
    short = ["arena"] + names
    for n in short:
        sys.modules.pop(n, None)
    sys.path.insert(0, path)
    out = {}
    try:
        for n in names:
            try:
                out[n] = importlib.import_module(n)
            except ImportError as e:            # e.g. osqp missing for mpc.py
                out[n] = None
                print(f"[bench] {folder}/{n}.py not loaded: {e}", file=sys.stderr)
    finally:
        sys.path.remove(path)
        for n in short:
            sys.modules.pop(n, None)
    return out


_reactive = _load_sample("close-area-planner-reactive", ["apf", "vfh_plus"])
_sampling = _load_sample("close-area-planner-sampling", ["rrt_star"])
_mpc = _load_sample("close-area-planner-mpc", ["mpc"])
_filters = _load_sample("close-area-safety-filter", ["filters"])
_dwabug = _load_sample("close-area-planner-dwa-bug", ["dwa", "bug"])
_dstar = _load_sample("close-area-planner-dstar", ["dstar_lite"])
DWA_MEM_S = 3.0                # s of remembered returns, as close-area-planner-dwa-bug/bench.py


class GeofencedAStar(astar_esdf.AStarESDF):
    """astar_esdf(known_map=False) with its log-odds map placed on the operator geofence."""

    def __init__(self, bounds, margin: float = 2.0):
        self.bounds, self.margin = bounds, margin
        super().__init__(known_map=False)

    def reset(self) -> None:
        super().reset()
        if self.map is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin


def _bounds(w):
    return (w.xmin, w.ymin, w.xmax, w.ymax)


def geofenced_dstar(bounds, margin: float = 2.0):
    """close-area-planner-dstar GridReplanner(backend="dstar") with the same geofence as
    GeofencedAStar. GridReplanner subclasses AStarESDF(known_map=False), so it has the same fixed
    map corner at (-2.5, -2.5) as shipped; the subclass is built here so the sample is not edited."""
    base_cls = _dstar["dstar_lite"].GridReplanner

    class GeofencedDStar(base_cls):
        def reset(self) -> None:
            super().reset()
            if self.map is not None:
                self.map.x0 = bounds[0] - margin
                self.map.y0 = bounds[1] - margin

    return GeofencedDStar(backend="dstar")


# name => (factory(world) -> Planner, filter name or None, label, source sample)
PLANNERS = {
    "straight": (lambda w: straight.make(), None, "straight line (floor)", "close-area-arena"),
    "freest_beam": (lambda w: run_faults.FreestBeam(), None, "freest beam", "close-area-arena"),
    "apf_escape": (lambda w: _reactive["apf"].make(), None, "APF + wall-follow escape",
                   "close-area-planner-reactive"),
    "vfh_plus": (lambda w: _reactive["vfh_plus"].make(), None, "VFH+", "close-area-planner-reactive"),
    "astar_known": (lambda w: astar_esdf.make(known_map=True), None, "A* known map", "close-area-arena"),
    "astar_unknown": (lambda w: GeofencedAStar(_bounds(w)), None, "A* unknown map", "close-area-arena"),
    "informed_rrt_star": (lambda w: _sampling["rrt_star"].make(iters=5000, informed=True, seed=0), None,
                          "Informed RRT* 5000, known map", "close-area-planner-sampling"),
    "astar_mpc": (lambda w: _mpc["mpc"].AStarMPC(known_map=True), None, "A* known + MPC follower",
                  "close-area-planner-mpc"),
    "astar_unknown_f2": (lambda w: GeofencedAStar(_bounds(w)), "F2", "A* unknown map + F2 filter",
                         "close-area-safety-filter"),
    "astar_unknown_prior": (lambda w: astar_esdf.make(known_map=False), None,
                            "A* unknown map, shipped map prior (diagnostic)", "close-area-arena"),
    "dwa": (lambda w: _dwabug["dwa"].make(), None, "DWA", "close-area-planner-dwa-bug"),
    "dwa_mem": (lambda w: _dwabug["dwa"].make(memory_s=DWA_MEM_S), None, "DWA + 3 s scan memory",
                "close-area-planner-dwa-bug"),
    "bug2": (lambda w: _dwabug["bug"].make("bug2"), None, "Bug2", "close-area-planner-dwa-bug"),
    "tangent_bug": (lambda w: _dwabug["bug"].make("tangent_bug"), None, "TangentBug",
                    "close-area-planner-dwa-bug"),
    "dstar_lite": (lambda w: geofenced_dstar(_bounds(w)), None, "D* Lite unknown map",
                   "close-area-planner-dstar"),
}
DEFAULT_PLANNERS = ("straight", "freest_beam", "apf_escape", "vfh_plus", "astar_known", "astar_unknown",
                    "informed_rrt_star", "astar_mpc", "astar_unknown_f2",
                    "dwa", "dwa_mem", "bug2", "tangent_bug", "dstar_lite")
NEW_PLANNERS = ("dwa", "dwa_mem", "bug2", "tangent_bug", "dstar_lite")   # added by --add-to (loop-46c)
NEEDS = {"apf_escape": (_reactive, "apf"), "vfh_plus": (_reactive, "vfh_plus"),
         "informed_rrt_star": (_sampling, "rrt_star"), "astar_mpc": (_mpc, "mpc"),
         "astar_unknown_f2": (_filters, "filters"), "dwa": (_dwabug, "dwa"), "dwa_mem": (_dwabug, "dwa"),
         "bug2": (_dwabug, "bug"), "tangent_bug": (_dwabug, "bug"), "dstar_lite": (_dstar, "dstar_lite")}
FAMILIES = ("random", "u_trap", "narrow_gap", "office", "warehouse", "forest", "maze", "glass_office")
PRESETS = ("ideal", "crazyflie")
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}
FILTER_SCAN_EVERY = 3          # physics steps, as close-area-safety-filter/run_kill.py
# Planners that were asked for but have no sample in this checkout yet.
TO_ADD = ()


def available(name: str) -> bool:
    if name not in NEEDS:
        return True
    mods, key = NEEDS[name]
    return bool(mods.get(key))


def max_time(family: str) -> float:
    return LONG_FAMILIES.get(family, run.DEFAULTS["max_time_s"])


def run_one(planner: str, family: str, preset: str, index: int, seed: int = 0, keep_trace: bool = False):
    """One flight. Returns the score row, plus (world, t, xy) when keep_trace."""
    cfg = run.DEFAULTS
    vk = cfg["vehicle"]
    radius = vk["radius"]
    w = world_glass.make_any_world(family, seed, index, radius=radius)
    factory, filt_name, _, _ = PLANNERS[planner]
    pl = factory(w)
    filt = _filters["filters"].make(filt_name) if filt_name else None
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    veh = vehicle.Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **vk)
    sensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 7]))   # run.py noise stream
    fsensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 8])) if filt else None
    ad = adapter.SimAdapter(w, veh, sensor)
    pl.reset()
    HZ, DT = vehicle.HZ, vehicle.DT
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    t_max = max_time(family)
    n_steps = int(round(t_max * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    grid = w.grid if getattr(pl, "uses_grid", False) else None
    ts, xy = [0.0], [(0.0, 0.0)]
    plan_ms, sp_nom, fscan = [], None, None
    n_int = n_f = 0
    t_wall = time.perf_counter()
    for k in range(n_steps):
        if k % ratio == 0:
            t0 = time.perf_counter()
            sp_nom = pl.step(ad.pose(), ad.ranges(), goal, grid, pdt)
            plan_ms.append((time.perf_counter() - t0) * 1e3)
            if filt is None:
                ad.send_setpoint(sp_nom)
        if filt is not None:
            pose = ad.pose()
            if k % FILTER_SCAN_EVERY == 0:
                fscan = fsensor.scan(w, veh.p[0], veh.p[1], veh.yaw, veh.t)
            health = {"t": pose.t, "quality": pose.quality, "reset_counter": pose.reset_counter,
                      "sigma_xy": pose.sigma_xy, "belief": None, "uwb": None}
            sp, intervened = filt.filter(sp_nom, pose, fscan, w, health, DT)
            n_f += 1
            n_int += int(intervened)
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
    mats = getattr(w, "materials", {}) or {}
    res.update({
        "planner": planner, "family": family, "preset": preset, "index": index, "seed": seed,
        "max_time_s": t_max, "layout_attempts": w.attempts,
        "n_obstacles": len(w.boxes) + len(w.cylinders),
        "n_glass": mats.get("boxes", []).count("glass"),
        "goal": [round(goal[0], 3), round(goal[1], 3)],
        "intervention_frac": round(n_int / n_f, 4) if filt else None,
        "planner_ms_mean": round(float(np.mean(plan_ms)), 3),
        "wall_s": round(time.perf_counter() - t_wall, 2),
    })
    # Planner-side counters, only for the planners that keep them (new rows; old rows unchanged).
    if hasattr(pl, "no_admissible_steps"):                      # DWA: steps with no admissible sample
        res["no_admissible_steps"] = pl.no_admissible_steps
    if planner in ("bug2", "tangent_bug"):
        res["mode_changes"] = len(pl.log)
        res["bug2_fail_exit"] = any(m == "fail" for _, m in pl.log)
    if planner == "dstar_lite":
        res["no_path_replans"] = pl.no_path
        res["search_ms_median"] = round(float(np.median(pl.search_ms)), 3) if pl.search_ms else None
    res["hit_material"] = None
    if res["collision"]:
        for (x, y) in xy:
            if w.clearance(x, y) < radius:
                res["hit_material"], _ = world_glass.nearest_material(w, x, y)
                break
    if keep_trace:
        return res, (w, np.array(ts), np.array(xy))
    return res


def _task(args):
    return run_one(*args)


def parity(layouts: int, seed: int) -> dict:
    """straight and astar_known on ideal x random: this loop vs run.evaluate."""
    out = {}
    for name, fac in (("straight", lambda: straight.make()),
                      ("astar_known", lambda: astar_esdf.make(known_map=True))):
        ref, _, _ = run.evaluate(fac, "random", layouts, seed)
        mine = [run_one(name, "random", "ideal", i, seed) for i in range(layouts)]
        same = sum(a["outcome"] == b["outcome"] and a["min_clearance_m"] == b["min_clearance_m"]
                   for a, b in zip(mine, ref))
        out[name] = f"{same}/{layouts}"
    return out


def summarize(rows):
    s = scorer.summarize(rows)
    hits = {}
    for r in rows:
        if r.get("hit_material"):
            hits[r["hit_material"]] = hits.get(r["hit_material"], 0) + 1
    s["collisions_by_material"] = hits
    s["wall_s_sum"] = round(sum(r["wall_s"] for r in rows), 1)
    return s


PRIOR_MAP = ("astar_known", "informed_rrt_star", "astar_mpc")   # plan on the true prior grid


def best(cells: dict, planners, family) -> str:
    """Highest reached %, then lowest collision %. Ties are all listed."""
    cand = [(p, cells[p][family]) for p in planners if family in cells.get(p, {})]
    if not cand:
        return "-"
    key = lambda ps: (-ps[1]["reached_pct"], ps[1]["collision_pct"])
    top = min(cand, key=key)
    ties = [p for p, s in cand if key((p, s)) == key(top)]
    return f"{'/'.join(ties)} ({top[1]['reached_pct']:g} / {top[1]['collision_pct']:g})"


def tables(summ: dict, planners, families, presets_) -> str:
    out = []
    for pr in presets_:
        cells = summ.get(pr, {})
        out += [f"### Preset `{pr}`", "", "Cell = reached % / collision % (20 layouts unless stated).", "",
                "| planner | " + " | ".join(families) + " |", "|---" * (len(families) + 1) + "|"]
        for p in planners:
            row = [f"{cells[p][f]['reached_pct']:g} / {cells[p][f]['collision_pct']:g}" if f in cells.get(p, {})
                   else "-" for f in families]
            out.append(f"| {p} | " + " | ".join(row) + " |")
        no_map = [p for p in planners if p not in PRIOR_MAP]
        out += ["", "Best planner per family (reached / collision %): "
                + "; ".join(f"{f} => {best(cells, planners, f)}" for f in families), "",
                "Best without a prior map (" + ", ".join(PRIOR_MAP) + " excluded): "
                + "; ".join(f"{f} => {best(cells, no_map, f)}" for f in families), ""]
    return "\n".join(out)


def detail_table(summ, planners, families, presets_) -> str:
    out = ["| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s "
           "| median min clearance m | collisions by material | sum of run wall s |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    f_ = lambda v: "-" if v is None else f"{v:g}"
    for pr in presets_:
        for p in planners:
            for f in families:
                s = summ.get(pr, {}).get(p, {}).get(f)
                if not s:
                    continue
                hm = ", ".join(f"{k} {v}" for k, v in sorted(s["collisions_by_material"].items())) or "-"
                out.append(f"| {pr} | {p} | {f} | {f_(s['reached_pct'])} | {f_(s['collision_pct'])} "
                           f"| {f_(s['stuck_pct'])} | {f_(s['timeout_pct'])} | {f_(s['median_time_to_goal_s'])} "
                           f"| {f_(s['median_min_clearance_m'])} | {hm} | {s['wall_s_sum']:g} |")
    return "\n".join(out)


def env():
    import importlib.metadata as md
    try:
        osqp_v = md.version("osqp")
    except md.PackageNotFoundError:
        osqp_v = None
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "osqp": osqp_v, "machine": platform.machine(), "system": platform.system(),
            "cpus": os.cpu_count()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--planners", default=",".join(DEFAULT_PLANNERS))
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--presets", default=",".join(PRESETS))
    ap.add_argument("--parity", action="store_true", help="check this loop against run.evaluate first")
    ap.add_argument("--stem", default=None, help="output stem in results/ (default matrix_<seed>)")
    ap.add_argument("--render", default=None, metavar="STEM", help="only rebuild results/STEM.md from its .json")
    ap.add_argument("--add-to", default=None, metavar="STEM",
                    help="run --planners and merge their rows into results/STEM.json; rows of other planners "
                         "stay as they are. Layouts, seed, families and presets are taken from STEM.json")
    ap.add_argument("--recheck", default="", metavar="P1,P2",
                    help="with --add-to: re-run these existing rows too and compare them run by run with "
                         "STEM.json (written to results/STEM_recheck.*; STEM.json keeps the old rows)")
    ap.add_argument("--cross-check", default=None, metavar="STEM",
                    help="compare the DWA / Bug rows of results/STEM.json with close-area-planner-dwa-bug's own run")
    a = ap.parse_args(argv)
    if a.cross_check:
        return cross_check(a.cross_check)
    if a.render:
        render(os.path.join(RESULTS, a.render))
        print(f"wrote results/{a.render}.md")
        return 0
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    planners = [p for p in a.planners.split(",") if p]
    skipped = [p for p in planners if not available(p)]
    planners = [p for p in planners if available(p)]
    families, presets_ = a.families.split(","), a.presets.split(",")
    par = parity(min(a.layouts, 10), a.seed) if a.parity else None
    if par:
        print("parity vs run.evaluate:", par, flush=True)
    if a.add_to:
        return add_to(a, cmd, planners, skipped)
    rows, wall = run_tasks(planners, families, presets_, a.layouts, a.seed, a.workers)
    summ = summarize_all(rows, planners, families, presets_)
    stem = os.path.join(RESULTS, a.stem or f"matrix_{a.seed}")
    os.makedirs(RESULTS, exist_ok=True)
    meta = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "workers": a.workers,
            "wall_s": wall, "planners": {p: {"label": PLANNERS[p][2], "sample": PLANNERS[p][3],
                                             "filter": PLANNERS[p][1]} for p in planners},
            "skipped_missing_module": skipped, "to_add": list(TO_ADD), "families": families,
            "presets": {pr: presets.SENSOR_PRESETS[pr] for pr in presets_},
            "max_time_s": {f: max_time(f) for f in families}, "parity_vs_run_evaluate": par,
            "env": env()}
    with open(stem + ".json", "w") as fh:
        json.dump({**meta, "summary": summ, "runs": rows}, fh, indent=1, default=list)
    render(stem)
    print(tables(summ, planners, families, list(presets_)))
    print(f"wall {wall} s; wrote {os.path.relpath(stem, HERE)}.json, .md")
    return 0


SLOW = {"astar_unknown": 0, "astar_unknown_f2": 0, "astar_unknown_prior": 0, "dwa_mem": 0, "informed_rrt_star": 1,
        "dstar_lite": 1, "astar_mpc": 2, "dwa": 2}


def run_tasks(planners, families, presets_, layouts, seed, workers):
    tasks = [(p, f, pr, i, seed) for p in planners for f in families for pr in presets_
             for i in range(layouts)]
    tasks.sort(key=lambda t: (t[1] not in LONG_FAMILIES, SLOW.get(t[0], 9)))   # long jobs first
    t_all = time.perf_counter()
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for k, r in enumerate(ex.map(_task, tasks, chunksize=1)):
            rows.append(r)
            if (k + 1) % 100 == 0:
                print(f"{k + 1}/{len(tasks)} runs, {time.perf_counter() - t_all:.0f} s", flush=True)
    wall = round(time.perf_counter() - t_all, 1)
    rows.sort(key=lambda r: (presets_.index(r["preset"]), planners.index(r["planner"]),
                             families.index(r["family"]), r["index"]))
    return rows, wall


def summarize_all(rows, planners, families, presets_) -> dict:
    summ: dict = {}
    for pr in presets_:
        for p in planners:
            for f in families:
                sel = [r for r in rows if r["preset"] == pr and r["planner"] == p and r["family"] == f]
                if sel:
                    summ.setdefault(pr, {}).setdefault(p, {})[f] = summarize(sel)
    return summ


RECHECK_KEYS = ("outcome", "min_clearance_m", "path_length_m", "time_to_goal_s")


def add_to(a, cmd, planners, skipped) -> int:
    """Run new planners (and re-run --recheck rows) on the layouts of an existing matrix and merge."""
    stem = os.path.join(RESULTS, a.add_to)
    d = json.load(open(stem + ".json"))
    families, presets_, layouts, seed = d["families"], list(d["presets"]), d["layouts"], d["seed"]
    recheck = [p for p in a.recheck.split(",") if p]
    missing = [p for p in recheck if p not in d["planners"]]
    if missing:
        raise SystemExit(f"--recheck {missing}: not rows of {a.add_to}.json")
    allp = planners + [p for p in recheck if p not in planners]
    rows, wall = run_tasks(allp, families, presets_, layouts, seed, a.workers)
    new_rows = [r for r in rows if r["planner"] in planners]
    # --- recheck: re-run rows vs the stored ones, run by run ---
    rc = None
    if recheck:
        old = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in d["runs"]}
        per, diffs = {}, []
        for r in rows:
            if r["planner"] not in recheck:
                continue
            o = old.get((r["planner"], r["family"], r["preset"], r["index"]))
            same = o is not None and all(o.get(k) == r.get(k) for k in RECHECK_KEYS)
            c = per.setdefault(r["planner"], [0, 0])
            c[0] += int(same)
            c[1] += 1
            if not same:
                diffs.append({"planner": r["planner"], "family": r["family"], "preset": r["preset"],
                              "index": r["index"], "old": {k: (o or {}).get(k) for k in RECHECK_KEYS},
                              "new": {k: r.get(k) for k in RECHECK_KEYS}})
        rc = {"command": cmd, "against": f"results/{a.add_to}.json", "keys": list(RECHECK_KEYS),
              "identical": {p: f"{c[0]}/{c[1]}" for p, c in per.items()}, "differences": diffs, "env": env()}
        with open(stem + "_recheck.json", "w") as fh:
            json.dump(rc, fh, indent=1)
        md = [f"`{cmd}` from samples/close-area-benchmark. Input: synthetic. Existing rows re-run on the same "
              f"{layouts} layouts x {len(families)} families x {len(presets_)} presets, seed {seed}, and compared "
              f"run by run with results/{a.add_to}.json on {', '.join(RECHECK_KEYS)}.", "",
              "| planner | runs identical |", "|---|---|"]
        md += [f"| {p} | {v} |" for p, v in rc["identical"].items()]
        md += ["", f"Differences: {len(diffs)}", ""]
        md += [f"- {x['planner']} {x['preset']} {x['family']} #{x['index']}: old {x['old']} new {x['new']}"
               for x in diffs]
        with open(stem + "_recheck.md", "w") as fh:
            fh.write("\n".join(md) + "\n")
        print("recheck vs", a.add_to, rc["identical"], f"{len(diffs)} differences", flush=True)
    # --- merge the new planners' rows; every other row of d stays as it was ---
    d["runs"] = [r for r in d["runs"] if r["planner"] not in planners] + new_rows
    summ = summarize_all(new_rows, planners, families, presets_)
    for pr in presets_:
        for p in planners:
            d["summary"].setdefault(pr, {})[p] = summ.get(pr, {}).get(p, {})
        d["summary"][pr] = {p: d["summary"][pr][p] for p in list(d["planners"]) + planners
                            if p in d["summary"][pr]}
    for p in planners:
        d["planners"][p] = {"label": PLANNERS[p][2], "sample": PLANNERS[p][3], "filter": PLANNERS[p][1]}
    d["to_add"] = list(TO_ADD)
    d["skipped_missing_module"] = sorted(set(d.get("skipped_missing_module", [])) | set(skipped))
    d.setdefault("additions", [])
    d["additions"] = [x for x in d["additions"] if not set(x["planners"]) & set(planners)]
    d["additions"].append({"command": cmd, "planners": planners, "recheck": rc["identical"] if rc else None,
                           "workers": a.workers, "wall_s": wall, "n_runs": len(rows), "env": env(),
                           "date": time.strftime("%Y-%m-%d")})
    with open(stem + ".json", "w") as fh:
        json.dump(d, fh, indent=1, default=list)
    render(stem)
    print(tables(d["summary"], list(d["planners"]), families, presets_))
    print(f"wall {wall} s for {len(rows)} runs; merged {len(new_rows)} rows into {os.path.relpath(stem, HERE)}.json, .md")
    return 0 if not rc or not rc["differences"] else 1


def cross_check(stem: str) -> int:
    """Compare the dwa/dwa_mem/bug2/tangent_bug rows of results/STEM.json (preset ideal) with
    close-area-planner-dwa-bug/results/dwa_bug_0.json (fan "default" = the same 72-ray arena fan,
    run through run.evaluate) on random, u_trap and narrow_gap, layouts 0..layouts-1 of the matrix.
    Writes results/STEM_cross_checks.md."""
    n = json.load(open(os.path.join(RESULTS, stem + ".json")))
    src = os.path.join(SAMPLES, "close-area-planner-dwa-bug", "results", "dwa_bug_0.json")
    d = json.load(open(src))
    on = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in n["runs"]}
    per, diffs = {}, []
    for cell in d["cells"]:
        if cell["fan"] != "default" or cell["planner"] not in ("dwa", "dwa_mem", "bug2", "tangent_bug"):
            continue
        for r in cell["runs"]:
            m = on.get((cell["planner"], cell["family"], "ideal", r["index"]))
            if m is None:
                continue
            same = m["outcome"] == r["outcome"] and m["min_clearance_m"] == r["min_clearance_m"]
            c = per.setdefault(cell["planner"], [0, 0])
            c[0] += int(same)
            c[1] += 1
            if not same:
                diffs.append(f"{cell['planner']} {cell['family']} #{r['index']}")
    md = [f"`python bench.py --cross-check {stem}`. Input: synthetic. Rows of results/{stem}.json (preset ideal) "
          "vs close-area-planner-dwa-bug/results/dwa_bug_0.json (fan default, run.evaluate, seed 0) on random, "
          "u_trap and narrow_gap, same layout indices. Same = identical outcome and min clearance.", "",
          "| planner | runs same |", "|---|---|"] + [f"| {p} | {c[0]}/{c[1]} |" for p, c in per.items()]
    md += ["", f"Differences: {len(diffs)}" + (" (" + ", ".join(diffs) + ")" if diffs else ""), ""]
    # D* Lite is astar_esdf's unknown-map planner with an incremental search: same outcome as astar_unknown?
    key = lambda r: (r["family"], r["preset"], r["index"])          # noqa: E731
    au = {key(r): r for r in n["runs"] if r["planner"] == "astar_unknown"}
    ds = {key(r): r for r in n["runs"] if r["planner"] == "dstar_lite"}
    if au and ds:
        md += ["dstar_lite vs astar_unknown (same geofence, same map and cost model, incremental search), runs "
               "with the same outcome, and mean planner step time over all runs of the preset (ms; 14 processes "
               "in parallel, not a clean timing):", "",
               "| preset | same outcome | astar_unknown mean step ms | dstar_lite mean step ms |", "|---|---|---|---|"]
        for pr in n["presets"]:
            ks = [k for k in au if k[1] == pr and k in ds]
            ms = lambda m: round(float(np.mean([m[k]["planner_ms_mean"] for k in ks])), 2)   # noqa: E731
            md.append(f"| {pr} | {sum(au[k]['outcome'] == ds[k]['outcome'] for k in ks)}/{len(ks)} | {ms(au)} "
                      f"| {ms(ds)} |")
        md.append("")
    with open(os.path.join(RESULTS, stem + "_cross_checks.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))
    return 0 if not diffs else 1


def render(stem: str) -> None:
    """Write <stem>.md from <stem>.json (python bench.py --render matrix_0 rebuilds it)."""
    d = json.load(open(stem + ".json"))
    planners, families, presets_ = list(d["planners"]), d["families"], list(d["presets"])
    summ = d["summary"]
    md = [f"`{d['command']}` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle "
          f"and sensors). Scored on truth. Seed {d['seed']}, {d['layouts']} layouts per cell, {d['workers']} "
          f"worker processes, wall {d['wall_s']} s. Run time limit per family (s): "
          + ", ".join(f"{f} {t:g}" for f, t in d["max_time_s"].items()) + ".", ""]
    if d.get("parity_vs_run_evaluate"):
        md += ["Parity with run.evaluate (ideal x random, runs with identical outcome and min clearance): "
               + ", ".join(f"{k} {v}" for k, v in d["parity_vs_run_evaluate"].items()), ""]
    if d.get("skipped_missing_module"):
        md += ["Skipped (module failed to import): " + ", ".join(d["skipped_missing_module"]), ""]
    for x in d.get("additions", []):
        md += [f"Rows {', '.join(x['planners'])} added later by `{x['command']}` ({x['date']}, same layouts and "
               f"limits, {x['workers']} worker processes, wall {x['wall_s']} s for {x['n_runs']} runs, Python "
               f"{x['env']['python']}, numpy {x['env']['numpy']}). All other rows are kept from the first run."
               + (" Existing rows re-run as a check, runs identical in outcome, min clearance, path length and "
                  "time to goal: " + ", ".join(f"{k} {v}" for k, v in x["recheck"].items()) + "."
                  if x.get("recheck") else ""), ""]
    if d.get("to_add"):
        md += ["Not in this checkout, to add: " + "; ".join(d["to_add"]), ""]
    md += [tables(summ, planners, families, presets_), "### All fields", "",
           detail_table(summ, planners, families, presets_), ""]
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(md))


if __name__ == "__main__":
    raise SystemExit(main())
