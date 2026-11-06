"""Geometry, multi-frame voting and scoring for the VPAIR end-to-end chain. numpy only.

Frames are 1 s apart (VPAIR ships no timestamps; same convention as ../relative-nav-benchmark).
Positions are local East/North metres from the first query.
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RELNAV = HERE.parent / "relative-nav-benchmark"
sys.path.insert(0, str(RELNAV))
sys.path.insert(0, str(RELNAV / "aerial"))
import common  # noqa: E402
from run_nadir_vo import ecef_to_lla, r_yaw  # noqa: E402

FRAME_DT = 1.0
CALIB_FRAMES = 10            # GNSS still available: VO model, tile scale and fix R are fitted here
FALSE_FIX_M = 50.0           # a fix this far from truth counts as false (= the altpnt alert limit)
DIST_MARKS_M = (1000, 2000, 4000, 6000, 8000)


def load_poses(root):
    """root contains poses_query.txt and poses_reference_view.txt."""
    root = Path(root)
    q = [l.strip().split(",") for l in open(root / "poses_query.txt") if l.strip()][1:]
    r = [l.strip().split(",") for l in open(root / "poses_reference_view.txt") if l.strip()][1:]
    lla = [ecef_to_lla(*map(float, x[1:4])) for x in q]
    lat0, lon0 = lla[0][0], lla[0][1]
    en = np.array([common.ll_to_enu(lat0, lon0, la, lo) for la, lo, _ in lla])
    tile_lla = [ecef_to_lla(*map(float, x[1:4])) for x in r]
    tile_en = np.array([common.ll_to_enu(lat0, lon0, la, lo) for la, lo, _ in tile_lla])
    att = np.array([[float(v) for v in x[5:8]] for x in q])
    return {"names": [Path(x[0]).name for x in q], "tile_names": [Path(x[0]).name for x in r],
            "en": en, "tile_en": tile_en, "att": att, "lat0": lat0, "lon0": lon0,
            "tile_att": np.array([[float(v) for v in x[5:8]] for x in r])}


def distance_along(en):
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(en, axis=0), axis=1))])


def map_tiles(n_tiles, stride):
    """Indices of reference renders kept in the map. The query's own render is excluded per query."""
    return [j for j in range(n_tiles) if j % stride == 0]


def nadir_offset(att_k, yaw_bias_rad, hagl, P):
    """Aircraft position minus the ground point at the image centre, East/North metres.

    Same model as the attitude-aided VO: body offset = hagl * P tan(roll, pitch), rotated by yaw."""
    return r_yaw(att_k[2] + yaw_bias_rad) @ (hagl * (P @ np.tan(att_k[:2])))


def fit_tile_scale(px_depth, en_offset):
    """en_offset ~ T @ px_depth with T = s * orthogonal (reflection allowed). px_depth = depth * (p - c)."""
    U, S, Vt = np.linalg.svd(en_offset.T @ px_depth)
    R = U @ Vt
    return S.sum() / np.sum(px_depth ** 2) * R


def fix_position(tile_en, T, depth, p_tile, c_tile, nadir_off):
    """Aircraft E/N from the tile pixel that the query image centre lands on."""
    return tile_en + T @ (depth * (np.asarray(p_tile) - np.asarray(c_tile))) + nadir_off


def single_frame_fix(cands):
    """Best candidate of one frame by inliers, or None. cands: list of dicts with 'pos', 'inliers'."""
    ok = [c for c in cands if c["pos"] is not None]
    return max(ok, key=lambda c: c["inliers"]) if ok else None


def vote(cands_by_frame, vo_pos, k, window, radius_m, min_support):
    """Multi-frame voting at frame k.

    Every gated candidate of frames k-window..k is moved to frame k with the VO displacement
    vo_pos[k] - vo_pos[s] (short window, so VO drift is small). Candidates within radius_m of
    each other vote for the same place; a frame contributes at most one vote (its best agreeing
    candidate, weighted by sqrt(inliers)). The winning cluster needs votes from min_support
    distinct frames including frame k. Returns (position, support, weight) or None."""
    pts = []
    for s in range(max(0, k - window), k + 1):
        for c in cands_by_frame.get(s, ()):
            if c["pos"] is not None:
                pts.append((s, np.asarray(c["pos"]) + vo_pos[k] - vo_pos[s], math.sqrt(c["inliers"])))
    best = None
    for s0, p0, _ in pts:
        if s0 != k:
            continue
        frames = {}
        for s, p, w in pts:
            if np.linalg.norm(p - p0) <= radius_m:
                frames[s] = max(frames.get(s, (0.0, None)), (w, tuple(p)), key=lambda x: x[0])
        if len(frames) < min_support:
            continue
        wsum = sum(w for w, _ in frames.values())
        # the fix is frame k's own candidate; older frames only confirm it, so VO drift is not fused twice
        if best is None or wsum > best[2]:
            best = (p0, len(frames), wsum)
    return best


def error_profile(est, truth, dist, start):
    """Horizontal error after the calibration window: final, max, RMS and at fixed distances."""
    err = np.linalg.norm(est - truth, axis=1)
    e = err[start:]
    out = {"final_m": round(float(err[-1]), 1), "max_m": round(float(e.max()), 1),
           "rms_m": round(float(np.sqrt(np.mean(e ** 2))), 1), "median_m": round(float(np.median(e)), 1),
           "final_pct_of_distance": round(100 * float(err[-1]) / float(dist[-1] - dist[start]), 2)}
    out["at_distance_m"] = {f"{x}": round(float(err[min(np.searchsorted(dist - dist[start], x), len(err) - 1)]), 1)
                            for x in DIST_MARKS_M if x < dist[-1] - dist[start]}
    return out, err
