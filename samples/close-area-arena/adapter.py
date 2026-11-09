"""Published drone interface plus the simulator implementation of it.

Pose, RangeScan, Setpoint and Adapter are the published interface: field names are identical in
templates/drone-adapter. Planner code that only calls pose(), ranges() and send_setpoint()
ports to a real drone adapter unchanged.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Callable, Protocol


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


class Adapter(Protocol):
    def pose(self) -> Pose: ...
    def ranges(self) -> RangeScan: ...
    def send_setpoint(self, sp: Setpoint) -> None: ...


PoseSource = Callable[[Pose], Pose]
"""Hook for a later estimator: receives the truth Pose, returns the Pose the planner sees."""


class SimAdapter:
    """Adapter over the arena sim. The caller advances time with tick().

    pose() returns truth (quality 100, sigma_xy 0.0) unless `pose_source` is given; then it
    returns pose_source(truth). ranges() always ray-casts from the true pose: the sensor sees
    the real world even when the estimate is wrong. A setpoint older than `setpoint_timeout`
    seconds is replaced by zero velocity, like PX4 dropping out of Offboard.
    """

    def __init__(self, world, vehicle, sensor, pose_source: PoseSource | None = None,
                 setpoint_timeout: float = 0.5):
        self.world = world
        self.vehicle = vehicle
        self.sensor = sensor
        self.pose_source = pose_source
        self.setpoint_timeout = setpoint_timeout
        self._sp = Setpoint(0.0, 0.0, 0.0, 0.0)
        self._sp_t = -math.inf
        self.last_pose: Pose | None = None      # what the planner was last given

    # ---- Adapter ----
    def pose(self) -> Pose:
        truth = self.truth()
        p = self.pose_source(truth) if self.pose_source is not None else truth
        self.last_pose = p
        return p

    def ranges(self) -> RangeScan:
        v = self.vehicle
        return self.sensor.scan(self.world, v.p[0], v.p[1], v.yaw, v.t)

    def send_setpoint(self, sp: Setpoint) -> None:
        self._sp = replace(sp)
        self._sp_t = self.vehicle.t

    # ---- sim only ----
    def truth(self) -> Pose:
        v = self.vehicle
        return Pose(t=v.t, x=float(v.p[0]), y=float(v.p[1]), z=float(v.p[2]),
                    vx=float(v.v[0]), vy=float(v.v[1]), vz=float(v.v[2]), yaw=float(v.yaw),
                    quality=100, reset_counter=0, sigma_xy=0.0)

    def tick(self, n: int = 1) -> None:
        for _ in range(n):
            sp = self._sp if self.vehicle.t - self._sp_t <= self.setpoint_timeout + 1e-9 else Setpoint(0.0, 0.0, 0.0, 0.0)
            self.vehicle.step(sp.vx, sp.vy, sp.vz, sp.yaw_rate)
