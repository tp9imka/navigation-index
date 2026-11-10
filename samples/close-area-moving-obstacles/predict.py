"""Constant-velocity predictor for range returns the prior map does not explain.

Pipeline, run once per planner step (10 Hz) on the latest RangeScan:

  1. explain  a hit is explained when the prior static map's ESDF at the hit cell is at most
              EXPLAIN_M (the hit lies on a mapped surface, within noise and one cell). Hits
              outside the grid are explained (arena boundary).
  2. cluster  unexplained hits, single linkage with CLUSTER_GAP_M (scipy connected components).
  3. centre   the fan sees the near side of a person, so the cluster centroid is pushed
              CENTRE_SHIFT * R_ASSUMED away from the sensor. R_ASSUMED is a person-size prior,
              not the simulator's radius read from truth.
  4. track    greedy nearest-neighbour association within GATE_M of each track's predicted
              position, then an alpha-beta filter (ALPHA, BETA). A track is confirmed after
              CONFIRM_HITS hits and dropped after DROP_S without a hit. Speed is capped at
              V_CAP (person walking or jogging).
  5. predict  constant velocity: p(t + tau) = p + v * min(tau, HORIZON_S). Beyond the 3 s
              horizon the track is held at its 3 s point. Uncertainty grows with tau:
              radius(tau) = R_ASSUMED + GROW_MPS * min(tau, HORIZON_S).

The tracker never reads truth. The sim people walk straight segments at constant speed with an
instant U-turn at each end; that is the motion model a constant-velocity predictor assumes, so
this setup favours it. Real people stop, turn and react to the drone.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

EXPLAIN_M = 0.15        # m, prior ESDF at or below this explains a hit (0.1 m cell + 0.02 m noise)
CLUSTER_GAP_M = 0.4     # m, single-linkage gap (5 deg beams are 0.35 m apart at 4 m)
R_ASSUMED = 0.25        # m, person radius prior (shoulder width about 0.5 m)
CENTRE_SHIFT = 0.7      # x R_ASSUMED, centroid => centre shift away from the sensor
GATE_M = 0.7            # m, association gate around the predicted track position
ALPHA, BETA = 0.5, 0.1  # alpha-beta gains at the 10 Hz scan rate (tuned on seed 0 only)
CONFIRM_HITS = 3        # hits before a track is used for prediction
DROP_S = 0.6            # s without a hit => track dropped
V_CAP = 2.5             # m/s, speed cap on a track
HORIZON_S = 3.0         # s, constant-velocity extrapolation horizon
GROW_MPS = 0.1          # m/s, footprint radius growth with prediction time
PEAK_DECAY = 0.2        # m/s per s, decay of the peak-held track speed used by the turn-around hedge


def prior_esdf(grid) -> np.ndarray:
    padded = np.pad(grid.occ, 1, constant_values=True)
    return (distance_transform_edt(~padded) * grid.res)[1:-1, 1:-1]


def scan_world(pose, scan):
    """World-frame (n, 2) hit points and the (n,) beam indices of finite returns."""
    a = pose.yaw + np.asarray(scan.angles, float)
    d = np.asarray(scan.distances, float)
    ok = np.flatnonzero(np.isfinite(d))
    pts = np.column_stack([pose.x + d[ok] * np.cos(a[ok]), pose.y + d[ok] * np.sin(a[ok])])
    return pts, ok


def unexplained(pts: np.ndarray, grid, esdf: np.ndarray) -> np.ndarray:
    """Boolean mask over pts: True when the prior map does not explain the hit."""
    if not len(pts):
        return np.zeros(0, bool)
    ix = np.floor((pts[:, 0] - grid.x0) / grid.res).astype(int)
    iy = np.floor((pts[:, 1] - grid.y0) / grid.res).astype(int)
    nx, ny = esdf.shape
    inside = (ix >= 0) & (iy >= 0) & (ix < nx) & (iy < ny)
    out = np.zeros(len(pts), bool)
    out[inside] = esdf[ix[inside], iy[inside]] > EXPLAIN_M
    return out


def cluster(pts: np.ndarray) -> list[np.ndarray]:
    """Single-linkage clusters of pts (index arrays)."""
    n = len(pts)
    if n == 0:
        return []
    if n == 1:
        return [np.array([0])]
    d = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
    i, j = np.nonzero(np.triu(d <= CLUSTER_GAP_M, 1))
    g = coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n))
    k, lab = connected_components(g, directed=False)
    return [np.flatnonzero(lab == c) for c in range(k)]


@dataclass
class Track:
    tid: int
    p: np.ndarray
    v: np.ndarray
    t: float
    last_hit_t: float
    hits: int = 1
    s_peak: float = 0.0  # m/s, peak-held speed: does not dip when the person U-turns
    beams: np.ndarray = field(default_factory=lambda: np.zeros(0, int))   # beam indices in the latest scan

    @property
    def confirmed(self) -> bool:
        return self.hits >= CONFIRM_HITS

    def at(self, tau):
        """Predicted centre(s) tau s after the track time. tau: float or array."""
        tau = np.minimum(np.asarray(tau, float), HORIZON_S)
        return self.p[None, :] + tau[..., None] * self.v[None, :] if tau.ndim else self.p + tau * self.v

    @staticmethod
    def radius(tau):
        return R_ASSUMED + GROW_MPS * np.minimum(np.asarray(tau, float), HORIZON_S)

    def reach_radius(self, tau, reach_s: float):
        """Turn-around hedge: radius of the disc around the CURRENT centre the person can reach in
        tau s at its peak-held speed, in any direction (None after reach_s). Added because the
        constant-velocity guess is worst right after a U-turn (INTEGRATION_predict.md)."""
        if tau > reach_s + 1e-9:
            return None
        return R_ASSUMED + max(self.s_peak, math.hypot(*self.v)) * tau


class Tracker:
    """Alpha-beta tracks of unexplained range clusters. Feed every scan with update()."""

    def __init__(self, grid):
        self.grid = grid
        self.esdf = prior_esdf(grid)
        self.tracks: list[Track] = []
        self.next_id = 0
        self.t = None
        self.unexplained_beams = np.zeros(0, int)    # beam indices of unexplained hits, latest scan
        self.log: list[list] = []                     # [t, tid, x, y, vx, vy] of confirmed tracks

    def update(self, pose, scan) -> list[Track]:
        t = float(pose.t)
        pts, beam = scan_world(pose, scan)
        m = unexplained(pts, self.grid, self.esdf)
        pts, beam = pts[m], beam[m]
        self.unexplained_beams = beam
        centres, members = [], []
        for idx in cluster(pts):
            c = pts[idx].mean(axis=0)
            away = c - np.array([pose.x, pose.y])
            n = math.hypot(*away)
            if n > 1e-6:
                c = c + away / n * CENTRE_SHIFT * R_ASSUMED
            centres.append(c)
            members.append(beam[idx])
        # predict every track to t
        for tr in self.tracks:
            dt = t - tr.t
            tr.p = tr.p + tr.v * dt
            tr.t = t
            tr.beams = np.zeros(0, int)
        # greedy nearest-neighbour association
        pairs = sorted((math.hypot(*(c - tr.p)), i, j) for i, tr in enumerate(self.tracks)
                       for j, c in enumerate(centres))
        used_t, used_c = set(), set()
        for d, i, j in pairs:
            if d > GATE_M or i in used_t or j in used_c:
                continue
            used_t.add(i)
            used_c.add(j)
            tr = self.tracks[i]
            dt = max(t - tr.last_hit_t, 1e-3)          # coasted steps count in the velocity gain
            r = centres[j] - tr.p
            tr.p = tr.p + ALPHA * r
            tr.v = tr.v + (BETA / dt) * r
            sp = math.hypot(*tr.v)
            if sp > V_CAP:
                tr.v = tr.v * (V_CAP / sp)
            tr.s_peak = max(math.hypot(*tr.v), tr.s_peak - PEAK_DECAY * dt)
            tr.hits += 1
            tr.last_hit_t = t
            tr.beams = members[j]
        self.tracks = [tr for tr in self.tracks if t - tr.last_hit_t <= DROP_S + 1e-9]
        for j, c in enumerate(centres):
            if j not in used_c:
                self.tracks.append(Track(self.next_id, c.copy(), np.zeros(2), t, t, beams=members[j]))
                self.next_id += 1
        self.t = t
        for tr in self.tracks:
            if tr.confirmed:
                self.log.append([round(t, 2), tr.tid, round(float(tr.p[0]), 3), round(float(tr.p[1]), 3),
                                 round(float(tr.v[0]), 3), round(float(tr.v[1]), 3)])
        return self.confirmed()

    def confirmed(self) -> list[Track]:
        return [tr for tr in self.tracks if tr.confirmed]

    def confirmed_beams(self) -> np.ndarray:
        """Beam indices (latest scan) that belong to confirmed tracks."""
        b = [tr.beams for tr in self.tracks if tr.confirmed and len(tr.beams)]
        return np.concatenate(b) if b else np.zeros(0, int)
