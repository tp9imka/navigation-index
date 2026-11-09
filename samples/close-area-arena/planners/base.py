"""Planner contract. A planner turns (pose, scan, goal, grid) into one velocity Setpoint.

It may keep state between calls. It must not read the sim: only the arguments. grid is the
0.1 m OccGrid (world.OccGrid) when the run gives the planner a prior map, else None.
"""
from __future__ import annotations

try:
    from ..adapter import Pose, RangeScan, Setpoint
except ImportError:
    from adapter import Pose, RangeScan, Setpoint


class Planner:
    name = "base"
    uses_grid = False          # True => run.py passes the prior OccGrid, else None

    def reset(self) -> None:
        """Called once before each run."""

    def step(self, pose: Pose, scan: RangeScan, goal: tuple[float, float, float],
             grid, dt: float) -> Setpoint:
        raise NotImplementedError
