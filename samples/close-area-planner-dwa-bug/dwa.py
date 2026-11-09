"""Dynamic window approach (Fox, Burgard, Thrun 1997) for a holonomic multicopter, on range returns.

Velocity space is the horizontal command (vx, vy) in the local ENU frame. The arena vehicle is
holonomic, so there is no (v, omega) unicycle pair; yaw just follows the chosen velocity so the
front beam of a sparse fan faces travel.

Per planner step (10 Hz in the arena):
1. Obstacle points = world-frame endpoints of the finite returns in this scan. With
   memory_s > 0 (variant "dwa_mem"), points from the last memory_s seconds are kept as well,
   placed with the pose at the time they were seen and thinned to one per MEM_CELL_M cell (a
   rolling local map, like the obstacle layer of a Nav2 local costmap; here the pose is truth,
   so this memory has no drift).
2. Dynamic window: commands reachable from the current velocity v0 in one window period,
   v0 +/- A_MAX * WINDOW_S per axis (A_MAX from the arena vehicle, 3 m/s^2). Sampled on an
   N_SAMPLES x N_SAMPLES grid, intersected with |v| <= min(V_MAX, K_GOAL * distance to B)
   (samples outside are pulled onto that circle). Zero velocity is always added.
3. Forward simulation of each sample over HORIZON_S with the arena vehicle model (first-order
   velocity lag tau 0.15 s, |a| <= A_MAX) in SIM_DT steps, command held constant.
4. Admissible: min clearance along the rollout (distance to the nearest obstacle point minus
   RADIUS) >= SAFETY_M, and |v| <= sqrt(2 * A_BRAKE * (clearance - SAFETY_M)) (Fox's
   admissible-velocity rule: can still stop before the nearest point).
5. Cost (maximised), each term in [0, 1]:
     W_HEADING * (1 - |angle(v_cmd) - bearing(rollout end => B)| / pi)
   + W_CLEAR   * min(clearance, CLEAR_CAP_M) / CLEAR_CAP_M
   + W_SPEED   * |v_cmd| / V_MAX
   No admissible sample => command zero velocity (the vehicle brakes; the arena scores a long
   stop as stuck).
DWA has no escape rule and no global path here: it is a local planner that Nav2 pairs with a
global planner. This file measures it on its own.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from .arena import VEHICLE, Planner, Setpoint
except ImportError:
    from arena import VEHICLE, Planner, Setpoint

# ---- vehicle (arena CONTRACT.md) ----
RADIUS = VEHICLE["radius"]          # 0.15 m
A_MAX = VEHICLE["a_max"]            # 3 m/s^2, window and rollout acceleration limit
TAU = VEHICLE["tau"]                # 0.15 s velocity lag in the rollout
# ---- window and rollout ----
WINDOW_S = 0.2                      # s, window half-width = A_MAX * WINDOW_S = 0.6 m/s per axis
N_SAMPLES = 11                      # per axis => 121 samples + zero
V_MAX = 1.0                         # m/s, cruise cap (arena vehicle allows 2)
K_GOAL = 1.0                        # 1/s, speed cap = K_GOAL * distance to B
HORIZON_S = 1.5                     # s, forward simulation horizon
SIM_DT = 0.1                        # s, rollout step
# ---- admissibility ----
SAFETY_M = 0.08                     # m, clearance beyond RADIUS a rollout must keep
A_BRAKE = 0.5 * A_MAX               # m/s^2, braking assumed in the admissible-velocity rule
# ---- cost weights ----
W_HEADING = 1.0
W_CLEAR = 0.6
W_SPEED = 0.2
CLEAR_CAP_M = 1.0                   # m, clearance above this scores the same
# ---- memory (dwa_mem only) ----
MEM_CELL_M = 0.1                    # m, remembered points are thinned to one per cell
# ---- yaw ----
K_YAW = 1.5                         # 1/s, yaw towards the commanded velocity


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


class DWA(Planner):
    name = "dwa"

    def __init__(self, memory_s: float = 0.0, **kw):
        self.memory_s = memory_s
        self.p = dict(WINDOW_S=WINDOW_S, N_SAMPLES=N_SAMPLES, V_MAX=V_MAX, K_GOAL=K_GOAL,
                      HORIZON_S=HORIZON_S, SIM_DT=SIM_DT, SAFETY_M=SAFETY_M, A_BRAKE=A_BRAKE,
                      W_HEADING=W_HEADING, W_CLEAR=W_CLEAR, W_SPEED=W_SPEED,
                      CLEAR_CAP_M=CLEAR_CAP_M, K_YAW=K_YAW)
        for k, v in kw.items():
            if k not in self.p:
                raise TypeError(f"unknown DWA parameter {k}")
            self.p[k] = v
        if memory_s > 0:
            self.name = "dwa_mem"
        self.reset()

    def reset(self):
        self.mem = []                    # (t, points (n, 2)) for memory_s > 0
        self.no_admissible_steps = 0

    def _points(self, pose, scan):
        a = np.asarray(scan.angles) + pose.yaw
        d = np.asarray(scan.distances)
        ok = np.isfinite(d)
        pts = np.stack([pose.x + d[ok] * np.cos(a[ok]), pose.y + d[ok] * np.sin(a[ok])], 1)
        if self.memory_s <= 0:
            return pts
        self.mem.append((pose.t, pts))
        self.mem = [(t, q) for t, q in self.mem if t >= pose.t - self.memory_s - 1e-9]
        allp = np.concatenate([q for _, q in self.mem], 0)
        if not len(allp):
            return allp
        # one point per MEM_CELL_M cell keeps the rollout cost flat
        key = np.floor(allp / MEM_CELL_M).astype(np.int64)
        _, first = np.unique(key, axis=0, return_index=True)
        return allp[np.sort(first)]

    def step(self, pose, scan, goal, grid, dt):
        P = self.p
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist = math.hypot(ex, ey)
        pts = self._points(pose, scan)

        # 2. dynamic window samples
        dv = A_MAX * P["WINDOW_S"]
        g = np.linspace(-dv, dv, P["N_SAMPLES"])
        cx, cy = np.meshgrid(pose.vx + g, pose.vy + g, indexing="ij")
        cand = np.stack([cx.ravel(), cy.ravel()], 1)
        vcap = min(P["V_MAX"], P["K_GOAL"] * dist)
        sp = np.hypot(cand[:, 0], cand[:, 1])
        scale = np.where(sp > vcap, vcap / np.maximum(sp, 1e-9), 1.0)
        cand = np.vstack([cand * scale[:, None], [[0.0, 0.0]]])
        spd = np.hypot(cand[:, 0], cand[:, 1])

        # 3. rollout with the vehicle model
        n = max(1, int(round(P["HORIZON_S"] / P["SIM_DT"])))
        h = P["SIM_DT"]
        pos = np.tile([pose.x, pose.y], (len(cand), 1)).astype(float)
        vel = np.tile([pose.vx, pose.vy], (len(cand), 1)).astype(float)
        traj = np.empty((len(cand), n, 2))
        for k in range(n):
            acc = (cand - vel) / TAU
            an = np.hypot(acc[:, 0], acc[:, 1])
            acc *= np.minimum(1.0, A_MAX / np.maximum(an, 1e-9))[:, None]
            # exact enough: the lag would make acc shrink within the step; clip so vel does not overshoot
            vel = vel + acc * h
            over = np.sum((vel - cand) * acc, 1) > 0
            vel[over] = cand[over]
            pos = pos + vel * h
            traj[:, k] = pos

        # 4. clearance and admissibility
        if len(pts):
            diff = traj[:, :, None, :] - pts[None, None, :, :]
            dmin = np.sqrt(np.min(np.sum(diff * diff, -1), axis=(1, 2)))
            # the current position counts too (an obstacle already close)
            clear = dmin - RADIUS
        else:
            clear = np.full(len(cand), np.inf)
        free = clear - P["SAFETY_M"]
        ok = (free >= 0) & (spd <= np.sqrt(2 * P["A_BRAKE"] * np.maximum(free, 0.0)) + 1e-9)
        if not ok.any():
            self.no_admissible_steps += 1
            hg = math.atan2(ey, ex)
            return Setpoint(0.0, 0.0, 0.0, P["K_YAW"] * float(wrap(hg - pose.yaw)))

        # 5. cost
        end = traj[:, -1]
        bearing = np.arctan2(goal[1] - end[:, 1], goal[0] - end[:, 0])
        vdir = np.arctan2(cand[:, 1], cand[:, 0])
        head = 1.0 - np.abs(wrap(vdir - bearing)) / np.pi
        head = np.where(spd < 1e-6, 0.0, head)
        clr = np.minimum(clear, P["CLEAR_CAP_M"]) / P["CLEAR_CAP_M"]
        score = P["W_HEADING"] * head + P["W_CLEAR"] * clr + P["W_SPEED"] * spd / P["V_MAX"]
        score[~ok] = -np.inf
        i = int(np.argmax(score))
        vx, vy = float(cand[i, 0]), float(cand[i, 1])
        hd = math.atan2(vy, vx) if math.hypot(vx, vy) > 0.05 else math.atan2(ey, ex)
        return Setpoint(vx, vy, 0.0, P["K_YAW"] * float(wrap(hd - pose.yaw)))


def make(**kw) -> Planner:
    return DWA(**kw)
