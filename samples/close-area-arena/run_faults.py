"""Run a planner on the VIO-like estimator (estimator.py) under every fault case (faults.py).

python run_faults.py --planner straight --layouts 50 --seed 0 [--family random] [--cases none,jump]

The planner sees the estimate; ranges and scoring stay on truth (CONTRACT.md). Besides the
fault cases it runs two references with the same layouts:
  truth         no pose source (planner sees truth), the arena baseline
  none_nodark   estimator with no fault and no dark zones, to check the drift calibration

--planner takes any planners/<name>.py, or freest_beam (the CONTRACT.md example, defined here
because this job may not add files under planners/).

Writes results/faults_<planner>_<case>_<seed>.json/.md per case and
results/faults_<planner>_summary_<seed>.md. A non-random family adds _<family> after the planner.
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

try:
    from . import estimator, faults, run
    from .adapter import Setpoint
    from .planners.base import Planner
except ImportError:
    import estimator
    import faults
    import run
    from adapter import Setpoint
    from planners.base import Planner


class FreestBeam(Planner):
    """CONTRACT.md example, unchanged logic."""
    name = "freest_beam"

    def step(self, pose, scan, goal, grid, dt):
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        hg = math.atan2(ey, ex)
        wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
        ok = [pose.yaw + a for a, d in zip(scan.angles, scan.distances) if d > 1.0]
        h = min(ok, key=lambda a: abs(wrap(a - hg)), default=hg + math.pi)
        v = min(1.0, math.hypot(ex, ey))
        vx, vy = v * math.cos(h), v * math.sin(h)
        for a, d in zip(scan.angles, scan.distances):
            if d < 0.6:
                vx -= 2 * (0.6 - d) * math.cos(pose.yaw + a); vy -= 2 * (0.6 - d) * math.sin(pose.yaw + a)
        return Setpoint(vx, vy, 0.0, 1.5 * wrap(hg - pose.yaw))


def planner_factory(name: str):
    if name == "freest_beam":
        return lambda: FreestBeam()
    return lambda: run.load_planner(name)


def r(v, n=4):
    return None if v is None else round(float(v), n)


def run_case(case: str, make_planner, family: str, layouts: int, seed: int):
    sink: list = []
    if case == "truth":
        mps = None
    elif case == "none_nodark":
        mps = estimator.make_pose_source_factory("none", dark=False, sink=sink)
    else:
        mps = estimator.make_pose_source_factory(case, dark=True, sink=sink)
    t0 = time.perf_counter()
    rows, summ, _ = run.evaluate(make_planner, family, layouts, seed, make_pose_source=mps)
    wall = time.perf_counter() - t0
    all_err, all_exceed, fired = [], [], 0
    for row, est in zip(rows, sink):
        e = np.array(est.errs)
        s = np.array(est.sigmas)
        q = np.array(est.qualities)
        row.update({
            "est_err_median_m": r(np.median(e)), "est_err_max_m": r(e.max()),
            "est_err_final_m": r(e[-1]),
            "frac_err_gt_2sigma": r(np.mean(e > 2 * s)),
            "frac_quality_lt_50": r(np.mean(q < 50)),
            "dark_step_frac": r(est.dark_steps / len(e)),
            "reset_counter_final": est.reset_counter,
            "fault_log": est.fault.log if est.fault else None,
            "dark_zones": [z.to_list() for z in est.zones],
        })
        all_err.append(e)
        all_exceed.append(e > 2 * s)
        fired += int(est.fault is not None and est.fault.log.get("fired_t") is not None)
    if sink:
        e = np.concatenate(all_err)
        summ.update({
            "est_err_median_m": r(np.median(e)), "est_err_max_m": r(e.max()),
            "est_err_run_max_median_m": r(np.median([x.max() for x in all_err])),
            "frac_err_gt_2sigma": r(np.mean(np.concatenate(all_exceed))),
            "fault_fired_runs": fired,
        })
    summ["wall_s"] = round(wall, 2)
    summ["collisions"] = sum(1 for x in rows if x["collision"])
    return rows, summ


def calibration(rows):
    """Origin-anchored drift of the no-fault, no-dark estimator vs path length."""
    pts = [(x["path_length_m"], x["est_err_final_m"]) for x in rows if x["path_length_m"] > 1.0]
    c_hat = math.sqrt(np.mean([e * e / d for d, e in pts])) if pts else None
    return {"runs_used": len(pts), "c_hat_m_per_sqrt_m": r(c_hat),
            "c_target_m_per_sqrt_m": r(estimator.DRIFT_C),
            "predicted_rms_at_10m_m": r(c_hat * math.sqrt(10)) if c_hat else None,
            "target_at_10m_m": 0.15,
            "source": "samples/relative-nav-benchmark/README.md: OpenVINS UZH-FPV indoor_forward_3, RPE over 10 m 1.5 % (real data)"}


def fmt(v):
    return "-" if v is None else f"{v}"


HEAD = ("| case | layouts | reached % | collision % | stuck % | timeout % | median min clearance m "
        "| est err median m | est err max m | median of run max err m | err > 2 sigma % | fault fired runs |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(case, s):
    ex = s.get("frac_err_gt_2sigma")
    return (f"| {case} | {s['n']} | {fmt(s['reached_pct'])} | {fmt(s['collision_pct'])} | {fmt(s['stuck_pct'])} "
            f"| {fmt(s['timeout_pct'])} | {fmt(s['median_min_clearance_m'])} | {fmt(s.get('est_err_median_m'))} "
            f"| {fmt(s.get('est_err_max_m'))} | {fmt(s.get('est_err_run_max_median_m'))} "
            f"| {fmt(None if ex is None else round(100 * ex, 1))} | {fmt(s.get('fault_fired_runs'))} |")


def runs_md(rows):
    out = ["| run | outcome | min clearance m | est err median m | est err max m | resets | fault fired t s | dark step % |",
           "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        fl = x.get("fault_log") or {}
        out.append(f"| {x['index']} | {x['outcome']} | {x['min_clearance_m']} | {fmt(x.get('est_err_median_m'))} "
                   f"| {fmt(x.get('est_err_max_m'))} | {fmt(x.get('reset_counter_final'))} | {fmt(fl.get('fired_t'))} "
                   f"| {fmt(None if x.get('dark_step_frac') is None else round(100 * x['dark_step_frac'], 1))} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--planner", default="straight")
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--family", default="random", choices=run.world_mod.FAMILIES)
    ap.add_argument("--cases", default=",".join(("truth", "none_nodark") + faults.CASES))
    ap.add_argument("--out", default=run.RESULTS)
    a = ap.parse_args(argv)
    cases = [c for c in a.cases.split(",") if c]
    cmd = "python run_faults.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tag = a.planner if a.family == "random" else f"{a.planner}_{a.family}"
    os.makedirs(a.out, exist_ok=True)
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    lines, calib = [], None
    for case in cases:
        rows, summ = run_case(case, planner_factory(a.planner), a.family, a.layouts, a.seed)
        extra = {}
        if case == "none_nodark":
            calib = extra["calibration"] = calibration(rows)
        stem = os.path.join(a.out, f"faults_{tag}_{case}_{a.seed}")
        with open(stem + ".json", "w") as fh:
            json.dump({"planner": a.planner, "family": a.family, "seed": a.seed, "layouts": a.layouts,
                       "case": case, "input": "synthetic", "command": cmd, "config": run.DEFAULTS,
                       "estimator": {"vio_hz": estimator.VIO_HZ, "imu_hz": estimator.IMU_HZ,
                                     "drift_c": estimator.DRIFT_C, "vio_white": estimator.VIO_WHITE,
                                     "acc_noise": estimator.ACC_NOISE, "acc_bias": estimator.ACC_BIAS,
                                     "q_acc": estimator.Q_ACC, "dark": estimator.DARK},
                       "summary": summ, **extra, "env": env, "runs": rows}, fh, indent=1)
        ln = line(case, summ)
        lines.append(ln)
        with open(stem + ".md", "w") as fh:
            fh.write(f"`{cmd}` (synthetic), case `{case}`, planner `{a.planner}`, family `{a.family}`, "
                     f"wall {summ['wall_s']} s\n\n{HEAD}\n{ln}\n\n{runs_md(rows)}\n")
        print(ln, flush=True)
    summ_path = os.path.join(a.out, f"faults_{tag}_summary_{a.seed}.md")
    with open(summ_path, "w") as fh:
        fh.write(f"`{cmd}` (synthetic). Planner sees the estimate; ranges and scores are on truth.\n\n"
                 f"{HEAD}\n" + "\n".join(lines) + "\n")
        if calib:
            fh.write(f"\nDrift calibration (none_nodark, {calib['runs_used']} runs, origin-anchored final error): "
                     f"fitted C = {calib['c_hat_m_per_sqrt_m']} m/sqrt(m) vs target {calib['c_target_m_per_sqrt_m']}; "
                     f"=> {calib['predicted_rms_at_10m_m']} m RMS at 10 m vs 0.15 m target ({calib['source']}).\n")
    print(f"wrote {summ_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
