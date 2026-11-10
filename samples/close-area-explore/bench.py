"""Search-arm benchmark: families x layouts x sensor presets x region radius x arm.

.venv/bin/python bench.py --layouts 20 --seed 0 [--families random,office,warehouse]
                          [--presets ideal,crazyflie] [--jobs 14]

Region radius: 0, 2, 5 m around a nominal, or "unknown" (no nominal). `frontier` ignores the
region, so it runs once per layout and its rows repeat under every radius; `nominal_frontier`
with no nominal is `frontier` and is not rerun. `oracle` (B given as a coordinate) runs once.
Writes results/bench_<seed>.json (every run row) and results/bench_<seed>.md (tables).
--jobs uses a process pool on the CLI only; explore.py itself has no threads or processes.
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

import explore

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
REGIONS = (0.0, 2.0, 5.0, None)
SEARCH_ARMS = ("frontier", "nominal_frontier", "lawnmower", "random_walk")


def rlabel(r):
    return "unknown" if r is None else f"{r:g} m"


def jobs_for(families, presets, layouts, seed):
    out = []
    for fam in families:
        for pre in presets:
            for i in range(layouts):
                out.append(("oracle", fam, seed, i, None, pre))
                out.append(("frontier", fam, seed, i, None, pre))
                for r in REGIONS:
                    if r is not None:
                        out.append(("nominal_frontier", fam, seed, i, r, pre))
                    out.append(("lawnmower", fam, seed, i, r, pre))
                    out.append(("random_walk", fam, seed, i, r, pre))
    return out


def _do(job):
    arm, fam, seed, i, r, pre = job
    return explore.run_one(arm, fam, seed, i, r, pre)


def cell_rows(rows, arm, region, fam=None, pre=None):
    """Rows for one table cell, with the reuse rules from the module docstring."""
    def keep(x):
        return (fam is None or x["family"] == fam) and (pre is None or x["preset"] == pre)
    if arm == "frontier" or (arm == "nominal_frontier" and region is None):
        return [x for x in rows if x["arm"] == "frontier" and keep(x)]
    if arm == "oracle":
        return [x for x in rows if x["arm"] == "oracle" and keep(x)]
    return [x for x in rows if x["arm"] == arm and x["region_m"] == region and keep(x)]


def fmt_ci(p, ci):
    return "-" if p is None else f"{p} [{ci[0]}, {ci[1]}]"


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| {k} | region | arm | n | found % [95 % CI] | reached % [95 % CI] | collision % [95 % CI] "
        "| stuck % | timeout % | median time to find s | median time to B s |")


def table(rows, families, presets, by):
    """by = 'preset' (pooled over families) or 'family,preset'."""
    out = []
    groups = ([(None, p) for p in presets] if by == "preset"
              else [(fa, p) for fa in families for p in presets])
    key = "preset" if by == "preset" else "family / preset"
    out.append(HEAD.format(k=key))
    out.append("|---" * 11 + "|")
    for fam, pre in groups:
        g = pre if fam is None else f"{fam} / {pre}"
        s = explore.summarize(cell_rows(rows, "oracle", None, fam, pre))
        out.append(f"| {g} | B given | oracle | {s['n']} | {fmt_ci(s['found_pct'], s['found_ci'])} | "
                   f"{fmt_ci(s['reached_pct'], s['reached_ci'])} | {fmt_ci(s['collision_pct'], s['collision_ci'])} | "
                   f"{f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_find_s'])} | "
                   f"{f(s['median_time_to_b_s'])} |")
        for r in REGIONS:
            for arm in SEARCH_ARMS:
                s = explore.summarize(cell_rows(rows, arm, r, fam, pre))
                name = arm + (" (= frontier)" if arm == "nominal_frontier" and r is None else "")
                name += " (region ignored)" if arm == "frontier" else ""
                out.append(f"| {g} | {rlabel(r)} | {name} | {s['n']} | {fmt_ci(s['found_pct'], s['found_ci'])} | "
                           f"{fmt_ci(s['reached_pct'], s['reached_ci'])} | "
                           f"{fmt_ci(s['collision_pct'], s['collision_ci'])} | {f(s['stuck_pct'])} | "
                           f"{f(s['timeout_pct'])} | {f(s['median_time_to_find_s'])} | {f(s['median_time_to_b_s'])} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--families", default="random,office,warehouse")
    ap.add_argument("--presets", default="ideal,crazyflie")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--name", default=None)
    a = ap.parse_args(argv)
    fams, pres = a.families.split(","), a.presets.split(",")
    jobs = jobs_for(fams, pres, a.layouts, a.seed)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    print(f"{len(jobs)} runs on {a.jobs} processes", flush=True)
    t0 = time.perf_counter()
    if a.jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(a.jobs) as ex:
            rows = list(ex.map(_do, jobs, chunksize=4))
    else:
        rows = [_do(j) for j in jobs]
    wall = time.perf_counter() - t0
    consts = {k: v for k, v in vars(explore).items() if k.isupper() and isinstance(v, (int, float, tuple))}
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, a.name or f"bench_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seed": a.seed, "layouts": a.layouts,
                   "families": fams, "presets": pres, "regions": [rlabel(r) for r in REGIONS],
                   "constants": consts, "wall_s": round(wall, 1), "jobs": a.jobs,
                   "env": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__, "machine": platform.machine(),
                           "system": platform.system()},
                   "runs": rows}, fh, indent=0)
    pooled = table(rows, fams, pres, "preset")
    per = table(rows, fams, pres, "family,preset")
    col = [r for r in rows if r["collision"]]
    lines = [f"`{cmd}` from samples/close-area-explore. Input: synthetic (simulated layouts, vehicle, "
             f"range sensor; B detection by exact range + line of sight). Scored on truth. "
             f"{len(rows)} runs, wall {wall:.1f} s on {a.jobs} processes.", "",
             f"Detection: within {explore.DETECT_RANGE_M} m of B with a clear line of sight. "
             f"Budget {explore.MAX_TIME_S:g} s per run. Wilson 95 % intervals. Times are medians over "
             "runs that found / reached B, measured from take-off.", "",
             "## Pooled over families", "", pooled, "",
             "## Per family", "", per, "",
             f"## Collisions ({len(col)} runs)", ""]
    for r in col:
        lines.append(f"- {r['family']} {r['preset']} layout {r['index']} {r['arm']} region "
                     f"{rlabel(r['region_m'])}: t {r['duration_s']} s, found {r['found']}, "
                     f"min clearance {r['min_clearance_m']} m")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(pooled)
    print(f"\nwall {wall:.1f} s; wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
