"""Drone-agnostic seam: three calls a planner needs, plus frame helpers.

Planner code talks only to `Adapter.pose()`, `Adapter.ranges()` and
`Adapter.send_setpoint()`. Everything is local ENU (x east, y north, z up, metres,
origin at point A) and body FLU (x forward, y left, z up). Each platform driver converts
at its own boundary; see frames.md for what each autopilot or SDK expects.

Stdlib only. Field names are shared with samples/close-area-arena; do not rename them.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

Vec3 = tuple[float, float, float]


@dataclass
class Pose:            # local ENU frame, metres, origin at point A
    t: float
    x: float; y: float; z: float
    vx: float; vy: float; vz: float
    yaw: float                     # rad, ENU, CCW from +x
    quality: int = -1              # 0-100 like MAVLink ODOMETRY.quality, -1 unknown
    reset_counter: int = 0         # increments on estimator jumps/resets
    sigma_xy: float | None = None  # reported 1-sigma horizontal, metres (may be overconfident)


@dataclass
class RangeScan:       # body frame
    t: float
    angles: list[float]            # rad, CCW, 0 = forward
    distances: list[float]         # metres, math.inf = no return
    max_range: float


@dataclass
class Setpoint:        # velocity command, local ENU
    vx: float; vy: float; vz: float
    yaw_rate: float = 0.0


@runtime_checkable
class Adapter(Protocol):
    def pose(self) -> Pose: ...
    def ranges(self) -> RangeScan: ...
    def send_setpoint(self, sp: Setpoint) -> None: ...


# ---------------------------------------------------------------------------
# Frame helpers. Vectors are (x, y, z) tuples: positions or velocities alike.
# Yaw angles are radians; results are wrapped to (-pi, pi].
# Yaw rates flip sign in both conversions because the vertical axis flips.
# ---------------------------------------------------------------------------

def wrap_pi(a: float) -> float:
    """Wrap an angle to (-pi, pi]."""
    a = math.fmod(a + math.pi, 2.0 * math.pi)
    if a <= 0.0:
        a += 2.0 * math.pi
    return a - math.pi


def enu_to_ned(v: Vec3) -> Vec3:
    """World vector ENU (east, north, up) => NED (north, east, down)."""
    e, n, u = v
    return (n, e, -u)


def ned_to_enu(v: Vec3) -> Vec3:
    """World vector NED (north, east, down) => ENU (east, north, up)."""
    n, e, d = v
    return (e, n, -d)


def flu_to_frd(v: Vec3) -> Vec3:
    """Body vector FLU (forward, left, up) => FRD (forward, right, down)."""
    f, l, u = v
    return (f, -l, -u)


def frd_to_flu(v: Vec3) -> Vec3:
    """Body vector FRD (forward, right, down) => FLU (forward, left, up)."""
    f, r, d = v
    return (f, -r, -d)


def yaw_enu_to_ned(yaw_enu: float) -> float:
    """Heading CCW from east (ENU) => heading CW from north (NED, MAVLink / PX4 / ArduPilot)."""
    return wrap_pi(math.pi / 2.0 - yaw_enu)


def yaw_ned_to_enu(yaw_ned: float) -> float:
    """Heading CW from north (NED) => heading CCW from east (ENU)."""
    return wrap_pi(math.pi / 2.0 - yaw_ned)


def yaw_rate_enu_to_ned(rate: float) -> float:
    """Yaw rate about +up => about +down. Same for FLU => FRD."""
    return -rate


yaw_rate_ned_to_enu = yaw_rate_enu_to_ned
yaw_rate_flu_to_frd = yaw_rate_enu_to_ned
yaw_rate_frd_to_flu = yaw_rate_enu_to_ned


def world_to_body(v: Vec3, yaw: float) -> Vec3:
    """ENU world vector => FLU body vector, given ENU yaw. Ignores roll and pitch
    (fine for velocity commands to a level-flying multirotor)."""
    c, s = math.cos(yaw), math.sin(yaw)
    x, y, z = v
    return (c * x + s * y, -s * x + c * y, z)


def body_to_world(v: Vec3, yaw: float) -> Vec3:
    """FLU body vector => ENU world vector, given ENU yaw. Ignores roll and pitch."""
    c, s = math.cos(yaw), math.sin(yaw)
    f, l, u = v
    return (c * f - s * l, s * f + c * l, u)
