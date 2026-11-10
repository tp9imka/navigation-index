"""Theta* and Lazy Theta* against astar_esdf: arena flights (8 families, 2 presets) and plan-only timing.

.venv/bin/python bench.py flights --layouts 20 --seed 0 --workers 12   # results/flights_0.*
.venv/bin/python bench.py plans --layouts 20 --seed 0                  # results/plans_0.*, 1 process
.venv/bin/python bench.py check                                        # A* rows vs the benchmark matrix

flights: the flight loop, layouts (world_glass.make_any_world), presets, time limits and scorer
are close-area-benchmark's run_one, imported by path (nothing edited there). The Theta* rows are
added to its PLANNERS dict at import time, in this process and in every worker. astar_unknown is
the benchmark's own row (A* unknown map, log-odds map on the area geofence); the Theta* unknown
rows use the same geofence. Known-map rows run on preset ideal only (the prior map makes the
range sensor irrelevant to the plan). Replan ms are wall time under parallel load.
plans: one plan from A on the known map, per layout, single process: A* + shortcut vs Theta* vs
Lazy Theta*. Planning ms (whole _plan: cost arrays + search + shortcut; the ESDF is cached),
planned length, cost on one scale (thetastar.path_cost), and the exact clearance of the planned
polyline (world.sdf every 2 cm).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import thetastar  # noqa: E402

RESULTS = os.path.join(HERE, "results")
BENCH = os.path.normpath(os.path.join(HERE, "..", "close-area-benchmark", "bench.py"))


def _load_benchmark():
    if "cab_bench" not in sys.modules:
        spec = importlib.util.spec_from_file_location("cab_bench", BENCH)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["cab_bench"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["cab_bench"]


B = _load_benchmark()
LAST = []          # the planner object of the run in progress (one run at a time per process)


def _keep(p):
    LAST[:] = [p]
    return p


THETA_PLANNERS = {
    "thetastar_known": (lambda w: _keep(thetastar.make(known_map=True)), None, "Theta* known map",
                        "close-area-planner-thetastar"),
    "lazy_thetastar_known": (lambda w: _keep(thetastar.make(known_map=True, lazy=True)), None,
                             "Lazy Theta* known map", "close-area-planner-thetastar"),
    "thetastar_unknown": (lambda w: _keep(thetastar.make(known_map=False, bounds=B._bounds(w))), None,
                          "Theta* unknown map", "close-area-planner-thetastar"),
    "lazy_thetastar_unknown": (lambda w: _keep(thetastar.make(known_map=False, lazy=True, bounds=B._bounds(w))),
                               None, "Lazy Theta* unknown map", "close-area-planner-thetastar"),
}
B.PLANNERS.update(THETA_PLANNERS)
# the A* rows, wrapped so their planner object is kept too (same factories as the benchmark's)
_base_known, _base_unknown = B.PLANNERS["astar_known"], B.PLANNERS["astar_unknown"]
B.PLANNERS["astar_known"] = (lambda w: _keep(_base_known[0](w)),) + _base_known[1:]
B.PLANNERS["astar_unknown"] = (lambda w: _keep(_base_unknown[0](w)),) + _base_unknown[1:]

KNOWN = ("astar_known", "thetastar_known", "lazy_thetastar_known")
UNKNOWN = ("astar_unknown", "thetastar_unknown", "lazy_thetastar_unknown")
FAMILIES = B.FAMILIES
CRAZYFLIE_FAMILIES = ("random", "office")


def _task(args):
    LAST.clear()
    row = B.run_one(*args)
    p = LAST[0]
    row["replans"] = len(p.replan_ms)
    row["fallback_replans"] = p.fallbacks
    row["no_path_replans"] = p.no_path
    return row, [round(m, 3) for m in p.replan_ms]


def env():
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system(), "cpus": os.cpu_count(),
            "loadavg_at_start": [round(x, 1) for x in os.getloadavg()]}


def _pct(ms, q):
    return round(float(np.percentile(ms, q)), 2) if ms else None


def flights(a, cmd) -> int:
    fams = [f for f in FAMILIES if f in a.families.split(",")]
    plist = [p for p in KNOWN + UNKNOWN if p in a.planners.split(",")]
    tasks = [(p, f, "ideal", i, a.seed) for p in plist for f in fams for i in range(a.layouts)]
    if not a.no_crazyflie:
        tasks += [(p, f, "crazyflie", i, a.seed) for p in plist if p in UNKNOWN
                  for f in CRAZYFLIE_FAMILIES if f in fams for i in range(a.layouts)]
    tasks.sort(key=lambda t: (t[1] not in B.LONG_FAMILIES, "unknown" not in t[0]))   # long jobs first
    e = env()
    t0 = time.perf_counter()
    out = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for k, r in enumerate(ex.map(_task, tasks, chunksize=1)):
            out.append(r)
            if (k + 1) % 50 == 0:
                print(f"{k + 1}/{len(tasks)} runs, {time.perf_counter() - t0:.0f} s", flush=True)
    wall = round(time.perf_counter() - t0, 1)
    rows = [r for r, _ in out]
    ms_of = {(r["planner"], r["family"], r["preset"], r["index"]): ms for r, ms in out}
    cells = {}
    for pr in ("ideal", "crazyflie"):
        for p in KNOWN + UNKNOWN:
            for f in FAMILIES:
                sel = sorted((r for r in rows if (r["planner"], r["family"], r["preset"]) == (p, f, pr)),
                             key=lambda r: r["index"])
                if not sel:
                    continue
                ms = [m for r in sel for m in ms_of[(p, f, pr, r["index"])]]
                cells.setdefault(pr, {}).setdefault(p, {})[f] = {
                    "summary": B.scorer.summarize(sel),
                    "replans": len(ms), "replan_ms_median": _pct(ms, 50), "replan_ms_p95": _pct(ms, 95),
                    "replan_ms_max": round(max(ms), 2) if ms else None,
                    "fallback_replans": sum(r["fallback_replans"] for r in sel),
                    "no_path_replans": sum(r["no_path_replans"] for r in sel),
                    "wall_s_sum": round(sum(r["wall_s"] for r in sel), 1)}
    paired = _paired(rows)
    stem = os.path.join(a.out, a.stem or f"flights_{a.seed}")
    os.makedirs(a.out, exist_ok=True)
    meta = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "workers": a.workers,
            "wall_s": wall, "families": list(FAMILIES), "crazyflie_families": list(CRAZYFLIE_FAMILIES),
            "max_time_s": {f: B.max_time(f) for f in FAMILIES}, "env": e,
            "loadavg_at_end": [round(x, 1) for x in os.getloadavg()],
            "planner_constants": {k: v for k, v in vars(arena.astar_esdf).items()
                                  if k.isupper() and isinstance(v, (int, float))}}
    with open(stem + ".json", "w") as fh:
        json.dump({**meta, "cells": cells, "paired": paired, "runs": rows,
                   "replan_ms": {"|".join(map(str, k)): v for k, v in ms_of.items()}}, fh, indent=1)
    md = render_flights(meta, cells, paired, pooled(rows, ms_of))
    with open(stem + ".md", "w") as fh:
        fh.write(md + "\n")
    print(md)
    print(f"wall {wall} s; wrote {os.path.relpath(stem, HERE)}.json, .md")
    return 0


PAIRS = (("ideal", "astar_known", "thetastar_known"), ("ideal", "astar_known", "lazy_thetastar_known"),
         ("ideal", "astar_unknown", "thetastar_unknown"), ("ideal", "astar_unknown", "lazy_thetastar_unknown"),
         ("crazyflie", "astar_unknown", "thetastar_unknown"),
         ("crazyflie", "astar_unknown", "lazy_thetastar_unknown"))


def _paired(rows):
    """Per family: layouts both planners reached; median of per-layout ratios (other / A*)."""
    idx = {(r["preset"], r["planner"], r["family"], r["index"]): r for r in rows}
    out = []
    for pr, base, other in PAIRS:
        for f in FAMILIES:
            keys = sorted(i for (p_, pl, fa, i) in idx if (p_, pl, fa) == (pr, base, f))
            both = [(idx[(pr, base, f, i)], idx[(pr, other, f, i)]) for i in keys if (pr, other, f, i) in idx]
            if not both:
                continue
            ok = [(x, y) for x, y in both if x["reached"] and y["reached"]]
            same = sum(x["outcome"] == y["outcome"] for x, y in both)
            rt = [y["time_to_goal_s"] / x["time_to_goal_s"] for x, y in ok]
            rl = [y["path_length_m"] / x["path_length_m"] for x, y in ok]
            dc = [y["min_clearance_m"] - x["min_clearance_m"] for x, y in ok]
            out.append({"preset": pr, "base": base, "other": other, "family": f, "n": len(both),
                        "same_outcome": same, "both_reached": len(ok),
                        "time_ratio_median": round(float(np.median(rt)), 3) if rt else None,
                        "faster_runs": sum(v < 1 for v in rt),
                        "length_ratio_median": round(float(np.median(rl)), 3) if rl else None,
                        "shorter_runs": sum(v < 1 for v in rl),
                        "clearance_diff_median_m": round(float(np.median(dc)), 3) if dc else None})
    return out


def pooled(rows, ms_of):
    """Replan ms pooled over every family of a (preset, planner), and the share above 200 ms."""
    out = {}
    for r in rows:
        out.setdefault((r["preset"], r["planner"]), []).extend(ms_of[(r["planner"], r["family"], r["preset"], r["index"])])
    return [{"preset": pr, "planner": p, "replans": len(ms), "median": _pct(ms, 50), "p95": _pct(ms, 95),
             "max": round(max(ms), 2), "over_200_pct": round(100.0 * sum(m > 200 for m in ms) / len(ms), 1)}
            for (pr, p), ms in out.items() if ms]


def render(stem) -> None:
    """Rebuild STEM.md from STEM.json."""
    d = json.load(open(stem + ".json"))
    ms_of = {tuple(k.split("|")[:2] + [k.split("|")[2], int(k.split("|")[3])]): v for k, v in d["replan_ms"].items()}
    with open(stem + ".md", "w") as fh:
        fh.write(render_flights(d, d["cells"], d["paired"], pooled(d["runs"], ms_of)) + "\n")


def render_flights(meta, cells, paired, pool) -> str:
    f_ = lambda v: "-" if v is None else f"{v:g}"   # noqa: E731
    L = [f"`{meta['command']}` from samples/close-area-planner-thetastar. Input: synthetic (simulated layouts, "
         f"vehicle and sensors), scored on truth. Seed {meta['seed']}, {meta['layouts']} layouts per cell, "
         f"{meta['workers']} worker processes, wall {meta['wall_s']} s. Flight loop, layouts, presets and time "
         f"limits are close-area-benchmark's run_one (limits s: "
         + ", ".join(f"{k} {v:g}" for k, v in meta["max_time_s"].items()) + "). "
         f"Machine load average at start {meta['env']['loadavg_at_start']}, at end {meta['loadavg_at_end']} "
         "(shared machine): replan ms are wall time under that load.", "",
         "| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to B s "
         "| median path m | median min clearance m | replans | replan ms median | replan ms p95 | replan ms max "
         "| fallback replans | no-path replans |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for pr, by_p in cells.items():
        for p, by_f in by_p.items():
            for fam, c in by_f.items():
                s = c["summary"]
                L.append(f"| {pr} | {p} | {fam} | {f_(s['reached_pct'])} | {f_(s['collision_pct'])} | "
                         f"{f_(s['stuck_pct'])} | {f_(s['timeout_pct'])} | {f_(s['median_time_to_goal_s'])} | "
                         f"{f_(s['median_path_length_m'])} | {f_(s['median_min_clearance_m'])} | {c['replans']} | "
                         f"{f_(c['replan_ms_median'])} | {f_(c['replan_ms_p95'])} | {f_(c['replan_ms_max'])} | "
                         f"{c['fallback_replans']} | {c['no_path_replans']} |")
    L += ["", "Replan ms pooled over all families of the row (wall time, same load caveat):", "",
          "| preset | planner | replans | median ms | p95 ms | max ms | replans over 200 ms % |", "|---|---|---|---|---|---|---|"]
    L += [f"| {r['preset']} | {r['planner']} | {r['replans']} | {f_(r['median'])} | {f_(r['p95'])} | {f_(r['max'])} | "
          f"{f_(r['over_200_pct'])} |" for r in sorted(pool, key=lambda r: (r["preset"] != "ideal", r["planner"]))]
    L += ["", "Paired by layout (runs both planners reached): median of per-layout ratio other / A* for time to "
          "B and flown path length (< 1 = Theta* better), runs where the ratio is < 1, and median of the "
          "per-layout min clearance difference (other - A*).", "",
          "| preset | A* row | other | family | layouts | same outcome | both reached | time ratio median "
          "| faster runs | length ratio median | shorter runs | clearance diff median m |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in paired:
        L.append(f"| {r['preset']} | {r['base']} | {r['other']} | {r['family']} | {r['n']} | {r['same_outcome']} | "
                 f"{r['both_reached']} | {f_(r['time_ratio_median'])} | {r['faster_runs']} | "
                 f"{f_(r['length_ratio_median'])} | {r['shorter_runs']} | {f_(r['clearance_diff_median_m'])} |")
    return "\n".join(L)


# ---- plan-only comparison ----

def _exact_clearance(w, xy, step=0.02):
    pts = [xy[0]]
    for p, q in zip(xy[:-1], xy[1:]):
        n = max(1, int(np.hypot(*(q - p)) / step))
        pts.extend(p + (q - p) * t for t in np.linspace(0, 1, n + 1)[1:])
    return float(np.min(w.sdf(np.array(pts))))


def plans(a, cmd) -> int:
    wg = B.world_glass
    Pose = arena.adapter.Pose
    makers = {"astar_shortcut": lambda: arena.astar_esdf.AStarESDF(known_map=True),
              "thetastar": lambda: thetastar.make(known_map=True),
              "lazy_thetastar": lambda: thetastar.make(known_map=True, lazy=True)}
    e = env()
    t_all = time.perf_counter()
    rows = []
    for f in FAMILIES:
        for i in range(a.layouts):
            w = wg.make_any_world(f, a.seed, i, radius=arena.run.DEFAULTS["vehicle"]["radius"])
            goal = (w.goal[0], w.goal[1], arena.run.DEFAULTS["z0"])
            pose = Pose(t=0.0, x=0.0, y=0.0, z=goal[2], vx=0.0, vy=0.0, vz=0.0, yaw=0.0)
            row = {"family": f, "index": i}
            for name, mk in makers.items():
                p = mk()
                p._layers(w.grid)                   # ESDF once, cached (as in flight after the first replan)
                ms = []
                for _ in range(a.repeats):
                    p._plan(pose, goal, w.grid)
                    ms.append(p.replan_ms[-1])
                xy = p.path_xy
                res = w.grid.res
                cells = [w.grid.to_index(x, y) for x, y in xy]
                _, esdf = p._layers(w.grid)
                cost = 1.0 + arena.astar_esdf.CLEARANCE_WEIGHT * np.clip(
                    1.0 - esdf / arena.astar_esdf.CLEARANCE_SOFT_M, 0.0, None)
                blocked = esdf <= arena.astar_esdf.RADIUS + 1e-9
                c = thetastar.path_cost(cells, cost, blocked) * res
                row[name] = {"ms_min": round(min(ms), 2), "ms_median": round(float(np.median(ms)), 2),
                             "vertices": len(xy), "length_m": round(float(np.hypot(*np.diff(xy, axis=0).T).sum()), 3),
                             "cost": round(c, 3), "exact_clearance_m": round(_exact_clearance(w, xy), 3),
                             "fallback": p.fallbacks > 0}
                if name != "astar_shortcut":
                    st = p.search_stats[-1]
                    row[name].update(expansions=st.get("expansions"), lines=st.get("lines"))
            rows.append(row)
            print(f, i, {k: (v["ms_median"], v["length_m"], v["cost"]) for k, v in row.items()
                         if isinstance(v, dict)}, flush=True)
    wall = round(time.perf_counter() - t_all, 1)
    summ = {}
    for f in list(FAMILIES) + ["all"]:
        sel = [r for r in rows if f in ("all", r["family"])]
        s = {}
        for name in makers:
            ms = [r[name]["ms_median"] for r in sel]
            s[name] = {"ms_median": _pct(ms, 50), "ms_p95": _pct(ms, 95), "ms_max": round(max(ms), 2),
                       "length_median_m": round(float(np.median([r[name]["length_m"] for r in sel])), 2),
                       "cost_median": round(float(np.median([r[name]["cost"] for r in sel])), 2),
                       "clearance_median_m": round(float(np.median([r[name]["exact_clearance_m"] for r in sel])), 3),
                       "clearance_min_m": round(float(min(r[name]["exact_clearance_m"] for r in sel)), 3),
                       "fallbacks": sum(r[name]["fallback"] for r in sel)}
            if name != "astar_shortcut":
                lr = [r[name]["length_m"] / r["astar_shortcut"]["length_m"] for r in sel]
                cr = [r[name]["cost"] / r["astar_shortcut"]["cost"] for r in sel]
                tr = [r[name]["ms_median"] / r["astar_shortcut"]["ms_median"] for r in sel]
                s[name].update(length_ratio_median=round(float(np.median(lr)), 3),
                               shorter=sum(v < 1 - 1e-9 for v in lr),
                               cost_ratio_median=round(float(np.median(cr)), 3),
                               cheaper=sum(v < 1 - 1e-9 for v in cr),
                               ms_ratio_median=round(float(np.median(tr)), 2))
        summ[f] = s
    stem = os.path.join(a.out, f"plans_{a.seed}")
    os.makedirs(a.out, exist_ok=True)
    meta = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "repeats": a.repeats,
            "wall_s": wall, "env": e, "loadavg_at_end": [round(x, 1) for x in os.getloadavg()]}
    with open(stem + ".json", "w") as fh:
        json.dump({**meta, "summary": summ, "rows": rows}, fh, indent=1)
    md = render_plans(meta, summ)
    with open(stem + ".md", "w") as fh:
        fh.write(md + "\n")
    print(md)
    return 0


def render_plans(meta, summ) -> str:
    f_ = lambda v: "-" if v is None else f"{v:g}"   # noqa: E731
    L = [f"`{meta['command']}` from samples/close-area-planner-thetastar. Input: synthetic. One plan from A to B "
         f"on the known prior grid per layout, seed {meta['seed']}, {meta['layouts']} layouts per family, "
         f"{meta['repeats']} repeats per plan (ms = median of the repeats), single process, wall {meta['wall_s']} s. "
         f"Load average at start {meta['env']['loadavg_at_start']}, at end {meta['loadavg_at_end']} (shared machine). "
         "Plan ms = the planner's whole _plan (cost arrays, search, shortcut for A*), ESDF cached. Cost = "
         "thetastar.path_cost of the planned polyline in metres x cost (same scale for all three). Clearance = "
         "world.sdf every 2 cm along the planned polyline.", "",
         "| family | planner | plan ms median | plan ms p95 | plan ms max | ms ratio median | length median m | length ratio median "
         "| shorter | cost median | cost ratio median | cheaper | clearance median m | clearance min m | fallback plans |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for fam, s in summ.items():
        for name, v in s.items():
            L.append(f"| {fam} | {name} | {f_(v['ms_median'])} | {f_(v['ms_p95'])} | {f_(v['ms_max'])} | "
                     f"{f_(v.get('ms_ratio_median'))} | {f_(v['length_median_m'])} | {f_(v.get('length_ratio_median'))} | {v.get('shorter', '-')} | "
                     f"{f_(v['cost_median'])} | {f_(v.get('cost_ratio_median'))} | {v.get('cheaper', '-')} | "
                     f"{f_(v['clearance_median_m'])} | {f_(v['clearance_min_m'])} | {v['fallbacks']} |")
    L += ["", "Ratios are medians of per-layout ratios Theta* / A* + shortcut (ms ratio: same layout, same "
          "process, a few ms apart, so less sensitive to machine load than the absolute ms); shorter / "
          "cheaper = layouts where the ratio is < 1."]
    return "\n".join(L)


def check(a, cmd) -> int:
    """A* rows of results/flights_<seed>.json vs close-area-benchmark/results/matrix_<seed>.json, run by run."""
    keys = ("outcome", "min_clearance_m", "path_length_m", "time_to_goal_s")
    mine = json.load(open(os.path.join(a.out, f"flights_{a.seed}.json")))
    ref_path = os.path.join(os.path.dirname(BENCH), "results", f"matrix_{a.seed}.json")
    ref = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in json.load(open(ref_path))["runs"]}
    cnt: dict = {}
    for r in mine["runs"]:
        if not r["planner"].startswith("astar"):
            continue
        o = ref.get((r["planner"], r["family"], r["preset"], r["index"]))
        c = cnt.setdefault((r["planner"], r["preset"]), [0, 0])
        c[0] += int(o is not None and all(o[k] == r[k] for k in keys))
        c[1] += 1
    md = [f"`{cmd}`. Input: synthetic. A* rows of results/flights_{a.seed}.json against "
          f"close-area-benchmark/results/matrix_{a.seed}.json, run by run on {', '.join(keys)}.", "",
          "| planner | preset | runs identical |", "|---|---|---|"]
    md += [f"| {p} | {pr} | {c[0]}/{c[1]} |" for (p, pr), c in cnt.items()]
    with open(os.path.join(a.out, f"matrix_check_{a.seed}.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))
    return 0 if all(c[0] == c[1] for c in cnt.values()) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("flights", "plans", "check", "render"))
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 4))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--planners", default=",".join(KNOWN + UNKNOWN))
    ap.add_argument("--no-crazyflie", action="store_true")
    ap.add_argument("--stem", default=None, help="output stem in --out (default flights_<seed>)")
    a = ap.parse_args(argv)
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.mode == "render":
        render(os.path.join(a.out, a.stem or f"flights_{a.seed}"))
        return 0
    return {"flights": flights, "plans": plans, "check": check}[a.mode](a, cmd)


if __name__ == "__main__":
    raise SystemExit(main())
