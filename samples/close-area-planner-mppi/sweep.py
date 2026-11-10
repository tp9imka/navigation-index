"""Sweep MPPI samples K and horizon H on random and maze, both guides, scored in the arena.

.venv/bin/python sweep.py --layouts 10 --seed 0 --workers 14

1. Step timing, one process, before any flight: for every (K, H) one planner.step() on random
   layout 0 at A with a real first scan, repeated REPS times after 3 warm-up calls (guide='none',
   so no A* search is inside; the A* cost is the same for every K, H and is in bench.py).
2. Flights: bench.run_one for every (guide, K, H, family, layout), preset ideal, in parallel.
Writes results/sweep_<seed>.json and .md.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bench  # noqa: E402
import mppi  # noqa: E402

KS = (64, 256, 1024)
HS = (10, 20, 40)
GUIDES = ("none", "astar")
FAMS = ("random", "maze")
REPS = 30


def step_timing(K, H, seed=0):
    w = bench.world_glass.make_any_world("random", seed, 0)
    sensor = bench.presets.make_sensor("ideal", np.random.default_rng([seed, 0, 7]))
    veh = bench.vehicle.Vehicle(0.0, 0.0, 1.0, yaw=0.0)
    ad = bench.arena.adapter.SimAdapter(w, veh, sensor)
    goal = (w.goal[0], w.goal[1], 1.0)
    p = mppi.make(guide="none", K=K, horizon=H, bounds=bench.bounds_of(w))
    pose, scan = ad.pose(), ad.ranges()
    for _ in range(3):
        p.step(pose, scan, goal, None, 0.1)
    ms = []
    for _ in range(REPS):
        t0 = time.perf_counter()
        p.step(pose, scan, goal, None, 0.1)
        ms.append((time.perf_counter() - t0) * 1e3)
    return round(float(np.median(ms)), 2), round(float(np.percentile(ms, 95)), 2)


def _task(a):
    guide, K, H, fam, i, seed = a
    r, _, _ = bench.run_one(f"mppi_{guide}", fam, "ideal", i, seed, {"K": K, "horizon": H})
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--out", default=bench.RESULTS)
    a = ap.parse_args(argv)
    cmd = "python sweep.py " + " ".join(argv if argv is not None else sys.argv[1:])
    timing = {f"{K}|{H}": step_timing(K, H, a.seed) for K, H in itertools.product(KS, HS)}
    print("step timing (median, p95 ms):", timing, flush=True)
    jobs = [(g, K, H, f, i, a.seed) for g, K, H, f in itertools.product(GUIDES, KS, HS, FAMS)
            for i in range(a.layouts)]
    t0 = time.perf_counter()
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(_task, jobs, chunksize=1))
    wall = time.perf_counter() - t0
    for j, r in zip(jobs, rows):
        r["K"], r["horizon"] = j[1], j[2]
    summ = {}
    for g, K, H, f in itertools.product(GUIDES, KS, HS, FAMS):
        sel = [r for j, r in zip(jobs, rows) if j[:4] == (g, K, H, f)]
        s = bench.scorer.summarize(sel)
        s["step_ms_median_under_load"] = round(float(np.median([r["step_ms_median"] for r in sel])), 2)
        summ[f"{g}|{K}|{H}|{f}"] = s
    doc = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "preset": "ideal",
           "workers": a.workers, "wall_s": round(wall, 1), "env": bench.env(),
           "mppi_constants": bench.mppi_constants(), "step_timing_one_process_ms": timing,
           "summary": summ, "runs": rows}
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"sweep_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump(doc, fh, indent=1)
    e = doc["env"]
    f = bench.fmt
    lines = [f"`{cmd}` from samples/close-area-planner-mppi. Input: synthetic, scored on truth. Preset ideal, "
             f"seed {a.seed}, {a.layouts} layouts per cell, {a.workers} worker processes, flights wall {wall:.1f} s, "
             f"Python {e['python']}, numpy {e['numpy']}, scipy {e['scipy']}, {e['machine']} {e['system']}. "
             "Other parameters at their defaults (lambda 1.0, sigma 0.6 m/s, beta 0.8, 0.1 s per step). "
             f"Step ms (one process): one planner.step() with guide none on random layout 0 at A, median / p95 "
             f"of {REPS} calls, no other load. Step ms under load: median over runs of the per-run median, "
             f"{a.workers} processes sharing the machine.", "",
             "| guide | K | horizon steps (s) | family | reached % | collision % | stuck % | timeout % "
             "| median time to B s | median path m | median min clearance m | step ms one process median / p95 "
             "| step ms under load |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g, K, H, fam in itertools.product(GUIDES, KS, HS, FAMS):
        s = summ[f"{g}|{K}|{H}|{fam}"]
        tm = timing[f"{K}|{H}"]
        lines.append(f"| {g} | {K} | {H} ({H * mppi.DT_MODEL:.1f}) | {fam} | {f(s['reached_pct'])} | "
                     f"{f(s['collision_pct'])} | {f(s['stuck_pct'])} | {f(s['timeout_pct'])} | "
                     f"{f(s['median_time_to_goal_s'])} | {f(s['median_path_length_m'])} | "
                     f"{f(s['median_min_clearance_m'])} | {tm[0]} / {tm[1]} | {s['step_ms_median_under_load']} |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[2:]))
    print(f"wall {wall:.1f} s, wrote {os.path.relpath(stem, HERE)}.json, .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
