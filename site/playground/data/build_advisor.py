#!/usr/bin/env python3
"""Build site/playground/data/advisor.json for the playground Advisor panel (loop-65). Stdlib only.

Reads:
  samples/close-area-benchmark/results/matrix_0.json   per-run rows, 14 planners x 8 families x 2 presets
  samples/close-area-benchmark/results/prior_check_0.json   shipped vs geofenced unknown-map A* (ideal)
  samples/close-area-relocalize/results/reloc_matrix_refs.md   A* known map under VIO dropout / jump, 7 families
Writes:
  site/playground/data/advisor.json

Every input is synthetic (simulated layouts, vehicle, sensors, VIO). Cell stats are recomputed from the
per-run rows and checked against the matrix's own summary; the script exits non-zero on a mismatch.

    python3 site/playground/data/build_advisor.py          # < 1 s
"""
import json
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = ROOT / "samples/close-area-benchmark/results/matrix_0.json"
PRIOR = ROOT / "samples/close-area-benchmark/results/prior_check_0.json"
RELOC = ROOT / "samples/close-area-relocalize/results/reloc_matrix_refs.md"
OUT = HERE / "advisor.json"
PLAYGROUND_LIMIT_S = 60.0          # run.DEFAULTS max_time_s: worker.js limit for every family not in PLAYGROUND_LONG
PLAYGROUND_LONG = {"maze": 120.0, "warehouse": 120.0}   # loop-73b: worker.js max_time_for = bench.py LONG_FAMILIES

PRIOR_MAP = {"astar_known", "informed_rrt_star", "astar_mpc"}
# playground option id => benchmark row. Ids not listed map to the benchmark row of the same name.
PG_TO_BENCH = {"straight": "straight", "freest_beam": "freest_beam", "astar_known": "astar_known",
               "astar_unknown": "astar_unknown", "apf": "apf_escape", "vfh_plus": "vfh_plus"}
# benchmark row => what to set in the playground (planner option id, filter option id)
BENCH_TO_PG = {"apf_escape": {"planner": "apf", "filter": "none"},
               "astar_unknown_f2": {"planner": "astar_unknown", "filter": "F2"}}
PG_NOW = set(PG_TO_BENCH)          # the 6 planner options in playground.js LABELS.planner on 2026-11-09

FAMILY_LABEL = {"random": "Random boxes + cylinders", "u_trap": "U trap", "narrow_gap": "Narrow gap",
                "office": "Office (rooms + corridor)", "warehouse": "Warehouse (shelf aisles)",
                "forest": "Forest (40-90 poles)", "maze": "Maze (10 x 10 cells)",
                "glass_office": "Glass office (glass panels)"}

B = "samples/close-area-benchmark/README.md"
A = "samples/close-area-arena/README.md"

# Short, plain option docs. Numbers come from the cited READMEs (all synthetic). The "matrix" lines
# per planner and the per-family impact lines are generated from matrix_0.json below.
PLANNER_DOCS = {
    "straight": dict(
        what="Flies the straight line from A to B. Slows to a stop for returns within 30 deg of the line and never steers.",
        needs="No map. Any range sensor.",
        good="Only a floor for comparisons.",
        fails="Stops in front of the first obstacle on the line (scored stuck). Its brake is late with 4 beams, so it collides.",
        src=[A]),
    "freest_beam": dict(
        what="Steers towards the range beam with the most free space near the direction of B. A few lines of code.",
        needs="No map. Range beams only, for example a Crazyflie Multi-ranger.",
        good="Open clutter. 86 % reached on random with true pose (50 layouts, arena README).",
        fails="Cannot leave a U trap or find a door. VIO errors cut reach: 86 => 40-58 % across the fault cases, still 0 % collision.",
        src=[A]),
    "apf_escape": dict(
        what="Artificial potential field: B pulls, range returns push. After 3 s without progress it follows the wall (escape rule).",
        needs="No map. Range scan and pose.",
        good="Safest map-free choice with walking people: 98 % / 94 % reached, 0 % / 2 % collision at 0.5 / 1.0 m/s (moving-obstacles README, 50 layouts).",
        fails="Doors and narrow gaps: the push from both door frames cancels the pull of B.",
        src=["samples/close-area-planner-reactive/README.md", "samples/close-area-moving-obstacles/README.md"]),
    "vfh_plus": dict(
        what="VFH+: a 72-sector polar histogram of obstacles, then picks the free valley closest to B. No escape rule.",
        needs="No map. A dense 360 deg scan.",
        good="Open clutter with a dense scan.",
        fails="With 4 beams it sees almost no obstacles and collides in 55-100 % of runs (benchmark README).",
        src=["samples/close-area-planner-reactive/README.md", B]),
    "astar_known": dict(
        what="A* on the true prior map, inflated by the vehicle radius + 0.10 m, with a clearance cost. Replans at 2-5 Hz and follows a carrot.",
        needs="An exact prior map and a good pose. Ignores the range sensor.",
        good="100 % reached, 0 % collision in every family on both presets (benchmark, true pose).",
        fails="Trusts the pose. With VIO faults it steers relative to the wrong position (fault docs). Obstacles missing from the map are invisible to it.",
        src=[B, A]),
    "astar_unknown": dict(
        what="The same A*, but on a map built during flight from range hits. Unknown cells count as free with a penalty.",
        needs="No prior map. A range sensor; works best with a dense 360 deg scan.",
        good="Best map-free planner on the ideal sensor in every family (55-100 % reached, 0 % collision).",
        fails="With 4 beams the map has holes: office 35 %, warehouse 0 % (50 % collision), glass_office 5 % (65 % collision).",
        src=[B]),
    "informed_rrt_star": dict(
        what="Informed RRT*: grows a random tree of paths on the prior map (5000 samples), then refines inside an ellipse around A and B.",
        needs="An exact prior map.",
        good="100 % reached, 0 % collision in every family (benchmark).",
        fails="Slow: in maze and warehouse 30 of its 40 successes took more than 60 s. Narrow gaps: 85.7 % planning success at a 0.4 m gap vs 100 % for A* (sampling README).",
        src=[B, "samples/close-area-planner-sampling/README.md"]),
    "astar_mpc": dict(
        what="A* on the prior map, followed by a linear MPC that keeps the drone inside a corridor of free space (OSQP, 0.22 ms median solve).",
        needs="An exact prior map. No unknown-map mode.",
        good="100 % reached, 0 % collision in every family; flies like the plain A* follower here.",
        fails="Same as A* known map: a wrong pose or a wrong map breaks it.",
        src=[B, A]),
    "astar_unknown_f2": dict(
        what="A* unknown map with the F2 safety filter (PX4-CBF as shipped) between the planner and the vehicle.",
        needs="No prior map. A range sensor.",
        good="With 4 beams it collides less: warehouse 50 => 0 %, maze reached 35 => 55 % (benchmark).",
        fails="With 72 beams it freezes in doors, gaps and aisles: 0 % reached on narrow_gap, office, warehouse, maze and glass_office. Blind to glass.",
        src=[B]),
    "dwa": dict(
        what="Dynamic Window Approach: samples velocities the drone can reach in the next step and scores them on progress and clearance.",
        needs="No map. Range scan.",
        good="Smooth local avoidance under a global planner.",
        fails="Alone it does not leave a U trap or find a door: 0 % on u_trap and maze on both presets.",
        src=[B, "samples/close-area-planner-dwa-bug/README.md"]),
    "dwa_mem": dict(
        what="DWA plus 3 s of remembered range returns, so obstacles stay known between sparse beams.",
        needs="No map. Range scan and a pose for the memory.",
        good="Makes DWA safe with 4 beams: crazyflie collisions office 55 => 0 %, forest 90 => 15 %, glass_office 60 => 5 %.",
        fails="Reach barely moves: in rooms the runs now end stuck instead (office 95 % stuck on crazyflie).",
        src=[B]),
    "bug2": dict(
        what="Bug2: fly the A-B line; at an obstacle, follow its wall until back on the line closer to B.",
        needs="No map. Range scan.",
        good="Leaves U traps: 90 % on u_trap (ideal). 90 % on random with 4 beams.",
        fails="Rooms and doors: at most 25 % on office, warehouse, glass_office. Collides in 20-40 % of crazyflie runs in most families.",
        src=[B]),
    "tangent_bug": dict(
        what="TangentBug: uses range readings to head for the obstacle edge (tangent point) that shortens the way to B.",
        needs="No map. A 360 deg range scan.",
        good="Best pure local planner on ideal narrow_gap after VFH+ (45 vs 50 %).",
        fails="Collides in 10-75 % of crazyflie runs in every family.",
        src=[B]),
    "dstar_lite": dict(
        what="D* Lite: the unknown-map A*, but it repairs the old plan when the map changes instead of searching again.",
        needs="No prior map. A range sensor.",
        good="Same flights as A* unknown map (153 of 160 identical outcomes on ideal) with 4-7x less search time per replan; matters above about 40 x 40 m.",
        fails="Same holes as A* unknown map with 4 beams: glass_office 10 % reached, 65 % collision.",
        src=[B, "samples/close-area-planner-dstar/README.md"]),
}

PRESET_DOCS = {
    "ideal": dict(
        what="72 rays, 360 deg, 6 m range, 0.02 m noise, 2 % dropout. Sees every material, glass included. Think of a 2D lidar.",
        impact="The prior-map planners do not read it. Map-free planners do best here."),
    "crazyflie": dict(
        what="4 cone beams of 27 deg (front, back, left, right), 3 m range, glass and mirrors invisible, dark surfaces seen to 1 m. Like a Crazyflie Multi-ranger deck.",
        impact="Holes between beams: map-free planners collide much more than on ideal."),
    "crazyflie_bright": dict(
        what="The Crazyflie preset in bright light: range drops to 0.73 m.",
        impact="Not in the benchmark. Arena README (random, 50 layouts): A* unknown map 62 % reached, 38 % collision vs 98 / 2 % on crazyflie; freest_beam 58 / 0 %.",
        src=[A]),
}

FAULT_DOCS = {
    "truth": dict(
        what="No estimator: the planner sees the true position.",
        impact="Every benchmark number in this panel uses this setting. Treat them as upper bounds."),
    "none": dict(
        what="A VIO-like EKF (30 Hz VIO + 50 Hz IMU) with 2 dark zones per layout where drift grows 4x and frames drop. No injected fault.",
        impact="Random, 100 layouts: A* known map 100 => 69 % reached, 0 % collision (safety-filter README). freest_beam 86 => 58 % (arena README). Most failures stop at the estimated B, more than 0.3 m from the real one.",
        src=["samples/close-area-safety-filter/README.md", A]),
    "jump": dict(
        what="The estimate jumps 0.5 m when the drone is within 1 m of an obstacle, like a VIO relocalization snap.",
        impact="The worst case. Random, 100 layouts: A* known map 34 % reached, 7 % collision. freest_beam 42 %, 0 % collision. Fix: scan-to-map relocalization reached 100 % on random (close-area-relocalize).",
        src=["samples/close-area-safety-filter/README.md", A, "samples/close-area-relocalize/README.md"]),
    "bias": dict(
        what="The estimate drifts at 0.05 m/s for 10 s (0.5 m in total).",
        impact="Random, 100 layouts: A* known map 30 % reached, 4 % collision. freest_beam 40 %, 0 % collision. Not run per family.",
        src=["samples/close-area-safety-filter/README.md", A]),
    "dropout": dict(
        what="VIO frames stop for 2 s; the EKF runs on the IMU only.",
        impact="Random, 100 layouts: A* known map 63 % reached, 1 % collision. freest_beam 46 %, 0 % collision.",
        src=["samples/close-area-safety-filter/README.md", A]),
}

FILTER_DOCS = {
    "none": dict(what="The planner's velocity goes straight to the vehicle.", impact="Baseline."),
    "F2": dict(
        what="PX4-CBF as shipped: a control barrier function on the raw range points that bends the velocity away from close returns. It keeps the drone centre about 0.7 m from every return, which closes passages narrower than about 1.4 m.",
        impact="Walking people (random, 50 layouts, A* replan): collisions 14 % / 36 % => 0 % at 0.5 / 1.0 m/s, at the price of 16 % stuck. Against obstacles the scan sees: 0 collisions in all 500 fault runs. It cannot help with glass or anything the sensor misses.",
        src=["samples/close-area-moving-obstacles/README.md", "samples/close-area-safety-filter/README.md", B]),
}


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def med(xs, nd):
    return round(statistics.median(xs), nd) if xs else None


def cell(runs, limit):
    n = len(runs)
    times = [r["time_to_goal_s"] for r in runs if r["reached"]]
    mats = {}
    for r in runs:
        if r["collision"] and r.get("hit_material"):
            mats[r["hit_material"]] = mats.get(r["hit_material"], 0) + 1
    out = {
        "n": n, "seed": sorted({r["seed"] for r in runs}),
        "reached": pct(sum(r["reached"] for r in runs), n),
        "collision": pct(sum(r["collision"] for r in runs), n),
        "stuck": pct(sum(r["stuck"] for r in runs), n),
        "timeout": pct(sum(r["timeout"] for r in runs), n),
        "median_time_s": med(times, 2),
        "median_clearance_m": med([r["min_clearance_m"] for r in runs], 3),
        "collisions_by_material": mats,
        "max_time_s": runs[0]["max_time_s"],
    }
    if limit < runs[0]["max_time_s"]:      # what a shorter playground limit would have scored as reached
        out["reached_within_60s"] = pct(sum(1 for t in times if t <= limit), n)
    return out


def crange(xs):
    lo, hi = min(xs), max(xs)
    return f"{lo:.0f} % everywhere" if lo == hi else f"{lo:.0f}-{hi:.0f} %"


def rank_key(c):
    return (-c["reached"], c["collision"], c["median_time_s"] if c["median_time_s"] is not None else 1e9)


def pick(cells, names):
    ordered = sorted(names, key=lambda p: (rank_key(cells[p]), p))
    w = ordered[0]
    ties = [p for p in ordered[1:] if cells[p]["reached"] == cells[w]["reached"] and cells[p]["collision"] == cells[w]["collision"]]
    return w, ties, ordered


def fmt_t(c):
    return f"{c['median_time_s']:.0f} s median" if c["median_time_s"] is not None else "no run reached B"


def reason(name, c, n_cand, group, fam, preset):
    return (f"{c['reached']:.0f} % reached, {c['collision']:.0f} % collision, {fmt_t(c)}: best of {n_cand} "
            f"{group} planners on {fam} with the {preset} sensor ({c['n']} layouts, seed 0, synthetic).")


def parse_reloc(path):
    """(a) estimator-only rows of reloc_matrix_refs.md => {family: {fault: {reached, collision, stuck, n}}}."""
    out = {}
    for line in path.read_text().splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 10 or cols[2] != "(a) estimator":
            continue
        fam, fault = cols[0], cols[1]
        out.setdefault(fam, {})[fault] = {"n": int(cols[3]), "reached": float(cols[4]),
                                          "collision": float(cols[7]), "stuck": float(cols[8])}
    return out


def main():
    m = json.loads(BENCH.read_text())
    prior = json.loads(PRIOR.read_text())
    reloc = parse_reloc(RELOC)
    fams, presets, planners = m["families"], list(m["presets"]), list(m["planners"])
    groups = {}
    for r in m["runs"]:
        groups.setdefault((r["family"], r["preset"], r["planner"]), []).append(r)

    cells, bad = {}, []
    for f in fams:
        for s in presets:
            for p in planners:
                c = cell(groups[(f, s, p)], PLAYGROUND_LONG.get(f, PLAYGROUND_LIMIT_S))
                ref = m["summary"][s][p][f]
                for k, rk in (("reached", "reached_pct"), ("collision", "collision_pct"), ("stuck", "stuck_pct"),
                              ("timeout", "timeout_pct"), ("median_time_s", "median_time_to_goal_s"),
                              ("median_clearance_m", "median_min_clearance_m")):
                    if c[k] != ref[rk]:
                        bad.append(f"{f}/{s}/{p} {k}: runs {c[k]} vs summary {ref[rk]}")
                if c["n"] != ref["n"]:
                    bad.append(f"{f}/{s}/{p} n")
                cells.setdefault(f, {}).setdefault(s, {})[p] = c
    if bad:
        print("mismatch with matrix_0.json summary:\n  " + "\n  ".join(bad[:20]), file=sys.stderr)
        sys.exit(1)

    rec = {}
    for f in fams:
        for s in presets:
            cs = cells[f][s]
            pm = [p for p in planners if p in PRIOR_MAP]
            nm = [p for p in planners if p not in PRIOR_MAP]
            wp, tp, _ = pick(cs, pm)
            wn, tn, on = pick(cs, nm)
            r = {
                "prior_map": {"winner": wp, "ties": tp, "reason": reason(wp, cs[wp], len(pm), "prior-map", f, s)},
                "no_map": {"winner": wn, "ties": tn, "reason": reason(wn, cs[wn], len(nm), "map-free", f, s)},
                "ranked": sorted(planners, key=lambda p: (rank_key(cs[p]), p)),
            }
            c = cs[wn]
            if c["reached"] < 50 or c["collision"] >= 20:
                safe = sorted(nm, key=lambda p: (cs[p]["collision"], -cs[p]["reached"], p))[0]
                r["no_map"]["weak"] = (f"Weak pick: no map-free planner reaches 50 % with under 20 % collisions here. "
                                       f"Safest map-free option: {m['planners'][safe]['label']} ({cs[safe]['reached']:.0f} % reached, "
                                       f"{cs[safe]['collision']:.0f} % collision).")
                r["no_map"]["safest"] = safe
            rec.setdefault(f, {})[s] = r

    # per-planner matrix lines: where it wins and where it loses
    pdocs = {}
    for p in planners:
        d = dict(PLANNER_DOCS[p])
        lines = []
        for s in presets:
            good = [f for f in fams if cells[f][s][p]["reached"] >= 90 and cells[f][s][p]["collision"] == 0]
            badf = [f for f in fams if cells[f][s][p]["reached"] <= 20 or cells[f][s][p]["collision"] >= 20]
            wins = [f for f in fams if p == rec[f][s]["prior_map" if p in PRIOR_MAP else "no_map"]["winner"]
                    or p in rec[f][s]["prior_map" if p in PRIOR_MAP else "no_map"]["ties"]]
            col = [cells[f][s][p]["collision"] for f in fams]
            lines.append(f"{s}: >= 90 % reached with 0 % collision on {', '.join(good) or 'no family'}; "
                         f"<= 20 % reached or >= 20 % collision on {', '.join(badf) or 'no family'}; "
                         f"collision {crange(col)}. Top of its group on {', '.join(wins) or 'no family'}.")
        d["matrix"] = lines
        d["needs_prior_map"] = p in PRIOR_MAP
        d["src"] = d.get("src", [B])
        pdocs[p] = d

    # sensor impact per family: best map-free reach and collisions, ideal vs crazyflie
    sdocs = {k: dict(v) for k, v in PRESET_DOCS.items()}
    for s in presets:
        byf = {}
        for f in fams:
            w = rec[f][s]["no_map"]["winner"]
            nm = [p for p in planners if p not in PRIOR_MAP and p != "straight"]
            ok = sum(1 for p in nm if cells[f][s][p]["reached"] >= 80 and cells[f][s][p]["collision"] < 10)
            byf[f] = (f"Best map-free planner {w}: {cells[f][s][w]['reached']:.0f} % reached, "
                      f"{cells[f][s][w]['collision']:.0f} % collision. {ok} of {len(nm)} map-free planners reach "
                      f">= 80 % with < 10 % collision (straight excluded).")
        sdocs[s]["by_family"] = byf
        sdocs[s]["src"] = [B]

    # F2 impact per family from the benchmark pair astar_unknown vs astar_unknown_f2
    fdocs = {k: dict(v) for k, v in FILTER_DOCS.items()}
    byf = {}
    for f in fams:
        parts = []
        for s in presets:
            a, b = cells[f][s]["astar_unknown"], cells[f][s]["astar_unknown_f2"]
            g = b["collisions_by_material"].get("glass", 0)
            parts.append(f"{s}: reached {a['reached']:.0f} => {b['reached']:.0f} %, collision {a['collision']:.0f} => "
                         f"{b['collision']:.0f} %" + (f" ({g} of the F2 collisions on glass)" if g else ""))
        byf[f] = "A* unknown map without => with F2. " + "; ".join(parts) + "."
    fdocs["F2"]["by_family"] = byf

    # VIO faults per family for A* known map (relocalize held-out refs, seeds 2-4)
    vdocs = {k: dict(v) for k, v in FAULT_DOCS.items()}
    for fault in ("dropout", "jump"):
        byf = {}
        for f, rows in reloc.items():
            if fault in rows:
                x = rows[fault]
                byf[f] = (f"A* known map: {x['reached']:.0f} % reached, {x['collision']:.0f} % collision, "
                          f"{x['stuck']:.0f} % stuck ({x['n']} runs, seeds 2-4; 100 % with true pose).")
        vdocs[fault]["by_family"] = byf
        vdocs[fault]["src"] = vdocs[fault]["src"] + ["samples/close-area-relocalize/results/reloc_matrix_refs.md"]

    shipped = {f: {"shipped_prior": prior["summary"]["ideal"]["astar_unknown_prior"][f]["reached_pct"],
                   "benchmark_geofence": prior["summary"]["ideal"]["astar_unknown"][f]["reached_pct"]}
               for f in ("office", "warehouse", "glass_office")}

    pl = {}
    for p in planners:
        pg = BENCH_TO_PG.get(p, {"planner": p, "filter": "none"})
        pl[p] = {"label": m["planners"][p]["label"], "sample": m["planners"][p]["sample"],
                 "needs_prior_map": p in PRIOR_MAP, "playground": pg, "in_playground_now": pg["planner"] in PG_NOW}

    doc = {
        "schema": "navidx-advisor/1",
        "input": "synthetic",
        "built_by": "python3 site/playground/data/build_advisor.py",
        "sources": {"matrix": str(BENCH.relative_to(ROOT)), "prior_check": str(PRIOR.relative_to(ROOT)),
                    "reloc_refs": str(RELOC.relative_to(ROOT))},
        "bench": {"command": m["command"], "layouts": m["layouts"], "seed": m["seed"], "max_time_s": m["max_time_s"],
                  "date": m["additions"][-1].get("date") if m.get("additions") else None,
                  "pose": "true pose (no VIO, no faults)", "filter_rows": ["astar_unknown_f2"]},
        "rule": "Highest reached %, then lowest collision %, then lowest median time to B. Ranked separately for "
                "planners that need a prior map and planners that do not.",
        "families": fams, "family_labels": FAMILY_LABEL, "presets": presets,
        "planners": pl,
        "playground_to_bench": PG_TO_BENCH,
        "not_in_benchmark": {"presets": ["crazyflie_bright"], "nearest_preset": {"crazyflie_bright": "crazyflie"},
                             "faults": ["none", "jump", "bias", "dropout"], "filters": "F2 only on astar_unknown"},
        "playground_differences": {
            "time_limit_s": PLAYGROUND_LIMIT_S, "time_limit_long_s": PLAYGROUND_LONG,
            "time_limit": "The playground uses the benchmark's run time limit: 120 s on maze and warehouse, 60 s on "
                          "the other families and on custom worlds.",
            "astar_unknown_map_corner": "The playground runs the shipped unknown-map A*; its map starts 2.5 m behind A. "
                                        "The benchmark moved the map corner to the area corner. Ideal sensor, 20 layouts: "
                                        "reached % shipped vs benchmark.",
            "astar_unknown_shipped_vs_bench": shipped,
            "one_layout": "Playground presets are layout 0 of each family. The benchmark is 20 layouts.",
        },
        "cells": cells,
        "recommend": rec,
        "docs": {"planner": pdocs, "preset": sdocs, "fault": vdocs, "filter": fdocs},
    }
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=True) + "\n")
    n_cells = sum(len(cells[f][s]) for f in fams for s in presets)
    print(f"wrote {OUT.relative_to(ROOT)}: {n_cells} cells, {len(fams) * len(presets)} recommendations, "
          f"{OUT.stat().st_size} bytes; stats match matrix_0.json summary for all cells")


if __name__ == "__main__":
    main()
