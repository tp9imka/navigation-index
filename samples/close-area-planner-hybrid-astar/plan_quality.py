"""Planning only, known map: path shape and time-to-B of the first plan A=>B, Hybrid A* vs astar_esdf.

.venv/bin/python plan_quality.py --layouts 20 --seed 0       # single process, results/plan_quality_0.*

Each planner plans once from A (at rest, heading towards B) on the arena's prior 0.1 m grid
(known_map=True). For each plan: path length, heading change per metre (metrics.heading_stats),
and the minimum time to fly it from rest to rest under the same limits for both planners
(metrics.time_along): |v| <= 1.5 m/s, |a_lon| <= 3 m/s^2, v^2 k <= 3 m/s^2 ("stock"), plus turn rate
v k <= 1.0 rad/s ("turn1"). Plan time is wall ms of one _plan call (ESDF cached for the known map,
as in flight). Exact clearance of the planned path = min world.sdf over its 0.1 m samples.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time

import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import hybrid_astar  # noqa: E402
import metrics  # noqa: E402

world_glass = arena.mod("world_glass")
FAMILIES = ("random", "u_trap", "narrow_gap", "office", "warehouse", "forest", "maze", "glass_office")
RESULTS = os.path.join(HERE, "results")


def plan_once(name, w):
    pl = hybrid_astar.make(known_map=True) if name == "hybrid_astar" else arena.astar_esdf.make(known_map=True)
    pl.reset()
    pose = arena.Pose(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, math.atan2(w.goal[1], w.goal[0]))
    goal = (w.goal[0], w.goal[1], 1.0)
    pl._layers(w.grid)                       # ESDF of the static map, cached as in flight
    t0 = time.perf_counter()
    pl._plan(pose, goal, w.grid)
    ms = (time.perf_counter() - t0) * 1e3
    P = pl.path_xy
    row = {"planner": name, "plan_ms": round(ms, 2), "found": P is not None}
    if P is None:
        return row
    dense = metrics.resample(P, 0.1)
    row.update({"path_length_m": round(float(np.hypot(*np.diff(P, axis=0).T).sum()), 3),
                "min_sdf_m": round(float(min(w.sdf(p) for p in dense)), 3),
                **metrics.heading_stats(P),
                "time_stock_s": round(metrics.time_along(P), 2),
                "time_turn1_s": round(metrics.time_along(P, omega=1.0), 2)})
    if name == "hybrid_astar":
        row["source"] = pl.last_source
        row["expansions"] = pl.expansions[-1]
        # the planner's own speed-profile time (follower cap), for reference
        prof = np.maximum(pl.prof, 1e-3)
        ds = np.hypot(*np.diff(P, axis=0).T)
        row["profile_time_s"] = round(float(np.sum(2 * ds / (prof[:-1] + prof[1:]))), 2)
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    cmd = "python plan_quality.py " + " ".join(argv if argv is not None else sys.argv[1:])
    rows = []
    t_all = time.perf_counter()
    for fam in FAMILIES:
        for i in range(a.layouts):
            w = world_glass.make_any_world(fam, a.seed, i)
            for name in ("astar_esdf", "hybrid_astar"):
                r = plan_once(name, w)
                r.update({"family": fam, "index": i})
                rows.append(r)
    wall = round(time.perf_counter() - t_all, 1)
    keys = ("path_length_m", "max_rad_per_m", "p95_rad_per_m", "share_above_cruise_kappa", "total_turn_rad",
            "time_stock_s", "time_turn1_s", "min_sdf_m")
    summ = {}
    for fam in FAMILIES + ("all",):
        for name in ("astar_esdf", "hybrid_astar"):
            sel = [r for r in rows if r["planner"] == name and (fam == "all" or r["family"] == fam)]
            ok = [r for r in sel if r["found"]]
            ms = [r["plan_ms"] for r in sel]
            s = {"n": len(sel), "found_pct": round(100.0 * len(ok) / len(sel), 1),
                 "plan_ms_median": round(float(np.median(ms)), 2), "plan_ms_p95": round(float(np.percentile(ms, 95)), 2)}
            for k in keys:
                s[k] = round(float(np.median([r[k] for r in ok])), 3) if ok else None
            if name == "hybrid_astar":
                s["grid_fallback_pct"] = round(100.0 * sum(r.get("source") == "grid" for r in ok) / max(1, len(ok)), 1)
            summ.setdefault(fam, {})[name] = s
    # paired per layout: hybrid - astar
    pair = {}
    for k in ("time_stock_s", "time_turn1_s", "path_length_m", "max_rad_per_m"):
        d = []
        for fam in FAMILIES:
            for i in range(a.layouts):
                ra = next(r for r in rows if r["planner"] == "astar_esdf" and r["family"] == fam and r["index"] == i)
                rh = next(r for r in rows if r["planner"] == "hybrid_astar" and r["family"] == fam and r["index"] == i)
                if ra["found"] and rh["found"]:
                    d.append(rh[k] - ra[k])
        pair[k] = {"median": round(float(np.median(d)), 3), "hybrid_lower_pct": round(100.0 * np.mean(np.array(d) < 0), 1),
                   "n": len(d)}
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, f"plan_quality_{a.seed}")
    envd = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system()}
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "wall_s": wall,
                   "env": envd, "summary": summ, "paired_hybrid_minus_astar": pair, "runs": rows}, fh, indent=1)
    f = lambda v: "-" if v is None else f"{v:g}"        # noqa: E731
    md = [f"`{cmd}` from samples/close-area-planner-hybrid-astar, single process, wall {wall} s. Input: synthetic "
          f"(arena layouts, known prior grid). One plan from A per layout, {a.layouts} layouts per family.", "",
          "Medians over layouts. rad/m = heading change per metre at 0.25 m spacing. share > k = share of joints "
          "with heading change above 0.67 rad/m (1.0 rad/s at 1.5 m/s). Time stock / turn1 = minimum rest-to-rest "
          "time along the path at |v| <= 1.5, |a| <= 3, lateral <= 3 m/s^2, turn1 adds turn rate <= 1.0 rad/s "
          "(metrics.py). Min sdf = exact clearance of the path centre line (vehicle radius 0.15 m).", "",
          "| family | planner | found % | plan ms median / p95 | path m | max rad/m | p95 rad/m | share > k | total turn rad "
          "| time stock s | time turn1 s | min sdf m |", "|" + "---|" * 12]
    for fam in FAMILIES + ("all",):
        for name in ("astar_esdf", "hybrid_astar"):
            s = summ[fam][name]
            md.append(f"| {fam} | {name} | {f(s['found_pct'])} | {f(s['plan_ms_median'])} / {f(s['plan_ms_p95'])} | "
                      f"{f(s['path_length_m'])} | {f(s['max_rad_per_m'])} | {f(s['p95_rad_per_m'])} | "
                      f"{f(s['share_above_cruise_kappa'])} | {f(s['total_turn_rad'])} | {f(s['time_stock_s'])} | "
                      f"{f(s['time_turn1_s'])} | {f(s['min_sdf_m'])} |")
    md += ["", f"Hybrid A* plans that fell back to the grid path: {f(summ['all']['hybrid_astar']['grid_fallback_pct'])} %.",
           "", "Paired per layout (hybrid_astar - astar_esdf):", "", "| metric | median delta | hybrid lower in % of layouts | layouts |",
           "|---|---|---|---|"]
    for k, v in pair.items():
        md.append(f"| {k} | {v['median']:g} | {v['hybrid_lower_pct']:g} | {v['n']} |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
