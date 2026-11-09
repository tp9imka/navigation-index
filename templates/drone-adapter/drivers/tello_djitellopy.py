"""DJI Tello / RoboMaster TT driver over djitellopy. Status: unrun, written from docs.

Setpoint path: `send_rc_control(lr, fb, ud, yaw)`, ints -100..100. These are STICK values, not
cm/s (frames.md correction). The driver converts ENU m/s => body FLU with `world_to_body`, then
lr = -left, fb = forward, ud = up, yaw = -yaw_rate (stick +yaw is clockwise), each scaled by a
bench-calibrated constant: STICK_PER_MPS (horizontal), STICK_PER_MPS_Z (vertical),
STICK_PER_DEG_S (yaw). They default to None and the driver refuses to fly until you set them.
A keep-alive thread re-sends at 10 Hz; the Tello lands after 15 s without a command.
Pose: DEAD RECKONING. The Tello reports no position. The driver integrates `get_speed_x/y()`
(units and frame undocumented in djitellopy => VEL_UNIT_M and SPEED_FRAME are bench constants),
yaw from `get_yaw()` (deg) relative to the take-off heading, z from `get_height()` (cm).
`quality` is fixed at QUALITY_DEAD_RECKONING = 10 and `sigma_xy` is None: drift is unbounded
and nothing measures it. Use mission pads or an external system if position matters.
Ranges: the Tello has no obstacle sensor. `ranges()` returns an empty scan (no beams,
max_range 0) so a planner cannot read it as clear space. Pass `range_source` to add one.

Docs used (fetched 2026-11-09):
- djitellopy tello.py (send_rc_control, set_speed, state getters):
  https://github.com/damiafuentes/DJITelloPy/blob/master/djitellopy/tello.py
- TelloPilots thread quoting Tello SDK 2.0 `rc` (search snippet only):
  https://tellopilots.com/threads/is-continuous-movement-available.3485/
- ../frames.md (Tello section), docs/research/close-area-nav/02-sims-platforms-competitions.md

Check on the bench first (calibrate before any planner flight):
1. Stick scale: hover, send rc 0 50 0 0 for 2.0 s (`calibrate_forward(50, 2.0)`), measure the
   distance d in metres. STICK_PER_MPS = 50 / (d / 2.0). Repeat for up/down and yaw.
2. Signs: +lr must go RIGHT, +fb forward, +ud up, +yaw clockwise. These are common usage, not
   confirmed in docs. Then check `get_yaw()` sign (assumed clockwise positive => YAW_SIGN = -1).
3. Speed telemetry: fly forward at a known speed; read get_speed_x/y. Set VEL_UNIT_M (metres
   per reported unit) and SPEED_FRAME ("body" or "takeoff") from what you see.
"""
from __future__ import annotations

import math
import threading
import time
from typing import Callable

try:
    from ._common import (KeepAlive, Pose, RangeScan, Setpoint, body_to_world, world_to_body,
                          wrap_pi)
except ImportError:
    from _common import (KeepAlive, Pose, RangeScan, Setpoint, body_to_world,  # type: ignore
                         world_to_body, wrap_pi)

# --- bench constants: None = not calibrated, the driver refuses to fly -------
STICK_PER_MPS: float | None = None      # rc stick units per m/s, horizontal
STICK_PER_MPS_Z: float | None = None    # rc stick units per m/s, vertical
STICK_PER_DEG_S: float | None = None    # rc stick units per deg/s of yaw rate
VEL_UNIT_M: float | None = None         # metres per second per get_speed_* unit
SPEED_FRAME = "body"                    # "body" or "takeoff": frame of get_speed_x/y (unknown)
YAW_SIGN = -1.0                         # get_yaw() assumed clockwise positive => ENU = -yaw

QUALITY_DEAD_RECKONING = 10             # fixed, low: no measurement of drift exists
RATE_HZ = 10.0
CMD_TIMEOUT_S = 0.5
STICK_MAX = 100
BEAM_ANGLES = [0.0, math.pi / 2, math.pi, -math.pi / 2]


def _clamp_stick(v: float) -> int:
    return int(max(-STICK_MAX, min(STICK_MAX, round(v))))


def setpoint_to_rc(sp: Setpoint, yaw_enu: float, k_xy: float, k_z: float,
                   k_yaw: float) -> tuple[int, int, int, int]:
    """ENU Setpoint => (lr, fb, ud, yaw) stick ints, following frames.md."""
    f, l, u = world_to_body((sp.vx, sp.vy, sp.vz), yaw_enu)
    return (_clamp_stick(-k_xy * l), _clamp_stick(k_xy * f), _clamp_stick(k_z * u),
            _clamp_stick(-k_yaw * math.degrees(sp.yaw_rate)))


def speed_to_enu(vx_raw: float, vy_raw: float, yaw_enu: float, unit_m: float,
                 frame: str = "body") -> tuple[float, float]:
    """Tello get_speed_x/y => ENU (vx, vy) in our frame (+x = take-off heading).
    Assumes x forward and y right in the reported frame (not confirmed)."""
    f, r = vx_raw * unit_m, vy_raw * unit_m
    if frame == "body":
        e, n, _ = body_to_world((f, -r, 0.0), yaw_enu)
        return e, n
    return f, -r


class TelloDjitellopyAdapter:
    """Adapter for a Tello via djitellopy over Wi-Fi. Set the bench constants (module level or
    constructor), `connect()`, `takeoff()`, `start()`, planner loop, `land()`."""

    def __init__(self, tello=None, stick_per_mps: float | None = None,
                 stick_per_mps_z: float | None = None, stick_per_deg_s: float | None = None,
                 vel_unit_m: float | None = None, speed_frame: str | None = None,
                 range_source: Callable[[], RangeScan] | None = None,
                 rate_hz: float = RATE_HZ, cmd_timeout_s: float = CMD_TIMEOUT_S) -> None:
        self.tello = tello                    # pass a djitellopy.Tello (or a fake) to skip connect()
        self.k_xy = stick_per_mps if stick_per_mps is not None else STICK_PER_MPS
        self.k_z = stick_per_mps_z if stick_per_mps_z is not None else STICK_PER_MPS_Z
        self.k_yaw = stick_per_deg_s if stick_per_deg_s is not None else STICK_PER_DEG_S
        self.vel_unit_m = vel_unit_m if vel_unit_m is not None else VEL_UNIT_M
        self.speed_frame = speed_frame or SPEED_FRAME
        self.range_source = range_source
        self._keepalive = KeepAlive(self._send, rate_hz, cmd_timeout_s)
        self._lock = threading.Lock()
        self._yaw0_deg: float | None = None
        self._z0 = 0.0
        self._x = self._y = 0.0
        self._v = (0.0, 0.0, 0.0)
        self._yaw = 0.0
        self._t = time.monotonic()

    # --- lifecycle ------------------------------------------------------------
    def connect(self) -> None:
        if self.tello is None:
            from djitellopy import Tello      # lazy: `import drivers` works without the SDK
            self.tello = Tello()
        self.tello.connect()

    def takeoff(self) -> None:
        self.tello.takeoff()

    def start(self) -> None:
        """Point A = here; +x = current heading. Starts the 10 Hz rc stream."""
        self._require_calibration()
        with self._lock:
            self._yaw0_deg = float(self.tello.get_yaw())
            self._z0 = 0.0                    # get_height() is already relative to take-off
            self._x = self._y = 0.0
            self._t = time.monotonic()
        self._keepalive.submit(Setpoint(0.0, 0.0, 0.0))
        self._keepalive.start()

    def land(self) -> None:
        self._keepalive.stop()
        self.tello.send_rc_control(0, 0, 0, 0)
        self.tello.land()

    def calibrate_forward(self, stick: int = 50, duration_s: float = 2.0) -> None:
        """Bench step 1: fly forward at a fixed stick value, then stop. Measure the distance."""
        t_end = time.monotonic() + duration_s
        while time.monotonic() < t_end:
            self.tello.send_rc_control(0, int(stick), 0, 0)
            time.sleep(0.1)
        self.tello.send_rc_control(0, 0, 0, 0)

    # --- Adapter protocol -----------------------------------------------------
    def pose(self) -> Pose:
        with self._lock:
            z = self.tello.get_height() / 100.0 - self._z0
            return Pose(self._t, self._x, self._y, z, self._v[0], self._v[1], self._v[2],
                        self._yaw, quality=QUALITY_DEAD_RECKONING, reset_counter=0,
                        sigma_xy=None)

    def ranges(self) -> RangeScan:
        if self.range_source is not None:
            return self.range_source()
        # no range sensor: empty scan, so a planner cannot mistake it for clear space
        return RangeScan(time.monotonic(), [], [], 0.0)

    def send_setpoint(self, sp: Setpoint) -> None:
        self._require_calibration()
        self._keepalive.submit(sp)

    # --- internals ------------------------------------------------------------
    def _require_calibration(self) -> None:
        missing = [n for n, v in (("STICK_PER_MPS", self.k_xy), ("STICK_PER_MPS_Z", self.k_z),
                                  ("STICK_PER_DEG_S", self.k_yaw), ("VEL_UNIT_M", self.vel_unit_m))
                   if v is None]
        if missing:
            raise RuntimeError(f"Tello not calibrated: set {', '.join(missing)} (see docstring)")

    def _send(self, sp: Setpoint, dt: float) -> None:
        self._dead_reckon(dt)
        self.tello.send_rc_control(*setpoint_to_rc(sp, self._yaw, self.k_xy, self.k_z, self.k_yaw))

    def _dead_reckon(self, dt: float) -> None:
        t = self.tello
        yaw = wrap_pi(YAW_SIGN * math.radians(float(t.get_yaw()) - (self._yaw0_deg or 0.0)))
        vx, vy = speed_to_enu(float(t.get_speed_x()), float(t.get_speed_y()), yaw,
                              self.vel_unit_m, self.speed_frame)
        vz = float(t.get_speed_z()) * self.vel_unit_m   # sign not confirmed
        dt = min(max(dt, 0.0), 0.5)
        with self._lock:
            self._x += vx * dt
            self._y += vy * dt
            self._v, self._yaw, self._t = (vx, vy, vz), yaw, time.monotonic()
