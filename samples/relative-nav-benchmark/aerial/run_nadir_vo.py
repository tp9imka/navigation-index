"""Part 3: frame-to-frame nadir VO on VPAIR (light aircraft, > 300 m AGL, downward camera).

Each consecutive pair gives a 2D similarity (SIFT + RANSAC) and so the displacement of the
image-centre ground point in pixels. Two ways to turn that into East/North metres:

- image only: chain the similarity rotations (and optionally scales) into frame-0 pixels, then
  one 2x2 similarity (heading + m/px) fitted on the first CALIB_STEPS steps;
- attitude-aided: rotate each step by the recorded yaw and remove the image shift caused by the
  roll/pitch change (AGL * delta tan(angle)); the mount rotation, m/px, axis mapping and one
  effective AGL are fitted on the same calibration window (3 linear unknowns per mapping).

After the calibration window both run open loop. VPAIR ships no intrinsics or AGL, so metric
scale cannot come from an altimeter here; the calibration window stands in for "known start
heading + altimeter-derived GSD". Attitude is the recorded 6-DoF pose (an idealised AHRS).

Usage: python aerial/run_nadir_vo.py --data <dir containing vpair_sample/>
"""
import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
CALIB_STEPS = 10
WORK_WIDTH = 800
RATIO = 0.75
MIN_INLIERS = 25
FRAME_DT = 1.0  # VPAIR gives no timestamps; one synthetic second per frame for the TUM/evo tooling


def ecef_to_lla(x, y, z):
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    b = a * (1 - f)
    ep2 = (a * a - b * b) / (b * b)
    p = math.hypot(x, y)
    th = math.atan2(z * a, p * b)
    lon = math.atan2(y, x)
    lat = math.atan2(z + ep2 * b * math.sin(th) ** 3, p - e2 * a * math.cos(th) ** 3)
    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return math.degrees(lat), math.degrees(lon), p / math.cos(lat) - n


def similarity(img1, img2, sift, matcher):
    k1, d1 = sift.detectAndCompute(img1, None)
    k2, d2 = sift.detectAndCompute(img2, None)
    if d1 is None or d2 is None:
        return None, 0
    m = [a for a, b in matcher.knnMatch(d1, d2, k=2) if a.distance < RATIO * b.distance]
    if len(m) < MIN_INLIERS:
        return None, len(m)
    p1 = np.float32([k1[x.queryIdx].pt for x in m])
    p2 = np.float32([k2[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    n = int(inl.sum()) if inl is not None else 0
    return (M if n >= MIN_INLIERS else None), n


def fit_similarity_2d(src, dst):
    """dst ~ C @ src with C = scale * orthogonal (reflection allowed: image y points down)."""
    U, S, Vt = np.linalg.svd(dst.T @ src)
    R = U @ Vt
    s = S.sum() / np.sum(src ** 2)
    return s * R


def r_yaw(psi):
    """(forward, right) body vector => (East, North) for NED yaw psi."""
    return np.array([[math.sin(psi), math.cos(psi)], [math.cos(psi), -math.sin(psi)]])


def signed_perms():
    out = []
    for swap in (False, True):
        for s1 in (1, -1):
            for s2 in (1, -1):
                P = np.array([[0, 1], [1, 0]]) if swap else np.eye(2)
                out.append(P * np.array([[s1], [s2]]))
    return out


def fit_attitude_model(d, dtan, body_gt):
    """body_step = C d + h P dtan; C rotation or reflection scaled, P signed axis permutation."""
    best = None
    for refl in (False, True):
        for P in signed_perms():
            X = np.zeros((2 * len(d), 3))
            for k, ((dx, dy), q) in enumerate(zip(d, dtan @ P.T)):
                X[2 * k], X[2 * k + 1] = ([dx, dy, q[0]], [-dy, dx, q[1]]) if refl else ([dx, -dy, q[0]], [dy, dx, q[1]])
            y = body_gt.reshape(-1)
            p = np.linalg.lstsq(X, y, rcond=None)[0]
            r = float(np.linalg.norm(X @ p - y))
            if best is None or r < best[0]:
                a, b, h = p
                C = np.array([[a, b], [b, -a]]) if refl else np.array([[a, -b], [b, a]])
                best = (r, C, h, P, refl)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--calib-steps", type=int, default=CALIB_STEPS)
    a = ap.parse_args()
    N = a.calib_steps
    root = Path(a.data) / "vpair_sample"
    rows = [l.strip().split(",") for l in open(root / "poses_query.txt") if l.strip()][1:]
    names = [Path(r[0]).name for r in rows]
    lla = [ecef_to_lla(*map(float, r[1:4])) for r in rows]
    att = np.array([[float(x) for x in r[5:8]] for r in rows])  # roll, pitch, yaw (rad, NED)
    lat0, lon0, _ = lla[0]
    en = np.array([common.ll_to_enu(lat0, lon0, la, lo) for la, lo, _ in lla])

    stats = common.RunStats()
    sift = cv2.SIFT_create(nfeatures=3000)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    load = lambda n: cv2.cvtColor(cv2.imread(str(root / "queries" / n)), cv2.COLOR_BGR2GRAY)
    prev = load(names[0])
    h, w = prev.shape
    c = np.array([w / 2, h / 2])
    L, L_rot = np.eye(2), np.eye(2)
    d_raw, steps_px, steps_px_const, scales, inliers, failed = [], [], [], [], [], 0
    for k in range(1, len(names)):
        cur = load(names[k])
        M, n = similarity(prev, cur, sift, matcher)
        inliers.append(n)
        if M is None:
            failed += 1
            M = np.hstack([np.eye(2), np.zeros((2, 1))])  # no motion: worst case for a real system
        A, t = M[:, :2], M[:, 2]
        d = np.linalg.solve(A, c - t) - c          # image-centre ground point motion, frame-k pixels
        d_raw.append(d)
        steps_px.append(L @ d)
        steps_px_const.append(L_rot @ d)
        s = math.sqrt(abs(np.linalg.det(A)))
        scales.append(s)
        L = L @ np.linalg.inv(A)
        L_rot = L_rot @ (np.linalg.inv(A) * s)
        prev = cur
    d_raw, steps_px, steps_px_const = map(np.array, (d_raw, steps_px, steps_px_const))
    vo_time = stats.done()
    gt_steps = np.diff(en, axis=0)
    dist = np.concatenate([[0], np.cumsum(np.linalg.norm(gt_steps, axis=1))])
    out = {"part": "aerial", "dataset": f"VPAIR sample (Zenodo 6473989): {len(names)} consecutive nadir frames, {w}x{h}",
           "method": "SIFT + RANSAC 2D similarity frame-to-frame; calibrated on the first "
                     f"{N} steps ({dist[N]:.0f} m) against GT, then open loop",
           "gt": {"source": "poses_query.txt (ECEF position + roll/pitch/yaw; GNSS-based per README)",
                  "path_m": float(dist[-1]),
                  "ellipsoid_height_m": [round(min(x[2] for x in lla), 1), round(max(x[2] for x in lla), 1)],
                  "roll_std_deg": round(float(np.degrees(att[:, 0].std())), 2),
                  "pitch_std_deg": round(float(np.degrees(att[:, 1].std())), 2),
                  "mean_step_m": float(np.mean(np.linalg.norm(gt_steps, axis=1)))},
           "pairs": len(d_raw), "failed_pairs": failed, "median_inliers": int(np.median(inliers)),
           "interframe_scale_range": [round(min(scales), 4), round(max(scales), 4)]}

    tracks = {}
    for label, px in (("image_only_gsd_from_image_scale", steps_px), ("image_only_constant_gsd", steps_px_const)):
        C = fit_similarity_2d(px[:N], gt_steps[:N])
        tracks[label] = (px @ C.T, {"m_per_px": round(float(np.sqrt(abs(np.linalg.det(C)))), 4)})
    dtan = np.diff(np.tan(att[:, :2]), axis=0)
    body_gt = np.array([r_yaw(att[k, 2]).T @ gt_steps[k] for k in range(len(gt_steps))])
    r, C, hagl, P, refl = fit_attitude_model(d_raw[:N], dtan[:N], body_gt[:N])
    for bias in (0.0, 2.0, 5.0):
        st = np.array([r_yaw(att[k, 2] + math.radians(bias)) @ (C @ d_raw[k] + hagl * (P @ dtan[k])) for k in range(len(d_raw))])
        tracks[f"attitude_aided_yaw_bias_{bias:g}deg"] = (st, {"m_per_px": round(float(np.sqrt(abs(np.linalg.det(C)))), 4),
                                                               "fitted_effective_agl_m": round(abs(float(hagl)), 1),
                                                               "mount_reflection": refl})

    stamps = np.arange(len(names)) * FRAME_DT
    to_T = lambda xy: [np.block([[np.eye(2), np.zeros((2, 1)), np.array([[x], [y]])], [np.zeros((2, 2)), np.eye(2)]]) for x, y in xy]
    res_dir = HERE / "results" / "aerial"
    res_dir.mkdir(parents=True, exist_ok=True)
    common.write_tum(res_dir / "vpair_gt.tum", stamps, to_T(en))
    variants, worlds = {}, {}
    for label, (st, info) in tracks.items():
        world = np.vstack([[0, 0], np.cumsum(st, axis=0)])
        worlds[label] = world
        ratio = np.linalg.norm(st, axis=1) / np.linalg.norm(gt_steps, axis=1)
        dirn = np.degrees(np.arctan2(st[:, 1], st[:, 0]) - np.arctan2(gt_steps[:, 1], gt_steps[:, 0]))
        dirn = (dirn + 180) % 360 - 180
        p = res_dir / f"vpair_{label}.tum"
        common.write_tum(p, stamps, to_T(world))
        err = np.linalg.norm(world - en, axis=1)
        variants[label] = info | {
            "final_error_m": round(float(err[-1]), 1),
            "final_drift_pct_of_distance": round(100 * float(err[-1]) / dist[-1], 2),
            "max_error_m": round(float(err.max()), 1),
            "error_at_distance_m": {f"{int(x)}m": round(float(err[np.searchsorted(dist, x)]), 1)
                                    for x in (1000, 2000, 4000, 6000, 8000) if x < dist[-1]},
            "per_step": {"length_ratio_median": round(float(np.median(ratio)), 3),
                         "length_ratio_p5_p95": [round(float(x), 3) for x in np.percentile(ratio, [5, 95])],
                         "direction_err_deg_median": round(float(np.median(dirn)), 2),
                         "direction_err_deg_std": round(float(np.std(dirn)), 2)},
            "evo_ate_se3_rmse_m": round(common.evo_metrics(str(res_dir / "vpair_gt.tum"), str(p), max_diff=0.01)["ate_aligned"]["rmse_m"], 1)}
    out["variants"] = variants
    out["run"] = vo_time | {"frames": len(names), "note": "wall/cpu cover image loading + SIFT + RANSAC"}
    primary = "attitude_aided_yaw_bias_0deg"
    (res_dir / "vpair_nadir_vo.tum").write_text((res_dir / f"vpair_{primary}.tum").read_text())

    nd = HERE / "results" / "navdash" / "vpair"
    common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "VPAIR query poses (GNSS)",
                         [{"t": float(t), "lat": la, "lon": lo} for t, (la, lo, _) in zip(stamps, lla)])
    ev = [{"t": N * FRAME_DT, "event": "source_switched", "text": "calibration window ends; open-loop nadir VO"}]
    for label, fn, role, color, prim, txt in ((primary, "nadir_vo_attitude.jsonl", "fused", "#4fc3f7", True, "Nadir VO + recorded attitude"),
                                             ("image_only_constant_gsd", "nadir_vo_image_only.jsonl", "ins", "#ffb74d", False, "Nadir VO, image only")):
        vo_rows = []
        for t, (e, nn) in zip(stamps, worlds[label]):
            la, lo = common.enu_to_ll(lat0, lon0, e, nn)
            vo_rows.append({"t": float(t), "lat": la, "lon": lo, "sources": ["nadir-vo"],
                            "health": "calibrating" if t < N * FRAME_DT else "open-loop"})
        common.write_navdash(str(nd / fn), label.replace("_", "-"), role, txt, vo_rows, color=color, primary=prim,
                             extra={"run_meta": {"time": "frame index, 1 s per frame (VPAIR has no timestamps)"}},
                             events=ev if prim else ())
    common.write_manifest(str(nd / "manifest.json"), "VPAIR sample: nadir VO at > 300 m AGL",
                          ["truth.jsonl", "nadir_vo_attitude.jsonl", "nadir_vo_image_only.jsonl"])
    (res_dir / "vpair_result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
