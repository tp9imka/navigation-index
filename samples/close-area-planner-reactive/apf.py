"""Artificial potential field on raw range returns, with a wall-follow escape. No map.

Velocity form of Khatib 1986 (res:khatib-potential-fields-ijrr-1986):

  v_att = unit(B - p) * min(v_cruise, k_att * |B - p|)
  v_rep = sum over beams with clearance c = d - radius < c0:
          w * k_rep * (1/c - 1/c0) * (-u_beam)          (u_beam: world-frame beam direction)
  v     = v_att + v_rep, norm capped at v_cruise

w = (2 pi / n_beams) / (2 pi / 72), so a beam stands for its angular share of the circle and the
4-beam fan pushes as hard per sector of wall as the 72-beam fan does.

Brake (range-only): for every visible beam, the velocity component towards it is capped at
k_brake * (c - c_stop). A wall between beams is not seen and not braked for.

Escape rule, named "wall-follow after 3 s of no progress" (Bug-style, Lumelsky and Stepanov):
- progress = the best distance to B so far improved by at least 0.3 m. No progress for
  T_stall = 3 s => WALL_FOLLOW. Side = the side of the goal direction with more free range.
- WALL_FOLLOW: nearest return u_n at d_n. Command v_wf along the tangent (u_n rotated by
  side * 90 deg) plus k_d * (d_n - d_des) along u_n. Wall lost (no return within 1.5 m):
  turn towards where it was (last u_n rotated by side * 45 deg).
- Leave when |B - p| < d_hit - 0.5 m and no return within 1.5 m in +/- 45 deg of the goal
  direction. 25 s in WALL_FOLLOW without leaving => flip side once per episode.
- Two variants are off by default because they did worse on the dev seed
  (results/dev_seed1_tuning.md): stall_window (also trigger when distance to B fell < 0.3 m over
  the last 3 s) and wf_weighted (wall direction = weighted mean of close returns).
- escape=False gives plain APF (bench.py row apf_noescape).
Yaw follows the commanded velocity, so the front beam of a sparse fan faces travel.
"""
from __future__ import annotations

import math

try:
    from .arena import Planner, Setpoint
except ImportError:
    from arena import Planner, Setpoint


def wrap(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class APF(Planner):
    name = "apf"

    def __init__(self, v_cruise=1.0, k_att=1.0, c0=1.0, k_rep=0.25, radius=0.15,
                 k_brake=1.5, c_stop=0.1, k_yaw=1.5,
                 escape=True, t_stall=3.0, progress_m=0.3, v_wf=0.6, d_des=0.6, k_d=1.0,
                 leave_margin=0.5, leave_free=1.5, wf_flip_s=25.0, stall_window=False, wf_weighted=False):
        self.v_cruise, self.k_att, self.c0, self.k_rep, self.radius = v_cruise, k_att, c0, k_rep, radius
        self.k_brake, self.c_stop, self.k_yaw = k_brake, c_stop, k_yaw
        self.escape, self.t_stall, self.progress_m = escape, t_stall, progress_m
        self.v_wf, self.d_des, self.k_d = v_wf, d_des, k_d
        self.leave_margin, self.leave_free, self.wf_flip_s = leave_margin, leave_free, wf_flip_s
        self.stall_window, self.wf_weighted = stall_window, wf_weighted
        self.reset()

    def reset(self):
        self.mode = "apf"
        self.best = math.inf
        self.t_progress = None
        self.side = 1
        self.d_hit = math.inf
        self.t_wf = 0.0
        self.flipped = False
        self.u_last = None
        self.hist = []                   # (t, distance to B) over the last t_stall seconds
        self.log = []                    # (t, mode) on each mode change, for the README

    # ---- helpers ----
    def _returns(self, pose, scan):
        out = []
        for a, d in zip(scan.angles, scan.distances):
            if math.isfinite(d):
                out.append((wrap(pose.yaw + a), d))
        return out

    def _brake(self, vx, vy, rets):
        for phi, d in rets:
            if d > 1.5:
                continue
            ux, uy = math.cos(phi), math.sin(phi)
            toward = vx * ux + vy * uy
            cap = max(0.0, self.k_brake * (d - self.radius - self.c_stop))
            if toward > cap:
                vx -= (toward - cap) * ux
                vy -= (toward - cap) * uy
        return vx, vy

    def _set_mode(self, t, mode):
        self.mode = mode
        self.log.append((round(t, 2), mode))

    # ---- step ----
    def step(self, pose, scan, goal, grid, dt):
        t = pose.t
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist = math.hypot(ex, ey)
        hg = math.atan2(ey, ex)
        rets = self._returns(pose, scan)
        n = max(1, len(scan.angles))
        w = 72.0 / n

        if self.t_progress is None:
            self.t_progress = t
        self.hist.append((t, dist))
        while self.hist and self.hist[0][0] < t - self.t_stall - 1e-9:
            self.hist.pop(0)
        windowed = self.stall_window and (self.hist[0][0] <= t - self.t_stall + 0.05
                    and self.hist[0][1] - dist < self.progress_m)
        if dist < self.best - self.progress_m:
            self.best, self.t_progress = dist, t

        if self.mode == "apf" and self.escape and (t - self.t_progress > self.t_stall or windowed):
            # pick the freer side of the goal direction (sum of clipped ranges)
            left = right = 0.0
            for a, d in zip(scan.angles, scan.distances):
                rel = wrap(pose.yaw + a - hg)
                r = min(d, scan.max_range)
                if 0 < rel < math.pi:
                    left += r
                elif -math.pi < rel < 0:
                    right += r
            # side +1: tangent = u_n rotated +90 deg (go left, obstacle on the right)
            self.side = 1 if left >= right else -1
            self.d_hit, self.t_wf, self.flipped = dist, t, False
            self._set_mode(t, "wall_follow")

        if self.mode == "wall_follow":
            goal_free = all(not (abs(wrap(phi - hg)) <= math.radians(45) and d < self.leave_free)
                            for phi, d in rets)
            if dist < self.d_hit - self.leave_margin and goal_free:
                self.best, self.t_progress, self.hist = dist, t, []
                self._set_mode(t, "apf")
            elif t - self.t_wf > self.wf_flip_s and not self.flipped:
                self.side, self.flipped, self.t_wf = -self.side, True, t
                self._set_mode(t, "wall_follow_flip")
                self.mode = "wall_follow"

        if self.mode == "wall_follow":
            # wall direction = weighted mean of close returns (in a concave corner: the bisector)
            ax = ay = 0.0
            for phi_i, d_i in rets:
                if d_i < 1.5:
                    wgt = 1.0 / max(d_i - self.radius, 0.02) - 1.0 / 1.35
                    ax += wgt * math.cos(phi_i)
                    ay += wgt * math.sin(phi_i)
            near = min(rets, key=lambda r: r[1], default=None)
            if near is not None and near[1] < 1.5 and math.hypot(ax, ay) > 1e-9:
                phi, d = (math.atan2(ay, ax) if self.wf_weighted else near[0]), near[1]
                self.u_last = phi
                ux, uy = math.cos(phi), math.sin(phi)
                tx, ty = -self.side * uy, self.side * ux
                vx = self.v_wf * tx + self.k_d * (d - self.radius - self.d_des) * ux
                vy = self.v_wf * ty + self.k_d * (d - self.radius - self.d_des) * uy
            else:
                base = self.u_last if self.u_last is not None else hg
                a = base + self.side * math.radians(45)
                vx, vy = self.v_wf * math.cos(a), self.v_wf * math.sin(a)
        else:
            s = min(self.v_cruise, self.k_att * dist)
            vx, vy = (s * ex / dist, s * ey / dist) if dist > 1e-6 else (0.0, 0.0)
            cmax = self.c0
            for phi, d in rets:
                c = max(d - self.radius, 0.02)
                if c < cmax:
                    mag = w * self.k_rep * (1.0 / c - 1.0 / cmax)
                    vx -= mag * math.cos(phi)
                    vy -= mag * math.sin(phi)

        sp = math.hypot(vx, vy)
        if sp > self.v_cruise:
            vx, vy = vx * self.v_cruise / sp, vy * self.v_cruise / sp
        vx, vy = self._brake(vx, vy, rets)
        h = math.atan2(vy, vx) if math.hypot(vx, vy) > 0.05 else hg
        return Setpoint(vx, vy, 0.0, self.k_yaw * wrap(h - pose.yaw))


def make(**kw) -> Planner:
    return APF(**kw)
