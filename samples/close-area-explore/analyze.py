"""Why nearest-frontier misses B: map coverage at the end of each run vs the layout's free area.

.venv/bin/python analyze.py [--bench results/bench_0.json]

For every run of the chosen arm, free area = cells of the arena's true 0.1 m grid that are not
occupied (inside the walls). known_free_m2 (from the run row) / free area = the fraction of the
room the planner's log-odds map holds as free when the run ends. Writes results/analysis_0.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

import explore

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default=os.path.join(HERE, "results", "bench_0.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "results", "analysis_0.md"))
    a = ap.parse_args(argv)
    doc = json.load(open(a.bench))
    rows = doc["runs"]
    free_area = {}
    for r in rows:
        k = (r["family"], r["seed"], r["index"])
        if k not in free_area:
            w = explore.A.world.make_world(r["family"], r["seed"], r["index"])
            free_area[k] = float((~w.grid.occ).sum()) * w.grid.res ** 2
    lines = [f"`python analyze.py` on {os.path.relpath(a.bench, HERE)} (synthetic). Map coverage = "
             "known-free area of the planner's log-odds map at the end of the run / free area of the "
             "true 0.1 m grid.", "",
             "| preset | arm | region | outcome group | runs | median coverage | min | max |",
             "|---|---|---|---|---|---|---|---|"]
    for pre in doc["presets"]:
        for arm, reg in (("frontier", None), ("nominal_frontier", 5.0), ("lawnmower", None)):
            sel = [r for r in rows if r["arm"] == arm and r["preset"] == pre and r["region_m"] == reg]
            for name, grp in (("found B", [r for r in sel if r["found"]]),
                              ("not found, stuck (hovering)", [r for r in sel if not r["found"] and r["stuck"]]),
                              ("not found, timeout", [r for r in sel if not r["found"] and r["timeout"]]),
                              ("not found, collision", [r for r in sel if not r["found"] and r["collision"]])):
                if not grp:
                    continue
                cov = [r["known_free_m2"] / free_area[(r["family"], r["seed"], r["index"])] for r in grp]
                rl = "unknown" if reg is None else f"{reg:g} m"
                lines.append(f"| {pre} | {arm} | {rl} | {name} | {len(grp)} | {np.median(cov):.2f} | "
                             f"{min(cov):.2f} | {max(cov):.2f} |")
    # rerun the ideal frontier runs that ended stuck without B: did the arm run out of frontiers?
    stuck = [r for r in rows if r["arm"] == "frontier" and r["preset"] == "ideal" and r["stuck"] and not r["found"]]
    orig = explore.Explorer.step
    seen = {}

    def spy(self, *args, **kw):
        sp = orig(self, *args, **kw)
        seen["none"] = self.target is None and self.last_none
        return sp

    explore.Explorer.step = spy
    n_none = 0
    for r in stuck:
        x = explore.run_one("frontier", r["family"], r["seed"], r["index"], None, "ideal")
        n_none += bool(x["outcome"] == r["outcome"] and seen.get("none"))
    explore.Explorer.step = orig
    lines += ["", f"Ideal `frontier` runs stuck without B, rerun: {n_none} of {len(stuck)} ended with no "
              "frontier left (last selection returned none, same outcome as bench)."]
    # coverage above 1: rerun the 3 highest-coverage ideal frontier runs with beam dropout off
    # (a runtime copy of the ideal preset; presets.py is not edited)
    P = explore.A.presets.SENSOR_PRESETS
    P["ideal_nodropout"] = dict(P["ideal"], dropout=0.0)
    fr = sorted((r["known_free_m2"] / free_area[(r["family"], r["seed"], r["index"])], r)
                for r in rows if r["arm"] == "frontier" and r["preset"] == "ideal")
    lines += ["", "Highest-coverage ideal `frontier` runs, rerun with dropout 0 (everything else equal):", "",
              "| family | layout | coverage, ideal (2 % dropout) | coverage, dropout 0 |", "|---|---|---|---|"]
    for cov, r in fr[-3:]:
        x = explore.run_one("frontier", r["family"], r["seed"], r["index"], None, "ideal_nodropout")
        c0 = x["known_free_m2"] / free_area[(r["family"], r["seed"], r["index"])]
        lines.append(f"| {r['family']} | {r['index']} | {cov:.2f} | {c0:.2f} |")
    del P["ideal_nodropout"]
    import bench
    head = ["", "## Headline (pooled over random, office, warehouse; same numbers as bench_0.md)", "",
            "| region | arm | ideal found % [95 % CI] | ideal collision % [95 % CI] | ideal median time to find s "
            "| ideal median time to B s | crazyflie found % [95 % CI] | crazyflie collision % [95 % CI] "
            "| crazyflie median time to B s |", "|---" * 9 + "|"]
    cells = [("B given", "oracle", None)] + [(bench.rlabel(r), arm, r) for r in bench.REGIONS
                                             for arm in bench.SEARCH_ARMS
                                             if not (arm == "nominal_frontier" and r is None)
                                             and not (arm == "frontier" and r is not None)]
    for lab, arm, r in cells:
        si = explore.summarize(bench.cell_rows(rows, arm, r, None, "ideal"))
        sc = explore.summarize(bench.cell_rows(rows, arm, r, None, "crazyflie"))
        head.append(f"| {lab} | {arm} | {bench.fmt_ci(si['found_pct'], si['found_ci'])} | "
                    f"{bench.fmt_ci(si['collision_pct'], si['collision_ci'])} | {bench.f(si['median_time_to_find_s'])} | "
                    f"{bench.f(si['median_time_to_b_s'])} | {bench.fmt_ci(sc['found_pct'], sc['found_ci'])} | "
                    f"{bench.fmt_ci(sc['collision_pct'], sc['collision_ci'])} | {bench.f(sc['median_time_to_b_s'])} |")
    lines += head
    with open(a.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
