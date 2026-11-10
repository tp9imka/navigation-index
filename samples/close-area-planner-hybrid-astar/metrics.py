"""Path shape and time metrics, the same for every planner (numpy only).

heading_stats(xy): resample the polyline every DS_SHAPE m of arc length, take the heading of each
  piece and |heading change| / DS_SHAPE at each joint (rad/m). Returns max, p95, the share of path
  length where it exceeds KAPPA_CRUISE (= 1.0 rad/s / 1.5 m/s: above it a vehicle with a 1 rad/s
  turn-rate limit must slow below cruise) and the total turning (rad).
time_along(xy, omega): minimum time to fly the polyline from rest to rest with |v| <= V_MAX,
  |a_lon| <= A_LON, lateral v^2 k <= A_LAT and, when omega is given, turn rate v k <= omega.
  Curvature per DS_TIME sample = |heading change| / DS_TIME, so a polyline corner of angle d costs
  at least d / omega s. Forward and backward passes, then t = sum 2 ds / (v_i + v_i+1).
"""
from __future__ import annotations

import math

import numpy as np

DS_SHAPE = 0.25         # m
DS_TIME = 0.1           # m
V_MAX = 1.5             # m/s, astar_esdf cruise (both planners cap there)
A_LON = 3.0             # m/s^2, arena a_max
A_LAT = 3.0             # m/s^2, arena a_max
KAPPA_CRUISE = 1.0 / 1.5   # rad/m


def resample(xy, ds):
    xy = np.asarray(xy, float)
    seg = np.hypot(*np.diff(xy, axis=0).T)
    keep = np.concatenate([[True], seg > 1e-9])
    xy = xy[keep]
    if len(xy) < 2:
        return xy
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
    n = max(2, int(s[-1] / ds) + 1)
    q = np.linspace(0.0, s[-1], n)
    return np.column_stack([np.interp(q, s, xy[:, 0]), np.interp(q, s, xy[:, 1])])


def _turns(xy, ds):
    r = resample(xy, ds)
    if len(r) < 3:
        return r, np.zeros(0), ds
    d = np.diff(r, axis=0)
    step = float(np.hypot(*d.T).mean())
    h = np.arctan2(d[:, 1], d[:, 0])
    dh = np.abs((np.diff(h) + math.pi) % (2 * math.pi) - math.pi)
    return r, dh, step


def heading_stats(xy) -> dict:
    _, dh, step = _turns(xy, DS_SHAPE)
    if not len(dh):
        return {"max_rad_per_m": 0.0, "p95_rad_per_m": 0.0, "share_above_cruise_kappa": 0.0, "total_turn_rad": 0.0}
    rate = dh / step
    return {"max_rad_per_m": round(float(rate.max()), 3),
            "p95_rad_per_m": round(float(np.percentile(rate, 95)), 3),
            "share_above_cruise_kappa": round(float((rate > KAPPA_CRUISE).mean()), 4),
            "total_turn_rad": round(float(dh.sum()), 3)}


def time_along(xy, omega=None) -> float:
    r, dh, step = _turns(xy, DS_TIME)
    if len(r) < 2:
        return 0.0
    n = len(r)
    v = np.full(n, V_MAX)
    k = dh / step                                     # curvature at interior points 1..n-2
    with np.errstate(divide="ignore"):
        lat = np.sqrt(A_LAT / k)
        v[1:-1] = np.minimum(v[1:-1], lat)
        if omega is not None:
            v[1:-1] = np.minimum(v[1:-1], omega / k)
    v[0] = v[-1] = 0.0
    for i in range(1, n):
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * A_LON * step))
    for i in range(n - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * A_LON * step))
    return float(np.sum(2 * step / np.maximum(v[:-1] + v[1:], 1e-9)))
