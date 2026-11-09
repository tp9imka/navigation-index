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
    health         dict(t, quality, reset_counter, sigma_xy) copied from the pose
    dt             filter period in s (the harness runs every arm at the 50 Hz physics rate)

Arms here:

  F0  PassThrough   no filter.
  F1  CPStop        PX4 Collision Prevention style: limits velocity toward range returns so the
                    vehicle stops CP_DIST from them, Position-mode semantics (docs/research/
                    close-area-nav/01 section 3, 04 section 3.1, and the PX4 docs page).
  F2  PX4CBF        NTNU PX4-CBF "as shipped" (fork branch cbf HEAD): analytic single-constraint
                    composite CBF on range returns, linear class-K, raw input, per-axis clamp
                    after, low-passed output, no FoV constraint (doc 05 sections 1.3, 1.4, 1.7).

Add an arm: subclass SafetyFilter, give it NAME and DEFAULTS (every parameter named, with its
source in a comment), implement reset() and filter(), and add it to REGISTRY. run_kill.py takes
--arms F0,F1,F2,F3 and builds each arm with make(name).
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np


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


REGISTRY = {cls.NAME: cls for cls in (PassThrough, CPStop, PX4CBF)}
LABELS = {
    "F0": "no filter",
    "F1": "CP-stop (PX4 Collision Prevention style)",
    "F2": "PX4-CBF as shipped (analytic, no FoV)",
}


def make(name: str, **overrides) -> SafetyFilter:
    if name not in REGISTRY:
        raise ValueError(f"unknown arm {name!r}, choose from {sorted(REGISTRY)}")
    return REGISTRY[name](**overrides)
