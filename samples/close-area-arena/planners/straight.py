"""Baseline: fly the straight line to B, slow down for obstacles ahead in the scan, never steer.

Speed = min(cruise, k_goal * distance to B) times a scale from the nearest return within
+/- cone of the travel direction: 1 beyond slow_dist, 0 at stop_dist. So it stops in front of
an obstacle on the line (=> "stuck") rather than flying into it. Yaw turns towards B.
"""
from __future__ import annotations

import math

try:
    from ..adapter import Setpoint
    from .base import Planner
except ImportError:
    from adapter import Setpoint
    from planners.base import Planner


class StraightPlanner(Planner):
    name = "straight"

    def __init__(self, cruise: float = 1.5, k_goal: float = 1.0, stop_dist: float = 0.4,
                 slow_dist: float = 2.0, cone: float = math.radians(30), k_yaw: float = 1.5):
        self.cruise, self.k_goal = cruise, k_goal
        self.stop_dist, self.slow_dist, self.cone, self.k_yaw = stop_dist, slow_dist, cone, k_yaw

    def step(self, pose, scan, goal, grid, dt):
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist = math.hypot(ex, ey)
        if dist < 1e-6:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        heading = math.atan2(ey, ex)
        ahead = math.inf
        for a, d in zip(scan.angles, scan.distances):
            rel = (pose.yaw + a - heading + math.pi) % (2 * math.pi) - math.pi
            if abs(rel) <= self.cone and d < ahead:
                ahead = d
        scale = min(1.0, max(0.0, (ahead - self.stop_dist) / (self.slow_dist - self.stop_dist)))
        speed = min(self.cruise, self.k_goal * dist) * scale
        yaw_err = (heading - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        return Setpoint(speed * ex / dist, speed * ey / dist, 0.0, self.k_yaw * yaw_err)


def make(**kw) -> Planner:
    return StraightPlanner(**kw)
