"""Arm (e): velocity-obstacle gate on the A* carrot follower.

Planner  astar_replan.AStarReplan unchanged (prior map + latest scan hits, 2.5-5 Hz replans,
         carrot follower at 10 Hz). Its velocity setpoint u0 is the nominal command.
Tracks   predict.Tracker on the same scan (confirmed tracks, constant velocity v_j).
Cone     for track j at relative position p_j = c_j - p and combined radius
         R_j = r_j + RADIUS + VO_MARGIN, a velocity u is inside the truncated velocity obstacle
         when the relative ray (u - v_j) t enters the disc |x - p_j| <= R_j for some
         t in [0, T_H] (T_H = predict.HORIZON_S = 3 s). Inside the disc already: u is inside
         the VO when it closes on the person ((u - v_j) . p_j > 0). numpy over all candidates x
         tracks at once. Turn-around hedge: a second cone per track treats the person as
         standing at c_j with radius R_j + s_j * REACH_S (s_j = peak-held track speed), truncated at REACH_S, so the vehicle
         does not commit to passing close in front of a person who may reverse.
Gate     u0 outside every VO => passed through unchanged. Otherwise pick, from N_DIRS
         directions x SPEEDS (hover included) plus u0, the VO-free candidate closest to u0
         whose straight run for STATIC_LOOK_S keeps the prior static ESDF above
         RADIUS + STATIC_MARGIN. If no candidate is VO-free, take the one with the latest time
         to contact. Velocity only; yaw rate is passed through.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from . import arena, astar_replan, predict
except ImportError:
    import arena
    import astar_replan
    import predict

A = arena.astar_esdf
VO_MARGIN = 0.3          # m, extra space around the person (tuned on seed 0 only)
T_H = predict.HORIZON_S  # s, VO truncation = prediction horizon
N_DIRS = 32
SPEEDS = (0.0, 0.3, 0.6, 0.9, 1.2, 1.5)    # m/s; 1.5 = astar_esdf V_CRUISE
STATIC_LOOK_S = 1.0      # s, straight-run static check per candidate
STATIC_MARGIN = 0.05     # m, beyond RADIUS
REACH_S = 1.0            # s, turn-around hedge (tuned on seed 0 only)


def time_to_contact(u: np.ndarray, rel_p: np.ndarray, v_obs: np.ndarray, R: np.ndarray) -> np.ndarray:
    """(n_cand, n_obs) first contact time of relative motion (u - v_obs) t with discs at rel_p.
    0 when already inside and closing, inf when no contact (or inside and opening)."""
    w = u[:, None, :] - v_obs[None, :, :]                     # (n, m, 2)
    p = rel_p[None, :, :]
    a = (w * w).sum(-1)
    b = -2.0 * (w * p).sum(-1)
    c = (p * p).sum(-1) - R[None, :] ** 2
    disc = b * b - 4 * a * c
    sq = np.sqrt(np.maximum(disc, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = (-b - sq) / (2 * a)
    hit = (disc >= 0) & (a > 1e-12) & (t1 >= 0)
    ttc = np.where(hit, t1, np.inf)
    inside = c <= 0
    closing = (w * p).sum(-1) > 0
    return np.where(inside, np.where(closing, 0.0, np.inf), ttc)


class VOGate(arena.Planner):
    name = "astar_vo"
    uses_grid = True

    def __init__(self, vo_margin: float = VO_MARGIN, reach_s: float = REACH_S, **kw):
        self.inner = astar_replan.make(**kw)
        self.vo_margin, self.reach_s = vo_margin, reach_s
        self.reset()

    def reset(self) -> None:
        self.inner.reset()
        self.tracker = None
        self.n_steps = self.n_gated = self.n_no_free = 0

    @property
    def replan_t(self):
        return self.inner.replan_t

    def _cands(self, u0):
        ang = np.arange(N_DIRS) * (2 * math.pi / N_DIRS)
        c = [np.zeros((1, 2))] + [s * np.column_stack([np.cos(ang), np.sin(ang)]) for s in SPEEDS if s > 0]
        return np.vstack([u0[None, :]] + c)

    def _static_ok(self, p, cand, grid):
        esdf = self.tracker.esdf
        nx, ny = esdf.shape
        ok = np.ones(len(cand), bool)
        for t in np.linspace(0.25, STATIC_LOOK_S, 4):
            q = p[None, :] + cand * t
            ix = np.clip(np.floor((q[:, 0] - grid.x0) / grid.res).astype(int), 0, nx - 1)
            iy = np.clip(np.floor((q[:, 1] - grid.y0) / grid.res).astype(int), 0, ny - 1)
            ok &= esdf[ix, iy] > A.RADIUS + STATIC_MARGIN
        return ok

    def step(self, pose, scan, goal, grid, dt):
        if self.tracker is None:
            self.tracker = predict.Tracker(grid)
        tracks = self.tracker.update(pose, scan)
        sp = self.inner.step(pose, scan, goal, grid, dt)
        self.n_steps += 1
        if not tracks:
            return sp
        p = np.array([pose.x, pose.y])
        rel = np.array([tr.p - p for tr in tracks])
        vel = np.array([tr.v for tr in tracks])
        R = np.array([float(tr.radius(0.0)) + A.RADIUS + self.vo_margin for tr in tracks])
        Rh = R + np.array([max(tr.s_peak, math.hypot(*tr.v)) for tr in tracks]) * self.reach_s
        zero = np.zeros_like(vel)

        def ttc_of(u):
            t_cv = time_to_contact(u, rel, vel, R).min(axis=1)
            if self.reach_s <= 0:
                return t_cv
            t_h = time_to_contact(u, rel, zero, Rh).min(axis=1)
            return np.minimum(t_cv, np.where(t_h <= self.reach_s, t_h, np.inf))

        u0 = np.array([sp.vx, sp.vy])
        if ttc_of(u0[None, :])[0] > T_H:
            return sp
        self.n_gated += 1
        cand = self._cands(u0)
        ttc = ttc_of(cand)
        ok = self._static_ok(p, cand, grid)
        ok[1] = True                                      # hover is always statically allowed
        dev = np.hypot(*(cand - u0[None, :]).T)
        free = ok & (ttc > T_H)
        if free.any():
            i = int(np.flatnonzero(free)[np.argmin(dev[free])])
        else:
            self.n_no_free += 1
            idx = np.flatnonzero(ok)
            i = int(idx[np.lexsort((dev[idx], -ttc[idx]))[0]])
        return arena.Setpoint(float(cand[i, 0]), float(cand[i, 1]), 0.0, sp.yaw_rate)


def make(**kw) -> VOGate:
    return VOGate(**kw)
