"""VFH+ on raw range returns (Ulrich and Borenstein 1998, res:ulrich-borenstein-vfhplus-icra-1998). No map.

Per planner step, from the current scan only:
1. Primary polar histogram, n_sec = 72 sectors of 5 deg, world frame. Each return at d < d_max
   adds m = w * (a - b d^2) (a - b d_max^2 = 1, b = 1) to every sector within the enlargement
   angle gamma = asin(min(1, r_rs / d)), r_rs = radius + d_s. w = 72 / n_beams, so one beam of
   a sparse fan stands for its share of the circle. VFH+ builds this histogram from a certainty
   grid in an active window; here each beam is read once (certainty 1), so there is no grid.
2. Binary histogram with hysteresis: blocked if H > tau_high, free if H < tau_low, else the
   previous step's value.
3. Masked histogram: skipped. VFH+ masks sectors a car-like robot cannot turn into; a
   multicopter is holonomic, so every free sector is reachable.
4. Valleys = runs of free sectors. Wide valley (> s_max sectors): candidates k_r + s_max/2,
   k_l - s_max/2 and the goal sector if it lies inside. Narrow valley: its centre.
   Cost g = mu1 * |c - k_goal| + mu2 * |c - k_heading| + mu3 * |c - k_prev| (mu1 > mu2 + mu3,
   as in the paper). No valley => hold position and yaw at yaw_search rad/s.
5. Speed from obstacle density: v = v_max * (1 - min(H_c, h_m) / h_m), floor v_min, where H_c is
   the primary histogram in the chosen sector. Yaw follows the chosen direction.
No escape rule: VFH+ as published has none, so this measures where it gets stuck on its own.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from .arena import Planner, Setpoint
except ImportError:
    from arena import Planner, Setpoint


def wrap(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


class VFHPlus(Planner):
    name = "vfh_plus"

    def __init__(self, n_sec=72, d_max=3.0, radius=0.15, d_s=0.1, tau_low=12.0, tau_high=24.0,
                 s_max=16, mu1=5.0, mu2=2.0, mu3=2.0, v_max=1.0, v_min=0.15, h_m=40.0,
                 k_yaw=1.5, yaw_search=0.8):
        self.n_sec, self.d_max, self.r_rs = n_sec, d_max, radius + d_s
        self.tau_low, self.tau_high, self.s_max = tau_low, tau_high, s_max
        self.mu1, self.mu2, self.mu3 = mu1, mu2, mu3
        self.v_max, self.v_min, self.h_m, self.k_yaw, self.yaw_search = v_max, v_min, h_m, k_yaw, yaw_search
        self.b = 1.0
        self.a = 1.0 + self.b * d_max ** 2
        self.alpha = 2 * math.pi / n_sec
        self.centres = -math.pi + (np.arange(n_sec) + 0.5) * self.alpha
        self.reset()

    def reset(self):
        self.binary = np.zeros(self.n_sec, bool)
        self.k_prev = None
        self.no_valley_steps = 0

    def sector(self, ang: float) -> int:
        return int((wrap(ang) + math.pi) // self.alpha) % self.n_sec

    def histogram(self, pose, scan) -> np.ndarray:
        h = np.zeros(self.n_sec)
        w = 72.0 / max(1, len(scan.angles))
        for a, d in zip(scan.angles, scan.distances):
            if not math.isfinite(d) or d >= self.d_max:
                continue
            beta = pose.yaw + a
            m = w * (self.a - self.b * d * d)
            gamma = math.asin(min(1.0, self.r_rs / max(d, 1e-3)))
            diff = np.abs((self.centres - beta + math.pi) % (2 * math.pi) - math.pi)
            h[diff <= gamma] += m
        return h

    def _dist(self, i: int, j: int) -> int:
        d = abs(i - j) % self.n_sec
        return min(d, self.n_sec - d)

    def valleys(self, free: np.ndarray) -> list[list[int]]:
        n = self.n_sec
        if free.all():
            return [list(range(n))]
        if not free.any():
            return []
        start = int(np.flatnonzero(~free)[0])        # rotate so index 0 is blocked
        out, cur = [], []
        for s in range(1, n + 1):
            k = (start + s) % n
            if free[k]:
                cur.append(k)
            elif cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
        return out

    def step(self, pose, scan, goal, grid, dt):
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist = math.hypot(ex, ey)
        k_t = self.sector(math.atan2(ey, ex))
        k_h = self.sector(pose.yaw)
        hp = self.histogram(pose, scan)
        self.binary = np.where(hp > self.tau_high, True, np.where(hp < self.tau_low, False, self.binary))
        vals = self.valleys(~self.binary)
        if not vals:
            self.no_valley_steps += 1
            return Setpoint(0.0, 0.0, 0.0, self.yaw_search)
        cands = []
        for v in vals:
            if len(v) == self.n_sec:
                cands.append(k_t)
                continue
            if len(v) > self.s_max:
                cands.append(v[self.s_max // 2])
                cands.append(v[-1 - self.s_max // 2])
                if k_t in v:
                    cands.append(k_t)
            else:
                cands.append(v[len(v) // 2])
        kp = self.k_prev if self.k_prev is not None else k_t

        def cost(c):
            return self.mu1 * self._dist(c, k_t) + self.mu2 * self._dist(c, k_h) + self.mu3 * self._dist(c, kp)

        c = min(cands, key=cost)
        self.k_prev = c
        direction = math.atan2(ey, ex) if c == k_t else float(self.centres[c])
        speed = max(self.v_min, self.v_max * (1.0 - min(hp[c], self.h_m) / self.h_m))
        speed = min(speed, dist)
        return Setpoint(speed * math.cos(direction), speed * math.sin(direction), 0.0,
                        self.k_yaw * wrap(direction - pose.yaw))


def make(**kw) -> Planner:
    return VFHPlus(**kw)
