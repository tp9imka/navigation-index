"""Planner seam. Same shape as samples/close-area-arena/planners/base.py in the hub, so
arena planners drop in unchanged (they return the arena's Setpoint, which has the same fields).

step() reads only its arguments: pose, body-frame scan, goal (x, y, z) in local ENU, grid
(prior occupancy grid or None) and dt (planner period, s). It must not talk to the vehicle.
"""
from __future__ import annotations

import math
from typing import Protocol, runtime_checkable

try:
    from .adapter import Pose, RangeScan, Setpoint, world_to_body
except ImportError:
    from adapter import Pose, RangeScan, Setpoint, world_to_body


@runtime_checkable
class Planner(Protocol):
    name: str
    uses_grid: bool

    def reset(self) -> None: ...

    def step(self, pose: Pose, scan: RangeScan, goal: tuple[float, float, float],
             grid, dt: float) -> Setpoint: ...


V_MAX_MS = 1.0               # cruise speed cap
K_P = 0.8                    # 1/s, velocity per metre of error
STOP_DIST_M = 0.6            # a return closer than this inside the cone => stop horizontally
STOP_CONE_RAD = math.radians(30)


class GoToGoal:
    """Straight at the goal, P on position error, stop if a return ahead is closer than
    STOP_DIST_M. Never steers around anything: it is the plumbing baseline."""
    name = "go_to_goal"
    uses_grid = False

    def __init__(self, v_max: float = V_MAX_MS, k_p: float = K_P,
                 stop_dist: float = STOP_DIST_M, cone: float = STOP_CONE_RAD) -> None:
        self.v_max, self.k_p, self.stop_dist, self.cone = v_max, k_p, stop_dist, cone

    def reset(self) -> None:
        pass

    def step(self, pose, scan, goal, grid, dt):
        err = (goal[0] - pose.x, goal[1] - pose.y, goal[2] - pose.z)
        v = [self.k_p * e for e in err]
        n = math.sqrt(sum(c * c for c in v))
        if n > self.v_max:
            v = [c * self.v_max / n for c in v]
        bx, by, _ = world_to_body((v[0], v[1], 0.0), pose.yaw)
        if math.hypot(bx, by) > 1e-9:
            heading = math.atan2(by, bx)
            if any(d < self.stop_dist and abs(math.remainder(a - heading, math.tau)) < self.cone
                   for a, d in zip(scan.angles, scan.distances)):
                v[0] = v[1] = 0.0
        return Setpoint(v[0], v[1], v[2], 0.0)
