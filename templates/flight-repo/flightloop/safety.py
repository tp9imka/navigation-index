"""Safety filter seam: last stage before send_setpoint. It may change the planner's setpoint
and must say whether it did (intervened), so the log shows how often the planner was unsafe.

RangeStop uses only the body-frame scan and yaw, not position, so a wrong position estimate
does not move its barrier. This is where the hub's integrity-aware filter idea plugs in
(docs/research/close-area-nav/README.md, "Recommended direction").
"""
from __future__ import annotations

import math
from typing import Protocol, runtime_checkable

try:
    from .adapter import Pose, RangeScan, Setpoint, body_to_world
    from .health import DEGRADED, HealthReport
except ImportError:
    from adapter import Pose, RangeScan, Setpoint, body_to_world
    from health import DEGRADED, HealthReport


@runtime_checkable
class SafetyFilter(Protocol):
    name: str

    def filter(self, setpoint: Setpoint, pose: Pose, scan: RangeScan,
               health: HealthReport) -> tuple[Setpoint, bool]: ...


class PassThrough:
    name = "pass_through"

    def filter(self, setpoint, pose, scan, health):
        return Setpoint(setpoint.vx, setpoint.vy, setpoint.vz, setpoint.yaw_rate), False


MARGIN_M = 0.35              # keep at least this far from any return (vehicle radius 0.15 + 0.20)
DEGRADED_EXTRA_MARGIN_M = 0.20  # added while nav health is degraded
A_BRAKE_MS2 = 2.0            # assumed braking deceleration for the stopping distance


class RangeStop:
    """For each return closer than margin + v_toward^2 / (2 * A_BRAKE_MS2), remove the
    horizontal velocity component toward it. Motion away from or along the obstacle stays."""
    name = "range_stop"

    def __init__(self, margin: float = MARGIN_M, a_brake: float = A_BRAKE_MS2,
                 degraded_extra: float = DEGRADED_EXTRA_MARGIN_M) -> None:
        self.margin, self.a_brake, self.degraded_extra = margin, a_brake, degraded_extra

    def filter(self, setpoint, pose, scan, health):
        margin = self.margin + (self.degraded_extra if health.state == DEGRADED else 0.0)
        vx, vy = setpoint.vx, setpoint.vy
        intervened = False
        for a, d in sorted(zip(scan.angles, scan.distances), key=lambda b: b[1]):
            if not math.isfinite(d):
                break
            ux, uy, _ = body_to_world((math.cos(a), math.sin(a), 0.0), pose.yaw)
            toward = vx * ux + vy * uy
            if toward > 0.0 and d < margin + toward * toward / (2.0 * self.a_brake):
                vx, vy = vx - toward * ux, vy - toward * uy
                intervened = True
        return Setpoint(vx, vy, setpoint.vz, setpoint.yaw_rate), intervened
