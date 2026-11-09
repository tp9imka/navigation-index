"""Shared pieces for the platform drivers. Stdlib only, no SDK imports.

- `import_adapter()`: the dataclasses and frame helpers, whether this folder is used as a
  package (`drone_adapter.drivers`) or run flat from inside templates/drone-adapter.
- `OriginLatch`: stores the first pose as point A and subtracts it afterwards.
- `JumpCounter`: increments `reset_counter` when the reported position jumps.
- `KeepAlive`: background thread that re-sends the last setpoint at a fixed rate and sends
  zero velocity if the planner has gone quiet (PX4 Offboard, ArduPilot GUIDED, Crazyflie
  streaming setpoints and Tello all stop, hold or land without fresh commands).
"""
from __future__ import annotations

import math
import threading
import time
from typing import Callable

try:                                    # package: drone_adapter.drivers
    from ..adapter import (Pose, RangeScan, Setpoint, body_to_world, enu_to_ned,  # noqa: F401
                           ned_to_enu, world_to_body, wrap_pi, yaw_enu_to_ned,
                           yaw_ned_to_enu, yaw_rate_enu_to_ned)
except ImportError:                     # flat: run from inside templates/drone-adapter
    from adapter import (Pose, RangeScan, Setpoint, body_to_world, enu_to_ned,  # noqa: F401
                         ned_to_enu, world_to_body, wrap_pi, yaw_enu_to_ned,
                         yaw_ned_to_enu, yaw_rate_enu_to_ned)

Vec3 = tuple[float, float, float]
ZERO = Setpoint(0.0, 0.0, 0.0, 0.0)

# Defaults shared by all drivers. Change per platform after the bench test.
RATE_HZ = 20.0          # keep-alive send rate; PX4 needs >= 2 Hz (frames.md)
CMD_TIMEOUT_S = 0.5     # planner silent longer than this => send zero velocity
JUMP_M = 0.5            # position step between two samples that counts as a reset


class OriginLatch:
    """Point A = ENU position passed to `set` (or the first one seen).

    By default only x and y are latched: z stays the estimator's height above its own origin,
    which for PX4, ArduPilot and Crazyflie is usually the take-off ground. A planner goal
    z = 1.0 then means 1 m above the floor at A, as in the mock. Pass `keep_z=False` to make
    z = 0 wherever `set` was called (for example in the air).
    """

    def __init__(self, keep_z: bool = True) -> None:
        self.keep_z = keep_z
        self.origin: Vec3 | None = None

    def set(self, p: Vec3) -> None:
        self.origin = (p[0], p[1], 0.0 if self.keep_z else p[2])

    def apply(self, p: Vec3) -> Vec3:
        if self.origin is None:
            self.set(p)
        ox, oy, oz = self.origin
        return (p[0] - ox, p[1] - oy, p[2] - oz)


class JumpCounter:
    """Counts position steps larger than `jump_m` between consecutive samples.
    A heuristic: fast flight at a low telemetry rate can also trigger it."""

    def __init__(self, jump_m: float = JUMP_M) -> None:
        self.jump_m = jump_m
        self.count = 0
        self._last: Vec3 | None = None

    def update(self, p: Vec3) -> int:
        if self._last is not None and math.dist(p, self._last) > self.jump_m:
            self.count += 1
        self._last = p
        return self.count


class KeepAlive:
    """Calls `send(sp)` at `rate_hz` with the latest setpoint from `submit()`.

    If `submit()` has not been called for `timeout_s`, it sends ZERO instead, so a crashed
    or stalled planner leaves the vehicle hovering, not drifting at the last velocity.
    `send` gets the time since its previous call as `dt` (seconds), for drivers that integrate.
    """

    def __init__(self, send: Callable[[Setpoint, float], None], rate_hz: float = RATE_HZ,
                 timeout_s: float = CMD_TIMEOUT_S) -> None:
        self._send = send
        self.period = 1.0 / rate_hz
        self.timeout_s = timeout_s
        self._sp = ZERO
        self._t_submit = 0.0
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_error: BaseException | None = None

    def submit(self, sp: Setpoint) -> None:
        with self._lock:
            self._sp, self._t_submit = sp, time.monotonic()

    def current(self) -> Setpoint:
        with self._lock:
            stale = time.monotonic() - self._t_submit > self.timeout_s
            return ZERO if stale else self._sp

    def start(self) -> None:
        if self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, daemon=True, name="keepalive")
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _run(self) -> None:
        t_prev = time.monotonic()
        next_t = t_prev
        while not self._stop.is_set():
            now = time.monotonic()
            try:
                self._send(self.current(), now - t_prev)
            except Exception as e:          # keep streaming; the driver can inspect last_error
                self.last_error = e
            t_prev = now
            next_t += self.period
            self._stop.wait(max(0.0, next_t - time.monotonic()))


def empty_scan(t: float, angles: list[float] | None = None, max_range: float = 0.0) -> RangeScan:
    """Scan with no returns. Default: no beams at all (the planner sees "no sensor")."""
    angles = list(angles or [])
    return RangeScan(t, angles, [math.inf] * len(angles), max_range)
