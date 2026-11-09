"""DWA, Bug2 and TangentBug next to APF (+ wall-follow escape) and VFH+ from the reactive sample.

.venv/bin/python bench.py --layouts 50 --seed 0              # full table
.venv/bin/python bench.py --layouts 5 --seed 1 --no-write     # quick check

Three arena families (random, u_trap, narrow_gap) x two fans (72-beam default, 4-beam cf4).
Scores are the arena's, on truth. Path ratio = path length of a reached run / known-map A*
length (arena.astar_length: 8-connected A* on the layout grid inflated by the radius), median
over reached runs. The A* length uses the layout geometry after the run, for the report only.
Writes results/dwa_bug_<seed>.json (every run row, summaries, env, command) and .md (the
table), plus results/<planner>_<fan>_u_trap_<seed>_run<k>.png.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

import numpy as np
import scipy

import arena
import bug
import dwa

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
FAMILIES = ("random", "u_trap", "narrow_gap")
DWA_MEM_S = 3.0          # s, scan memory of the dwa_mem variant

apf, vfh_plus = arena.reactive()
PLANNERS = {
    "dwa": lambda: dwa.make(),
    "dwa_mem": lambda: dwa.make(memory_s=DWA_MEM_S),
    "bug2": lambda: bug.make("bug2"),
    "tangent_bug": lambda: bug.make("tangent_bug"),
    "apf": lambda: apf.make(),                 # reactive sample: APF with wall-follow escape
    "vfh_plus": lambda: vfh_plus.make(),       # reactive sample: VFH+
}

_ASTAR: dict = {}


def astar_ref(w, family, index):
    key = (family, w.seed, index)
    if key not in _ASTAR:
        _ASTAR[key] = arena.astar_length(w)
    return _ASTAR[key]


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
    for r, p, (w, _, _) in zip(rows, made, traces):
        ref = astar_ref(w, family, r["index"])
        r["astar_known_m"] = ref
        r["path_ratio"] = round(r["path_length_m"] / ref, 3) if (r["reached"] and ref) else None
        if pname in ("bug2", "tangent_bug"):
            r["mode_changes"] = len(p.log)
            r["bug2_fail_exit"] = any(m == "fail" for _, m in p.log)
        if pname.startswith("dwa"):
            r["no_admissible_steps"] = p.no_admissible_steps
    return rows, summ, traces, wall


def fmt(v):
    return "-" if v is None else f"{v}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--plot-index", type=int, default=0, help="u_trap run to plot per planner and fan")
    ap.add_argument("--only", default=None, help="comma-separated planner names")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    names = a.only.split(",") if a.only else list(PLANNERS)

    t_all = time.perf_counter()
    cells, lines = [], []
    for pname in names:
        for fan in arena.FANS:
            for fam in FAMILIES:
                rows, s, traces, wall = run_cell(pname, fan, fam, a.layouts, a.seed)
                ratios = [r["path_ratio"] for r in rows if r["path_ratio"] is not None]
                med_ratio = round(float(np.median(ratios)), 2) if ratios else None
                extra = {}
                if pname == "bug2":
                    extra["runs_with_fail_exit"] = sum(1 for r in rows if r["bug2_fail_exit"])
                if pname.startswith("dwa"):
                    extra["runs_with_no_admissible"] = sum(1 for r in rows if r["no_admissible_steps"] > 0)
                cells.append({"planner": pname, "fan": fan, "family": fam, "summary": s,
                              "median_path_ratio": med_ratio, "wall_s": round(wall, 2), **extra, "runs": rows})
                lines.append(f"| {pname} | {fan} | {fam} | {s['n']} | {fmt(s['reached_pct'])} | {fmt(s['collision_pct'])} "
                             f"| {fmt(s['stuck_pct'])} | {fmt(s['timeout_pct'])} | {fmt(s['median_time_to_goal_s'])} "
                             f"| {fmt(s['median_min_clearance_m'])} | {fmt(med_ratio)} |")
                print(lines[-1], f"wall {wall:.1f} s", extra or "", flush=True)
                if fam == "u_trap" and not a.no_write:
                    k = min(max(a.plot_index, 0), len(traces) - 1)
                    w, _, xy = traces[k]
                    png = os.path.join(RESULTS, f"{pname}_{fan}_u_trap_{a.seed}_run{k}.png")
                    os.makedirs(RESULTS, exist_ok=True)
                    arena.run.plot_run(png, w, xy, rows[k], arena.VEHICLE["radius"])
                    print(f"wrote {os.path.relpath(png, HERE)} (run {k}: {rows[k]['outcome']})")
    wall_all = time.perf_counter() - t_all

    head = ("| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % "
            "| median time to goal s | median min clearance m | median path / A* known |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|")
    md = (f"`{cmd}` (synthetic arena, seed {a.seed}, {a.layouts} layouts per cell), wall {wall_all:.1f} s\n\n"
          f"Fans: default = {arena.FANS['default']}; cf4 = {arena.FANS['cf4']} (angles in rad).\n"
          f"dwa_mem keeps {DWA_MEM_S} s of returns. apf and vfh_plus are imported unchanged from "
          f"samples/close-area-planner-reactive.\n\n{head}\n" + "\n".join(lines) + "\n")
    print("\n" + md)
    if a.no_write:
        return 0
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, f"dwa_bug_{a.seed}")
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    dwa_params = {k: getattr(dwa, k) for k in dir(dwa) if k.isupper()}
    bug_params = {k: getattr(bug, k) for k in dir(bug) if k.isupper()}
    with open(stem + ".json", "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seed": a.seed, "layouts": a.layouts,
                   "fans": arena.FANS, "arena_config": arena.run.DEFAULTS, "dwa_mem_s": DWA_MEM_S,
                   "dwa_params": dwa_params, "bug_params": bug_params,
                   "wall_s": round(wall_all, 2),
                   "env": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__, "machine": platform.machine(), "system": platform.system()},
                   "cells": cells}, fh, indent=1, default=str)
    print(f"wrote {os.path.relpath(stem, HERE)}.md, .json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
