"""MPPI (Model Predictive Path Integral control) for the close-area arena, numpy only.

Information-theoretic MPPI (Williams et al., ICRA 2017; Williams et al., IEEE T-RO 2018). Every
planner step (10 Hz):
  1. Map: integrate the range scan into a log-odds grid (the arena's astar_esdf.LogOddsMap, hits
     only, no prior map) and take its ESDF (scipy distance_transform_edt, outside = occupied).
  2. Sample K velocity-setpoint sequences U + eps over HORIZON steps of DT_MODEL. eps is AR(1) in
     time, eps_t = BETA eps_{t-1} + sqrt(1 - BETA^2) n_t, n_t ~ N(0, SIGMA^2) per axis (white noise
     with the smoothness cost leaves the nominal sequence winning every step).
     Three fixed samples: 0 = the nominal U (eps = 0), 1 = hover (all-zero setpoints), 2 = fly
     straight at the target and slow down on it (K_DIRECT). Without sample 2 the softmin stalled
     0.55-0.73 m short of B at a 4 s horizon (seen in the first seed-0 sweep, fixed before the
     published runs).
     Setpoints are clipped to V_MAX before the rollout and eps is taken after clipping.
  3. Roll all K out in parallel on the arena's point-mass model (vehicle.py: first-order velocity
     lag TAU, |a| <= A_MAX, |v| <= V_LIM), SUBSTEPS Euler steps per control step.
  4. Cost per sample S_k:
       goal       W_GOAL * sum_t |p_t - target| * DT_MODEL + W_TERM * |p_H - target|
                  target = B (guide='none') or the point LOOKAHEAD_M along the A* path from the
                  vehicle's projection on it (guide='astar', unknown-map A* from the same scans)
       path       guide='astar' only: W_PATH * sum_t (distance from p_t to the A* polyline) * DT_MODEL
       obstacle   W_OBS * sum relu(D_SAFE - d)^2 * dt_sub + W_COLL if any d < R_COLL
                  d = ESDF at the substep position minus half a cell (surface distance)
       smooth     W_SMOOTH * sum_t |u_t - u_{t-1}|^2 (u_{-1} = last command sent)
       control    GAMMA * sum_t u_t . eps_t / SIGMA^2 (the information-theoretic cross term)
  5. Weights w_k = exp(-(S_k - min S) / LAMBDA), U <- U + sum w_k eps_k / sum w_k.
  6. Send U[0] as the velocity setpoint, yaw towards it (K_YAW), shift U one step (warm start).

guide='astar' reuses planners/astar_esdf.AStarESDF(known_map=False) for the path (same
constants, replan every 0.4 s or when a new hit touches the path) and its map; MPPI replaces the
carrot follower. guide='none' has no global plan: the goal term is the straight-line distance to B.

bounds=(xmin, ymin, xmax, ymax) places the map on an operator geofence (corner = bounds - 2 m,
24 m square), as samples/close-area-benchmark does for astar_unknown. Without bounds the corner is
(min(0, Bx) - 2.5, min(0, By) - 2.5), picked on the first step, so a B at negative x or y stays
inside the map.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy.ndimage import distance_transform_edt

import arena   # this folder's arena.py; reuses close_area_arena when it is already imported

ast = arena.astar_esdf
Planner, Setpoint = arena.Planner, arena.Setpoint

# ---- sampling ----
K = 256                  # samples per step
HORIZON = 20             # control steps
DT_MODEL = 0.1           # s per control step (= the planner period)
SUBSTEPS = 5             # Euler substeps per control step (0.02 s = the arena physics step)
LAMBDA = 1.0             # temperature
SIGMA = 0.6              # m/s, per-axis std of the velocity-setpoint noise
BETA = 0.8               # AR(1) time correlation of the noise (0 = white); marginal std stays SIGMA
GAMMA = 0.1              # weight of the u . eps / SIGMA^2 control term
# ---- model (CONTRACT.md vehicle) ----
TAU = 0.15               # s, velocity lag
A_MAX = 3.0              # m/s^2
V_LIM = 2.0              # m/s, vehicle speed limit
V_MAX = 1.5              # m/s, setpoint norm cap (A* cruise speed)
# ---- cost ----
W_GOAL = 1.0             # per m per s
W_TERM = 3.0             # per m at the end of the horizon
W_OBS = 100.0            # per m^2 per s inside D_SAFE
D_SAFE = 0.4             # m, surface distance where the obstacle cost starts
R_COLL = ast.RADIUS      # m, surface distance counted as a collision (the vehicle radius)
W_COLL = 1000.0          # once per sample that reaches R_COLL
W_SMOOTH = 0.5           # per (m/s)^2 change between consecutive setpoints
LOOKAHEAD_M = 2.0        # m along the A* path (guide='astar')
W_PATH = 3.0             # per m per s of distance from the A* path polyline (guide='astar')
K_DIRECT = 1.0           # 1/s, speed gain of the straight-at-target sample (sample 2)
K_YAW = 1.5              # 1/s, yaw towards the commanded velocity
GEOFENCE_MARGIN_M = 2.0  # m, map corner = bounds - this


def _polyline_dist(P, path):
    """P (..., 2), path (m, 2) => distance from each point to the polyline."""
    a, b = path[:-1], path[1:]
    ab = b - a
    L = np.maximum((ab ** 2).sum(1), 1e-12)
    q = P[..., None, :] - a                                    # (..., m-1, 2)
    t = np.clip((q * ab).sum(-1) / L, 0.0, 1.0)
    r = q - t[..., None] * ab
    return np.sqrt((r ** 2).sum(-1)).min(-1)


class MPPI(Planner):
    uses_grid = False

    def __init__(self, guide="none", K=K, horizon=HORIZON, lam=LAMBDA, sigma=SIGMA, beta=BETA, gamma=GAMMA,
                 substeps=SUBSTEPS, v_max=V_MAX, lookahead_m=LOOKAHEAD_M, bounds=None, seed=0):
        if guide not in ("none", "astar"):
            raise ValueError("guide must be 'none' or 'astar'")
        self.guide, self.K, self.H = guide, int(K), int(horizon)
        self.lam, self.sigma, self.gamma = float(lam), float(sigma), float(gamma)
        self.beta = float(beta)
        self.sub, self.v_max, self.lookahead_m = int(substeps), float(v_max), float(lookahead_m)
        self.bounds, self.seed = bounds, seed
        self.name = f"mppi_{guide}"
        self.step_ms: list[float] = []        # whole step() time, kept across runs
        self.astar_ms: list[float] = []       # A* replans inside those steps (guide='astar')
        self.runs = 0
        self.reset()

    # ---- lifecycle ----
    def reset(self) -> None:
        self.runs += 1
        self.rng = np.random.default_rng([self.seed, self.runs, 31])
        self.U = np.zeros((self.H, 2))
        self.u_prev = np.zeros(2)
        self.astar = ast.AStarESDF(known_map=False) if self.guide == "astar" else None
        self.map = self.astar.map if self.astar else ast.LogOddsMap()
        self.placed = False
        self.esdf = None
        self.last_ess = None
        self.last_rollouts = None             # (K, H, 2) positions, kept for plots

    def _place_map(self, goal):
        if self.bounds is not None:
            x0, y0 = self.bounds[0] - GEOFENCE_MARGIN_M, self.bounds[1] - GEOFENCE_MARGIN_M
        else:
            x0, y0 = min(0.0, goal[0]) + ast.MAP_X0, min(0.0, goal[1]) + ast.MAP_Y0
        self.map.x0, self.map.y0 = x0, y0
        self.placed = True

    # ---- map ----
    def _esdf(self):
        padded = np.pad(self.map.occupied(), 1, constant_values=True)
        return (distance_transform_edt(~padded) * self.map.res)[1:-1, 1:-1]

    def _lookup(self, P):
        """P (..., 2) => surface distance (ESDF minus half a cell); outside the map = 0."""
        res, x0, y0 = self.map.res, self.map.x0, self.map.y0
        nx, ny = self.esdf.shape
        ix = np.floor((P[..., 0] - x0) / res).astype(np.int64)
        iy = np.floor((P[..., 1] - y0) / res).astype(np.int64)
        inside = (ix >= 0) & (iy >= 0) & (ix < nx) & (iy < ny)
        d = np.zeros(P.shape[:-1])
        d[inside] = self.esdf[ix[inside], iy[inside]] - 0.5 * res
        return d

    # ---- guide ----
    def _target(self, pose, goal, new_occ):
        if self.astar is None:
            return np.array(goal[:2], float)
        a = self.astar
        due = pose.t - a.last_plan_t >= ast.REPLAN_PERIOD_S - 1e-9
        if due or a.path_xy is None or a._blocked_by(new_occ):
            n = len(a.replan_ms)
            a._plan(pose, goal, None)
            a.last_plan_t = pose.t
            self.astar_ms.extend(a.replan_ms[n:])
        if a.path_xy is None:
            return np.array(goal[:2], float)
        return np.asarray(a._carrot_at(pose.x, pose.y, self.lookahead_m), float)

    # ---- MPPI ----
    def rollout(self, p0, v0, V):
        """V (K, H, 2) setpoints => positions (K, H * substeps, 2) on the arena point-mass model."""
        Kn, H, _ = V.shape
        dts = DT_MODEL / self.sub
        p = np.broadcast_to(np.asarray(p0, float), (Kn, 2)).copy()
        v = np.broadcast_to(np.asarray(v0, float), (Kn, 2)).copy()
        out = np.empty((Kn, H * self.sub, 2))
        for t in range(H):
            u = V[:, t]
            for s in range(self.sub):
                a = (u - v) / TAU
                an = np.hypot(a[:, 0], a[:, 1])
                a *= np.minimum(1.0, A_MAX / np.maximum(an, 1e-9))[:, None]
                v = v + a * dts
                vn = np.hypot(v[:, 0], v[:, 1])
                v *= np.minimum(1.0, V_LIM / np.maximum(vn, 1e-9))[:, None]
                p = p + v * dts
                out[:, t * self.sub + s] = p
        return out

    def costs(self, P, V, eps, target, path=None):
        dts = DT_MODEL / self.sub
        d = self._lookup(P)                                        # (K, H*sub)
        obs = W_OBS * (np.maximum(D_SAFE - d, 0.0) ** 2).sum(1) * dts
        obs += W_COLL * (d < R_COLL).any(1)
        Pc = P[:, self.sub - 1::self.sub]                          # (K, H, 2) end of each control step
        dist = np.hypot(Pc[..., 0] - target[0], Pc[..., 1] - target[1])
        goal = W_GOAL * dist.sum(1) * DT_MODEL + W_TERM * dist[:, -1]
        if path is not None and W_PATH > 0 and len(path) > 1:
            goal = goal + W_PATH * _polyline_dist(Pc, path).sum(1) * DT_MODEL
        dU = np.diff(np.concatenate([np.broadcast_to(self.u_prev, (len(V), 1, 2)), V], axis=1), axis=1)
        smooth = W_SMOOTH * (dU ** 2).sum((1, 2))
        ctrl = self.gamma * (self.U[None] * eps).sum((1, 2)) / (self.sigma ** 2)
        return goal + obs + smooth + ctrl

    def _direct(self, p0, target):
        """Sample 2: fly straight at the target, speed min(V_MAX, K_DIRECT * distance), on a
        kinematic prediction (p += u dt). Gives the softmin one sample that stops at B."""
        out = np.empty((self.H, 2))
        p = np.array(p0, float)
        for t in range(self.H):
            e = target - p
            d = math.hypot(e[0], e[1])
            u = e * (min(self.v_max, K_DIRECT * d) / d) if d > 1e-6 else np.zeros(2)
            out[t] = u
            p = p + u * DT_MODEL
        return out

    def _clip(self, V):
        n = np.hypot(V[..., 0], V[..., 1])
        return V * np.minimum(1.0, self.v_max / np.maximum(n, 1e-9))[..., None]

    def update(self, p0, v0, target, path=None):
        n = self.rng.normal(0.0, self.sigma, (self.K, self.H, 2))
        eps = np.empty_like(n)
        eps[:, 0] = n[:, 0]
        c = math.sqrt(1.0 - self.beta ** 2)
        for t in range(1, self.H):
            eps[:, t] = self.beta * eps[:, t - 1] + c * n[:, t]
        eps[0] = 0.0
        V = self.U[None] + eps
        V[1] = 0.0
        V[2] = self._direct(p0, target)
        V = self._clip(V)
        eps = V - self.U[None]
        P = self.rollout(p0, v0, V)
        S = self.costs(P, V, eps, target, path)
        w = np.exp(-(S - S.min()) / self.lam)
        w /= w.sum()
        self.U = self._clip(self.U + np.einsum("k,kth->th", w, eps))
        self.last_ess = float(1.0 / (w ** 2).sum())
        self.last_rollouts = P[:, self.sub - 1::self.sub]
        self.last_cost_min = float(S.min())
        return self.U[0].copy()

    def step(self, pose, scan, goal, grid, dt):
        t0 = time.perf_counter()
        if not self.placed:
            self._place_map(goal)
        new_occ = self.map.update(pose, scan)
        target = self._target(pose, goal, new_occ)
        self.esdf = self._esdf()
        path = self.astar.path_xy if self.astar is not None else None
        u = self.update((pose.x, pose.y), (pose.vx, pose.vy), target, path)
        self.u_prev = u
        self.U = np.concatenate([self.U[1:], self.U[-1:]])
        sp_yaw = 0.0
        if math.hypot(u[0], u[1]) > 0.05:
            err = (math.atan2(u[1], u[0]) - pose.yaw + math.pi) % (2 * math.pi) - math.pi
            sp_yaw = K_YAW * err
        self.step_ms.append((time.perf_counter() - t0) * 1e3)
        return Setpoint(float(u[0]), float(u[1]), 0.0, sp_yaw)


def make(guide="none", **kw) -> MPPI:
    """make() works with no arguments: guide='none', K=256, horizon=20 (2 s), lambda=1, sigma=0.6."""
    return MPPI(guide=guide, **kw)
