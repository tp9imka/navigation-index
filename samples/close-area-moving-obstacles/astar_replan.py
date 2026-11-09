"""A* + ESDF that replans on a grid rebuilt from the prior map plus the latest range returns.

Reuses the arena's planners/astar_esdf.py (A*, ESDF clearance cost, shortcut, carrot follower,
speed from clearance) unchanged; only the map layer and the replan timing differ:

  map    every replan: occupied = prior static OccGrid OR the cells of the hits of the latest
         RangeScan. No memory of earlier scans, so a mover leaves no ghost trail and an old
         sighting never blocks a path. Moving obstacles are not in the prior map.
  timing periodic every REPLAN_PERIOD_S (0.4 s = 2.5 Hz), plus an early replan when a hit
         that is not in the prior map lies within RADIUS + TRACK_MARGIN of the current path,
         rate-limited to MIN_REPLAN_S (0.2 s = 5 Hz). So the rate stays between 2.5 and 5 Hz.
  follow between replans the carrot speed uses the ESDF of the last rebuilt grid.

No prediction: the planner sees where a mover is, not where it is going.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import distance_transform_edt

try:
    from . import arena
except ImportError:
    import arena

A = arena.astar_esdf
REPLAN_PERIOD_S = 0.4      # s, 2.5 Hz periodic (same as astar_esdf)
MIN_REPLAN_S = 0.2         # s, 5 Hz cap on event-triggered replans


class AStarReplan(A.AStarESDF):
    def __init__(self, replan_period_s: float = REPLAN_PERIOD_S, min_replan_s: float = MIN_REPLAN_S):
        super().__init__(known_map=True)
        self.name = "astar_replan"
        self.replan_period_s, self.min_replan_s = replan_period_s, min_replan_s

    def reset(self) -> None:
        super().reset()
        self.scan_occ = None
        self.replan_t: list[float] = []

    def _scan_cells(self, pose, scan, grid):
        a = pose.yaw + np.asarray(scan.angles, float)
        d = np.asarray(scan.distances, float)
        ok = np.isfinite(d)
        hx = np.floor((pose.x + d[ok] * np.cos(a[ok]) - grid.x0) / grid.res).astype(int)
        hy = np.floor((pose.y + d[ok] * np.sin(a[ok]) - grid.y0) / grid.res).astype(int)
        nx, ny = grid.occ.shape
        m = (hx >= 0) & (hy >= 0) & (hx < nx) & (hy < ny)
        return hx[m], hy[m]

    def _layers(self, grid):
        occ = grid.occ | self.scan_occ
        padded = np.pad(occ, 1, constant_values=True)
        esdf = (distance_transform_edt(~padded) * grid.res)[1:-1, 1:-1]
        self.geo = (grid.res, grid.x0, grid.y0) + occ.shape
        return np.zeros_like(occ), esdf

    def step(self, pose, scan, goal, grid, dt):
        hx, hy = self._scan_cells(pose, scan, grid)
        occ = np.zeros_like(grid.occ)
        occ[hx, hy] = True
        self.scan_occ = occ
        new = np.column_stack([hx, hy])[~grid.occ[hx, hy]] if len(hx) else np.zeros((0, 2), int)
        if self.geo is None:
            self.geo = (grid.res, grid.x0, grid.y0) + grid.occ.shape
        since = pose.t - self.last_plan_t
        due = since >= self.replan_period_s - 1e-9
        early = since >= self.min_replan_s - 1e-9 and self._blocked_by(new)
        if due or early or self.path_xy is None:
            self._plan(pose, goal, grid)
            self.last_plan_t = pose.t
            self.replan_t.append(pose.t)
        if self.path_xy is None:
            return arena.Setpoint(0.0, 0.0, 0.0, 0.0)
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist_goal = math.hypot(ex, ey)
        c = self._carrot(pose.x, pose.y)
        cx, cy = c[0] - pose.x, c[1] - pose.y
        dc = math.hypot(cx, cy)
        if dc < 1e-6:
            return arena.Setpoint(0.0, 0.0, 0.0, 0.0)
        clr = self._min_esdf((pose.x, pose.y), c)
        frac = (clr - A.V_CLEAR_STOP_M) / (A.V_CLEAR_FULL_M - A.V_CLEAR_STOP_M)
        speed = A.V_CRUISE * min(1.0, max(A.V_MIN_FRAC, frac))
        speed = min(speed, A.K_GOAL * dist_goal)
        h = math.atan2(cy, cx)
        yaw_err = (h - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        return arena.Setpoint(speed * cx / dc, speed * cy / dc, 0.0, A.K_YAW * yaw_err)


def make(**kw) -> AStarReplan:
    return AStarReplan(**kw)
