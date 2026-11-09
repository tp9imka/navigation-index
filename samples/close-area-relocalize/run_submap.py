"""Rolling-submap relocalization on a 4-beam sensor (submap.py) vs the spin-stack and AF-MCL arms.

.venv/bin/python run_submap.py                 # held out: seed 2, 100 layouts, crazyflie random + office, ideal random
.venv/bin/python run_submap.py --layouts 5 --families random --presets crazyflie --faults jump   # quick look
.venv/bin/python run_submap.py --tune          # static seed-1 sweep behind WINDOW_S and the ratio (no fault)

Arms (A* known map, planners/astar_esdf.py known_map=True, scored on truth by the arena):
  spin_ig    (i) loop-54 reference: hover + yaw spin stack + info-gain move (sparse.py, via run_mcl.run_task)
  mcl        (m) loop-67 reference: AF-MCL-style particle filter, planner flies the mean (mcl.py, via run_mcl.run_task)
  submap     (s) rolling submap in the odometry frame, matched on loss, hover until accept (submap.py)
  submap_ig  (s+ig) (s) + info-gain move after 1 s without accept; the move's returns join the submap
  submap_arc, submap_arc_ig  extra: (s), (s+ig) with ArcScanMatcher (cone arc) instead of the cone opening
  submap_fwd, submap_fwd_ig  extra: arc hypotheses re-scored by the forward cone model (ConeVerifier)
  submap_arc_ig_notrack  extra ablation: (a+ig) without nominal tracking
  submap_bridge  extra ablation: inertial bridge across the loss, keep the pre-loss anchor, no matching,
                 no innovation test, no tracking (what the bridge alone does)
Cells: crazyflie preset on random and office, ideal preset on random (sanity). Faults: dropout (2 s)
and jump (0.5 m), estimator with its 2 dark zones per layout. Same sensor noise stream for every
arm ([seed, index, 4301]). Columns and definitions as run_mcl.py (wrong commit = pose > 0.5 m off
truth when navigation resumes; truth recover = AF-MCL's definition).
Writes results/submap_<stem>.json / .md (default stem seed<seed>). Input: synthetic.

--tune: seed 1 (flights not held out from it), 20 layouts per family, crazyflie, no fault. The
planner flies on truth; the estimator runs alongside (dark zones) to give raw positions. Every 1 s
from t = 3 s, submaps of several windows are built from the raw positions as SubmapPoseSource
builds them, and scored at the true pose (score at truth), and matched with the window centred
0.5 m off truth (best error, best / second ratio). Writes results/submap_tune_seed1.json.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

from arena import astar_esdf, estimator, run, world
import experiment as X
import relocalize as R
import run_disambiguate as RD
import run_mcl as RM
import run_sparse as RS
import submap as SM

presets = importlib.import_module("close_area_arena.presets")

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("spin_ig", "mcl", "submap", "submap_ig")
SUBMAP_ARMS = ("submap", "submap_ig", "submap_arc", "submap_arc_ig", "submap_fwd", "submap_fwd_ig",
               "submap_arc_ig_notrack", "submap_bridge")
EXTRA_ARMS = SUBMAP_ARMS[2:]   # --arms; run after the main table
LABEL = {"spin_ig": "(i) spin_ig", "mcl": "(m) mcl", "submap": "(s) submap", "submap_ig": "(s+ig) submap_ig",
         "submap_arc": "(a) submap_arc", "submap_arc_ig": "(a+ig) submap_arc_ig",
         "submap_fwd": "(v) submap_fwd", "submap_fwd_ig": "(v+ig) submap_fwd_ig",
         "submap_arc_ig_notrack": "(a+ig-t) submap_arc_ig_notrack", "submap_bridge": "(x) submap_bridge"}
CELLS = (("random", "crazyflie"), ("office", "crazyflie"), ("random", "ideal"))
FAULTS = ("dropout", "jump")
WRONG_M = X.WRONG_M
PASS_REACHED = 90.0


def beam_angles(preset):
    p = presets.SENSOR_PRESETS[preset]
    n = p["n_beams"]
    return -math.pi + np.arange(n) * (2 * math.pi / n)


def build_submap(arm, preset, w, est, seed, index):
    p = presets.SENSOR_PRESETS[preset]
    hc = math.radians(p["cone_deg"]) / 2 if p["model"] == "cone" else 0.0
    src = SM.SubmapPoseSource(est, w.grid, RS.sensor_fn(preset, w, seed, index), p["max_range"], hc,
                              np.random.default_rng([seed, index, 4801]), moves="_ig" in arm,
                              track=not (arm.endswith("_notrack") or arm == "submap_bridge"),
                              innovation=arm != "submap_bridge",
                              goal=w.goal, beam_angles=beam_angles(preset), match=arm != "submap_bridge",
                              scoring="arc_fwd" if "_fwd" in arm else ("arc" if "_arc" in arm else "opening"),
                              cone=p)
    return src, RD.DisambGate(astar_esdf.make(known_map=True), src)


def run_task(args):
    family, preset, fault, arm, seed, index = args
    if arm not in SUBMAP_ARMS:
        _, out = RM.run_task((family, preset, fault, arm, seed, index, RM.M.N_PARTICLES, False))
        return args, out
    w = world.make_world(family, seed, index)
    est = estimator.make_pose_source_factory(fault, dark=True, sink=[])(w, seed, index)
    src, planner = build_submap(arm, preset, w, est, seed, index)
    rec = RM.Recorder(src)
    t0 = time.perf_counter()
    row, _, _ = run.run_one(planner, w, seed, index, run.DEFAULTS, rec)
    wall = time.perf_counter() - t0
    out = {k: row.get(k) for k in ("outcome", "reached", "collision", "stuck", "timeout", "time_to_goal_s", "index")}
    fl = est.fault.log
    out["fault_fired_t"] = fl.get("fired_t")
    t_end = None if fl.get("fired_t") is None else (fl["start_t"] + fl["dur_s"] if "dur_s" in fl else fl["fired_t"])
    out["truth_recover"], out["truth_recover_s"] = RM.truth_recover(rec.log, fl.get("fired_t"), t_end)
    dt = 1.0 / run.DEFAULTS["plan_hz"]
    out["flown_wrong_s"] = round(sum(dt for _, e, q in rec.log if q > 0 and e > WRONG_M), 2)
    out["hover_s"] = round(sum(dt for _, _, q in rec.log if q == 0), 2)
    out["err_median_m"] = round(float(np.median([x[1] for x in rec.log])), 4)
    out["err_max_m"] = round(float(max(x[1] for x in rec.log)), 4)
    tf = fl.get("fired_t")
    pre = [x[1] for x in rec.log if tf is None or x[0] < tf]
    out["pre_fault_max_err_m"] = round(float(max(pre)), 4) if pre else None
    keep = ("t_trigger", "reason", "result", "err_m", "pre_err_m", "recover_s", "last_verdict", "last_returns",
            "truth_in_set", "max_window_m", "settle_s", "shift_m", "settle_timeout", "returns_at_first_match",
            "span_s_at_first_match", "n_moves", "verdicts")
    out["events"] = [{k: e[k] for k in keep} for e in src.event_dicts()]
    out["moves"] = [m for e in src.extra for m in e["moves"]]
    out["innov_checks"] = src.innov_runs
    out["track_updates"] = src.track_updates
    out["track_m"] = round(src.track_m, 3)
    out["ms_per_scan_median"] = round(float(np.median(src.match_ms)), 3) if src.match_ms else None
    out["wall_s"] = round(wall, 2)
    return args, out


def med(v):
    return round(float(np.median(v)), 2) if len(v) else None


def stats(rows, arm):
    s = RM.stats(rows)
    ev = [e for r in rows for e in r["events"]]
    if arm in SUBMAP_ARMS:
        op = [e for e in ev if e["result"] == "open"]
        s.update({
            "events_by_reason": {k: sum(1 for e in ev if e["reason"] == k) for k in ("reset_counter", "quality_0", "innovation")},
            "median_returns_at_first_match": med([e["returns_at_first_match"] for e in ev if e.get("returns_at_first_match") is not None]),
            "median_span_s_at_first_match": med([e["span_s_at_first_match"] for e in ev if e.get("span_s_at_first_match") is not None]),
            "median_settle_s": med([e["settle_s"] for e in ev if e.get("settle_s") is not None]),
            "settle_timeouts": sum(1 for e in ev if e.get("settle_timeout")),
            "open_by_last_verdict": {
                "none_too_few_returns": sum(1 for e in op if e["last_verdict"] == "none" and (e["last_returns"] or 0) < R.MIN_RETURNS),
                "none_low_score": sum(1 for e in op if e["last_verdict"] == "none" and (e["last_returns"] or 0) >= R.MIN_RETURNS),
                "ambiguous": sum(1 for e in op if e["last_verdict"] == "ambiguous"),
                "pending_or_settling": sum(1 for e in op if e["last_verdict"] in (None, "pending"))},
            "moves_flown": sum(1 for r in rows for m in r.get("moves", []) if m.get("move") is not None),
            "wrong_commit_reasons": {k: sum(1 for e in ev if e["result"] == "accepted" and e["err_m"] is not None
                                            and e["err_m"] > WRONG_M and e["reason"] == k)
                                     for k in ("reset_counter", "quality_0", "innovation")},
        })
    return s


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) "
        "| runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) "
        "| truth recover s median / p95 (loss runs, not recovered) | event recover s median / p95 | events / still lost at end "
        "| median hover s per run | submap returns at first match, median | ms per matched scan |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(fam, pre, fl, arm, s):
    ci = s["reached_ci95"]
    sub = arm in SUBMAP_ARMS
    return (f"| {fam} | {pre} | {fl} | {LABEL[arm]} | {s['reached_pct']} ({ci[0]}-{ci[1]}) | {s['collision_pct']} "
            f"| {s['stuck_pct']} | {s['wrong_commits']} | {s['runs_lost_before_fault']} "
            f"| {s['runs_flown_wrong']} ({f(s['median_flown_wrong_s'])}) "
            f"| {f(s['truth_recover_median_s'])} / {f(s['truth_recover_p95_s'])} ({s['truth_loss_runs']}, {s['truth_not_recovered']}) "
            f"| {f(s['event_recover_median_s'])} / {f(s['event_recover_p95_s'])} | {s['events']} / {s['open_at_end']} "
            f"| {f(s['median_hover_s'])} | {f(s.get('median_returns_at_first_match')) if sub else '-'} "
            f"| {f(s['ms_per_scan_median'])} |")


# ---------------- static tune (seed 1) ----------------
TUNE_WINDOWS = (2.0, 4.0, 6.0, 10.0)
TUNE_RATIOS = (1.02, 1.05, 1.10, 1.15)
TUNE_CONES = ("raw", "opening", "arc")   # centre ray, cone_opening_local (the arm), ArcScanMatcher (extra)


class _Rec:
    def __init__(self, est, fn):
        self.est, self.fn, self.log = est, fn, []

    def __call__(self, truth):
        raw = self.est(truth)
        self.log.append((truth.t, np.array([raw.x, raw.y]), raw.yaw, self.fn(truth), np.array([truth.x, truth.y])))
        return truth


def tune_layout(args):
    family, i, seed = args
    w = world.make_world(family, seed, i)
    est = estimator.make_pose_source_factory("none", dark=True, sink=[])(w, seed, i)
    rec = _Rec(est, RS.sensor_fn("crazyflie", w, seed, i))
    run.run_one(X.HoverGate(astar_esdf.make(known_map=True)), w, seed, i, run.DEFAULTS, rec)
    mats = {"raw": R.ScanMatcher(w.grid), "arc": SM.ArcScanMatcher(w.grid, SM.ARC_SUB)}
    mats["opening"] = mats["raw"]
    hc = math.radians(presets.SENSOR_PRESETS["crazyflie"]["cone_deg"]) / 2
    rng = np.random.default_rng([seed, i, 4803])
    out = []
    for win in TUNE_WINDOWS:
        sm = SM.Submap(win, SM.MAX_POINTS)
        for k, (t, rxy, yaw, scan, txy) in enumerate(rec.log):
            sm.maybe_add(t, rxy, yaw, scan)
            sm.trim(t)
            if t < 3.0 - 1e-9 or abs(t - round(t)) > 1e-6:
                continue
            th = rng.uniform(-math.pi, math.pi)
            cen = (txy[0] + 0.5 * math.cos(th), txy[1] + 0.5 * math.sin(th))
            for cone in TUNE_CONES:
                m = mats[cone]
                sc = sm.pseudo(t, rxy, yaw, 3.0, 0.0 if cone == "raw" else hc, SM.ARC_SUB if cone == "arc" else 0)
                r = {"family": family, "layout": i, "t": round(t, 1), "window_s": win, "cone": cone,
                     "returns": len(sc.distances) // (SM.ARC_SUB if cone == "arc" else 1), "est_err_m": round(float(np.hypot(*(rxy - txy))), 3)}
                r["score_truth"] = m.score_at(sc, yaw, txy)
                hy = m.hypotheses(sc, yaw, cen)
                if hy:
                    r.update({"err": math.hypot(hy[0].x - txy[0], hy[0].y - txy[1]), "best": hy[0].score,
                              "ratio": hy[0].score / hy[1].score if len(hy) > 1 and hy[1].score > 0 else 99.0})
                out.append(r)
    return out


def tune(argv, layouts=20, seed=1, workers=8):
    t0 = time.perf_counter()
    tasks = [(fam, i, seed) for fam in ("random", "office") for i in range(layouts)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        recs = [r for rr in ex.map(tune_layout, tasks) for r in rr]
    res = {}
    for fam in ("random", "office"):
        for win in TUNE_WINDOWS:
            for cone in TUNE_CONES:
                rr = [r for r in recs if r["family"] == fam and r["window_s"] == win and r["cone"] == cone]
                st = [r["score_truth"] for r in rr if r["score_truth"] is not None]
                ok = [r for r in rr if "err" in r]
                grid = {}
                for rt in TUNE_RATIOS:
                    pp = [r for r in ok if r["best"] >= SM.SUBMAP_S_MIN and r["ratio"] >= rt]
                    grid[f"ratio {rt}"] = {"pass": len(pp), "pass_wrong": sum(1 for r in pp if r["err"] > WRONG_M)}
                res[f"{fam} w{win:g} {cone}"] = {
                    "samples": len(rr), "median_returns": float(np.median([r["returns"] for r in rr])),
                    "too_few_returns": sum(1 for r in rr if r["score_truth"] is None),
                    "score_at_truth_p5_p50": [round(float(np.percentile(st, 5)), 3), round(float(np.median(st)), 3)] if st else None,
                    "below_s_innov": sum(1 for v in st if v < SM.S_INNOV),
                    "matched": len(ok), "best_wrong": sum(1 for r in ok if r["err"] > WRONG_M),
                    "rule_grid": grid}
    out = {"input": "synthetic", "seed": seed, "layouts_per_family": layouts, "preset": "crazyflie", "fault": "none",
           "command": "python run_submap.py " + " ".join(argv or []), "max_points": SM.MAX_POINTS,
           "window": "hypotheses centred 0.5 m off truth, +-2 m", "variants": res,
           "wall_s": round(time.perf_counter() - t0, 1)}
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "submap_tune_seed1.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for k, d in res.items():
        print(k, d["median_returns"], d["too_few_returns"], d["score_at_truth_p5_p50"], d["below_s_innov"],
              d["matched"], d["best_wrong"], {kk: f"{vv['pass']}/{vv['pass_wrong']}" for kk, vv in d["rule_grid"].items()})
    print(f"wrote submap_tune_seed1.json, {out['wall_s']} s")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--families", default="random,office")
    ap.add_argument("--presets", default="crazyflie,ideal")
    ap.add_argument("--faults", default=",".join(FAULTS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=min(14, os.cpu_count() or 1))
    ap.add_argument("--stem", default=None)
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--tune", action="store_true", help="static seed-1 sweep, no fault")
    a = ap.parse_args(argv)
    if a.tune:
        return tune(argv if argv is not None else sys.argv[1:], workers=a.workers)
    sp = lambda s: [x for x in s.split(",") if x]
    fams, pres, fls, arms = sp(a.families), sp(a.presets), sp(a.faults), sp(a.arms)
    cells = [c for c in CELLS if c[0] in fams and c[1] in pres]
    cmd = "python run_submap.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tasks = [(fam, pre, fl, arm, a.seed, i) for fam, pre in cells for fl in fls for arm in arms for i in range(a.layouts)]
    tasks.sort(key=lambda t: t[3] == "mcl")
    t0 = time.perf_counter()
    rows = {}
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for j, (args, row) in enumerate(ex.map(run_task, tasks, chunksize=2)):
            rows[args] = row
            if (j + 1) % 200 == 0:
                print(f"{j + 1}/{len(tasks)} runs, {time.perf_counter() - t0:.0f} s", flush=True)
    wall = round(time.perf_counter() - t0, 1)
    res, lines, verdicts = {}, [HEAD], []
    for fam, pre in cells:
        for fl in fls:
            for arm in arms:
                rr = [rows[(fam, pre, fl, arm, a.seed, i)] for i in range(a.layouts)]
                s = stats(rr, arm)
                res.setdefault(fam, {}).setdefault(pre, {}).setdefault(fl, {})[arm] = {"summary": s, "runs": rr}
                lines.append(line(fam, pre, fl, arm, s))
                if pre == "crazyflie" and arm in SUBMAP_ARMS and arm != "submap_bridge":
                    ok = s["reached_pct"] >= PASS_REACHED and s["wrong_commits"] == 0
                    verdicts.append({"family": fam, "fault": fl, "arm": arm, "reached_pct": s["reached_pct"],
                                     "wrong_commits": s["wrong_commits"], "pass": ok})
    tab = "\n".join(lines)
    vtxt = ""
    if verdicts:
        allp = {arm: all(v["pass"] for v in verdicts if v["arm"] == arm) for arm in {v["arm"] for v in verdicts}}
        vtxt = ("\n\nVerdict (crazyflie, >= 90 % reached and 0 wrong commits in every family x fault cell): "
                + "; ".join(f"{LABEL[k]} {'PASS' if v else 'FAIL'}" for k, v in sorted(allp.items())) + "\n\n"
                + "\n".join(f"- {v['family']} {v['fault']} {LABEL[v['arm']]}: {v['reached_pct']} % reached, "
                            f"{v['wrong_commits']} wrong commits => {'PASS' if v['pass'] else 'FAIL'}" for v in verdicts))
    print(tab + vtxt)
    print(f"\nwall {wall} s")
    os.makedirs(a.out, exist_ok=True)
    stem = "submap_" + (a.stem or f"seed{a.seed}")
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system(), "date": time.strftime("%Y-%m-%d")}
    params = {k: getattr(SM, k) for k in ("WINDOW_S", "MAX_POINTS", "KEY_MOVE_M", "KEY_YAW_RAD", "PARALLAX_M",
                                           "ACC_BIAS", "ACC_NOISE", "SETTLE_TOL_M", "SETTLE_N", "SETTLE_MIN",
                                           "SETTLE_MAX_S", "SUBMAP_RATIO", "SUBMAP_S_MIN", "S_INNOV", "INNOV_SCANS",
                                           "N_ALONG")}
    params.update({k: getattr(R, k) for k in ("MIN_RETURNS", "N_SCANS", "W0_M", "W_MAX_M", "SEP_M", "K_MAX", "NONE_WIDEN")})
    params.update({"WRONG_M": WRONG_M, "PASS_REACHED_PCT": PASS_REACHED})
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seed": a.seed, "layouts": a.layouts, "wall_s": wall,
                   "workers": a.workers, "params": params, "config": run.DEFAULTS, "env": env,
                   "verdicts": verdicts, "results": res}, fh, default=list)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall} s, {a.workers} workers, {a.layouts} layouts, seed {a.seed}.\n\n{tab}{vtxt}\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
