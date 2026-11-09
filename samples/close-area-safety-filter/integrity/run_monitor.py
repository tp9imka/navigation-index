"""Fly the arena A* planner on the VIO-EKF under VIO and UWB faults; run the integrity monitor
passively on every 10 Hz epoch and score its protection level against truth.

python run_monitor.py --layouts 100 --seed 0 --workers 14 [--cases none,vio_jump] [--variants ss2,ss1]

Per run (one random-family layout, one case):
  planner   arena planners/astar_esdf.py, make(known_map=True), 10 Hz, flies on the VIO-EKF
            estimate (arena estimator.py with dark zones), so faults change the path
  sources   VIO-EKF position + sigma_xy (arena estimator.py), UWB ranges (uwb.py), both sampled
            at each planner step (10 Hz) from truth; the monitor does not feed back
  monitor   monitor.py, every variant replayed on the same epochs
  scoring   truth: breach = available epoch with |x_out - truth| > PL

Cases: none (dark zones only), vio_jump, vio_bias, vio_dropout (arena faults.py jump / bias /
dropout), uwb_nlos (uwb.make_nlos), both (VIO bias + UWB NLOS starting at the same time).

Writes results/monitor_<seed>.json and results/monitor_<seed>.md. All inputs are synthetic.
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

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import _arena  # noqa: E402
import monitor  # noqa: E402
import uwb  # noqa: E402

RESULTS = os.path.join(HERE, "results")
FAMILY = "random"
CASES = ("none", "vio_jump", "vio_bias", "vio_dropout", "uwb_nlos", "both")
VIO_FAULT = {"none": "none", "vio_jump": "jump", "vio_bias": "bias", "vio_dropout": "dropout",
             "uwb_nlos": "none", "both": "bias"}
BREACH_TARGET = 1e-2
CORRIDORS = (0.5, 1.0)


class Recorder:
    """PoseSource: returns the VIO-EKF pose to the planner, logs VIO and UWB per call."""

    def __init__(self, est, ranger):
        self.est, self.ranger, self.log = est, ranger, []

    def __call__(self, truth):
        pose = self.est(truth)
        r = self.ranger.measure(truth.t, truth.x, truth.y, truth.z)
        self.log.append((truth.t, truth.x, truth.y, truth.z, pose.x, pose.y, pose.sigma_xy, *r))
        return pose


def fly(case: str, index: int, seed: int):
    run = _arena.run
    w = _arena.world.make_world(FAMILY, seed, index, radius=run.DEFAULTS["vehicle"]["radius"])
    sink: list = []
    est = _arena.estimator.make_pose_source_factory(VIO_FAULT[case], dark=True, sink=sink)(w, seed, index)
    nlos = None
    if case == "uwb_nlos":
        nlos = uwb.make_nlos(w, seed, index)
    elif case == "both":
        nlos = uwb.make_nlos(w, seed, index, t0=est.fault.t0)
    ranger = uwb.UwbRanger(w, np.random.default_rng([seed, index, 4400]), nlos=nlos)
    rec = Recorder(est, ranger)
    row, _, _ = run.run_one(_arena.astar_esdf.make(known_map=True), w, seed, index, run.DEFAULTS, rec)
    log = np.array(rec.log)
    vio_on = est.fault.log.get("fired_t") if VIO_FAULT[case] != "none" else None
    t_end = float(log[-1, 0])
    nlos_on = nlos.t0 if (nlos is not None and nlos.t0 <= t_end) else None
    return w, row, log, ranger.anchors, est.fault.log, nlos, vio_on, nlos_on


def faulty_groups(t, vio_on, nlos):
    out = set()
    if vio_on is not None and t >= vio_on - 1e-9:
        out.add("vio")
    if nlos is not None and nlos.active(t):
        out |= {f"a{nlos.anchor}", "uwb"}
    return out


def score_variant(variant, log, anchors, vio_on, nlos, nlos_on):
    mon = monitor.Monitor(anchors, variant)
    onsets = [t for t in (vio_on, nlos_on) if t is not None]
    onset = min(onsets) if onsets else None
    c = {"epochs": 0, "avail": 0, "breach": 0, "ambiguous": 0, "amb_multiple": 0, "amb_none": 0,
         "excluded": 0, "wrong_excl": 0, "correct_excl": 0, "detected": 0, "nofault_epochs": 0,
         "false_alarm": 0, "post_epochs": 0, "post_ambiguous": 0, "post_avail": 0}
    pls, errs, ratio_max = [], [], 0.0
    first_det = None
    excl_names: dict = {}
    for row in log:
        t, tx, ty, tz, vx, vy, vs = row[:7]
        out = mon.step((vx, vy), vs, row[7:], tz)
        bad = faulty_groups(t, vio_on, nlos)
        err = float(math.hypot(out["x"][0] - tx, out["x"][1] - ty))
        c["epochs"] += 1
        post = onset is not None and t >= onset - 1e-9
        c["post_epochs"] += int(post)
        if not bad:
            c["nofault_epochs"] += 1
            c["false_alarm"] += int(out["detected"])
        if out["detected"]:
            c["detected"] += 1
            if post and first_det is None:
                first_det = t
        if out["ambiguous"]:
            c["ambiguous"] += 1
            c["post_ambiguous"] += int(post)
            c["amb_multiple" if out["reason"] == "multiple_consistent" else "amb_none"] += 1
        if out["status"] == "excluded":
            c["excluded"] += 1
            key = "+".join(out["excluded"])
            excl_names[key] = excl_names.get(key, 0) + 1
            if set(out["excluded"]) - bad:
                c["wrong_excl"] += 1
            else:
                c["correct_excl"] += 1
        if math.isfinite(out["pl"]):
            c["avail"] += 1
            c["post_avail"] += int(post)
            pls.append(out["pl"])
            errs.append(err)
            ratio_max = max(ratio_max, err / out["pl"])
            if err > out["pl"]:
                c["breach"] += 1
    c["det_delay_s"] = None if (first_det is None or onset is None) else round(first_det - onset, 3)
    c["onset_t"] = onset
    c["excluded_names"] = excl_names
    c["err_over_pl_max"] = round(ratio_max, 4)
    return c, np.array(pls), np.array(errs)


def run_layout(args):
    case, index, seed, variants = args
    t0 = time.perf_counter()
    w, row, log, anchors, flog, nlos, vio_on, nlos_on = fly(case, index, seed)
    t_fly = time.perf_counter() - t0
    vio_err = np.hypot(log[:, 4] - log[:, 1], log[:, 5] - log[:, 2])
    res = {"case": case, "index": index, "outcome": row["outcome"], "duration_s": row["duration_s"],
           "path_length_m": row["path_length_m"], "vio_fault_log": flog,
           "nlos": None if nlos is None else nlos.log, "vio_onset_t": vio_on, "nlos_onset_t": nlos_on,
           "vio_err_max_m": round(float(vio_err.max()), 4),
           "vio_err_gt_3sigma_axis_frac": round(float(np.mean(vio_err > 3 * log[:, 6] / math.sqrt(2))), 4),
           "fly_s": round(t_fly, 3), "variants": {}}
    arrays = {}
    for v in variants:
        c, pls, errs = score_variant(v, log, anchors, vio_on, nlos, nlos_on)
        res["variants"][v] = c
        arrays[v] = (pls.astype(np.float32), errs.astype(np.float32))
    res["wall_s"] = round(time.perf_counter() - t0, 3)
    return res, arrays


def r(x, n=4):
    return None if x is None else round(float(x), n)


def summarize(runs, arrays, variant):
    cs = [x["variants"][variant] for x in runs]
    tot = {k: sum(c[k] for c in cs) for k in cs[0] if isinstance(cs[0][k], int)}
    pls = np.concatenate([a[variant][0] for a in arrays]) if arrays else np.array([])
    errs = np.concatenate([a[variant][1] for a in arrays]) if arrays else np.array([])
    fired = [c for c in cs if c["onset_t"] is not None]
    delays = [c["det_delay_s"] for c in fired if c["det_delay_s"] is not None]
    n_all = tot["epochs"]
    pl_all = np.full(n_all, np.inf)
    pl_all[:len(pls)] = pls
    s = {
        "runs": len(cs), "fault_fired_runs": len(fired), "epochs": n_all, "avail_epochs": tot["avail"],
        "breaches": tot["breach"],
        "breach_frac": r(tot["breach"] / tot["avail"], 6) if tot["avail"] else None,
        "breach_target": BREACH_TARGET,
        "breach_pass": (tot["breach"] / tot["avail"] < BREACH_TARGET) if tot["avail"] else None,
        "pl_median_m": r(np.median(pls)) if len(pls) else None,
        "pl_p95_m": r(np.percentile(pls, 95)) if len(pls) else None,
        "err_median_m": r(np.median(errs)) if len(errs) else None,
        "err_over_pl_max": r(max(c["err_over_pl_max"] for c in cs)),
        "detected_runs": len(delays),
        "det_delay_median_s": r(np.median(delays), 3) if delays else None,
        "det_delay_max_s": r(max(delays), 3) if delays else None,
        "wrong_excl_runs": sum(1 for c in cs if c["wrong_excl"] > 0),
        "wrong_excl_epochs": tot["wrong_excl"], "correct_excl_epochs": tot["correct_excl"],
        "excluded_epochs": tot["excluded"],
        "ambiguous_frac": r(tot["ambiguous"] / n_all, 5),
        "ambiguous_post_onset_frac": r(tot["post_ambiguous"] / tot["post_epochs"], 5) if tot["post_epochs"] else None,
        "ambiguous_multiple": tot["amb_multiple"], "ambiguous_none": tot["amb_none"],
        "false_alarm_frac": r(tot["false_alarm"] / tot["nofault_epochs"], 5) if tot["nofault_epochs"] else None,
    }
    for al in CORRIDORS:
        s[f"pl_le_{al}_frac"] = r(np.mean(pl_all <= al), 4)
    return s


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "PASS" if v else "FAIL"
    return f"{v}"


HEAD = ("| case | variant | runs (fault fired) | epochs | breaches | breach frac (avail) | < 1e-2 | median PL m "
        "| p95 PL m | PL <= 0.5 m | PL <= 1.0 m | detected runs | delay median / max s | wrong-excl runs "
        "| wrong-excl epochs | ambiguous % (post onset %) | false alarm % | median err m |\n"
        "|" + "---|" * 18)


def line(case, v, s):
    pct = lambda x: "-" if x is None else f"{round(100 * x, 2)}"
    return (f"| {case} | {v} | {s['runs']} ({s['fault_fired_runs']}) | {s['epochs']} | {s['breaches']} "
            f"| {fmt(s['breach_frac'])} | {fmt(s['breach_pass'])} | {fmt(s['pl_median_m'])} | {fmt(s['pl_p95_m'])} "
            f"| {pct(s['pl_le_0.5_frac'])} % | {pct(s['pl_le_1.0_frac'])} % | {s['detected_runs']} "
            f"| {fmt(s['det_delay_median_s'])} / {fmt(s['det_delay_max_s'])} | {s['wrong_excl_runs']} "
            f"| {s['wrong_excl_epochs']} | {pct(s['ambiguous_frac'])} ({pct(s['ambiguous_post_onset_frac'])}) "
            f"| {pct(s['false_alarm_frac'])} | {fmt(s['err_median_m'])} |")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cases", default=",".join(CASES))
    ap.add_argument("--variants", default=",".join(monitor.VARIANTS))
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--tag", default="monitor")
    a = ap.parse_args(argv)
    cases = [c for c in a.cases.split(",") if c]
    variants = [v for v in a.variants.split(",") if v]
    cmd = "python run_monitor.py " + " ".join(argv if argv is not None else sys.argv[1:])
    jobs = [(c, i, a.seed, variants) for c in cases for i in range(a.layouts)]
    t0 = time.perf_counter()
    if a.workers > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            out = list(ex.map(run_layout, jobs, chunksize=2))
    else:
        out = [run_layout(j) for j in jobs]
    wall = time.perf_counter() - t0
    summary, lines, rows = {}, [], {}
    for c in cases:
        sel = [(res, arr) for res, arr in out if res["case"] == c]
        runs = [x for x, _ in sel]
        arrs = [y for _, y in sel]
        rows[c] = runs
        outcomes = {}
        for x in runs:
            outcomes[x["outcome"]] = outcomes.get(x["outcome"], 0) + 1
        summary[c] = {"outcomes": outcomes,
                      "vio_err_gt_3sigma_axis_frac_mean": r(np.mean([x["vio_err_gt_3sigma_axis_frac"] for x in runs])),
                      "variants": {}}
        for v in variants:
            s = summarize(runs, arrs, v)
            summary[c]["variants"][v] = s
            lines.append(line(c, v, s))
            print(lines[-1], flush=True)
    os.makedirs(a.out, exist_ok=True)
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    cfg = {"IR": monitor.IR, "P_FA": monitor.P_FA, "PRIOR_VIO": monitor.PRIOR_VIO,
           "PRIOR_ANCHOR": monitor.PRIOR_ANCHOR, "variants": monitor.VARIANTS,
           "uwb": {"hz": uwb.HZ, "sigma_white": uwb.SIGMA_WHITE, "cal_bias": uwb.CAL_BIAS,
                   "sigma_model": uwb.SIGMA_MODEL, "nlos_bias": uwb.NLOS_BIAS, "nlos_dur_s": uwb.NLOS_DUR_S,
                   "anchor_inset": uwb.ANCHOR_INSET, "anchor_z": uwb.ANCHOR_Z},
           "family": FAMILY, "planner": "astar_esdf known_map=True on the VIO-EKF estimate"}
    stem = os.path.join(a.out, f"{a.tag}_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts,
                   "wall_s": round(wall, 1), "workers": a.workers, "config": cfg, "env": env,
                   "summary": summary, "runs": rows}, fh, indent=1)
    with open(stem + ".md", "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {round(wall, 1)} s on {a.workers} workers. "
                 f"PL at integrity risk {monitor.IR} per epoch; breach = available epoch with true error > PL.\n\n"
                 f"{HEAD}\n" + "\n".join(lines) + "\n\nRun outcomes per case (A* on the VIO-EKF estimate):\n\n")
        for c in cases:
            fh.write(f"- {c}: {summary[c]['outcomes']}, mean fraction of epochs with VIO error > 3 x "
                     f"per-axis sigma: {summary[c]['vio_err_gt_3sigma_axis_frac_mean']}\n")
    print(f"wrote {os.path.relpath(stem, HERE)}.json/.md, wall {wall:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
