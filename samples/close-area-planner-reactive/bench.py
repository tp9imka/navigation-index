"""Run APF and VFH+ over the arena families with two range fans and say where they get stuck.

.venv/bin/python bench.py --layouts 50 --seed 0            # full table, about 80 s
.venv/bin/python bench.py --layouts 10 --seed 1 --no-write  # dev seed used for tuning

Writes results/reactive_<seed>.json (every run row, summaries, env, command) and
results/reactive_<seed>.md (the tables), plus results/<planner>_<fan>_u_trap_<seed>_run<k>.png.
"End place" uses the world geometry, after the run, for the report only; planners never see it.
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

import arena
import apf
import vfh_plus

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
PLANNERS = {"apf": apf.make, "apf_noescape": lambda: apf.make(escape=False), "vfh_plus": vfh_plus.make}
FAMILIES = ("random", "u_trap", "narrow_gap")


def end_place(w, xy, outcome) -> str:
    """Where a run that did not reach B ended, from the layout geometry."""
    if outcome == "reached":
        return "reached"
    x, y = float(xy[-1, 0]), float(xy[-1, 1])
    if w.family == "u_trap":
        cup = w.boxes[:4]
        x0 = min(b.cx - b.hx for b in cup); x1 = max(b.cx + b.hx for b in cup)
        y0 = min(b.cy - b.hy for b in cup); y1 = max(b.cy + b.hy for b in cup)
        return "in_cup" if (x0 <= x <= x1 and y0 <= y <= y1) else "outside_cup"
    if w.family == "narrow_gap":
        b0, b1 = w.boxes[0], w.boxes[1]
        vertical = abs(b0.cx - b1.cx) < 1e-9
        pos = b0.cx if vertical else b0.cy
        p, g = (x, w.goal[0]) if vertical else (y, w.goal[1])
        if (p - pos) * (g - pos) > 0:
            return "past_wall"
        # gap centre along the wall: between the two segments
        lo = (b0.cy + b0.hy) if vertical else (b0.cx + b0.hx)
        hi = (b1.cy - b1.hy) if vertical else (b1.cx - b1.hx)
        along = y if vertical else x
        near_gap = abs(along - 0.5 * (lo + hi)) <= 1.0 and abs(p - pos) <= 1.0
        return "at_gap" if near_gap else "before_wall"
    return "near_obstacle" if w.clearance(x, y) < 0.8 else "open"


def run_cell(pname, fan, family, layouts, seed):
    made = []

    def factory():
        p = PLANNERS[pname]()
        made.append(p)
        return p

    t0 = time.perf_counter()
    rows, summ, traces = arena.run.evaluate(factory, family, layouts, seed, cfg=arena.cfg_for(fan),
                                            keep_traces=True)
    wall = time.perf_counter() - t0
    for r, p, (w, _, xy) in zip(rows, made, traces):
        r["end_place"] = end_place(w, xy, r["outcome"])
        r["end_dist_to_goal_m"] = round(math.hypot(xy[-1, 0] - w.goal[0], xy[-1, 1] - w.goal[1]), 3)
        if pname.startswith("apf"):
            r["escapes"] = sum(1 for _, m in p.log if m == "wall_follow")
        if pname == "vfh_plus":
            r["no_valley_steps"] = p.no_valley_steps
    return rows, summ, traces, wall


def fmt(v):
    return "-" if v is None else f"{v}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--plot-index", type=int, default=0, help="u_trap run to plot per planner and fan")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])

    t_all = time.perf_counter()
    cells, main_rows, where_rows = [], [], []
    for pname in PLANNERS:
        for fan in arena.FANS:
            for fam in FAMILIES:
                rows, s, traces, wall = run_cell(pname, fan, fam, a.layouts, a.seed)
                places = {}
                for r in rows:
                    places[r["end_place"]] = places.get(r["end_place"], 0) + 1
                fail = [r["end_dist_to_goal_m"] for r in rows if r["outcome"] != "reached"]
                extra = {}
                if pname.startswith("apf"):
                    extra["runs_with_escape"] = sum(1 for r in rows if r["escapes"] > 0)
                    extra["reached_after_escape"] = sum(1 for r in rows if r["escapes"] > 0 and r["reached"])
                else:
                    extra["runs_with_no_valley"] = sum(1 for r in rows if r["no_valley_steps"] > 0)
                cells.append({"planner": pname, "fan": fan, "family": fam, "summary": s, "wall_s": round(wall, 2),
                              "end_places": places, "median_fail_end_dist_m": round(float(np.median(fail)), 2) if fail else None,
                              **extra, "runs": rows})
                main_rows.append(f"| {pname} | {fan} | {fam} | {s['n']} | {fmt(s['reached_pct'])} | {fmt(s['collision_pct'])} "
                                 f"| {fmt(s['stuck_pct'])} | {fmt(s['timeout_pct'])} | {fmt(s['median_time_to_goal_s'])} "
                                 f"| {fmt(s['median_min_clearance_m'])} |")
                pl = ", ".join(f"{k} {v}" for k, v in sorted(places.items(), key=lambda kv: -kv[1]))
                ex = (f"escape in {extra['runs_with_escape']}, reached after escape {extra['reached_after_escape']}"
                      if pname.startswith("apf") else f"no-valley stop in {extra['runs_with_no_valley']}")
                where_rows.append(f"| {pname} | {fan} | {fam} | {pl} | {fmt(cells[-1]['median_fail_end_dist_m'])} | {ex} |")
                print(main_rows[-1], f"wall {wall:.1f} s", flush=True)
                if fam == "u_trap" and not a.no_write:
                    k = min(max(a.plot_index, 0), len(traces) - 1)
                    w, _, xy = traces[k]
                    png = os.path.join(RESULTS, f"{pname}_{fan}_u_trap_{a.seed}_run{k}.png")
                    os.makedirs(RESULTS, exist_ok=True)
                    arena.run.plot_run(png, w, xy, rows[k], arena.run.DEFAULTS["vehicle"]["radius"])
                    print(f"wrote {os.path.relpath(png, HERE)} (run {k}: {rows[k]['outcome']})")
    wall_all = time.perf_counter() - t_all

    head = ("| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % "
            "| median time to goal s | median min clearance m |\n|---|---|---|---|---|---|---|---|---|---|")
    whead = ("| planner | fan | family | where runs ended (count) | median end distance to B, failed runs, m | escape / stop |\n"
             "|---|---|---|---|---|---|")
    md = (f"`{cmd}` (synthetic arena, seed {a.seed}, {a.layouts} layouts per cell), wall {wall_all:.1f} s\n\n"
          f"Fans: default = {arena.FANS['default']}; cf4 = {arena.FANS['cf4']} (angles in rad).\n\n"
          f"{head}\n" + "\n".join(main_rows) + f"\n\n{whead}\n" + "\n".join(where_rows) + "\n")
    print("\n" + md)
    if a.no_write:
        return 0
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, f"reactive_{a.seed}")
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    with open(stem + ".json", "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seed": a.seed, "layouts": a.layouts,
                   "fans": arena.FANS, "arena_config": arena.run.DEFAULTS,
                   "planner_params": {"apf": vars(apf.APF()) | {"log": None},
                                      "vfh_plus": {k: v for k, v in vars(vfh_plus.VFHPlus()).items()
                                                   if not isinstance(v, np.ndarray)}},
                   "wall_s": round(wall_all, 2),
                   "env": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__, "machine": platform.machine(), "system": platform.system()},
                   "cells": cells}, fh, indent=1, default=str)
    print(f"wrote {os.path.relpath(stem, HERE)}.md, .json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
