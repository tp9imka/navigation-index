"""Fly MPPI (guide none / astar) and the unknown-map A* baseline over the 8 arena families.

.venv/bin/python bench.py --preset ideal --layouts 20 --seed 0 --workers 14
.venv/bin/python bench.py --preset crazyflie --families random,office --layouts 20 --seed 0 --workers 14
.venv/bin/python bench.py --timing --workers 1          # replan timing in one process, no load

Writes results/bench_<preset>_<seed>.json and .md (or timing_<seed>.*).

The flight loop is a copy of samples/close-area-benchmark/bench.py run_one without the safety
filter: world from world_glass.make_any_world (glass_office keeps glass), sensor from
presets.make_sensor with the run.py noise stream [seed, index, 7], run time limit 60 s (120 s for
maze and warehouse), stop conditions and scorer from the arena, scored on truth.
astar_unknown is the benchmark's GeofencedAStar: astar_esdf(known_map=False) with its map corner
on the area bounds - 2 m. The MPPI planners get the same bounds. Nothing in another sample is
edited; --parity compares astar_unknown run by run with close-area-benchmark/results/matrix_0.json.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import mppi  # noqa: E402

A = lambda m: importlib.import_module(f"close_area_arena.{m}")   # noqa: E731
run, scorer, world_glass, presets, vehicle = A("run"), A("scorer"), A("world_glass"), A("presets"), A("vehicle")
astar_esdf = arena.astar_esdf
RESULTS = os.path.join(HERE, "results")
MATRIX = os.path.join(HERE, "..", "close-area-benchmark", "results", "matrix_0.json")

FAMILIES = ("random", "u_trap", "narrow_gap", "office", "warehouse", "forest", "maze", "glass_office")
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}     # as close-area-benchmark/bench.py


class GeofencedAStar(astar_esdf.AStarESDF):
    """close-area-benchmark/bench.py GeofencedAStar, copied: map corner on the area bounds - 2 m."""

    def __init__(self, bounds, margin: float = 2.0):
        self.bounds, self.margin = bounds, margin
        super().__init__(known_map=False)

    def reset(self) -> None:
        super().reset()
        if self.map is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin


def bounds_of(w):
    return (w.xmin, w.ymin, w.xmax, w.ymax)


# name => factory(world, **mppi_kw) -> Planner
PLANNERS = {
    "astar_unknown": lambda w, **kw: GeofencedAStar(bounds_of(w)),
    "mppi_none": lambda w, **kw: mppi.make(guide="none", bounds=bounds_of(w), **kw),
    "mppi_astar": lambda w, **kw: mppi.make(guide="astar", bounds=bounds_of(w), **kw),
}


def max_time(family):
    return LONG_FAMILIES.get(family, run.DEFAULTS["max_time_s"])


def run_one(planner, family, preset, index, seed=0, kw=None, keep_trace=False):
    cfg = run.DEFAULTS
    vk = cfg["vehicle"]
    radius = vk["radius"]
    w = world_glass.make_any_world(family, seed, index, radius=radius)
    pl = PLANNERS[planner](w, **(kw or {}))
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    veh = vehicle.Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **vk)
    sensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 7]))
    ad = arena.adapter.SimAdapter(w, veh, sensor)
    pl.reset()
    HZ = vehicle.HZ
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    t_max = max_time(family)
    n_steps = int(round(t_max * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    ts, xy, step_ms = [0.0], [(0.0, 0.0)], []
    t_wall = time.perf_counter()
    for k in range(n_steps):
        if k % ratio == 0:
            t0 = time.perf_counter()
            sp = pl.step(ad.pose(), ad.ranges(), goal, None, pdt)
            step_ms.append((time.perf_counter() - t0) * 1e3)
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
    astar_ms = getattr(pl, "astar_ms", None)
    if astar_ms is None:
        astar_ms = getattr(pl, "replan_ms", [])
    res.update({"planner": planner, "family": family, "preset": preset, "index": index, "seed": seed,
                "max_time_s": t_max, "goal": [round(goal[0], 3), round(goal[1], 3)],
                "step_ms_median": round(float(np.median(step_ms)), 3),
                "step_ms_p95": round(float(np.percentile(step_ms, 95)), 3),
                "astar_replans": len(astar_ms),
                "wall_s": round(time.perf_counter() - t_wall, 2)})
    if keep_trace:
        return res, step_ms, list(astar_ms), (w, np.array(ts), np.array(xy), pl)
    return res, step_ms, list(astar_ms)


def _task(args):
    return run_one(*args)


def pct(v, q):
    return round(float(np.percentile(v, q)), 2) if len(v) else None


def summarize(rows, ms, ams):
    s = scorer.summarize(rows)
    s["step_ms_median"], s["step_ms_p95"], s["step_ms_max"] = pct(ms, 50), pct(ms, 95), pct(ms, 100)
    s["steps"] = len(ms)
    s["astar_replans"], s["astar_ms_median"], s["astar_ms_p95"] = len(ams), pct(ams, 50), pct(ams, 95)
    return s


def parity(rows):
    """astar_unknown rows vs close-area-benchmark/results/matrix_0.json (same layouts, seed 0)."""
    if not os.path.exists(MATRIX):
        return None
    ref = {(r["preset"], r["family"], r["index"]): r for r in json.load(open(MATRIX))["runs"]
           if r["planner"] == "astar_unknown"}
    n = same = 0
    for r in rows:
        if r["planner"] != "astar_unknown" or r["seed"] != 0:
            continue
        m = ref.get((r["preset"], r["family"], r["index"]))
        if m is None:
            continue
        n += 1
        same += (m["outcome"] == r["outcome"] and m["min_clearance_m"] == r["min_clearance_m"]
                 and m["path_length_m"] == r["path_length_m"])
    return {"compared": n, "identical": same}


def env():
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system(), "cpus": os.cpu_count()}


def mppi_constants():
    return {k: v for k, v in vars(mppi).items() if k.isupper() and isinstance(v, (int, float))}


def fmt(v):
    return "-" if v is None else f"{v}"


def table(summ, header_note=""):
    lines = ["| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s "
             "| median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (pl, fam), s in summ.items():
        lines.append(f"| {pl} | {fam} | {s['n']} | {fmt(s['reached_pct'])} | {fmt(s['collision_pct'])} | "
                     f"{fmt(s['stuck_pct'])} | {fmt(s['timeout_pct'])} | {fmt(s['median_time_to_goal_s'])} | "
                     f"{fmt(s['median_path_length_m'])} | {fmt(s['median_min_clearance_m'])} | "
                     f"{fmt(s['step_ms_median'])} | {fmt(s['step_ms_p95'])} | {fmt(s['astar_ms_median'])} | "
                     f"{fmt(s['astar_ms_p95'])} |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", default="ideal")
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--planners", default="astar_unknown,mppi_none,mppi_astar")
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--timing", action="store_true",
                    help="random and maze, 5 layouts, MPPI planners, for one-process step timing")
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.timing:
        a.families, a.layouts = "random,maze", 5
    fams, pls = a.families.split(","), a.planners.split(",")
    jobs = [(p, f, a.preset, i, a.seed) for p in pls for f in fams for i in range(a.layouts)]
    t0 = time.perf_counter()
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            out = list(ex.map(_task, jobs, chunksize=1))
    else:
        out = [_task(j) for j in jobs]
    wall = time.perf_counter() - t0
    rows = [o[0] for o in out]
    summ = {}
    for p in pls:
        for f in fams:
            sel = [o for o in out if o[0]["planner"] == p and o[0]["family"] == f]
            summ[(p, f)] = summarize([o[0] for o in sel], [m for o in sel for m in o[1]],
                                     [m for o in sel for m in o[2]])
    par = parity(rows)
    stem = os.path.join(a.out, (f"timing_{a.seed}" if a.timing else f"bench_{a.preset}_{a.seed}"))
    os.makedirs(a.out, exist_ok=True)
    doc = {"command": cmd, "input": "synthetic", "preset": a.preset, "seed": a.seed, "layouts": a.layouts,
           "workers": a.workers, "wall_s": round(wall, 1), "max_time_s": {f: max_time(f) for f in fams},
           "mppi_constants": mppi_constants(), "env": env(), "parity_astar_unknown_vs_matrix_0": par,
           "summary": {f"{p}|{f}": s for (p, f), s in summ.items()}, "runs": rows}
    with open(stem + ".json", "w") as fh:
        json.dump(doc, fh, indent=1)
    e = doc["env"]
    head = (f"`{cmd}` from samples/close-area-planner-mppi. Input: synthetic (simulated layouts, vehicle and "
            f"sensor), scored on truth. Preset `{a.preset}`, seed {a.seed}, {a.layouts} layouts per cell, "
            f"{a.workers} worker process(es), wall {wall:.1f} s, Python {e['python']}, numpy {e['numpy']}, "
            f"scipy {e['scipy']}, {e['machine']} {e['system']}. Run time limit 60 s, 120 s for maze and warehouse. "
            "step ms = the whole planner.step() call (map update, ESDF, A* when due, MPPI) at 10 Hz; "
            "A* replan ms = the A* searches inside those steps.")
    if a.workers > 1:
        head += f" Timings were taken with {a.workers} processes sharing the machine; see timing_0.md for one process."
    if par:
        head += f"\n\nParity: astar_unknown runs identical to close-area-benchmark matrix_0.json (outcome, min clearance, path length): {par['identical']}/{par['compared']}."
    lines = [head, "", table(summ), "", "Per run (outcome, time to B s, min clearance m, path m):", "",
             "| family | run | " + " | ".join(pls) + " |", "|---|---|" + "---|" * len(pls)]
    idx = {(r["planner"], r["family"], r["index"]): r for r in rows}
    for f in fams:
        for i in range(a.layouts):
            cells = []
            for p in pls:
                r = idx[(p, f, i)]
                cells.append(f"{r['outcome']} {fmt(r['time_to_goal_s'])} {r['min_clearance_m']} {r['path_length_m']}")
            lines.append(f"| {f} | {i} | " + " | ".join(cells) + " |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(table(summ))
    print(f"parity {par}  wall {wall:.1f} s  wrote {os.path.relpath(stem, HERE)}.json, .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
