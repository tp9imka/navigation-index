"""PX4 driver over MAVSDK-Python Offboard. Status: unrun, written from docs.

Setpoint path: Offboard `set_velocity_ned(VelocityNedYaw(north_m_s, east_m_s, down_m_s, yaw_deg))`.
VelocityNedYaw takes an ABSOLUTE heading (deg, 0 = north, CW), not a yaw rate (frames.md).
The driver integrates `Setpoint.yaw_rate` into an ENU heading target `psi` and sends
`degrees(yaw_enu_to_ned(psi))`. A keep-alive thread streams the latest setpoint at 20 Hz; it
starts BEFORE `offboard.start()`, because PX4 refuses Offboard without a setpoint stream.
Pose: telemetry `position_velocity_ned()` + `attitude_euler()`, NED => ENU, minus the pose at A.
Ranges: a pluggable `range_source()` callable, else telemetry `distance_sensor()` (one beam).

Docs used (fetched 2026-11-09):
- MAVSDK-Python offboard: https://mavsdk-python-docs.s3.amazonaws.com/plugins/offboard.html
- MAVSDK-Python telemetry: https://mavsdk-python-docs.s3.amazonaws.com/plugins/telemetry.html
- PX4 Offboard mode: https://docs.px4.io/main/en/flight_modes/offboard.html
- PX4 frame conventions: https://docs.px4.io/main/en/ros2/user_guide.html
- ../frames.md (PX4 section)

Check on the bench first (props off, then SITL, then a tethered hover):
1. Heading: send Setpoint(0, 0, 0, yaw_rate=+0.3). The nose must turn LEFT (CCW seen from
   above) and stop turning when yaw_rate returns to 0. If it turns right, the sign is wrong.
2. Axes and origin: right after `start_offboard()`, `pose()` reads about (0, 0, 0). A +x
   setpoint moves the vehicle EAST, +z climbs. If the EKF has no heading reference (indoor,
   no mag), "east" is whatever the EKF thinks; check it against the room.
3. Keep-alive: `start_offboard()` is accepted only after the stream runs; stop calling
   `send_setpoint()` and the vehicle hovers after 0.5 s (driver timeout); kill the script and
   PX4 leaves Offboard after COM_OF_LOSS_T (check the configured failsafe action).

Not confirmed: the connection URL scheme for your MAVSDK version ("udpin://0.0.0.0:14540" in
newer releases, "udp://:14540" in older ones), and how `distance_sensor()` behaves with more than
one sensor (the type has no sensor id).
"""
from __future__ import annotations

import asyncio
import math
import threading
import time
from typing import Callable

try:
    from ._common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,
                          RangeScan, Setpoint, empty_scan, enu_to_ned, ned_to_enu, wrap_pi,
                          yaw_enu_to_ned, yaw_ned_to_enu)
except ImportError:
    from _common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,  # type: ignore
                         RangeScan, Setpoint, empty_scan, enu_to_ned, ned_to_enu, wrap_pi,
                         yaw_enu_to_ned, yaw_ned_to_enu)

MAX_HEADING_LEAD = math.radians(30.0)   # heading target may lead the measured yaw by this much
MAX_DT = 0.2                            # clamp for the yaw integration step, seconds


def heading_step(psi: float, yaw_rate: float, dt: float, yaw_now: float | None,
                 max_lead: float = MAX_HEADING_LEAD) -> float:
    """Integrate an ENU yaw rate into an ENU heading target. Keeps the target within
    `max_lead` of the measured yaw so a slow vehicle does not wind up a large error."""
    psi = wrap_pi(psi + yaw_rate * min(max(dt, 0.0), MAX_DT))
    if yaw_now is not None:
        err = wrap_pi(psi - yaw_now)
        if abs(err) > max_lead:
            psi = wrap_pi(yaw_now + math.copysign(max_lead, err))
    return psi


def ned_velocity_yaw(sp: Setpoint, psi_enu: float) -> tuple[float, float, float, float]:
    """ENU Setpoint + ENU heading target => (north, east, down, yaw_deg) for VelocityNedYaw."""
    n, e, d = enu_to_ned((sp.vx, sp.vy, sp.vz))
    return (n, e, d, math.degrees(yaw_enu_to_ned(psi_enu)))


def distance_sensor_beam(current_m: float, max_m: float, yaw_deg: float,
                         pitch_deg: float) -> tuple[float, float] | None:
    """MAVSDK DistanceSensor => (body angle rad CCW, distance m), or None for an up/down sensor.
    Orientation yaw is CW (MAVSDK EulerAngle); RangeScan angles are CCW."""
    if abs(pitch_deg) > 45.0:
        return None
    if math.isnan(current_m) or current_m <= 0.0 or (not math.isnan(max_m) and current_m >= max_m):
        d = math.inf
    else:
        d = current_m
    return (wrap_pi(-math.radians(yaw_deg)), d)


class Px4MavsdkAdapter:
    """Adapter for a PX4 vehicle via MAVSDK-Python. Construct, `connect()`, take off with your
    own tooling or `arm_and_takeoff()`, then `start_offboard()`; the planner then calls
    pose() / ranges() / send_setpoint()."""

    def __init__(self, address: str = "udpin://0.0.0.0:14540",
                 range_source: Callable[[], RangeScan] | None = None,
                 rate_hz: float = RATE_HZ, cmd_timeout_s: float = CMD_TIMEOUT_S) -> None:
        self.address = address
        self.range_source = range_source
        self._keepalive = KeepAlive(self._send, rate_hz, cmd_timeout_s)
        self._origin = OriginLatch()
        self._jumps = JumpCounter()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._drone = None
        self._sdk = None                      # mavsdk.offboard module, set in connect()
        self._pv = None                       # latest PositionVelocityNed
        self._yaw_deg: float | None = None    # latest attitude_euler yaw, NED deg
        self._t_pose = 0.0
        self._ds = None                       # latest DistanceSensor
        self._t_ds = 0.0
        self._psi: float | None = None        # ENU heading target, rad

    # --- lifecycle ------------------------------------------------------------
    def connect(self, timeout_s: float = 30.0) -> None:
        from mavsdk import System             # lazy: `import drivers` works without the SDK
        from mavsdk import offboard
        self._sdk = offboard
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True, name="mavsdk").start()

        async def _connect():
            drone = System()
            await drone.connect(system_address=self.address)
            async for state in drone.core.connection_state():
                if state.is_connected:
                    break
            self._drone = drone
            for coro in (self._watch_pv(), self._watch_att(), self._watch_ds()):
                asyncio.ensure_future(coro)
        self._run(_connect(), timeout_s)

    def arm_and_takeoff(self, altitude_m: float = 1.0, wait_s: float = 8.0) -> None:
        async def _go():
            await self._drone.action.set_takeoff_altitude(altitude_m)
            await self._drone.action.arm()
            await self._drone.action.takeoff()
        self._run(_go(), 15.0)
        time.sleep(wait_s)

    def start_offboard(self, set_origin_here: bool = True, prestream_s: float = 1.0) -> None:
        """Stream zero velocity, then switch to Offboard. Stores point A unless told not to."""
        p = self._raw_enu()
        if set_origin_here:
            self._origin.set(p[0])
        self._psi = p[1]
        self._keepalive.submit(Setpoint(0.0, 0.0, 0.0))
        self._keepalive.start()               # stream first: PX4 needs setpoints before Offboard
        time.sleep(prestream_s)
        self._run(self._drone.offboard.start(), 5.0)

    def stop(self, land: bool = True) -> None:
        """Leave Offboard (PX4 goes to Hold), then land if asked."""
        try:
            self._run(self._drone.offboard.stop(), 5.0)
        finally:
            self._keepalive.stop()
        if land:
            self._run(self._drone.action.land(), 5.0)

    # --- Adapter protocol -----------------------------------------------------
    def pose(self) -> Pose:
        (x, y, z), yaw, (vx, vy, vz) = self._raw_enu(with_vel=True)
        x, y, z = self._origin.apply((x, y, z))
        return Pose(self._t_pose, x, y, z, vx, vy, vz, yaw,
                    quality=-1,                       # MAVSDK telemetry exposes no ODOMETRY.quality
                    reset_counter=self._jumps.update((x, y, z)),
                    sigma_xy=None)

    def ranges(self) -> RangeScan:
        if self.range_source is not None:
            return self.range_source()
        ds = self._ds
        if ds is None:
            return empty_scan(time.monotonic())
        beam = distance_sensor_beam(ds.current_distance_m, ds.maximum_distance_m,
                                    ds.orientation.yaw_deg, ds.orientation.pitch_deg)
        if beam is None:
            return empty_scan(self._t_ds)
        mx = ds.maximum_distance_m if not math.isnan(ds.maximum_distance_m) else math.inf
        return RangeScan(self._t_ds, [beam[0]], [beam[1]], mx)

    def send_setpoint(self, sp: Setpoint) -> None:
        self._keepalive.submit(sp)            # the keep-alive thread does the actual send

    # --- internals ------------------------------------------------------------
    def _send(self, sp: Setpoint, dt: float) -> None:
        yaw_now = None if self._yaw_deg is None else yaw_ned_to_enu(math.radians(self._yaw_deg))
        if self._psi is None:
            self._psi = yaw_now or 0.0
        self._psi = heading_step(self._psi, sp.yaw_rate, dt, yaw_now)
        n, e, d, yaw_deg = ned_velocity_yaw(sp, self._psi)
        cmd = self._sdk.VelocityNedYaw(n, e, d, yaw_deg)
        self._run(self._drone.offboard.set_velocity_ned(cmd), 0.5)

    def _raw_enu(self, with_vel: bool = False):
        pv, yaw_deg = self._pv, self._yaw_deg
        if pv is None or yaw_deg is None:
            raise RuntimeError("no telemetry yet: call connect() and wait for position/attitude")
        pos = ned_to_enu((pv.position.north_m, pv.position.east_m, pv.position.down_m))
        yaw = yaw_ned_to_enu(math.radians(yaw_deg))
        if not with_vel:
            return pos, yaw
        vel = ned_to_enu((pv.velocity.north_m_s, pv.velocity.east_m_s, pv.velocity.down_m_s))
        return pos, yaw, vel

    def _run(self, coro, timeout_s: float):
        if self._loop is None:
            raise RuntimeError("call connect() first")
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout_s)

    async def _watch_pv(self):
        async for pv in self._drone.telemetry.position_velocity_ned():
            self._pv, self._t_pose = pv, time.monotonic()

    async def _watch_att(self):
        async for att in self._drone.telemetry.attitude_euler():
            self._yaw_deg = att.yaw_deg

    async def _watch_ds(self):
        async for ds in self._drone.telemetry.distance_sensor():
            self._ds, self._t_ds = ds, time.monotonic()
