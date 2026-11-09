"""Run a safety-filter arm from samples/close-area-safety-filter (the kill test) in this loop.

    safety = ArmShim("F2", world=ad.world)     # main.py: --safety arm:F2

The kill-test arms have the signature
    filter(setpoint, pose, scan, map_obstacles, health_dict, dt) -> (setpoint, intervened)
and this loop's SafetyFilter has
    filter(setpoint, pose, scan, health_report) -> (setpoint, intervened).
ArmShim converts: map_obstacles = the arena World (F0-F2 ignore it), health = the dict the kill
test builds from the pose (t, quality, reset_counter, sigma_xy), dt = the loop period 0.05 s.
The loop's NavHealth report (HealthReport: state ok / degraded / lost, reasons) goes to arms
whose filter() has a `nav_health` parameter, as filter(..., dt, nav_health=report). F0-F2 do
not have it and get the exact kill-test call. The loop still applies its own degraded cap and
lost => hover before the filter either way.

Differences from the kill-test harness (run_kill.py), which runs the arm at 50 Hz on a 16.7 Hz
scan: here the arm runs at 20 Hz on a fresh 20 Hz scan. F2's output low-pass gain is defined per
step at 100 Hz, so at dt 0.05 s it passes about 99 % of the new value each step.

Stdlib at import time. filters.py (numpy) loads when the shim is built.
"""
from __future__ import annotations

import importlib.util
import inspect
import os
import sys

try:
    from .adapter import Setpoint
except ImportError:
    from adapter import Setpoint

LOOP_DT_S = 0.05
_MOD = "close_area_safety_filter_filters"


def load_filters(filter_dir: str):
    """Load samples/close-area-safety-filter/filters.py by path, under a private module name."""
    if _MOD in sys.modules:
        return sys.modules[_MOD]
    path = os.path.join(os.path.abspath(filter_dir), "filters.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"filters.py not found in {filter_dir}: pass --safety-dir")
    spec = importlib.util.spec_from_file_location(_MOD, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MOD] = mod
    spec.loader.exec_module(mod)
    return mod


def accepts_nav_health(arm) -> bool:
    """True if arm.filter() takes a `nav_health` argument (the loop's HealthReport)."""
    try:
        return "nav_health" in inspect.signature(arm.filter).parameters
    except (TypeError, ValueError):
        return False


class ArmShim:
    """flightloop SafetyFilter around one kill-test arm (F0, F1, F2)."""

    def __init__(self, arm: str, filter_dir: str, world=None, dt: float = LOOP_DT_S, **overrides) -> None:
        self.filters = load_filters(filter_dir)
        self.arm = self.filters.make(arm, **overrides)
        self.name = f"arm:{arm}"
        self.world, self.dt = world, dt
        self.health_aware = accepts_nav_health(self.arm)

    def reset(self) -> None:
        self.arm.reset()

    def filter(self, setpoint, pose, scan, health):
        h = {"t": pose.t, "quality": pose.quality, "reset_counter": pose.reset_counter,
             "sigma_xy": pose.sigma_xy}
        kw = {"nav_health": health} if self.health_aware else {}
        sp, intervened = self.arm.filter(setpoint, pose, scan, self.world, h, self.dt, **kw)
        return Setpoint(float(sp.vx), float(sp.vy), float(sp.vz), float(sp.yaw_rate)), bool(intervened)
