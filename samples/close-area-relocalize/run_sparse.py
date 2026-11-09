"""Relocalization with a 4-beam sensor: existing arms vs the spin-stack variant (sparse.py).

.venv/bin/python run_sparse.py --layouts 100 --seed 0          # presets ideal and crazyflie, dropout and jump

The relocalizer's range sensor is the arena preset (samples/close-area-arena/presets.py):
  ideal      72 rays, 360 deg, 6 m (the arena default; same noise stream as experiment.py, so the
             existing arms reproduce the published rows)
  crazyflie  4 cones of 27 deg (front, left, back, right), 3 m, zranger noise, 5 % dropout
The planner (A* known map) does not read the scan, so only relocalization sees the preset.

Arms (A* known map behind a gate that hovers while pose quality is 0, scored on truth):
  single       (b) commit to the best match at once + innovation test (experiment.py)
  multi_sep    (e) RatioPersistence + separation move after 1 s (disambiguate.py, unchanged)
  multi_ig     (f) RatioPersistence + info-gain move after 1 s (disambiguate.py, unchanged)
  spin         (g) hover + yaw spin, match the stacked quarter-turn, RatioPersistence
  spin_single  (h) as (g), commit to the best match on the first full stack
  spin_ig      (i) as (g) + info-gain move 1 s after the stack is complete
(g)-(i) apply the cone correction (sparse.cone_opening) when the preset has cones; (g) and (i)
use the sparse rule (ratio 1.10). (e) / (f) run disambiguate.py unchanged, with the preset scan.
Writes results/sparse_<family>_<seed>.json / .md.

.venv/bin/python run_sparse.py --tune     # static seed-1 sweep that set INF_DROP and SPARSE_RATIO
Static, no flight: random free poses (clearance >= 0.3 m) in seed-1 random layouts, a perfect
hover with a quarter-turn spin (17 scans, 0.1 rad apart) of the crazyflie preset, the window
centred 0.5 m off truth (as tune.py). Counts how often the best hypothesis passes the rule and how
often a passing one is more than 0.5 m wrong. Writes results/sparse_tune_seed1.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

import arena  # noqa: F401  (loads close_area_arena)
import importlib
from arena import astar_esdf, estimator, run, world
import disambiguate as D
import experiment as X
import relocalize as R
import run_disambiguate as RD
import sparse as S

presets = importlib.import_module("close_area_arena.presets")

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("single", "multi_sep", "multi_ig", "spin", "spin_single", "spin_ig")
LABEL = {"single": "(b)", "multi_sep": "(e)", "multi_ig": "(f)", "spin": "(g)", "spin_single": "(h)",
         "spin_ig": "(i)"}
PRESETS = ("ideal", "crazyflie")
FAULTS = ("dropout", "jump")


def sensor_fn(preset, w, seed, index):
    """The relocalizer's range read: preset sensor at the true pose, experiment.py's noise stream."""
    fan = presets.make_sensor(preset, np.random.default_rng([seed, index, 4301]))
    return lambda truth: fan.scan(w, truth.x, truth.y, truth.yaw, truth.t)


def build(arm, preset, w, est, seed, index, spin_rate=S.SPIN_RATE_RAD_S, stack_arc=S.STACK_ARC_RAD):
    fn = sensor_fn(preset, w, seed, index)
    p = presets.SENSOR_PRESETS[preset]
    mr = p["max_range"]
    hc = math.radians(p["cone_deg"]) / 2 if p["model"] == "cone" else 0.0
    rng = np.random.default_rng([seed, index, 4501])
    inner = astar_esdf.make(known_map=True)
    if arm == "single":
        return R.RelocPoseSource(est, w.grid, fn, mode="single"), X.HoverGate(inner)
    if arm in ("multi_sep", "multi_ig"):
        src = D.DisambPoseSource(est, w.grid, fn, "separation" if arm == "multi_sep" else "infogain",
                                 rng=rng, goal=w.goal)
        return src, RD.DisambGate(inner, src)
    if arm in ("spin", "spin_single"):
        src = S.SpinStackPoseSource(est, w.grid, fn, mr, hc, mode="multi" if arm == "spin" else "single",
                                    spin_rate=spin_rate, stack_arc=stack_arc)
    else:
        src = S.SpinMovePoseSource(est, w.grid, fn, mr, hc, "infogain", rng=rng, goal=w.goal,
                                   spin_rate=spin_rate, stack_arc=stack_arc)
    return src, S.SpinGate(inner, src)


def extra(row, est, src, fault):
    out = RD.extra(row, est, src, fault)
    if isinstance(src, S.SpinMixin):
        for i, ev in enumerate(out["events"]):
            lg = src.spin_log.get(i, {})
            ev["spin_s"] = round(lg.get("spin_steps", 0) / run.DEFAULTS["plan_hz"], 2)
            ev["arc_done_t"] = lg.get("arc_done_t")
            ev["first_stack_returns"] = lg.get("first_stack_returns")
        out["spin_s"] = round(src.spin_steps / run.DEFAULTS["plan_hz"], 2)
    return out


def run_cell(args):
    preset, fault_name, arm, family, layouts, seed, spin_rate, stack_arc = args
    rows = []
    t0 = time.perf_counter()
    for i in range(layouts):
        w = world.make_world(family, seed, i)
        est = estimator.make_pose_source_factory(fault_name, dark=True, sink=[])(w, seed, i)
        src, planner = build(arm, preset, w, est, seed, i, spin_rate, stack_arc)
        row, _, _ = run.run_one(planner, w, seed, i, run.DEFAULTS, src)
        row.update(extra(row, est, src, est.fault))
        rows.append(row)
    return preset, fault_name, arm, rows, round(time.perf_counter() - t0, 1)


def med(v):
    return round(float(np.median(v)), 2) if len(v) else None


def summarize(rows):
    s = RD.summarize(rows)
    ev = [e for x in rows for e in x.get("events", [])]
    sp = [e["spin_s"] for e in ev if "spin_s" in e]
    sr = [e["first_stack_returns"] for e in ev if e.get("first_stack_returns") is not None]
    s.update({
        "median_spin_s_per_event": med(sp),
        "p95_spin_s_per_event": round(float(np.percentile(sp, 95)), 2) if sp else None,
        "median_spin_s_per_run": med([x["spin_s"] for x in rows if "spin_s" in x]),
        "median_first_stack_returns": med(sr),
        "events_arc_never_done": sum(1 for e in ev if "arc_done_t" in e and e["arc_done_t"] is None),
        "median_hover_s_per_run": med([x["hover_s"] for x in rows]),
        "no_returns_closed": sum(1 for e in ev if e["result"] == "no_returns"),
    })
    return s


def fmt(v):
    return "-" if v is None else f"{v}"


HEAD = ("| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted "
        "| wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous "
        "| median / p95 recover s | median spin s per event | median lost s per run | moves flown "
        "| median first-stack returns | median run max err m |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(preset, fault, arm, s):
    o = s["open_by_last_verdict"]
    spin = arm.startswith("spin")
    mv = arm in ("multi_sep", "multi_ig", "spin_ig")
    return (f"| {preset} | {fault} | {LABEL[arm]} {arm} | {s['reached_pct']} | {s['collision_pct']} | {s['stuck_pct']} "
            f"| {'/'.join(str(v) for v in s['events_by_reason'].values())} | {s['accepted']} | {s['wrong_commits']} "
            f"| {s['no_returns_closed']} "
            f"| {o['none_too_few_returns']} / {o['none_low_score']} / {o['ambiguous']} "
            f"| {fmt(s['median_recover_s'])} / {fmt(s['p95_recover_s'])} "
            f"| {fmt(s['median_spin_s_per_event']) if spin else '-'} | {fmt(s['median_hover_s_per_run'])} "
            f"| {s['moves_total'] if mv else '-'} | {fmt(s['median_first_stack_returns']) if spin else '-'} "
            f"| {fmt(s['median_run_max_err_m'])} |")


TUNE_RATIOS = (1.02, 1.05, 1.10, 1.15)
TUNE_SMIN = (0.6, 0.7)


def tune(argv, layouts=20, poses=15, seed=1, n_scans=17, step=0.1):
    t0 = time.perf_counter()
    hc = math.radians(presets.SENSOR_PRESETS["crazyflie"]["cone_deg"]) / 2
    variants = {"cone_raw": (hc, None), "cone_open_drop0": (hc, 0), "cone_open_drop1": (hc, 1),
                "cone_open_drop2": (hc, 2), "cone_open_drop3": (hc, 3), "ray_no_cone": (0.0, None)}
    recs = {v: [] for v in variants}
    for i in range(layouts):
        w = world.make_world("random", seed, i)
        m = R.ScanMatcher(w.grid)
        rng = np.random.default_rng([seed, i, 4303])
        k = 0
        while k < poses:
            x, y = rng.uniform(w.xmin + 0.3, w.xmax - 0.3), rng.uniform(w.ymin + 0.3, w.ymax - 0.3)
            if w.clearance(x, y) < 0.3:
                continue
            k += 1
            yaw0 = rng.uniform(-math.pi, math.pi)
            th = rng.uniform(-math.pi, math.pi)
            cen = (x + 0.5 * math.cos(th), y + 0.5 * math.sin(th))
            yaw = yaw0 + (n_scans - 1) * step
            for v, (h, drop) in variants.items():
                pr = dict(presets.SENSOR_PRESETS["crazyflie"])
                if v == "ray_no_cone":
                    pr["n_sub"] = 1
                fan = presets.ConeRangeFan(rng=np.random.default_rng([seed, i, k, 4302]),
                                           **{q: pr[q] for q in presets._CONE_KEYS})
                st = S.ScanStack(arc_rad=None)
                for j in range(n_scans):
                    st.add(j * step, (x, y), yaw0 + j * step, fan.scan(w, x, y, yaw0 + j * step, j * step))
                sc = st.pseudo(0.0, (x, y), yaw, 3.0, h if drop is not None else 0.0, drop or 0)
                s_t = m.score_at(sc, yaw, (x, y))
                hy = m.hypotheses(sc, yaw, cen)
                r = {"returns": int(np.isfinite(sc.distances).sum()), "score_truth": s_t}
                if hy:
                    r.update({"err": math.hypot(hy[0].x - x, hy[0].y - y), "best": hy[0].score,
                              "ratio": hy[0].score / hy[1].score if len(hy) > 1 and hy[1].score > 0 else 99.0})
                recs[v].append(r)
    out = {"input": "synthetic", "seed": seed, "layouts": layouts, "poses_per_layout": poses,
           "spin": {"scans": n_scans, "step_rad": step}, "command": "python run_sparse.py --tune",
           "window": "centred 0.5 m off truth, +-2 m", "variants": {}}
    for v, rr in recs.items():
        st = [r["score_truth"] for r in rr if r["score_truth"] is not None]
        ok = [r for r in rr if "err" in r]
        grid = {}
        for rt in TUNE_RATIOS:
            for sm in TUNE_SMIN:
                pp = [r for r in ok if r["best"] >= sm and r["ratio"] >= rt]
                grid[f"ratio {rt} s_min {sm}"] = {"pass": len(pp), "pass_wrong": sum(1 for r in pp if r["err"] > X.WRONG_M)}
        out["variants"][v] = {
            "poses": len(rr), "median_returns": float(np.median([r["returns"] for r in rr])),
            "too_few_returns": sum(1 for r in rr if r["score_truth"] is None),
            "score_at_truth_p5_p50": [round(float(np.percentile(st, 5)), 3), round(float(np.median(st)), 3)] if st else None,
            "matched": len(ok), "best_wrong": sum(1 for r in ok if r["err"] > X.WRONG_M),
            "rule_grid": grid}
    out["wall_s"] = round(time.perf_counter() - t0, 1)
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "sparse_tune_seed1.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for v, d in out["variants"].items():
        g = d["rule_grid"]
        print(v, d["median_returns"], d["score_at_truth_p5_p50"], d["matched"], d["best_wrong"],
              {kk: f"{vv['pass']}/{vv['pass_wrong']}" for kk, vv in g.items()})
    print("wrote sparse_tune_seed1.json")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--family", default="random", choices=world.FAMILIES)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--presets", default=",".join(PRESETS))
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--stem", default=None)
    ap.add_argument("--spin-rate", type=float, default=S.SPIN_RATE_RAD_S, help="rad/s")
    ap.add_argument("--stack-arc-deg", type=float, default=math.degrees(S.STACK_ARC_RAD))
    ap.add_argument("--tune", action="store_true", help="static seed-1 sweep, no flight")
    a = ap.parse_args(argv)
    if a.tune:
        return tune(argv)
    arms = [x for x in a.arms.split(",") if x]
    pres = [x for x in a.presets.split(",") if x]
    cmd = "python run_sparse.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.perf_counter()
    sr, sa = a.spin_rate, math.radians(a.stack_arc_deg)
    cells = [(p, fl, arm, a.family, a.layouts, a.seed, sr, sa) for p in pres for fl in FAULTS for arm in arms]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        out = list(ex.map(run_cell, cells))
    wall = time.perf_counter() - t0
    res = {}
    for p, fl, arm, rows, cw in out:
        res.setdefault(p, {}).setdefault(fl, {})[arm] = {"summary": summarize(rows), "cell_wall_s": cw, "runs": rows}
    lines = [HEAD] + [line(p, fl, arm, res[p][fl][arm]["summary"]) for p in pres for fl in FAULTS for arm in arms]
    tab = "\n".join(lines)
    print(tab)
    print(f"\nwall {wall:.1f} s")
    os.makedirs(a.out, exist_ok=True)
    stem = a.stem or f"sparse_{a.family}_{a.seed}"
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    params = {k: getattr(S, k) for k in ("SPIN_RATE_RAD_S", "MIN_ARC_RAD", "STACK_ARC_RAD", "INF_DROP",
                                         "SPARSE_RATIO", "SPARSE_S_MIN", "STILL_MPS", "STILL_WAIT_S")}
    params.update({"spin_rate_used": sr, "stack_arc_rad_used": round(sa, 4)})
    params.update({k: getattr(R, k) for k in ("MIN_RETURNS", "S_MIN", "RATIO", "N_SCANS", "W0_M", "SEP_M",
                                              "K_MAX", "S_INNOV", "INNOV_SCANS", "SETTLE_SCANS")})
    params.update({k: getattr(D, k) for k in ("HOVER_TIMEOUT_S", "MAX_MOVES", "MOVE_SPEED")})
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "family": a.family, "seed": a.seed,
                   "wall_s": round(wall, 1), "workers": a.workers, "params": params,
                   "presets": {p: presets.SENSOR_PRESETS[p] for p in pres}, "config": run.DEFAULTS,
                   "env": env, "results": res}, fh, indent=1, default=list)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s, {a.workers} workers\n\n{tab}\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
