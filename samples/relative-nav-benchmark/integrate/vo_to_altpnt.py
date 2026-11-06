"""Part 4: turn a measured odometry trajectory into the relative-source error model of
samples/altpnt-integrity, then rerun that sample's integrity monitor with it.

altpnt-integrity simulates VIO as 1 Hz velocity with error = scale * v + yaw * (v rotated 90 deg)
+ white noise. Here those three numbers are fitted from real (gt, estimate) TUM pairs written by
parts 1-3; the estimate is anchored on the first 10 % of the path (as if GNSS was there at the start), so
later heading drift shows up as yaw error.

Usage: python integrate/vo_to_altpnt.py results/lidar/kitti04_gt.tum results/lidar/kitti04_kiss_icp.tum [--label kiss-icp] ...
       (pairs of gt/est; see run_all.sh)
"""
import argparse
import cmath
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
ALTPNT = HERE.parent / "altpnt-integrity"
WINDOW_S = 1.0
ANCHOR_FRACTION = 0.1
ANCHOR_MIN_M = 20.0
RETUNE_MARGIN = 1.25


def load_tum(p):
    a = np.loadtxt(p)
    return a[:, 0], a[:, 1:4]


def resample(t, xyz, grid):
    return np.stack([np.interp(grid, t, xyz[:, i]) for i in range(3)], axis=1)


def fit_error_model(gt_tum, est_tum):
    tg, pg = load_tum(gt_tum)
    te, pe = load_tum(est_tum)
    t0, t1 = max(tg[0], te[0]), min(tg[-1], te[-1])
    grid = np.arange(t0, t1, WINDOW_S)
    g, e = resample(tg, pg, grid), resample(te, pe, grid)
    # Anchor like "GNSS available at the start, then lost": 2D rotation fitted on positions over the
    # first ANCHOR_FRACTION of the GT path (at least ANCHOR_MIN_M). A single start pose is not used:
    # near-hover starts give no heading, and GT body vs estimator frame may differ by a fixed rotation.
    gc = np.array([complex(*p) for p in g[:, :2] - g[0, :2]])
    ec0 = np.array([complex(*p) for p in e[:, :2] - e[0, :2]])
    run_len = np.concatenate([[0], np.cumsum(np.abs(np.diff(gc)))])
    k = max(2, int(np.searchsorted(run_len, max(ANCHOR_MIN_M, ANCHOR_FRACTION * run_len[-1]))))
    rot = np.sum(np.conj(ec0[:k]) * gc[:k])
    rot /= abs(rot)
    ec = ec0 * rot
    dg, de = np.diff(gc) / WINDOW_S, np.diff(ec) / WINDOW_S
    moving = np.abs(dg) > 0.2
    dg, de = dg[moving], de[moving]
    c = np.sum(np.conj(dg) * de) / np.sum(np.abs(dg) ** 2)
    resid = de - c * dg
    dist = float(np.sum(np.abs(dg)) * WINDOW_S)
    end_err = float(abs(ec[-1] - gc[-1]))
    return {"anchor_window_m": round(float(run_len[k]), 1), "samples_1hz": int(len(dg)), "mean_speed_mps": float(np.mean(np.abs(dg))),
            "distance_m": dist, "scale_err": float(abs(c) - 1), "yaw_err_rad": float(cmath.phase(c)),
            "white_mps": float(np.sqrt(0.5 * np.mean(np.abs(resid) ** 2))),
            "end_error_2d_m": end_err, "end_error_pct": 100 * end_err / max(dist, 1e-9)}


def run_altpnt(model, seed=1, retune=False):
    sys.path.insert(0, str(ALTPNT))
    import altpnt_integrity as A
    saved = {k: getattr(A, k) for k in ("VIO_SCALE_ERR", "VIO_YAW_ERR", "VIO_WHITE", "VIO_R", "VIO_GM_SIGMA")}
    try:
        if model is not None:
            A.VIO_SCALE_ERR = model["scale_err"]
            A.VIO_YAW_ERR = model["yaw_err_rad"]
            # White noise in m/s does not transfer across speeds; carry it as a fraction of speed.
            A.VIO_WHITE = model["white_mps"] / model["mean_speed_mps"] * A.SPEED
            if retune:
                # Inflate white-noise R and the VIO velocity-bias prior so they cover the fitted error.
                A.VIO_R = max(A.VIO_R, A.VIO_WHITE * RETUNE_MARGIN)
                bias = math.hypot(model["scale_err"], model["yaw_err_rad"]) * A.SPEED
                A.VIO_GM_SIGMA = max(A.VIO_GM_SIGMA, bias * RETUNE_MARGIN)
                A.F_EPOCH, A.Q_EPOCH = A._transition()  # Q is precomputed at import
        sc = A.Scenario(gnss=False)
        data = A.simulate(sc, seed)
        s = A.summarize(A.run(sc, seed, "full", data=data), sc)
        return {k: s[k] for k in ("hpe_rms", "hpe_p95", "hpe_max", "hpl_median", "availability", "mi", "hmi")} | {
            "vio_truth_params": {"scale": A.VIO_SCALE_ERR, "yaw_rad": A.VIO_YAW_ERR, "white_mps_at_30mps": round(A.VIO_WHITE, 4),
                                 "filter_R": A.VIO_R, "filter_bias_sigma": A.VIO_GM_SIGMA}}
    finally:
        for k, v in saved.items():
            setattr(A, k, v)
        A.F_EPOCH, A.Q_EPOCH = A._transition()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="+", help="label=gt.tum,est.tum ...")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default=str(HERE / "results" / "altpnt_from_vo.json"))
    a = ap.parse_args()
    out = {"note": "altpnt-integrity scenario with GNSS off (alt-PNT only), alert limit 50 m, 600 s at 30 m/s; "
                   "VIO truth error replaced by the fitted model, filter tuning unchanged unless 'retuned'."}
    avg = lambda rs: {k: round(float(np.mean([r[k] for r in rs])), 3) for k in rs[0] if k != "vio_truth_params"}
    out["default_model"] = avg([run_altpnt(None, s) for s in range(1, a.seeds + 1)])
    for p in a.pairs:
        label, files = p.split("=", 1)
        gt, est = files.split(",")
        m = fit_error_model(gt, est)
        r = {"fit": m,
             "altpnt_as_tuned": avg([run_altpnt(m, s) for s in range(1, a.seeds + 1)]),
             "altpnt_retuned_R": avg([run_altpnt(m, s, retune=True) for s in range(1, a.seeds + 1)])}
        r["altpnt_truth_params"] = run_altpnt(m, 1)["vio_truth_params"]
        r["altpnt_retuned_params"] = run_altpnt(m, 1, retune=True)["vio_truth_params"]
        out[label] = r
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
