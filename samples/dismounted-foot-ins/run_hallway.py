"""Evaluate the stdlib foot-mounted INS on the pyshoe hallway dataset (36 real trials).

usage:
  python3 run_hallway.py data/hallway [--pyshoe results/pyshoe_markers.json] [--jobs 8]
         [--only walk/0] [--tables filter,detectors,aiding] [--out results/hallway.json]

Error frame: ground truth is a set of surveyed floor markers (gt) hit at known IMU
indices (gt_idx). The INS frame's initial yaw is unknown, so, like pyshoe's
process_error_hallway.py, the estimate is rotated about the start so that the
position at gt_idx[1] points at gt[1]. For aided runs the same angle is used as the
initial yaw ("known entry heading"), so corridor headings and anchors are in one frame.
"""
import argparse
import glob
import json
import math
import os
import random
import sys
import zlib
from multiprocessing import Pool

import detectors
import matfile
import foot_ins
from foot_ins import FootINS, wrap

T_NOMINAL = 1.0 / 200  # mean rate of every trial; per-sample ROS stamps are bunched (median dt 5.18 ms)
BIAS_INIT_SAMPLES = 200  # ~1 s standstill at the start of every trial
THRESH = {"shoe": [3.0e7, 8.5e7, 2.0e8], "ared": [0.3, 0.55, 0.8],
          "amvd": [0.02, 0.05, 0.1], "mbgtd": [0.5, 0.75, 1.0]}  # amvd/mbgtd: picked so stance share ~ SHOE's on walk/0
DEFAULT_DET = ("shoe", 8.5e7)
FILTERS = {
    "pyshoe9": {"states": 9, "bg_init": False, "zaru": False, "pyshoe_order": True},
    "ins9": {"states": 9, "bg_init": False, "zaru": False, "pyshoe_order": False},
    "ins9_bg": {"states": 9, "bg_init": True, "zaru": False, "pyshoe_order": False},
    "ins15": {"states": 15, "bg_init": False, "zaru": False, "pyshoe_order": False},
    "ins15_bg": {"states": 15, "bg_init": True, "zaru": False, "pyshoe_order": False},
    "ins15_zaru": {"states": 15, "bg_init": False, "zaru": True, "pyshoe_order": False},
    "ins15_py": {"states": 15, "bg_init": False, "zaru": False, "pyshoe_order": True},
    "ins15_py_zaru": {"states": 15, "bg_init": False, "zaru": True, "pyshoe_order": True},
    "ins15_py_yrw": {"states": 15, "bg_init": False, "zaru": False, "pyshoe_order": True, "yaw_rw": True},
}
DEFAULT_FILTER = "ins15_py"
ZARU_MAX_RATE = 0.02  # rad/s; SHOE "stance" at G=8.5e7 admits |omega| up to ~0.8 rad/s

# Corridor heading constraint (heuristic drift elimination, Borenstein 2009 style)
DOMINANT_DIRS = [0.0, math.pi / 2, math.pi, -math.pi / 2]  # building is axis-aligned in the gt frame
MIN_STRIDE_M = 0.4
STRAIGHT_STEPS = 3
STRAIGHT_TOL = math.radians(8)
SNAP_TOL = math.radians(15)
HDE_SIGMA = math.radians(5)

# Simulated UWB: 4 wall-mounted anchors set back from the corridor centre lines, ranges only
# at odd marker epochs (held-out = even markers)
ANCHORS = [(8.0, 14.0, 2.5), (40.0, 6.0, 2.5), (54.0, 35.0, 2.5), (46.0, 52.0, 2.5)]
UWB_MAX_RANGE = 25.0
UWB_SIGMA = 0.15
NLOS_PROB = 0.3
NLOS_BIAS = (1.0, 5.0)  # positive excess delay, m
NIS_GATE = 6.63  # chi-square 1 dof, 99 %
DRIFT_FRAC = 0.02  # measured unaided drift is 1-2 % of distance; ZUPT covariance alone is overconfident
FLOOR_Z_DOWN = 0.0  # single-storey route: foot on the floor in stance (stand-in for a barometer)
FLOOR_SIGMA = 0.05
MAG_SIGMA = math.radians(5)  # what a datasheet-level compass heading would be trusted to


AIDING = {
    "aid_none": {},
    "aid_hde": {"hde": True},
    "aid_floor": {"floor": True},
    "aid_floor_uwb_raw": {"floor": True, "uwb": "raw"},
    "aid_floor_uwb_gated": {"floor": True, "uwb": "gated"},
    "aid_floor_uwb_inflated": {"floor": True, "uwb": "inflated"},
    "aid_hde_floor": {"hde": True, "floor": True},
    "aid_hde_floor_uwb_gated": {"hde": True, "floor": True, "uwb": "gated"},
    "aid_hde_floor_uwb_inflated": {"hde": True, "floor": True, "uwb": "inflated"},
}


def load_trial(path):
    d = matfile.loadmat(path)
    imu = d["imu"]
    ts = d["ts"][0]
    return {"acc": [r[:3] for r in imu], "gyro": [r[3:] for r in imu], "ts": ts,
            "gi": [int(v) for v in d["gt_idx"][0]], "gt": d["gt"]}


def det_stat(tr, name):
    if name == "shoe":
        return detectors.shoe(tr["acc"], tr["gyro"])
    if name == "ared":
        return detectors.ared(tr["gyro"])
    if name == "amvd":
        return detectors.amvd(tr["acc"])
    return detectors.mbgtd(tr["acc"])


def mag_angle(C, m_body):
    """Direction of the horizontal magnetic field in the nav frame (rad)."""
    mx = C[0][0] * m_body[0] + C[0][1] * m_body[1] + C[0][2] * m_body[2]
    my = C[1][0] * m_body[0] + C[1][1] * m_body[1] + C[1][2] * m_body[2]
    return math.atan2(my, mx)


def to_gt(p):
    return (p[0], p[1], -p[2])  # NED => gt frame (x, y, up); no mirror needed, checked on walk/0


def run(tr, zv, yaw0=0.0, dt_mode="T200", filt=DEFAULT_FILTER, hde=False, uwb=None, floor=False, stop=None,
        rng_seed=0, keep_track=False, mag=None, mag_apply=False):
    acc, gyro, ts = tr["acc"], tr["gyro"], tr["ts"]
    cfg = FILTERS[filt]
    n = len(acc) if stop is None else stop + 1
    bg0 = [0.0] * 3
    if cfg["bg_init"]:
        bg0 = [sum(g[i] for g in gyro[:BIAS_INIT_SAMPLES]) / BIAS_INIT_SAMPLES for i in range(3)]
    f = FootINS(acc, yaw0=yaw0, gyro_bias0=bg0, freeze_biases=cfg["states"] == 9, pyshoe_order=cfg["pyshoe_order"],
                yaw_rw=foot_ins.SIGMA_YAW_RW if cfg.get("yaw_rw") else 0.0)
    uwb_at = {}
    if uwb:
        rnd = random.Random(rng_seed)
        for m in range(1, len(tr["gi"]), 2):
            g = tr["gt"][m]
            meas = []
            for a in ANCHORS:
                r = math.dist(g, a)
                if r > UWB_MAX_RANGE:
                    continue
                nlos = rnd.random() < NLOS_PROB
                meas.append((a, r + rnd.gauss(0, UWB_SIGMA) + (rnd.uniform(*NLOS_BIAS) if nlos else 0.0), nlos))
            uwb_at[tr["gi"][m]] = meas
    stats = {"uwb_used": 0, "uwb_rejected": 0, "nlos": 0, "nlos_rejected": 0, "hde_updates": 0}
    if mag:
        m0 = [sum(m[i] for m in mag[:BIAS_INIT_SAMPLES]) / BIAS_INIT_SAMPLES for i in range(3)]
        alpha_ref = mag_angle(f.C, m0)
        stats["mag_resid_deg"], stats["mag_norm"] = [], []
    out = {0: to_gt(f.p)}
    stats["sigma_h"] = {0: f.sigma_h()}
    track = [] if keep_track else None
    last_stance_p, steps, prev_zv = None, [], True
    dist_since_fix, last_p = 0.0, f.p[:]
    for k in range(1, n):
        dt = (ts[k] - ts[k - 1]) if dt_mode == "ts" else T_NOMINAL
        f.propagate(acc[k], gyro[k], dt)
        if zv[k]:
            f.zupt()
            if cfg["zaru"] and math.sqrt(sum((gyro[k][i] - f.bg[i]) ** 2 for i in range(3))) < ZARU_MAX_RATE:
                f.zaru(gyro[k])
            if hde and not prev_zv:
                if last_stance_p is not None:
                    dx, dy = f.p[0] - last_stance_p[0], f.p[1] - last_stance_p[1]
                    if math.hypot(dx, dy) > MIN_STRIDE_M:
                        steps = (steps + [math.atan2(dy, dx)])[-STRAIGHT_STEPS:]
                        if len(steps) == STRAIGHT_STEPS and max(abs(wrap(s - steps[-1])) for s in steps) < STRAIGHT_TOL:
                            dom = min(DOMINANT_DIRS, key=lambda d: abs(wrap(d - steps[-1])))
                            if abs(wrap(dom - steps[-1])) < SNAP_TOL:
                                f.yaw_residual_update(wrap(dom - steps[-1]), HDE_SIGMA)
                                stats["hde_updates"] += 1
                last_stance_p = f.p[:]
            if floor and not prev_zv:
                f.height_update(FLOOR_Z_DOWN, FLOOR_SIGMA)
            if mag and not prev_zv:
                y = wrap(alpha_ref - mag_angle(f.C, mag[k]))
                stats["mag_resid_deg"].append(math.degrees(y))
                stats["mag_norm"].append(math.sqrt(sum(c * c for c in mag[k])))
                if mag_apply:
                    f.yaw_residual_update(y, MAG_SIGMA)
        prev_zv = zv[k]
        if uwb:
            dist_since_fix += math.hypot(f.p[0] - last_p[0], f.p[1] - last_p[1])
            last_p = f.p[:]
        if k in uwb_at and uwb_at[k]:
            if uwb == "inflated":
                f.inflate_horizontal((DRIFT_FRAC * dist_since_fix) ** 2)
            dist_since_fix = 0.0
            for a, r, nlos in uwb_at[k]:
                a_ned = (a[0], a[1], -a[2])
                stats["nlos"] += nlos
                gate = NIS_GATE if uwb in ("gated", "inflated") else None
                nis = f.range_update(a_ned, r, UWB_SIGMA, gate=gate)
                rejected = gate is not None and nis > gate
                stats["uwb_rejected" if rejected else "uwb_used"] += 1
                stats["nlos_rejected"] += nlos and rejected
        if k in tr["gi_set"]:
            out[k] = to_gt(f.p)
            stats["sigma_h"][k] = f.sigma_h()
        if keep_track and k % TRACK_DECIMATE == 0:
            track.append((ts[k], to_gt(f.p), f.sigma_h(), bool(zv[k])))
    return out, stats, track


TRACK_DECIMATE = 40  # ~5 Hz output for the dashboard / CoT
R95_PER_SIGMA = 2.45  # 2D Gaussian 95 % radius / per-axis-equivalent sigma


def align_angle(est1, gt1):
    return math.atan2(gt1[1], gt1[0]) - math.atan2(est1[1], est1[0])


def rotate(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (c * p[0] - s * p[1], s * p[0] + c * p[1], p[2])


def metrics(tr, est, markers=None, sigma_h=None):
    gi, gt = tr["gi"], tr["gt"]
    idx = list(range(len(gi)) if markers is None else markers)
    e3 = [math.dist(est[gi[m]], gt[m]) for m in idx]
    eh = [math.dist(est[gi[m]][:2], gt[m][:2]) for m in range(len(gi))]
    path = sum(math.dist(gt[i][:2], gt[i + 1][:2]) for i in range(len(gt) - 1))
    out = {"armse3d": sum(e3) / len(e3), "armse_h": sum(eh[m] for m in idx) / len(idx),
           "final_h": eh[-1], "final_pct": 100 * eh[-1] / path, "max_h": max(eh), "path_m": path}
    if sigma_h:
        out["r95_cover"] = sum(eh[m] <= R95_PER_SIGMA * sigma_h[gi[m]] for m in idx[1:]) / len(idx[1:])
    return out


def entry_yaw(tr, zv, dt_mode="T200", filt=DEFAULT_FILTER):
    est, _, _ = run(tr, zv, dt_mode=dt_mode, filt=filt, stop=tr["gi"][1])
    return align_angle(est[tr["gi"][1]], tr["gt"][1])


def job(args):
    path, data_dir, tables = args
    trial = os.path.relpath(os.path.dirname(path), data_dir)
    tr = load_trial(path)
    tr["gi_set"] = set(tr["gi"])
    res = {}
    stats_cache = {}

    def zv_for(name, g):
        if name not in stats_cache:
            stats_cache[name] = det_stat(tr, name)
        return detectors.stance(stats_cache[name], g)

    zv = zv_for(*DEFAULT_DET)
    res["zv"] = "".join("1" if z else "0" for z in zv)

    def evaluate(label, zv_, dt_mode="T200", filt=DEFAULT_FILTER, markers=None, **kw):
        yaw0 = entry_yaw(tr, zv_, dt_mode, filt)
        est, st, _ = run(tr, zv_, yaw0=yaw0, dt_mode=dt_mode, filt=filt, rng_seed=zlib.crc32(trial.encode()), **kw)
        m = metrics(tr, est, markers, st.pop("sigma_h"))
        m.update(st)
        res[label] = m

    if "filter" in tables:
        for filt in FILTERS:
            evaluate(filt + "_T200", zv, filt=filt)
        evaluate("pyshoe9_ts", zv, dt_mode="ts", filt="pyshoe9")
        est9, _, _ = run(tr, zv, dt_mode="T200", filt="pyshoe9")
        res["pyshoe9_T200_raw"] = [list(est9[k]) for k in tr["gi"]]
    if "detectors" in tables:
        for name, gs in THRESH.items():
            for g in gs:
                evaluate("det_%s_%g" % (name, g), zv_for(name, g))
    if "aiding" in tables:
        held = list(range(0, len(tr["gi"]), 2))
        for label, kw in AIDING.items():
            evaluate(label, zv, markers=held, **kw)
    print(trial, flush=True, file=sys.stderr)
    return trial, res


def pyshoe_metrics(tr, est_gi):
    gi = tr["gi"]
    est = {gi[m]: est_gi[m] for m in range(len(gi))}
    ang = align_angle(est[gi[1]], tr["gt"][1])
    return metrics(tr, {k: rotate(p, ang) for k, p in est.items()})


def summarize(results, keys, arm="armse3d"):
    groups = ["walk", "run", "comb", "all"]
    print("| config | " + " | ".join(groups) + " | r95 covers error (all) |")
    print("|---|" + "---|" * (len(groups) + 1))
    for key in keys:
        row = [key]
        for g in groups:
            vals = [r[key] for t, r in results.items() if key in r and (g == "all" or t.startswith(g))]
            if not vals:
                row.append("-")
                continue
            a = sum(v[arm] for v in vals) / len(vals)
            fp = sum(v["final_pct"] for v in vals) / len(vals)
            mx = sum(v["max_h"] for v in vals) / len(vals)
            row.append("%.2f / %.2f%% / %.2f" % (a, fp, mx))
        cov = [r[key]["r95_cover"] for r in results.values() if "r95_cover" in r.get(key, {})]
        row.append("%.0f%%" % (100 * sum(cov) / len(cov)) if cov else "-")
        print("| " + " | ".join(row) + " |")
    print("cells: mean %s at markers (m) / mean final horizontal error as %% of the 214.6 m marker path / "
          "mean max horizontal marker error (m)" % ("ARMSE 3D" if arm == "armse3d" else "horizontal ARMSE"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    ap.add_argument("--pyshoe")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--only", default="")
    ap.add_argument("--tables", default="filter,detectors,aiding")
    ap.add_argument("--out", default="results/hallway.json")
    a = ap.parse_args()
    tables = set(a.tables.split(","))
    paths = sorted(p for p in glob.glob(os.path.join(a.data_dir, "*/*/*/processed_data.mat")) if a.only in p)
    with Pool(a.jobs) as pool:
        results = dict(pool.map(job, [(p, a.data_dir, tables) for p in paths]))

    if a.pyshoe and "filter" in tables:
        with open(a.pyshoe) as fh:
            pys = json.load(fh)
        agree, max_gap = [], 0.0
        for p in paths:
            t = os.path.relpath(os.path.dirname(p), a.data_dir)
            if t not in pys:
                continue
            tr = load_trial(p)
            for lab in ("T200", "ts"):
                results[t]["pyshoe_" + lab] = pyshoe_metrics(tr, pys[t][lab])
            z1, z2 = results[t]["zv"], pys[t]["zv"]
            agree.append(sum(x == y for x, y in zip(z1, z2)) / len(z1))
            max_gap = max(max_gap, max(math.dist(u, v) for u, v in zip(pys[t]["T200"], results[t]["pyshoe9_T200_raw"])))
        print("SHOE stance labels identical to pyshoe on %.4f%% of samples (min over trials %.4f%%)"
              % (100 * sum(agree) / len(agree), 100 * min(agree)))
        print("max |stdlib pyshoe9_T200 - pyshoe_T200| at any marker, unaligned: %.2e m" % max_gap)

    for r in results.values():
        r.pop("zv", None)
        r.pop("pyshoe9_T200_raw", None)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(results, fh, indent=1)

    if "filter" in tables:
        print("\n## Filter comparison (SHOE G=8.5e7 W=5)")
        summarize(results, ["pyshoe_T200", "pyshoe_ts", "pyshoe9_ts"] + [f + "_T200" for f in FILTERS])
    if "detectors" in tables:
        print("\n## Detectors (%s, nominal 200 Hz)" % DEFAULT_FILTER)
        summarize(results, ["det_%s_%g" % (n, g) for n, gs in THRESH.items() for g in gs])
    if "aiding" in tables:
        print("\n## Aiding (ARMSE on even markers only; UWB ranges at odd markers)")
        summarize(results, list(AIDING), arm="armse_h")
        for key in ("aid_floor_uwb_gated", "aid_floor_uwb_inflated"):
            u = [r[key] for r in results.values()]
            print("%s: %d ranges used, %d rejected; %d of %d NLOS ranges rejected" % (
                key, sum(x["uwb_used"] for x in u), sum(x["uwb_rejected"] for x in u),
                sum(x["nlos_rejected"] for x in u), sum(x["nlos"] for x in u)))


if __name__ == "__main__":
    main()
