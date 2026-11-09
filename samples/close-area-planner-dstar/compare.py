"""D* Lite vs A* from scratch in close-area-arena's unknown-map mode. Synthetic inputs only.

.venv/bin/python compare.py run --layouts 50 --seed 0      # outcomes + planning time, 3 families
.venv/bin/python compare.py verify --layouts 5 --seed 0    # path cost D* Lite vs A* at every replan
.venv/bin/python compare.py scale --tiles 1,2,4,8 --replans 25   # search time vs map side (tiled maps)
.venv/bin/python compare.py fuzz --trials 300 [--strict]  # random grids, D* Lite vs A* path cost

Writes results/compare_<seed>.{json,md}, results/correctness_<seed>.{json,md}, results/scaling.{json,md}, results/fuzz[_strict].{json,md}.
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
from scipy.ndimage import distance_transform_edt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arena  # noqa: E402
import dstar_lite as D  # noqa: E402

A = arena.astar_esdf
RESULTS = os.path.join(HERE, "results")
FAMILIES = ("random", "u_trap", "narrow_gap")


def env():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system(), "processor": platform.processor()}


def pct(xs, q):
    return round(float(np.percentile(xs, q)), 2) if len(xs) else None


def fly(backend, fam, layouts, seed, verify=False):
    made = []

    def factory():
        p = D.make(backend=backend, verify=verify)
        made.append(p)
        return p

    t0 = time.perf_counter()
    rows, summ, _ = arena.run.evaluate(factory, fam, layouts, seed)
    return rows, summ, made, time.perf_counter() - t0


def cmd_run(a):
    out = {"input": "synthetic", "seed": a.seed, "layouts": a.layouts, "env": env(),
           "command": "python compare.py " + " ".join(sys.argv[1:]), "families": {}}
    for fam in a.families.split(","):
        fo = out["families"][fam] = {}
        for backend in ("astar", "dstar"):
            rows, summ, made, wall = fly(backend, fam, a.layouts, a.seed)
            tot = [x for p in made for x in p.replan_ms]
            se = [x for p in made for x in p.search_ms]
            la = [x for p in made for x in p.layers_ms]
            per_run = [sum(p.replan_ms) / 1e3 for p in made]
            per_run_search = [sum(p.search_ms) / 1e3 for p in made]
            for r, p in zip(rows, made):
                r.update({"replans": len(p.replan_ms), "plan_total_s": round(sum(p.replan_ms) / 1e3, 3),
                          "search_total_s": round(sum(p.search_ms) / 1e3, 3),
                          "fallback_replans": p.fallbacks, "no_path_replans": p.no_path})
            m = {"summary": summ, "wall_s": round(wall, 1), "replans": len(tot),
                 "plan_ms": {"median": pct(tot, 50), "p95": pct(tot, 95), "max": pct(tot, 100)},
                 "search_ms": {"median": pct(se, 50), "p95": pct(se, 95), "max": pct(se, 100)},
                 "layers_ms": {"median": pct(la, 50), "p95": pct(la, 95)},
                 "plan_total_per_run_s": {"median": pct(per_run, 50), "max": pct(per_run, 100)},
                 "search_total_per_run_s": {"median": pct(per_run_search, 50), "max": pct(per_run_search, 100)},
                 "fallback_replans": sum(p.fallbacks for p in made),
                 "no_path_replans": sum(p.no_path for p in made), "runs": rows}
            if backend == "dstar":
                first = [p.dstats[0][2] for p in made if p.dstats]
                inc = [s for p in made for s in p.dstats[1:]]
                m["dstar"] = {"first_search_pops_median": pct(first, 50),
                              "incremental_changed_cells_median": pct([s[0] for s in inc], 50),
                              "incremental_updated_vertices_median": pct([s[1] for s in inc], 50),
                              "incremental_pops_median": pct([s[2] for s in inc], 50),
                              "incremental_pops_p95": pct([s[2] for s in inc], 95)}
            fo[backend] = m
            print(fam, backend, summ, m["plan_ms"], m["search_ms"], f"wall {wall:.1f}", flush=True)
        ra, rd = fo["astar"]["runs"], fo["dstar"]["runs"]
        fo["same_outcome_runs"] = sum(x["outcome"] == y["outcome"] for x, y in zip(ra, rd))
        ref = os.path.join(arena.ARENA, "results", f"astar_esdf_{fam}_{a.seed}.json")
        if os.path.exists(ref):
            with open(ref) as fh:
                old = json.load(fh)["modes"]["astar_esdf unknown_map"]["runs"]
            n = min(len(old), len(ra))
            fo["astar_backend_matches_arena_results"] = {
                "file": os.path.relpath(ref, HERE), "runs_compared": n,
                "identical": sum(old[i]["outcome"] == ra[i]["outcome"] and old[i]["time_to_goal_s"] == ra[i]["time_to_goal_s"]
                                 and old[i]["path_length_m"] == ra[i]["path_length_m"] for i in range(n))}
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, f"compare_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump(out, fh, indent=1)
    f = lambda v: "-" if v is None else f"{v}"
    L = [f"`{out['command']}` (synthetic: simulated layouts, vehicle and sensor; {env()['machine']}, "
         f"CPython {env()['python']}, numpy {np.__version__}, scipy {scipy.__version__})", "",
         "Planning time = whole replan (ESDF + cost arrays + search + shortcut). Search = the search call only.", "",
         "| family | search | reached % | collision % | stuck % | timeout % | median time to goal s | replans "
         "| plan ms median | plan ms p95 | search ms median | search ms p95 | plan s per run median | plan s per run max | wall s |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for fam, fo in out["families"].items():
        for b in ("astar", "dstar"):
            m, s = fo[b], fo[b]["summary"]
            L.append(f"| {fam} | {'A* from scratch' if b == 'astar' else 'D* Lite'} | {f(s['reached_pct'])} | "
                     f"{f(s['collision_pct'])} | {f(s['stuck_pct'])} | {f(s['timeout_pct'])} | "
                     f"{f(s['median_time_to_goal_s'])} | {m['replans']} | {m['plan_ms']['median']} | {m['plan_ms']['p95']} | "
                     f"{m['search_ms']['median']} | {m['search_ms']['p95']} | {m['plan_total_per_run_s']['median']} | "
                     f"{m['plan_total_per_run_s']['max']} | {m['wall_s']} |")
    L += ["", "| family | same outcome A* vs D* (runs) | A* backend identical to arena results (runs) "
          "| D* first search pops median | D* incremental: changed cells / updated vertices / pops median | pops p95 |",
          "|---|---|---|---|---|---|"]
    for fam, fo in out["families"].items():
        d, mt = fo["dstar"]["dstar"], fo.get("astar_backend_matches_arena_results")
        L.append(f"| {fam} | {fo['same_outcome_runs']} / {a.layouts} | "
                 f"{'-' if not mt else str(mt['identical']) + ' / ' + str(mt['runs_compared'])} | "
                 f"{d['first_search_pops_median']} | {d['incremental_changed_cells_median']} / "
                 f"{d['incremental_updated_vertices_median']} / {d['incremental_pops_median']} | {d['incremental_pops_p95']} |")
    L += ["", "Per run (outcome A* / D*):", "", "| run | " + " | ".join(out["families"]) + " |",
          "|---|" + "---|" * len(out["families"])]
    for i in range(a.layouts):
        L.append(f"| {i} | " + " | ".join(f"{fo['astar']['runs'][i]['outcome']} / {fo['dstar']['runs'][i]['outcome']}"
                                          for fo in out["families"].values()) + " |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {stem}.json, {stem}.md")
    return 0


def cmd_verify(a):
    out = {"input": "synthetic", "seed": a.seed, "layouts": a.layouts, "env": env(),
           "command": "python compare.py " + " ".join(sys.argv[1:]), "families": {}}
    for fam in FAMILIES:
        rows, _, made, wall = fly("dstar", fam, a.layouts, a.seed, verify=True)
        ch = [c for p in made for c in p.checks]
        both = [c for c in ch if c["dstar_cost"] is not None and c["astar_cost"] is not None]
        rel = [(c["astar_cost"] - c["dstar_cost"]) / c["dstar_cost"] for c in both]
        gerr = [abs(c["dstar_g"] - c["dstar_cost"]) for c in both if c["dstar_g"] is not None]
        out["families"][fam] = {
            "searches": len(ch), "both_found": len(both),
            "none_mismatch": sum(c["dstar_none"] != c["astar_none"] for c in ch),
            "dstar_invalid_path": sum((not c["dstar_none"]) and c["dstar_cost"] is None for c in ch),
            "dstar_costlier_than_astar": sum(r < -1e-9 for r in rel),
            "astar_minus_dstar_rel_max": max(rel) if rel else None,
            "astar_minus_dstar_rel_median": float(np.median(rel)) if rel else None,
            "dstar_g_vs_path_cost_abs_max": max(gerr) if gerr else None,
            "outcomes": [r["outcome"] for r in rows], "wall_s": round(wall, 1)}
        print(fam, out["families"][fam], flush=True)
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, f"correctness_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump(out, fh, indent=1)
    L = [f"`{out['command']}` (synthetic). At every replan of each D* Lite flight, A* from scratch ran on the same "
         "frozen blocked / cost arrays and the same start cell. Cost = sum of step length x cost of the entered cell.", "",
         "| family | searches | both found a path | found / not found mismatch | invalid D* path | D* costlier than A* "
         "| (A* - D*) / D* max | median | abs(g(start) - D* path cost) max |", "|---|---|---|---|---|---|---|---|---|"]
    for fam, r in out["families"].items():
        e = lambda v: "-" if v is None else f"{v:.2e}"
        L.append(f"| {fam} | {r['searches']} | {r['both_found']} | {r['none_mismatch']} | {r['dstar_invalid_path']} | "
                 f"{r['dstar_costlier_than_astar']} | {e(r['astar_minus_dstar_rel_max'])} | "
                 f"{e(r['astar_minus_dstar_rel_median'])} | {e(r['dstar_g_vs_path_cost_abs_max'])} |")
    L += ["", "A* pushes f = g + 1.0001 h (tie-break in astar_esdf.astar), so it may return a path up to 0.01 % "
          "costlier than optimal; D* Lite uses the plain octile h. A positive (A* - D*) gap below 1e-4 is that tie-break."]
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {stem}.json, {stem}.md")
    return 0


def cmd_scale(a):
    """Tile k x k arena 'random' obstacle grids (seed 0, layouts 0..k*k-1) into a 20k x 20k m map. A point
    vehicle moves 0.6 m (1.5 m/s x 0.4 s) along its current path per replan; cells within 6 m become known
    (no occlusion). Per replan: ESDF + cost (shared), A* from scratch, D* Lite incremental, same arrays."""
    res = A.MAP_RES
    out = {"input": "synthetic", "env": env(), "command": "python compare.py " + " ".join(sys.argv[1:]),
           "replans": a.replans, "sizes": []}
    for k in [int(v) for v in a.tiles.split(",")]:
        tiles = [arena.world.make_world("random", 0, i) for i in range(k * k)]
        t = tiles[0].grid.occ.shape[0]
        occ = np.zeros((k * t, k * t), bool)
        for i, w in enumerate(tiles):
            bx, by = divmod(i, k)
            occ[bx * t:(bx + 1) * t, by * t:(by + 1) * t] = w.grid.occ
        n = occ.shape[0]
        a0 = tiles[0].grid.to_index(0.0, 0.0)
        wl = tiles[-1]
        gl = wl.grid.to_index(wl.goal[0], wl.goal[1])
        goal = ((k - 1) * t + gl[0], (k - 1) * t + gl[1])
        pos = np.array([a0[0] + 0.5, a0[1] + 0.5]) * res
        known = np.zeros_like(occ)
        X, Y = np.meshgrid((np.arange(n) + 0.5) * res, (np.arange(n) + 0.5) * res, indexing="ij")
        ds = None
        rows = []
        for r in range(a.replans):
            t0 = time.perf_counter()
            known |= (X - pos[0]) ** 2 + (Y - pos[1]) ** 2 <= 36.0
            occk = occ & known
            esdf = (distance_transform_edt(~np.pad(occk, 1, constant_values=True)) * res)[1:-1, 1:-1]
            cost = 1.0 + A.CLEARANCE_WEIGHT * np.clip(1.0 - esdf / A.CLEARANCE_SOFT_M, 0.0, None) + A.UNKNOWN_PENALTY * ~known
            blocked = esdf <= A.RADIUS + A.TRACK_MARGIN + 1e-9
            s = (int(pos[0] / res), int(pos[1] / res))
            if blocked[s]:
                free = np.argwhere(~blocked)
                s = tuple(int(v) for v in free[int(np.argmin(np.hypot(free[:, 0] - s[0], free[:, 1] - s[1])))])
            t1 = time.perf_counter()
            pa = A.astar(blocked, cost, s, goal)
            t2 = time.perf_counter()
            if ds is None:
                ds = D.DStarLite(blocked.shape, goal)
            pd = ds.plan(blocked, cost, s)
            t3 = time.perf_counter()
            ca, cd = D.path_cost(pa, cost, blocked), D.path_cost(pd, cost, blocked)
            rows.append({"replan": r, "layers_ms": round((t1 - t0) * 1e3, 2), "astar_ms": round((t2 - t1) * 1e3, 2),
                         "dstar_ms": round((t3 - t2) * 1e3, 2), "dstar_pops": ds.pops, "dstar_updated": ds.updated,
                         "astar_cost": ca, "dstar_cost": cd})
            print(k, rows[-1], flush=True)
            if pd is None or len(pd) < 2:
                break
            # advance 0.6 m along the D* path (cell centres)
            P = (np.array(pd, float) + 0.5) * res
            seg = np.hypot(*np.diff(P, axis=0).T)
            cum = np.concatenate([[0.0], np.cumsum(seg)])
            j = int(np.searchsorted(cum, 0.6))
            pos = P[min(j, len(P) - 1)]
        inc = rows[1:]
        rel = [abs(x["astar_cost"] - x["dstar_cost"]) / x["dstar_cost"] for x in rows if x["astar_cost"] and x["dstar_cost"]]
        out["sizes"].append({
            "tiles": k, "side_m": round(n * res, 1), "cells": int(n * n), "replans_run": len(rows),
            "layers_ms_median": pct([x["layers_ms"] for x in rows], 50),
            "astar_ms_median": pct([x["astar_ms"] for x in rows], 50), "astar_ms_p95": pct([x["astar_ms"] for x in rows], 95),
            "dstar_first_ms": rows[0]["dstar_ms"],
            "dstar_inc_ms_median": pct([x["dstar_ms"] for x in inc], 50), "dstar_inc_ms_p95": pct([x["dstar_ms"] for x in inc], 95),
            "cost_rel_diff_max": max(rel) if rel else None, "rows": rows})
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, "scaling")
    with open(stem + ".json", "w") as fh:
        json.dump(out, fh, indent=1)
    L = [f"`{out['command']}` (synthetic: tiled arena 'random' layouts, idealised 6 m disc reveal without occlusion, "
         f"point vehicle moved 0.6 m per replan; {env()['machine']}, CPython {env()['python']})", "",
         "| map side m | cells | replans | ESDF + cost ms median | A* ms median | A* ms p95 | D* first search ms "
         "| D* incremental ms median | D* incremental ms p95 | max rel cost diff |", "|---|---|---|---|---|---|---|---|---|---|"]
    for z in out["sizes"]:
        cd = "-" if z["cost_rel_diff_max"] is None else f"{z['cost_rel_diff_max']:.1e}"
        L.append(f"| {z['side_m']} | {z['cells']} | {z['replans_run']} | {z['layers_ms_median']} | {z['astar_ms_median']} | "
                 f"{z['astar_ms_p95']} | {z['dstar_first_ms']} | {z['dstar_inc_ms_median']} | {z['dstar_inc_ms_p95']} | {cd} |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {stem}.json, {stem}.md")
    return 0


def fuzz_trial(seed, move, blockch, costch, n=20, iters=30):
    """Random n x n grid; per iteration flip 3 % of cells blocked, redraw 5 % of costs (1-3), move the
    start. D* Lite (kept across iterations) vs A* from scratch. Returns the first failing iteration or None."""
    rng = np.random.default_rng(seed)
    blk = rng.random((n, n)) < 0.2
    blk[0, :] = blk[-1, :] = blk[:, 0] = blk[:, -1] = True
    cost = 1.0 + rng.integers(0, 3, (n, n)).astype(float)
    s, g = (2, 2), (n - 3, n - 3)
    blk[s] = blk[g] = False
    d = D.DStarLite((n, n), g)
    for it in range(iters):
        if it:
            if blockch:
                blk = blk ^ (rng.random((n, n)) < 0.03)
                blk[0, :] = blk[-1, :] = blk[:, 0] = blk[:, -1] = True
                blk[g] = False
            if costch:
                cost = np.where(rng.random((n, n)) < 0.05, 1 + rng.integers(0, 3, (n, n)), cost).astype(float)
            if move:
                s = (int(rng.integers(1, n - 1)), int(rng.integers(1, n - 1)))
            blk[s] = False
        ca = D.path_cost(A.astar(blk, cost, s, g), cost, blk)
        cd = D.path_cost(d.plan(blk.copy(), cost.copy(), s), cost, blk)
        if (ca is None) != (cd is None) or (ca is not None and abs(ca - cd) > 1e-6 * ca):
            return it
    return None


def cmd_fuzz(a):
    D.KEY_EPS = None if a.strict else 1e-9
    tag = "_strict" if a.strict else ""
    cases = [(m, b, c) for m in (0, 1) for b in (0, 1) for c in (0, 1) if b or c]
    L = [f"`python compare.py {' '.join(sys.argv[1:])}` ({'strict textbook key test' if a.strict else 'KEY_EPS 1e-9 tie tolerance'}; synthetic random 20 x 20 grids, 30 incremental plans per "
         "trial, path cost D* Lite vs A* from scratch, tolerance 1e-6 relative)", "",
         "| start moves | cells flip blocked | costs change | trials | failing trials |", "|---|---|---|---|---|"]
    res = []
    for m, b, c in cases:
        fails = [sd for sd in range(a.trials) if fuzz_trial(sd, m, b, c) is not None]
        res.append({"move": m, "block_changes": b, "cost_changes": c, "trials": a.trials, "failing": fails})
        L.append(f"| {bool(m)} | {bool(b)} | {bool(c)} | {a.trials} | {len(fails)} |")
        print(res[-1], flush=True)
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, f"fuzz{tag}.json"), "w") as fh:
        json.dump({"input": "synthetic", "key_eps": D.KEY_EPS, "env": env(), "cases": res}, fh, indent=1)
    with open(os.path.join(RESULTS, f"fuzz{tag}.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--layouts", type=int, default=50)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--families", default=",".join(FAMILIES))
    v = sub.add_parser("verify")
    v.add_argument("--layouts", type=int, default=5)
    v.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("scale")
    s.add_argument("--tiles", default="1,2,4")
    s.add_argument("--replans", type=int, default=25)
    z = sub.add_parser("fuzz")
    z.add_argument("--trials", type=int, default=300)
    z.add_argument("--strict", action="store_true", help="strict (k1, k2) < key(start) test (shows the tie bug)")
    a = ap.parse_args(argv)
    return {"run": cmd_run, "verify": cmd_verify, "scale": cmd_scale, "fuzz": cmd_fuzz}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
