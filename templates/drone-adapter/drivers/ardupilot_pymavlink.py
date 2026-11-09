"""ArduPilot Copter driver over pymavlink in GUIDED mode. Status: unrun, written from docs.

Setpoint path: SET_POSITION_TARGET_LOCAL_NED, frame MAV_FRAME_LOCAL_NED (1), type_mask 1479
(velocity + yaw rate) or 3527 (velocity only), streamed at 20 Hz by a keep-alive thread.
Copter stops after 3 s without a velocity command (frames.md). Conversion:
`enu_to_ned(v)`, `yaw_rate_enu_to_ned(r)` (rad/s, CW positive in NED).
Pose: LOCAL_POSITION_NED + ATTITUDE (yaw rad, NED), NED => ENU, minus the pose at A.
Ranges: DISTANCE_SENSOR (cm; ArduPilot also sends its proximity sectors this way) and
OBSTACLE_DISTANCE (72 cm bins) if some component on the link broadcasts it; or a pluggable
`range_source()` callable.

Docs used (fetched 2026-11-09):
- ArduPilot Copter commands in Guided mode: https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html
- MAVLink common messages: https://mavlink.io/en/messages/common.html
  (SET_POSITION_TARGET_LOCAL_NED, LOCAL_POSITION_NED, ATTITUDE, DISTANCE_SENSOR, OBSTACLE_DISTANCE,
  MAV_CMD_SET_MESSAGE_INTERVAL)
- ArduPilot code: libraries/GCS_MAVLink/GCS_Common.cpp (send_proximity => DISTANCE_SENSOR),
  libraries/AP_Proximity/AP_Proximity_MAV.cpp (orientation * 45 deg)
- pymavlink mavutil.py (mavlink_connection, set_mode, arducopter_arm, motors_armed_wait)
- ../frames.md (ArduPilot section)

Check on the bench first:
1. Range orientation: hold a board on the vehicle's RIGHT. The beam must come out at body angle
   -pi/2. MAVLink's DISTANCE_SENSOR text calls YAW_90 "left-facing", while ArduPilot's proximity
   code treats orientation * 45 deg as a clockwise yaw (YAW_90 = right). This driver follows
   ArduPilot; flip ORIENT_SIGN if your sensor disagrees.
2. Pose exists indoors: LOCAL_POSITION_NED only makes sense once the EKF has an origin (GPS, or
   an origin set for non-GPS flight). Check messages arrive at the requested rate and that
   `pose()` reads about (0, 0, 0) at A.
3. Yaw-rate sign and mask: Setpoint(0, 0, 0, yaw_rate=+0.3) must turn the nose LEFT. Then stop
   the planner: the driver sends zero after 0.5 s; kill the script and the vehicle should stop
   within 3 s.
"""
from __future__ import annotations

import math
import threading
import time
from typing import Callable

try:
    from ._common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,
                          RangeScan, Setpoint, empty_scan, enu_to_ned, ned_to_enu, wrap_pi,
                          yaw_ned_to_enu, yaw_rate_enu_to_ned)
except ImportError:
    from _common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,  # type: ignore
                         RangeScan, Setpoint, empty_scan, enu_to_ned, ned_to_enu, wrap_pi,
                         yaw_ned_to_enu, yaw_rate_enu_to_ned)

MAV_FRAME_LOCAL_NED = 1
MAV_FRAME_GLOBAL = 0
MAV_FRAME_BODY_FRD = 12
MASK_VEL = 3527            # 0x0DC7: ignore position, accel, yaw, yaw rate
MASK_VEL_YAWRATE = 1479    # 3527 - 2048: also use yaw rate
MAV_CMD_SET_MESSAGE_INTERVAL = 511
MSG_ATTITUDE, MSG_LOCAL_POSITION_NED, MSG_DISTANCE_SENSOR = 30, 32, 132
ORIENT_SIGN = 1            # +1: orientation*45 deg is CW (ArduPilot). -1: CCW (MAVLink text)
STALE_RANGE_S = 1.0        # drop range readings older than this
UINT16_MAX = 65535


def setpoint_to_local_ned(sp: Setpoint, use_yaw_rate: bool = True):
    """ENU Setpoint => (type_mask, vx, vy, vz, yaw_rate) for SET_POSITION_TARGET_LOCAL_NED."""
    vn, ve, vd = enu_to_ned((sp.vx, sp.vy, sp.vz))
    if use_yaw_rate:
        return MASK_VEL_YAWRATE, vn, ve, vd, yaw_rate_enu_to_ned(sp.yaw_rate)
    return MASK_VEL, vn, ve, vd, 0.0


def distance_sensor_to_beam(orientation: int, current_cm: int, min_cm: int, max_cm: int):
    """DISTANCE_SENSOR => (body angle rad CCW, distance m), or None for up/down/custom sensors."""
    if orientation > 7:                      # only ROTATION_NONE..YAW_315 are horizontal
        return None
    angle = wrap_pi(-ORIENT_SIGN * math.radians(45.0 * orientation))
    if current_cm >= max_cm or current_cm < min_cm:
        return (angle, math.inf)
    return (angle, current_cm / 100.0)


def obstacle_distance_to_beams(distances, increment, increment_f, angle_offset, max_cm,
                               frame, yaw_enu: float):
    """OBSTACLE_DISTANCE => list of (body angle rad CCW, distance m). Bins are clockwise.
    frame 0 (MAV_FRAME_GLOBAL, the default) is north-aligned, so the vehicle yaw is removed."""
    inc = increment_f if increment_f else float(increment)
    if inc == 0:
        return []
    out = []
    for i, d in enumerate(distances):
        if d == UINT16_MAX:
            continue                          # unknown / unused bin
        cw_deg = (angle_offset or 0.0) + i * inc
        if frame == MAV_FRAME_BODY_FRD:
            ang = -math.radians(cw_deg)
        else:                                 # north-aligned, CW from north => body CCW
            ang = yaw_ned_to_enu(math.radians(cw_deg)) - yaw_enu
        out.append((wrap_pi(ang), math.inf if d > max_cm else d / 100.0))
    return out


class ArduPilotPymavlinkAdapter:
    """Adapter for ArduPilot Copter via pymavlink. Construct, `connect()`, `arm_and_takeoff()`
    (or take off by hand and switch to GUIDED), `start()`, then the planner loop."""

    def __init__(self, url: str = "udpin:0.0.0.0:14550", conn=None,
                 range_source: Callable[[], RangeScan] | None = None,
                 use_yaw_rate: bool = True, rate_hz: float = RATE_HZ,
                 cmd_timeout_s: float = CMD_TIMEOUT_S, telemetry_hz: float = 30.0) -> None:
        self.url = url
        self.conn = conn                     # pass a pymavlink connection (or a fake) to skip connect()
        self.range_source = range_source
        self.use_yaw_rate = use_yaw_rate
        self.telemetry_hz = telemetry_hz
        self._keepalive = KeepAlive(self._send, rate_hz, cmd_timeout_s)
        self._origin = OriginLatch()
        self._jumps = JumpCounter()
        self._lock = threading.Lock()
        self._lpn = None
        self._att = None
        self._t_pose = 0.0
        self._ds: dict[int, tuple[float, object]] = {}   # sensor id => (t, msg)
        self._od: tuple[float, object] | None = None
        self._stop = threading.Event()
        self._rx: threading.Thread | None = None
        self._t0 = time.monotonic()

    # --- lifecycle ------------------------------------------------------------
    def connect(self, timeout_s: float = 30.0) -> None:
        if self.conn is None:
            from pymavlink import mavutil     # lazy: `import drivers` works without the SDK
            self.conn = mavutil.mavlink_connection(self.url)
        self.conn.wait_heartbeat(timeout=timeout_s)
        for msg_id in (MSG_ATTITUDE, MSG_LOCAL_POSITION_NED, MSG_DISTANCE_SENSOR):
            self._command_long(MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, 1e6 / self.telemetry_hz)
        self._rx = threading.Thread(target=self._recv_loop, daemon=True, name="mavlink-rx")
        self._rx.start()

    def arm_and_takeoff(self, altitude_m: float = 1.0, wait_s: float = 8.0) -> None:
        self.conn.set_mode("GUIDED")
        self.conn.arducopter_arm()
        self.conn.motors_armed_wait()
        self._command_long(22, 0, 0, 0, 0, 0, 0, altitude_m)   # MAV_CMD_NAV_TAKEOFF
        time.sleep(wait_s)

    def start(self, set_origin_here: bool = True) -> None:
        """Store point A and start the 20 Hz setpoint stream. Vehicle must be in GUIDED."""
        if set_origin_here:
            self._origin.set(self._raw_enu()[0])
        self._keepalive.submit(Setpoint(0.0, 0.0, 0.0))
        self._keepalive.start()

    def stop(self, land: bool = True) -> None:
        self._keepalive.stop()
        if land:
            self.conn.set_mode("LAND")
        self._stop.set()

    # --- Adapter protocol -----------------------------------------------------
    def pose(self) -> Pose:
        (x, y, z), yaw, (vx, vy, vz) = self._raw_enu()
        x, y, z = self._origin.apply((x, y, z))
        return Pose(self._t_pose, x, y, z, vx, vy, vz, yaw,
                    quality=-1,                # no ODOMETRY.quality from ArduPilot by default
                    reset_counter=self._jumps.update((x, y, z)),
                    sigma_xy=None)

    def ranges(self) -> RangeScan:
        if self.range_source is not None:
            return self.range_source()
        now = time.monotonic()
        beams: list[tuple[float, float]] = []
        max_range = 0.0
        with self._lock:
            ds = list(self._ds.values())
            od = self._od
            att = self._att
        for t, m in ds:
            if now - t > STALE_RANGE_S:
                continue
            b = distance_sensor_to_beam(m.orientation, m.current_distance, m.min_distance,
                                        m.max_distance)
            if b is not None:
                beams.append(b)
                max_range = max(max_range, m.max_distance / 100.0)
        if od is not None and now - od[0] <= STALE_RANGE_S and att is not None:
            m = od[1]
            beams += obstacle_distance_to_beams(
                m.distances, m.increment, getattr(m, "increment_f", 0.0),
                getattr(m, "angle_offset", 0.0), m.max_distance,
                getattr(m, "frame", MAV_FRAME_GLOBAL), yaw_ned_to_enu(att.yaw))
            max_range = max(max_range, m.max_distance / 100.0)
        if not beams:
            return empty_scan(now)
        beams.sort()
        return RangeScan(now, [a for a, _ in beams], [d for _, d in beams], max_range)

    def send_setpoint(self, sp: Setpoint) -> None:
        self._keepalive.submit(sp)

    # --- internals ------------------------------------------------------------
    def _send(self, sp: Setpoint, dt: float) -> None:
        mask, vn, ve, vd, r = setpoint_to_local_ned(sp, self.use_yaw_rate)
        boot_ms = int((time.monotonic() - self._t0) * 1000) & 0xFFFFFFFF
        self.conn.mav.set_position_target_local_ned_send(
            boot_ms, self.conn.target_system, self.conn.target_component,
            MAV_FRAME_LOCAL_NED, mask,
            0.0, 0.0, 0.0, vn, ve, vd, 0.0, 0.0, 0.0, 0.0, r)

    def _command_long(self, cmd: int, *params: float) -> None:
        p = list(params) + [0.0] * (7 - len(params))
        self.conn.mav.command_long_send(self.conn.target_system, self.conn.target_component,
                                        cmd, 0, *p[:7])

    def _raw_enu(self):
        with self._lock:
            lpn, att = self._lpn, self._att
        if lpn is None or att is None:
            raise RuntimeError("no LOCAL_POSITION_NED / ATTITUDE yet (EKF origin set?)")
        return (ned_to_enu((lpn.x, lpn.y, lpn.z)), yaw_ned_to_enu(att.yaw),
                ned_to_enu((lpn.vx, lpn.vy, lpn.vz)))

    def handle(self, m) -> None:
        """Feed one received message. Public so a test or a replay can call it directly."""
        kind = m.get_type()
        now = time.monotonic()
        with self._lock:
            if kind == "LOCAL_POSITION_NED":
                self._lpn, self._t_pose = m, now
            elif kind == "ATTITUDE":
                self._att = m
            elif kind == "DISTANCE_SENSOR":
                self._ds[m.id * 64 + m.orientation] = (now, m)
            elif kind == "OBSTACLE_DISTANCE":
                self._od = (now, m)

    def _recv_loop(self) -> None:
        types = ["LOCAL_POSITION_NED", "ATTITUDE", "DISTANCE_SENSOR", "OBSTACLE_DISTANCE"]
        while not self._stop.is_set():
            m = self.conn.recv_match(type=types, blocking=True, timeout=0.5)
            if m is not None:
                self.handle(m)
