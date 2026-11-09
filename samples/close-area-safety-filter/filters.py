"""Safety filters that sit between a planner and the vehicle (kill test for the hub's headline).

Interface, the same for every arm:

    f = make("F2")                       # fresh instance per run; make("F2", eps=0.5) overrides
    f.reset()
    sp_out, intervened = f.filter(setpoint, pose, scan, map_obstacles, health, dt)

    setpoint       planner velocity Setpoint (local ENU, arena adapter type), never modified in place
    pose           Pose the vehicle reports (the ESTIMATE, not truth); yaw, vx, vy are read
    scan           latest RangeScan the filter has (body frame), or None; scan.t is its time
    map_obstacles  prior map (an arena World: boxes, cylinders, grid, sdf()). Query it only at
                   the estimated position. F0-F2 ignore it; map-based arms (F3+) use it
    health         dict(t, quality, reset_counter, sigma_xy) copied from the pose, plus "belief":
                   the estimator's belief() (EKF mean, covariance, noise settings) or None (truth)
    dt             filter period in s (the harness runs every arm at the 50 Hz physics rate)

Arms here:

  F0  PassThrough   no filter.
  F1  CPStop        PX4 Collision Prevention style: limits velocity toward range returns so the
                    vehicle stops CP_DIST from them, Position-mode semantics (docs/research/
                    close-area-nav/01 section 3, 04 section 3.1, and the PX4 docs page).
  F2  PX4CBF        NTNU PX4-CBF "as shipped" (fork branch cbf HEAD): analytic single-constraint
                    composite CBF on range returns, linear class-K, raw input, per-axis clamp
                    after, low-passed output, no FoV constraint (doc 05 sections 1.3, 1.4, 1.7).
  F3  BeliefCBF     F2 + Belief-CBF (Vahs 2023) rows on every map obstacle near the EKF mean:
                    clearance shrunk by k * sigma, covariance growth between updates in the
                    second-order ECBF, Theorem 3 update-jump margin gamma (doc 05 2.2-2.4).
                    Needs health["belief"] = estimator.VioEstimator.belief(). F3p: P alone.
  F4  MRCBF         F2 + MR-CBF (Dean 2020, Cosner 2021) rows on map obstacles with a fixed
                    worst-case error bound eps measured offline (doc 05 4.2-4.4).

Add an arm: subclass SafetyFilter, give it NAME and DEFAULTS (every parameter named, with its
source in a comment), implement reset() and filter(), and add it to REGISTRY. run_kill.py takes
--arms F0,F1,F2,F3 and builds each arm with make(name).
"""
from __future__ import annotations

import math
from dataclasses import replace
from itertools import combinations
from statistics import NormalDist

import numpy as np
from scipy.optimize import minimize


def scan_points_body(scan, max_range: float) -> np.ndarray:
    """(n, 2) body-frame points of finite returns at or below max_range."""
    if scan is None:
        return np.zeros((0, 2))
    a = np.asarray(scan.angles, float)
    d = np.asarray(scan.distances, float)
    ok = np.isfinite(d) & (d <= max_range)
    return np.column_stack([d[ok] * np.cos(a[ok]), d[ok] * np.sin(a[ok])])


def rot(yaw: float) -> np.ndarray:
    c, s = math.cos(yaw), math.sin(yaw)
    return np.array([[c, -s], [s, c]])


class SafetyFilter:
    NAME = "base"
    DEFAULTS: dict = {}

    def __init__(self, **overrides):
        unknown = set(overrides) - set(self.DEFAULTS)
        if unknown:
            raise ValueError(f"{self.NAME}: unknown parameters {sorted(unknown)}")
        self.p = dict(self.DEFAULTS)
        self.p.update(overrides)
        self.reset()

    def reset(self) -> None:
        pass

    def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
        raise NotImplementedError


# ---------------------------------------------------------------- F0

class PassThrough(SafetyFilter):
    NAME = "F0"
    DEFAULTS: dict = {}

    def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
        return setpoint, False


# ---------------------------------------------------------------- F1

def max_speed_from_distance(jerk: float, accel: float, dist: float, final_speed: float = 0.0) -> float:
    """Highest speed from which a jerk- and acceleration-limited stop fits in `dist`.
    Same closed form as PX4 math::trajectory::computeMaxSpeedFromDistance (TrajMath.hpp),
    written from memory of that source; not re-read in this job."""
    b = 4.0 * accel * accel / jerk
    c = -2.0 * accel * max(dist, 0.0) - final_speed * final_speed
    return 0.5 * (-b + math.sqrt(b * b - 4.0 * c))


class CPStop(SafetyFilter):
    """PX4 Collision Prevention style limit (our reading of the PX4 docs, not PX4 code).

    Returns are binned into N_SECTORS body-frame sectors (PX4 obstacle_distance has 72 of 5 deg;
    the arena fan has 72 beams 5 deg apart, so one beam per sector). A beam with no return counts
    as an obstacle at max range ("the range of the sensors for each sector is also taken into
    account"). For every sector in the hemisphere of the motion, the velocity component toward
    that sector is capped at the speed that still stops CP_DIST short of it, after spending
    CP_DELAY at the current (estimated) speed, with a jerk-limited brake (MPC_JERK_MAX,
    MPC_ACC_HOR). Only the component toward the sector is cut, so the vehicle may slide along a
    wall, as in acceleration-based Position mode. Guidance: if a direction within CP_GUIDE_ANG of
    the command allows more speed, by more than GUIDE_MARGIN, the command is turned to it.
    No scan for NO_DATA_TIMEOUT_S => zero horizontal velocity. Sectors without any beam block
    motion (CP_GO_NO_DATA = 0); the 360 deg fan leaves none.
    """
    NAME = "F1"
    DEFAULTS = {
        "cp_dist": 0.5,            # m. PX4 default is -1 (disabled); 0.5 m is OUR choice (radius 0.15 m + 0.35 m)
        "cp_delay": 0.4,           # s, CP_DELAY default (PX4 parameter reference)
        "cp_guide_ang_deg": 30.0,  # deg, CP_GUIDE_ANG default (PX4 parameter reference; docs: "30 degrees is a good balance")
        "cp_go_no_data": 0,        # CP_GO_NO_DATA default (doc 01 section 3)
        "acc_hor": 3.0,            # m/s^2, MPC_ACC_HOR default (PX4 parameter reference)
        "jerk_max": 8.0,           # m/s^3, MPC_JERK_MAX default (PX4 parameter reference)
        "no_data_timeout_s": 0.5,  # s, "no range data for 0.5 s => xy setpoints zero" (doc 01 section 3)
        "n_sectors": 72,           # PX4 obstacle_distance sectors (PX4 docs, 5 deg each)
        "guide_step_deg": 5.0,     # deg, guidance search step = sector width (ours)
        "guide_margin": 0.1,       # guidance must gain > 10 % speed (ours; docs say "significant margin")
        "change_tol": 1e-3,        # m/s, output differs from input => intervened (ours)
    }

    def reset(self):
        self.last_dirs = None

    def _sectors(self, pose, scan):
        n = int(self.p["n_sectors"])
        width = 2 * math.pi / n
        d = np.full(n, np.nan)                   # nan = no beam in the sector (no data)
        a = np.asarray(scan.angles, float)
        r = np.asarray(scan.distances, float)
        r = np.where(np.isfinite(r), r, scan.max_range)
        idx = np.mod(np.rint(a / width).astype(int), n)
        for i, v in zip(idx, r):
            d[i] = v if np.isnan(d[i]) else min(d[i], v)
        ang = pose.yaw + np.arange(n) * width   # world-frame sector centres
        return np.column_stack([np.cos(ang), np.sin(ang)]), d

    def _limit(self, v, dirs, d, vlim):
        """Cut the component of v toward each sector to its limit, closest sector first, 2 passes."""
        v = v.copy()
        order = np.argsort(np.where(np.isnan(d), -1.0, d))
        for _ in range(2):
            for i in order:
                proj = float(dirs[i] @ v)
                if proj <= 0.0:
                    continue
                cap = 0.0 if np.isnan(d[i]) else vlim[i]
                if proj > cap:
                    v -= (proj - cap) * dirs[i]
        return v

    def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
        p = self.p
        v_in = np.array([setpoint.vx, setpoint.vy], float)
        if scan is None or pose.t - scan.t > p["no_data_timeout_s"] + 1e-9:
            out = np.zeros(2)
        else:
            dirs, d = self._sectors(pose, scan)
            if p["cp_go_no_data"]:
                d = np.where(np.isnan(d), np.inf, d)
            vnow = math.hypot(pose.vx, pose.vy)
            s = np.where(np.isnan(d), 0.0, d) - p["cp_dist"] - p["cp_delay"] * vnow
            vlim = np.array([max_speed_from_distance(p["jerk_max"], p["acc_hor"], si) if si > 0 else 0.0
                             for si in s])
            out = self._limit(v_in, dirs, d, vlim)
            speed = float(np.linalg.norm(v_in))
            if speed > 1e-6 and float(np.linalg.norm(out)) < speed - 1e-6:
                best, best_k = float(np.linalg.norm(out)), 0
                kmax = int(p["cp_guide_ang_deg"] // p["guide_step_deg"])
                for k in sorted(range(-kmax, kmax + 1), key=abs):
                    if k == 0:
                        continue
                    cand = self._limit(rot(math.radians(k * p["guide_step_deg"])) @ v_in, dirs, d, vlim)
                    sc = float(np.linalg.norm(cand))
                    if sc > best * (1.0 + p["guide_margin"]) + 1e-9:
                        best, best_k, best_v = sc, k, cand
                if best_k != 0:
                    out = best_v
        changed = bool(np.linalg.norm(out - v_in) > p["change_tol"])
        return replace(setpoint, vx=float(out[0]), vy=float(out[1])), changed


# ---------------------------------------------------------------- F2

class PX4CBF(SafetyFilter):
    """PX4-CBF as shipped (doc 05 section 1.7 pseudo-code; fork branch cbf HEAD, section 1.3).

    The arena vehicle takes velocity setpoints, so the filter wraps them in a P velocity loop
    (doc 05 section 1.8): a_sp = VEL_P_ACC * (v_sp - v_est), filters a_sp, and converts back
    v_cmd = v_est + a_out / VEL_P_ACC. VEL_P_ACC = 1 / tau of the arena vehicle, so with no
    correction and no low-pass the command equals the planner's. Obstacles are body-frame points
    of the latest scan (no position used); the estimated velocity and yaw are used.
    """
    NAME = "F2"
    DEFAULTS = {
        "eps": 0.7,            # m, safety distance (doc 05 1.4: paper Table II, composite_cbf; fork param 0.5)
        "p0": -2.5,            # exponential-CBF pole (doc 05 1.4: Table II; fork -2)
        "kappa": 70.0,         # soft-min sharpness (doc 05 1.4: Table II; fork 10)
        "gamma": 40.0,         # tanh saturation scale (doc 05 1.4: Table II = fork 40)
        "alpha": 2.0,          # linear class-K gain, alpha*h as in the fork (doc 05 1.3, 1.4: Table II; fork 1)
        "lp_gain_out": 0.6,    # output low-pass gain per step (doc 05 1.4: composite_cbf lp_gain_out)
        "lp_ref_hz": 100.0,    # rate the gain is defined at (doc 05 1.5: filter runs at 100 Hz)
        "a_max_xy": 3.0,       # m/s^2, per-axis clamp after the correction (doc 05 1.4: CBF_CLAMP_XY / max_acc_xy)
        "obs_timeout_s": 1.0,  # s, obstacles older than this are cleared => pass-through (doc 05 1.4, 1.6)
        "max_range": 5.0,      # m, returns beyond are dropped (doc 05 1.5: ToF ranges clamped at 5 m)
        "lg_min": 1e-5,        # ||Lg h||^2 at or below => no correction (doc 05 1.6)
        "vel_p_acc": 1.0 / 0.15,  # 1/s, wrapper velocity loop gain = 1 / arena tau (doc 05 1.8; ours)
    }

    def reset(self):
        self.a_out = None
        self.last = {}

    def _terms(self, P, v):
        """Composite barrier h, Lf h, Lg h for body points P (n,2) and body velocity v (doc 05 1.2)."""
        p = self.p
        eps, p0, kap, gam = p["eps"], p["p0"], p["kappa"], p["gamma"]
        nu1 = -2.0 * (P @ v) - p0 * ((P * P).sum(1) - eps * eps)
        th = np.tanh(nu1 / gam)
        z = -kap * th
        m = float(z.max())
        e = np.exp(z - m)
        L = float(e.sum())
        h = -(gam / kap) * (m + math.log(L))
        lam = e * (1.0 - th * th) / L            # lambda_i / Lambda, scaled consistently
        Lf = float(lam @ (2.0 * ((v + p0 * P) @ v)))
        Lg = (lam[:, None] * (-2.0 * P)).sum(0)
        return h, Lf, Lg

    def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
        p = self.p
        K = p["vel_p_acc"]
        v_w = np.array([pose.vx, pose.vy], float)
        a_sp_w = K * (np.array([setpoint.vx, setpoint.vy], float) - v_w)
        R = rot(pose.yaw)
        a_in = R.T @ a_sp_w                       # raw input (fork: no input low-pass)
        v_b = R.T @ v_w
        P = np.zeros((0, 2))
        if scan is not None and pose.t - scan.t <= p["obs_timeout_s"] + 1e-9:
            P = scan_points_body(scan, p["max_range"])
        eta = 0.0
        if not len(P):
            self.a_out = a_in.copy()              # pass-through as in the code; keep LP state current (ours)
            a_cmd = a_in
            self.last = {"h": None, "eta": 0.0}
        else:
            h, Lf, Lg = self._terms(P, v_b)
            lg2 = float(Lg @ Lg)
            if lg2 > p["lg_min"]:
                eta = -(Lf + float(Lg @ a_in) + p["alpha"] * h) / lg2
            a_star = np.clip(a_in + max(eta, 0.0) * Lg, -p["a_max_xy"], p["a_max_xy"])
            g = 1.0 - (1.0 - p["lp_gain_out"]) ** (dt * p["lp_ref_hz"])
            if self.a_out is None:
                self.a_out = a_star.copy()
            self.a_out = (1.0 - g) * self.a_out + g * a_star
            a_cmd = self.a_out
            self.last = {"h": h, "eta": eta}
        v_cmd = v_w + (R @ a_cmd) / K
        return replace(setpoint, vx=float(v_cmd[0]), vy=float(v_cmd[1])), bool(eta > 0.0)


# ---------------------------------------------------------------- map geometry and solvers (F3, F4)

def map_features(world, p, query_m: float):
    """Nearest-surface distance d (m,) and outward unit normal n (m, 2) at point p, one entry per
    map obstacle (walls, boxes, cylinders of the arena World) with d < query_m. Exact geometry,
    queried at p only (p is the ESTIMATED position)."""
    x, y = float(p[0]), float(p[1])
    ds = [x - world.xmin, world.xmax - x, y - world.ymin, world.ymax - y]
    ns = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
    d_out, n_out = [], []
    for d, n in zip(ds, ns):
        if d < query_m:
            d_out.append(d)
            n_out.append(n)
    P = np.array([x, y])
    if len(world._bc):
        rel = P[None] - world._bc
        q = np.abs(rel) - world._bh
        sg = np.where(rel >= 0.0, 1.0, -1.0)
        for i in range(len(q)):
            qi = q[i]
            if qi.max() > 0.0:
                vv = np.maximum(qi, 0.0)
                d = float(np.hypot(vv[0], vv[1]))
                n = sg[i] * vv / d
            else:
                k = int(np.argmax(qi))
                d = float(qi[k])
                n = np.zeros(2)
                n[k] = sg[i][k]
            if d < query_m:
                d_out.append(d)
                n_out.append((float(n[0]), float(n[1])))
    if len(world._cc):
        rel = P[None] - world._cc
        dist = np.hypot(rel[:, 0], rel[:, 1])
        for i in range(len(dist)):
            d = float(dist[i] - world._cr[i])
            if d < query_m:
                n = rel[i] / dist[i] if dist[i] > 1e-9 else np.array([1.0, 0.0])
                d_out.append(d)
                n_out.append((float(n[0]), float(n[1])))
    return np.array(d_out, float), np.array(n_out, float).reshape(-1, 2)


def _kkt_enum(A, bb, z0, Winv, max_size):
    """min 1/2 (z - z0)^T W (z - z0) s.t. A z >= bb, W diagonal, by active-set enumeration.
    Strictly convex, so the first KKT point found is the optimum. None if no KKT point exists
    (infeasible). Returns (z, active index tuple)."""
    if bool(np.all(A @ z0 >= bb - 1e-12)):
        return z0.copy(), ()
    for size in range(1, max_size + 1):
        for S in combinations(range(len(bb)), size):
            AS = A[list(S)]
            M = (AS * Winv) @ AS.T
            if abs(np.linalg.det(M)) < 1e-12:
                continue
            lam = np.linalg.solve(M, bb[list(S)] - AS @ z0)
            if lam.min() < -1e-10:
                continue
            z = z0 + Winv * (AS.T @ lam)
            if bool(np.all(A @ z >= bb - 1e-9)):
                return z, S
    return None


def qp_halfspaces(a0, G, b, rho: float, n_hard: int = 0):
    """min ||a - a0||^2 s.t. G a >= b (2D a). If no a satisfies every row, the slack version
    min ||a - a0||^2 + rho s^2 s.t. G a >= b - s on rows n_hard.. (one shared slack, s >= 0),
    G a >= b on the first n_hard rows, is solved instead; the slack is used only when the hard
    problem is infeasible. The first n_hard rows must be feasible on their own (F2's single
    range row is). Exact (active-set enumeration). Returns (a, s, active_row_mask)."""
    m = len(b)
    a0 = np.asarray(a0, float)
    act = np.zeros(m, bool)
    if m == 0:
        return a0.copy(), 0.0, act
    hard = _kkt_enum(G, b, a0, np.ones(2), 2)
    if hard is not None:
        act[list(hard[1])] = True
        return hard[0], 0.0, act
    scol = np.ones((m, 1))
    scol[:n_hard] = 0.0
    A = np.vstack([np.hstack([G, scol]), [0.0, 0.0, 1.0]])   # rows on z = (a, s)
    soft = _kkt_enum(A, np.append(b, 0.0), np.array([a0[0], a0[1], 0.0]),
                     np.array([1.0, 1.0, 1.0 / rho]), 3)
    if soft is None:
        raise RuntimeError("qp_halfspaces: no KKT point found")   # the slack QP is always feasible
    act[[i for i in soft[1] if i < m]] = True
    return soft[0][:2], float(max(soft[0][2], 0.0)), act


class _MapCBF(PX4CBF):
    """F2's range barrier plus barriers on map obstacles, all in one QP on the world-frame
    acceleration, then F2's per-axis clamp and output low-pass (doc 04 section 3.4: "F2 + ...
    margin on map obstacles"). Subclasses give the map rows. With no map rows the result equals
    F2 exactly (one half-space with unbounded input is F2's closed form)."""

    def reset(self):
        super().reset()
        self.stats = {"steps": 0, "active_steps": 0, "map_active_steps": 0, "slack_steps": 0,
                      "max_slack": 0.0}

    def _range_rows(self, pose, scan, R, v_b):
        p = self.p
        P = np.zeros((0, 2))
        if scan is not None and pose.t - scan.t <= p["obs_timeout_s"] + 1e-9:
            P = scan_points_body(scan, p["max_range"])
        if not len(P):
            return False, []
        h, Lf, Lg = self._terms(P, v_b)
        if float(Lg @ Lg) <= p["lg_min"]:
            return True, []
        return True, [(R @ Lg, -(Lf + p["alpha"] * h))]   # world-frame row: g . a >= b

    def _solve(self, a_in_w, lin_rows, map_terms):
        raise NotImplementedError

    def filter(self, setpoint, pose, scan, map_obstacles, health, dt):
        p = self.p
        K = p["vel_p_acc"]
        v_w = np.array([pose.vx, pose.vy], float)
        a_sp_w = K * (np.array([setpoint.vx, setpoint.vy], float) - v_w)
        R = rot(pose.yaw)
        a_in = R.T @ a_sp_w
        v_b = R.T @ v_w
        have_pts, lin_rows = self._range_rows(pose, scan, R, v_b)
        map_terms = self._map_terms(pose, map_obstacles, health)
        self.stats["steps"] += 1
        if not have_pts and not map_terms:
            self.a_out = a_in.copy()                      # F2 pass-through semantics
            v_cmd = v_w + (R @ a_in) / K
            return replace(setpoint, vx=float(v_cmd[0]), vy=float(v_cmd[1])), False
        a_star_w, slack, map_active = self._solve(a_sp_w, lin_rows, map_terms)
        active = bool(np.linalg.norm(a_star_w - a_sp_w) > 1e-9)
        self.stats["active_steps"] += int(active)
        self.stats["map_active_steps"] += int(map_active)
        if slack > 1e-6:
            self.stats["slack_steps"] += 1
            self.stats["max_slack"] = max(self.stats["max_slack"], round(float(slack), 4))
        a_star = np.clip(R.T @ a_star_w, -p["a_max_xy"], p["a_max_xy"])
        g = 1.0 - (1.0 - p["lp_gain_out"]) ** (dt * p["lp_ref_hz"])
        if self.a_out is None:
            self.a_out = a_star.copy()
        self.a_out = (1.0 - g) * self.a_out + g * a_star
        v_cmd = v_w + (R @ self.a_out) / K
        return replace(setpoint, vx=float(v_cmd[0]), vy=float(v_cmd[1])), active


# ---------------------------------------------------------------- F3

class BeliefCBF(_MapCBF):
    """Belief-CBF (Vahs, Pek, Tumova, RA-L 2023) on map obstacles, plus F2's range barrier.

    Doc 05 section 2.4, per map obstacle within QUERY_M of the EKF mean mu (walls, boxes,
    cylinders, the unsensed ones included), linearised at the mean (paper eq. 27, 28):
        n  = outward normal at mu,  d = distance from mu to the surface
        s  = sqrt(n^T Sigma_pp n)                  Sigma = EKF covariance (+ VIO drift, see below)
        s' = n^T (C + C^T) n / (2 s)               covariance prediction Sigma_dot = A S + S A^T + Q
        s''= n^T V n / s - s'^2 / s                (A = double integrator: P_dot = C + C^T, P_ddot = 2 V)
        gamma = max(0, Phi^-1(1 - eps_jump) sqrt(n^T Lam n) - k (s_minus - s_plus))   Theorem 3
        h  = d - r_safe - k s - gamma,   h' = n.v - k s'          k = Phi^-1(1 - delta)
        row: n . a >= k s'' - z1 h' - z0 h                         second-order ECBF (paper eq. 4)
    Lam = K (H S H^T + R) K^T and Sigma_plus = (I - K H) S for the next VIO position update
    (H = [I 0], R = vio_r^2 I from the estimator), computed from the current covariance (doc 05:
    our simplification). The EKF has predicted the covariance to the current time, so Sigma grows
    between VIO updates and through a dropout, and s', s'' carry that growth into the constraint.

    Sigma: the arena EKF fuses the VIO output as an absolute position with 5 mm noise, so its P
    alone does not contain the VIO drift (estimator.py docstring). With drift_in_sigma (default,
    OUR choice) the position block gets + drift_var / 2 per axis, the drift variance the VIO model
    accumulated (what sigma_xy reports), and s' gets its growth rate (drift_c^2 |v| + time_walk^2)
    / 2; the update does not shrink it. F3p is the same arm on the EKF P alone.
    """
    NAME = "F3"
    DEFAULTS = dict(PX4CBF.DEFAULTS, **{
        "delta": 0.01,          # risk per constraint (doc 05 2.3: paper sim delta = 0.01; hardware 0.05).
                                # Doc 05 5 asks for "our integrity risk"; ours is not built yet, so 0.01 (ours)
        "eps_jump": 0.01,       # update-jump risk eps of Theorem 3 (doc 05 2.3: paper runs eps 0.5 and 0.01)
        "ecbf_pole": 2.5,       # 1/s, both ECBF poles; z0 = pole^2, z1 = 2 pole (doc 05 2.4 form; the paper
                                # gives no gains; value OURS, equal to |p0| of F2's Table II)
        "r_safe": 0.15,         # m, safe set ||x - obstacle|| >= vehicle radius (doc 05 2.2 eq. 27; arena radius)
        "drift_in_sigma": True, # add VIO drift variance to Sigma (OURS, see docstring)
        "query_m": 3.0,         # m, obstacles farther from the mean get no row (ours, compute bound)
        "slack_rho": 1e4,       # penalty on the shared slack (doc 05 2.3 "heavily penalised slack"; value ours)
    })

    def reset(self):
        super().reset()
        self.stats.update({"margin_max_m": 0.0, "margin_sum_m": 0.0, "margin_n": 0, "gamma_max_m": 0.0})

    def _map_terms(self, pose, world, health):
        p = self.p
        bel = (health or {}).get("belief")
        mu = np.array([pose.x, pose.y], float)
        v = np.array([pose.vx, pose.vy], float)
        d, n = map_features(world, mu, p["query_m"])
        if not len(d):
            return []
        nd = NormalDist()
        k = nd.inv_cdf(1.0 - p["delta"])
        kj = nd.inv_cdf(1.0 - p["eps_jump"])
        z0, z1 = p["ecbf_pole"] ** 2, 2.0 * p["ecbf_pole"]
        if bel is None:                                   # truth pose: zero covariance
            S, Dv, Dr, r_meas = np.zeros((4, 4)), 0.0, 0.0, 0.005
        else:
            S = bel["P"]
            r_meas = bel["vio_r"]
            Dv = bel["drift_var"] / 2.0 if p["drift_in_sigma"] else 0.0
            speed = float(np.hypot(v[0], v[1]))
            Dr = ((bel["drift_c"] ** 2) * speed + bel["time_walk"] ** 2) / 2.0 if p["drift_in_sigma"] else 0.0
        Pp, C, V = S[:2, :2], S[:2, 2:], S[2:, 2:]
        Sy = Pp + np.eye(2) * r_meas ** 2                 # H S H^T + R
        Kg = S[:, :2] @ np.linalg.inv(Sy)                 # 4x2 gain
        Lam = (Kg @ Sy @ Kg.T)[:2, :2]
        Pplus = Pp - Kg[:2] @ Pp
        rows = []
        CC = C + C.T
        for di, ni in zip(d, n):
            var = float(ni @ Pp @ ni) + Dv
            s = math.sqrt(max(var, 0.0))
            if s > 1e-9:
                sd = (float(ni @ CC @ ni) + Dr) / (2.0 * s)
                sdd = float(ni @ V @ ni) / s - sd * sd / s
            else:
                sd = sdd = 0.0
            s_plus = math.sqrt(max(float(ni @ Pplus @ ni) + Dv, 0.0))
            xi = k * (s - s_plus)
            gam = max(0.0, kj * math.sqrt(max(float(ni @ Lam @ ni), 0.0)) - xi)
            h = di - p["r_safe"] - k * s - gam
            hd = float(ni @ v) - k * sd
            rows.append((ni, k * sdd - z1 * hd - z0 * h, k * s + gam, gam, di))
        j = int(np.argmin(d))
        st = self.stats
        st["margin_max_m"] = max(st["margin_max_m"], round(rows[j][2], 4))
        st["gamma_max_m"] = max(st["gamma_max_m"], round(max(r[3] for r in rows), 4))
        st["margin_sum_m"] += rows[j][2]
        st["margin_n"] += 1
        return rows

    def _solve(self, a_in_w, lin_rows, map_terms):
        G = np.array([g for g, _ in lin_rows] + [r[0] for r in map_terms], float).reshape(-1, 2)
        b = np.array([bb for _, bb in lin_rows] + [r[1] for r in map_terms], float)
        a, s, act = qp_halfspaces(a_in_w, G, b, self.p["slack_rho"], n_hard=len(lin_rows))
        return a, s, bool(act[len(lin_rows):].any())


class BeliefCBFPOnly(BeliefCBF):
    """F3 with Sigma = the arena EKF covariance P alone (no VIO drift variance)."""
    NAME = "F3p"
    DEFAULTS = dict(BeliefCBF.DEFAULTS, drift_in_sigma=False)


# ---------------------------------------------------------------- F4

class MRCBF(_MapCBF):
    """Measurement-robust CBF (Dean et al. CoRL 2020; Cosner et al. IROS 2021) on map obstacles
    with a FIXED worst-case state-error bound eps_m, plus F2's range barrier.

    Doc 05 section 4.4: per map obstacle within QUERY_M of the estimate, the same exponential CBF
    as PX4-CBF in the world frame, on the obstacle's nearest surface point q (fixed for the step):
        e = p_hat - q,  h = 2 e.v - p0 (|e|^2 - r_safe^2),  Lf h = 2|v|^2 - 2 p0 e.v,  Lg h = 2 e
    MR-CBF condition (Dean, R-MR-OP, Theorem 2 constants):
        Lf h - (L_Lfh + alpha L_h) eps + Lg h . a - L_Lgh eps ||a|| >= -alpha h - slack
    Lipschitz constants on the ball of radius eps around x_hat = (p_hat, v_hat): the gradients of h
    and Lf h are affine in the state, so L = ||grad(x_hat)|| + sigma_max(Jacobian) eps bounds the
    largest gradient norm in the ball (exact form of doc 05's "max slope on a local grid").
    L_Lgh = 2. The F2 range row enters the same program with no eps terms. Solved as a small SOCP
    with scipy SLSQP (cvxpy is not in this sample's venv); slack use is counted.
    eps_m is constant for every run and case, measured offline against truth (Cosner practice):
    run_kill.py --calibrate, results/kill_b_eps_calib_1.md.
    """
    NAME = "F4"
    DEFAULTS = dict(PX4CBF.DEFAULTS, **{
        "eps_m": 1.0558,        # m (m/s), worst |(dp, dv)| in 100 nominal runs, seed 1 (Cosner practice, doc 05
                                # 4.3; value from results/kill_b_eps_calib_1.md; using the max is our choice)
        "mr_p0": -2.5,          # ECBF pole of the map barrier (doc 05 4.4 "same ECBF as PX4-CBF"; Table II)
        "mr_alpha": 2.0,        # linear class-K gain on the map barrier (doc 05 4.4 / Table II alpha)
        "r_safe": 0.15,         # m, safe distance from the surface point = vehicle radius (ours; doc 05 4.4 uses r)
        "query_m": 3.0,         # m, obstacles farther from the estimate get no row (ours, compute bound)
        "e_min": 1e-3,          # m, |e| floor when the estimate is inside an obstacle (ours)
        "slack_rho": 1e4,       # slack penalty p (doc 05 4.3: value not given in the paper; ours)
        "norm_smooth": 1e-6,    # ||a|| ~ sqrt(|a|^2 + this) for the solver; overstates ||a|| by <= 1e-3 (ours)
    })

    def reset(self):
        super().reset()
        p0 = self.p["mr_p0"]
        I2, Z2 = np.eye(2), np.zeros((2, 2))
        Jh = np.block([[-2 * p0 * I2, 2 * I2], [2 * I2, Z2]])
        Jf = np.block([[Z2, -2 * p0 * I2], [-2 * p0 * I2, 4 * I2]])
        self._sh = float(np.linalg.norm(Jh, 2))
        self._sf = float(np.linalg.norm(Jf, 2))
        self.stats.update({"solver_fail_steps": 0})

    def _map_terms(self, pose, world, health):
        p = self.p
        ph = np.array([pose.x, pose.y], float)
        v = np.array([pose.vx, pose.vy], float)
        d, n = map_features(world, ph, p["query_m"])
        p0, al, eps, r = p["mr_p0"], p["mr_alpha"], p["eps_m"], p["r_safe"]
        rows = []
        for di, ni in zip(d, n):
            e = max(di, p["e_min"]) * ni
            ev = float(e @ v)
            h = 2.0 * ev - p0 * (float(e @ e) - r * r)
            Lf = 2.0 * float(v @ v) - 2.0 * p0 * ev
            gh = np.concatenate([2 * v - 2 * p0 * e, 2 * e])
            gf = np.concatenate([-2 * p0 * v, 4 * v - 2 * p0 * e])
            L_h = float(np.linalg.norm(gh)) + self._sh * eps
            L_f = float(np.linalg.norm(gf)) + self._sf * eps
            c = Lf - (L_f + al * L_h) * eps + al * h        # c + Lg.a - b ||a|| >= -slack
            rows.append((2.0 * e, c, 2.0 * eps))
        return rows

    def _solve(self, a_in_w, lin_rows, map_terms):
        G = np.array([g for g, _ in lin_rows] + [r[0] for r in map_terms], float).reshape(-1, 2)
        c = np.array([-bb for _, bb in lin_rows] + [r[1] for r in map_terms], float)
        bn = np.array([0.0] * len(lin_rows) + [r[2] for r in map_terms], float)
        rho = self.p["slack_rho"]
        nl = len(lin_rows)
        sm = self.p["norm_smooth"]

        def cons(a):                                       # >= 0 means the row holds
            return c + G @ a - bn * math.sqrt(float(a @ a) + sm)

        def jcons(a):
            return G - bn[:, None] * (a / math.sqrt(float(a @ a) + sm))[None]

        a0 = np.asarray(a_in_w, float)
        if bool(np.all(cons(a0) >= 0.0)):
            return a0.copy(), 0.0, False
        # 1) hard SOCP: min ||a - a0||^2 s.t. every row >= 0
        res = minimize(lambda a: (float((a - a0) @ (a - a0)), 2 * (a - a0)), a0, jac=True, method="SLSQP",
                       constraints=[{"type": "ineq", "fun": cons, "jac": jcons}],
                       options={"maxiter": 100, "ftol": 1e-10})
        if res.success and np.all(np.isfinite(res.x)) and float(cons(res.x).min()) >= -1e-7:
            a, s = res.x, 0.0
        else:
            # 2) infeasible (or SLSQP failed): R-MR-OP with one shared slack on the map rows; the F2
            # range row stays hard (it is feasible on its own). For fixed a the best slack is
            # max(0, -min map row), so minimise ||a - a0||^2 + rho * that^2 over a (convex, 2D);
            # the range row enters as a stiff penalty, then a is projected onto it exactly.
            def pen(a):
                g = cons(a)
                s_ = max(0.0, -float(g[nl:].min())) if len(g) > nl else 0.0
                hv = max(0.0, -float(g[:nl].min())) if nl else 0.0
                return float((a - a0) @ (a - a0)) + rho * s_ * s_ + 1e8 * hv * hv
            best = None
            for start in (a0, np.zeros(2)):
                r2 = minimize(pen, start, method="Nelder-Mead",
                              options={"xatol": 1e-5, "fatol": 1e-10, "maxiter": 400})
                if best is None or r2.fun < best.fun:
                    best = r2
            a = best.x.copy()
            for i in range(nl):                           # exact projection onto the range half-plane
                gi = G[i]
                viol = -float(cons(a)[i])
                if viol > 0.0:
                    a = a + viol / float(gi @ gi) * gi
            s = max(0.0, -float(cons(a)[nl:].min())) if len(c) > nl else 0.0
            if s <= 1e-7:
                self.stats["solver_fail_steps"] += 1       # hard step failed but a feasible point exists
        act_map = bool(np.any(cons(a)[nl:] + s < 1e-5)) if len(map_terms) else False
        return a, float(s), act_map


# F2 is kept last: test_smoke.py compares the last arm it iterates over with the saved F2 jump row.
REGISTRY = {cls.NAME: cls for cls in (PassThrough, CPStop, BeliefCBF, BeliefCBFPOnly, MRCBF, PX4CBF)}
LABELS = {
    "F0": "no filter",
    "F1": "CP-stop (PX4 Collision Prevention style)",
    "F2": "PX4-CBF as shipped (analytic, no FoV)",
    "F3": "F2 + Belief-CBF on map obstacles (EKF covariance + VIO drift, prediction, Theorem 3 jump margin)",
    "F3p": "F3 on the EKF covariance P alone (no VIO drift variance)",
    "F4": "F2 + MR-CBF on map obstacles, fixed worst-case bound eps",
}


def make(name: str, **overrides) -> SafetyFilter:
    if name not in REGISTRY:
        raise ValueError(f"unknown arm {name!r}, choose from {sorted(REGISTRY)}")
    return REGISTRY[name](**overrides)
