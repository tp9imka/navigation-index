"""Planning-only sweep on narrow_gap layouts with a fixed gap width.

For each gap width and layout index (arena narrow_gap layout, seed 0, gap replaced, see
arena.gap_world) plan once from A to B on the known 0.1 m grid with:
  - A*: planners/astar_esdf (known_map=True), its own _plan, deterministic, 1 run.
  - RRT* and Informed RRT* at two iteration budgets, 10 RNG seeds each.
No flight here: success = a path was returned within the budget. Every path is then checked on
the exact geometry (world.sdf every 2 cm along the path).

python sweep.py [--layouts 30] [--seeds 10] [--widths 0.4,0.5,...] [--budgets 1000,5000] [--jobs 12]
Writes results/sweep_<seed>.json (per-plan rows) and results/sweep_<seed>.md (table).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import rrt_star  # noqa: E402

RESULTS = os.path.join(HERE, "results")


def truth_clearance(w, xy) -> float:
    pts = []
    for a, b in zip(xy[:-1], xy[1:]):
        m = int(math.hypot(*(b - a)) / 0.02) + 2
        t = np.linspace(0, 1, m)[:, None]
        pts.append(a + (b - a) * t)
    return float(w.sdf(np.concatenate(pts)).min())


def one_layout(task):
    width, index, seed, n_seeds, budgets = task
    w = arena.gap_world(width, seed, index)
    rows = []
    if w is None:
        return rows
    esdf = w.grid.esdf()
    goal = (w.goal[0], w.goal[1], 1.0)
    p = arena.astar_esdf.AStarESDF(known_map=True)
    p.reset()
    p._plan(arena.Pose(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0), goal, w.grid)
    ok = p.path_xy is not None
    rows.append({"planner": "astar", "budget": None, "width": width, "index": index, "rng": None,
                 "ok": ok, "ms": round(p.replan_ms[-1], 3), "fallback": p.fallbacks,
                 "length_m": round(rrt_star.path_length(p.path_xy), 4) if ok else None,
                 "truth_clear_m": round(truth_clearance(w, p.path_xy), 4) if ok else None,
                 "first_iter": None, "first_ms": None})
    for informed in (False, True):
        name = "informed_rrt_star" if informed else "rrt_star"
        for budget in budgets:
            for s in range(n_seeds):
                rng = np.random.default_rng([s, index, int(round(width * 1000)), budget])
                r = rrt_star.plan_on_grid(w.grid, esdf, (0.0, 0.0), goal, budget, rng, informed)
                ok = r["path_xy"] is not None
                rows.append({"planner": name, "budget": budget, "width": width, "index": index, "rng": s,
                             "ok": ok, "ms": round(r["ms"], 3), "fallback": r["fallback"],
                             "length_m": round(rrt_star.path_length(r["path_xy"]), 4) if ok else None,
                             "truth_clear_m": round(truth_clearance(w, r["path_xy"]), 4) if ok else None,
                             "first_iter": r["first_iter"],
                             "first_ms": None if r["first_ms"] is None else round(r["first_ms"], 3)})
    return rows


def summarize(rows, astar_len):
    """astar_len: {(width, index): A* length} for the length ratio."""
    ok = [r for r in rows if r["ok"]]
    ms = [r["ms"] for r in rows]
    by_layout = {}
    for r in ok:
        by_layout.setdefault(r["index"], []).append(r["length_m"])
    stds = [float(np.std(v)) for v in by_layout.values() if len(v) >= 2]
    ratios = [r["length_m"] / astar_len[(r["width"], r["index"])] for r in ok
              if astar_len.get((r["width"], r["index"]))]
    fi = [r["first_ms"] for r in ok if r["first_ms"] is not None]
    rnd = lambda v, k=2: None if v is None else round(float(v), k)
    return {
        "plans": len(rows),
        "success_pct": rnd(100.0 * len(ok) / len(rows), 1) if rows else None,
        "fallback_pct_of_ok": rnd(100.0 * sum(r["fallback"] for r in ok) / len(ok), 1) if ok else None,
        "length_mean_m": rnd(np.mean([r["length_m"] for r in ok])) if ok else None,
        "length_std_within_layout_m": rnd(np.mean(stds), 3) if stds else None,
        "length_ratio_vs_astar": rnd(np.mean(ratios), 3) if ratios else None,
        "ms_median": rnd(np.median(ms), 1) if ms else None,
        "ms_p95": rnd(np.percentile(ms, 95), 1) if ms else None,
        "first_solution_ms_median": rnd(np.median(fi), 1) if fi else None,
        "min_truth_clearance_m": rnd(min(r["truth_clear_m"] for r in ok), 3) if ok else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=30)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0, help="layout seed")
    ap.add_argument("--widths", default="0.4,0.5,0.6,0.7,0.8,1.0,1.2")
    ap.add_argument("--budgets", default="1000,5000")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    widths = [float(v) for v in a.widths.split(",")]
    budgets = [int(v) for v in a.budgets.split(",")]
    cmd = "python sweep.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tasks = [(wd, i, a.seed, a.seeds, budgets) for wd in widths for i in range(a.layouts)]
    t0 = time.perf_counter()
    rows = []
    with Pool(a.jobs) as pool:
        for k, part in enumerate(pool.imap_unordered(one_layout, tasks)):
            rows.extend(part)
            if (k + 1) % 20 == 0:
                print(f"{k + 1}/{len(tasks)} layouts, {time.perf_counter() - t0:.0f} s", flush=True)
    wall = time.perf_counter() - t0
    rows.sort(key=lambda r: (r["width"], r["index"], r["planner"], r["budget"] or 0, r["rng"] or 0))
    astar_len = {(r["width"], r["index"]): r["length_m"] for r in rows if r["planner"] == "astar" and r["ok"]}
    configs = [("astar", None)] + [(n, b) for n in ("rrt_star", "informed_rrt_star") for b in budgets]
    cells = []
    for wd in widths:
        for name, b in configs:
            sel = [r for r in rows if r["width"] == wd and r["planner"] == name and r["budget"] == b]
            cells.append({"width": wd, "planner": name, "budget": b,
                          "layouts": len({r["index"] for r in sel}), **summarize(sel, astar_len)})
    import scipy
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"sweep_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "wall_s": round(wall, 1), "jobs": a.jobs,
                   "widths": widths, "budgets": budgets, "layouts": a.layouts, "rng_seeds": a.seeds,
                   "constants": {k: v for k, v in vars(rrt_star).items()
                                 if k.isupper() and isinstance(v, (int, float))},
                   "env": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__, "machine": platform.machine(),
                           "system": platform.system()},
                   "cells": cells, "rows": rows}, fh, indent=1)
    f = lambda v: "-" if v is None else f"{v}"
    lines = [f"`{cmd}` (synthetic: arena narrow_gap layouts with the gap width fixed, planning only, "
             f"no flight), wall {wall:.1f} s on {a.jobs} processes\n",
             "| gap m | planner | budget | layouts | plans | success % | fallback % of ok | length mean m "
             "| length std within layout m | length / A* | plan median ms | plan p95 ms "
             "| first solution median ms | min truth clearance m |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        lines.append(f"| {c['width']} | {c['planner']} | {f(c['budget'])} | {c['layouts']} | {c['plans']} | "
                     f"{f(c['success_pct'])} | {f(c['fallback_pct_of_ok'])} | {f(c['length_mean_m'])} | "
                     f"{f(c['length_std_within_layout_m'])} | {f(c['length_ratio_vs_astar'])} | "
                     f"{f(c['ms_median'])} | {f(c['ms_p95'])} | {f(c['first_solution_ms_median'])} | "
                     f"{f(c['min_truth_clearance_m'])} |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
