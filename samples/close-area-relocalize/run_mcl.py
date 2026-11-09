"""Kill test from doc 10: hub arm (f) multi_ig against an AF-MCL-style particle filter (mcl.py).

.venv/bin/python run_mcl.py                      # 100 layouts, seed 2, random + office, ideal + crazyflie, dropout + jump
.venv/bin/python run_mcl.py --layouts 5 --families random --presets ideal --faults jump   # quick look

Arms (A* known map, planners/astar_esdf.py known_map=True, scored on truth by the arena):
  multi_ig  (f) the hub arm: up to 5 hypotheses, RatioPersistence, hover while lost, info-gain move
            after 1 s (disambiguate.py, unchanged; built by run_sparse.build so the preset scan is used)
  mcl       (m) AF-MCL style: particle mean, no hover gate (mcl.MCLPoseSource mode "mean")
  mcl_gate  (m+g) same filter, hover while the particle spread sigma > 0.25 m (mode "gate")
Sensor presets (samples/close-area-arena/presets.py), the relocalizer's read only; the planner does
not read the scan. Same noise stream for every arm ([seed, index, 4301]).
Faults: the arena's dropout (2 s) and jump (0.5 m), estimator with its 2 dark zones per layout.

Per run, on truth (never fed back): the output pose error and whether the planner was navigating
(quality > 0) at every 10 Hz step.
  wrong commit       a loss / ambiguity event closed with the pose > 0.5 m from truth: that is the
                     pose navigation resumes on. (f): accept. mcl / mcl_gate: sigma back at or
                     below 0.25 m for 3 scans.
  flown wrong        navigating steps with the pose > 0.5 m off. For mcl every step navigates.
  truth recover s    AF-MCL's definition: after the fault fires, the first time the error goes
                     above 0.2 m, then the first time it stays at or below 0.2 m for 1 s; measured
                     from the fault onset. Runs where it never exceeded 0.2 m count as "no loss".
  event recover s    trigger to accept (f), or ambiguity open to close (mcl arms).
  --hardened         MCL arms only: posterior-mean output + empty-beam fallback after 5 updates.
Writes results/mcl_<stem>.json / .md (default stem: seed<seed>). Input: synthetic.
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

from arena import astar_esdf, estimator, run, world
import experiment as X
import mcl as M
import relocalize as R
import run_disambiguate as RD
import run_sparse as RS

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("multi_ig", "mcl", "mcl_gate")
LABEL = {"multi_ig": "(f) multi_ig", "mcl": "(m) mcl", "mcl_gate": "(m+g) mcl_gate", "spin_ig": "(i) spin_ig"}
HUB_ARMS = ("multi_ig", "spin_ig")   # spin_ig: optional, the hub's 4-beam arm (sparse.py), --arms spin_ig
FAMILIES = ("random", "office")
PRESETS = ("ideal", "crazyflie")
FAULTS = ("dropout", "jump")
WRONG_M = X.WRONG_M          # 0.5 m
REC_M = 0.2                  # m, "low error" for truth recover s
REC_HOLD = 10                # 10 Hz steps = 1 s
REC_WINDOW_S = 3.0           # s after the fault ends in which a loss must start
Z = 1.959964


def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1))


class Recorder:
    """PoseSource pass-through: logs (t, |pose - truth|, quality) of what the planner gets."""

    def __init__(self, inner):
        self.inner = inner
        self.log: list[tuple] = []

    def __call__(self, truth):
        p = self.inner(truth)
        self.log.append((truth.t, math.hypot(p.x - truth.x, p.y - truth.y), p.quality))
        return p


HARD = {"estimate": "posterior", "empty_fallback": 5}


def build(arm, preset, w, est, seed, index, n, hardened=False):
    if arm in HUB_ARMS:
        return RS.build(arm, preset, w, est, seed, index)
    mr = RS.presets.SENSOR_PRESETS[preset]["max_range"]
    src = M.MCLPoseSource(est, w.grid, RS.sensor_fn(preset, w, seed, index), mr,
                          np.random.default_rng([seed, index, 4601]), mode="gate" if arm == "mcl_gate" else "mean", n=n,
                          **(HARD if hardened else {}))
    inner = astar_esdf.make(known_map=True)
    return src, (X.HoverGate(inner) if arm == "mcl_gate" else inner)


def truth_recover(log, t_fault, t_fault_end):
    """Loss = error above REC_M within REC_WINDOW_S after the fault ends (dark-zone drift later is not
    the fault). Recovered = first time after that the error stays <= REC_M for REC_HOLD steps."""
    if t_fault is None:
        return "not_fired", None
    e = [x[1] for x in log if x[0] >= t_fault - 1e-9]
    t = [x[0] for x in log if x[0] >= t_fault - 1e-9]
    first = next((k for k, v in enumerate(e) if v > REC_M and t[k] <= t_fault_end + REC_WINDOW_S), None)
    if first is None:
        return "no_loss", None
    for j in range(first, len(e) - REC_HOLD + 1):
        if max(e[j:j + REC_HOLD]) <= REC_M:
            return "recovered", round(t[j] - t_fault, 2)
    return "not_recovered", None


def run_task(args):
    family, preset, fault, arm, seed, index, n, hardened = args
    w = world.make_world(family, seed, index)
    est = estimator.make_pose_source_factory(fault, dark=True, sink=[])(w, seed, index)
    src, planner = build(arm, preset, w, est, seed, index, n, hardened)
    rec = Recorder(src)
    t0 = time.perf_counter()
    row, _, _ = run.run_one(planner, w, seed, index, run.DEFAULTS, rec)
    wall = time.perf_counter() - t0
    out = {k: row.get(k) for k in ("outcome", "reached", "collision", "stuck", "timeout", "time_to_goal_s", "index")}
    fl = est.fault.log
    out["fault_fired_t"] = fl.get("fired_t")
    t_end = None if fl.get("fired_t") is None else (fl["start_t"] + fl["dur_s"] if "dur_s" in fl else fl["fired_t"])
    status, rs = truth_recover(rec.log, fl.get("fired_t"), t_end)
    out["truth_recover"] = status
    out["truth_recover_s"] = rs
    dt = 1.0 / run.DEFAULTS["plan_hz"]
    out["flown_wrong_s"] = round(sum(dt for _, e, q in rec.log if q > 0 and e > WRONG_M), 2)
    out["hover_s"] = round(sum(dt for _, _, q in rec.log if q == 0), 2)
    out["err_median_m"] = round(float(np.median([x[1] for x in rec.log])), 4)
    out["err_max_m"] = round(float(max(x[1] for x in rec.log)), 4)
    tf = fl.get("fired_t")
    pre = [x[1] for x in rec.log if tf is None or x[0] < tf]
    out["pre_fault_max_err_m"] = round(float(max(pre)), 4) if pre else None
    if arm in HUB_ARMS:
        ev = RD.extra(row, est, src, est.fault)["events"]
        out["events"] = [{"t_trigger": e["t_trigger"], "reason": e["reason"], "result": e["result"],
                          "err_m": e["err_m"], "recover_s": e["recover_s"], "last_verdict": e["last_verdict"],
                          "moves": len([m for m in e.get("moves", []) if m.get("move") is not None])} for e in ev]
        out["ms_per_scan_median"] = round(float(np.median(src.match_ms)), 3) if src.match_ms else None
    else:
        out["events"] = src.events
        out["inject_steps"] = src.inject_steps
        out["injected_particles"] = src.injected
        out["empty_beam_steps"] = src.empty_steps
        out["fallback_steps"] = src.pf.fallback_steps
        out["sigma_median_m"] = round(float(np.median(src.sigmas)), 4)
        out["ms_per_scan_median"] = round(float(np.median(src.update_ms)), 3)
    out["wall_s"] = round(wall, 2)
    return args, out


def med(v):
    return round(float(np.median(v)), 2) if len(v) else None


def p95(v):
    return round(float(np.percentile(v, 95)), 2) if len(v) else None


def stats(rows):
    n = len(rows)
    k = sum(1 for r in rows if r["reached"])
    ev = [e for r in rows for e in r["events"]]
    acc = [e for e in ev if e["result"] == "accepted"]
    tr = [r["truth_recover_s"] for r in rows if r["truth_recover"] == "recovered"]
    fw = [r["flown_wrong_s"] for r in rows if r["flown_wrong_s"] > 0]
    return {
        "n": n, "reached": k, "reached_pct": round(100 * k / n, 1), "reached_ci95": wilson(k, n),
        "collision_pct": round(100 * sum(1 for r in rows if r["collision"]) / n, 1),
        "stuck_pct": round(100 * sum(1 for r in rows if r["stuck"]) / n, 1),
        "timeout_pct": round(100 * sum(1 for r in rows if r["timeout"]) / n, 1),
        "events": len(ev), "accepted": len(acc),
        "wrong_commits": sum(1 for e in acc if e["err_m"] is not None and e["err_m"] > WRONG_M),
        "runs_with_wrong_commit": sum(1 for r in rows if any(e["result"] == "accepted" and e["err_m"] is not None
                                                             and e["err_m"] > WRONG_M for e in r["events"])),
        "open_at_end": sum(1 for e in ev if e["result"] == "open"),
        "runs_flown_wrong": len(fw), "median_flown_wrong_s": med(fw), "total_flown_wrong_s": round(sum(fw), 1),
        "fault_fired_runs": sum(1 for r in rows if r["fault_fired_t"] is not None),
        "runs_lost_before_fault": sum(1 for r in rows if (r["pre_fault_max_err_m"] or 0) > WRONG_M),
        "truth_loss_runs": sum(1 for r in rows if r["truth_recover"] in ("recovered", "not_recovered")),
        "truth_not_recovered": sum(1 for r in rows if r["truth_recover"] == "not_recovered"),
        "truth_recover_median_s": med(tr), "truth_recover_p95_s": p95(tr),
        "event_recover_median_s": med([e["recover_s"] for e in acc]),
        "event_recover_p95_s": p95([e["recover_s"] for e in acc]),
        "median_hover_s": med([r["hover_s"] for r in rows]),
        "median_err_m": med([r["err_median_m"] for r in rows]),
        "median_run_max_err_m": med([r["err_max_m"] for r in rows]),
        "ms_per_scan_median": med([r["ms_per_scan_median"] for r in rows if r["ms_per_scan_median"] is not None]),
        "median_inject_steps": med([r["inject_steps"] for r in rows if "inject_steps" in r]) if "inject_steps" in rows[0] else None,
        "empty_beam_steps_median": med([r["empty_beam_steps"] for r in rows if "empty_beam_steps" in r]) if "empty_beam_steps" in rows[0] else None,
    }


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) "
        "| runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) | truth recover s median / p95 (loss runs, not recovered) "
        "| event recover s median / p95 | still lost at end | median hover s per run | ms per scan |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(fam, pre, fl, arm, s):
    ci = s["reached_ci95"]
    return (f"| {fam} | {pre} | {fl} | {LABEL[arm]} | {s['reached_pct']} ({ci[0]}-{ci[1]}) | {s['collision_pct']} "
            f"| {s['stuck_pct']} | {s['wrong_commits']} | {s['runs_lost_before_fault']} | {s['runs_flown_wrong']} ({f(s['median_flown_wrong_s'])}) "
            f"| {f(s['truth_recover_median_s'])} / {f(s['truth_recover_p95_s'])} ({s['truth_loss_runs']}, {s['truth_not_recovered']}) "
            f"| {f(s['event_recover_median_s'])} / {f(s['event_recover_p95_s'])} | {s['open_at_end']} "
            f"| {f(s['median_hover_s'])} | {f(s['ms_per_scan_median'])} |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--presets", default=",".join(PRESETS))
    ap.add_argument("--faults", default=",".join(FAULTS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--particles", type=int, default=M.N_PARTICLES)
    ap.add_argument("--hardened", action="store_true",
                    help="MCL arms: posterior-mean output and empty-beam fallback (mcl.py ESTIMATE / EMPTY_FALLBACK)")
    ap.add_argument("--workers", type=int, default=min(14, os.cpu_count() or 1))
    ap.add_argument("--stem", default=None)
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    sp = lambda s: [x for x in s.split(",") if x]
    fams, pres, fls, arms = sp(a.families), sp(a.presets), sp(a.faults), sp(a.arms)
    cmd = "python run_mcl.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tasks = [(fam, pre, fl, arm, a.seed, i, a.particles, a.hardened) for fam in fams for pre in pres for fl in fls for arm in arms
             for i in range(a.layouts)]
    tasks.sort(key=lambda t: t[3] not in HUB_ARMS)     # slowest arms first
    t0 = time.perf_counter()
    rows = {}
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for j, (args, row) in enumerate(ex.map(run_task, tasks, chunksize=2)):
            rows[args] = row
            if (j + 1) % 200 == 0:
                print(f"{j + 1}/{len(tasks)} runs, {time.perf_counter() - t0:.0f} s", flush=True)
    wall = round(time.perf_counter() - t0, 1)
    res, lines = {}, [HEAD]
    for fam in fams:
        for pre in pres:
            for fl in fls:
                for arm in arms:
                    rr = [rows[(fam, pre, fl, arm, a.seed, i, a.particles, a.hardened)] for i in range(a.layouts)]
                    s = stats(rr)
                    res.setdefault(fam, {}).setdefault(pre, {}).setdefault(fl, {})[arm] = {"summary": s, "runs": rr}
                    lines.append(line(fam, pre, fl, arm, s))
    tab = "\n".join(lines)
    print(tab)
    print(f"\nwall {wall} s")
    os.makedirs(a.out, exist_ok=True)
    stem = "mcl_" + (a.stem or f"seed{a.seed}")
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system(), "date": time.strftime("%Y-%m-%d")}
    params = {k: getattr(M, k) for k in ("Z_MAX", "Z_RAND", "Z_SHORT", "Z_HIT", "SIGMA_0", "GAMMA", "LAMBDA_SHORT",
                                          "SIGMA_U", "SIGMA_OBS", "ALPHA_SLOW", "ALPHA_FAST", "CHI", "NU",
                                          "N_PARTICLES", "SIGMA_GATE", "N_CONV", "OUT_CVAL_M")}
    params["particles_used"] = a.particles
    params["hardened"] = HARD if a.hardened else None
    params.update({"WRONG_M": WRONG_M, "REC_M": REC_M, "REC_HOLD_STEPS": REC_HOLD, "REC_WINDOW_S": REC_WINDOW_S})
    params.update({k: getattr(R, k) for k in ("S_MIN", "RATIO", "N_SCANS", "W0_M", "SEP_M", "K_MAX", "S_INNOV")})
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "seed": a.seed, "layouts": a.layouts, "wall_s": wall,
                   "workers": a.workers, "params": params, "config": run.DEFAULTS, "env": env, "results": res},
                  fh, default=list)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall} s, {a.workers} workers, {a.layouts} layouts, seed {a.seed}.\n\n{tab}\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
