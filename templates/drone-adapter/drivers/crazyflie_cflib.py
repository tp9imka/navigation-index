"""Crazyflie 2.x driver over cflib. Status: unrun, written from docs.

Setpoint path (mode="world", default): `commander.send_velocity_world_setpoint(vx, vy, vz,
yawrate_deg_s)`, world frame, needs a position estimate (Flow deck, Lighthouse, Loco, mocap).
Mode "hover": `commander.send_hover_setpoint(vx_body, vy_body, yawrate_deg_s, z_m)`, body frame
with an absolute height; the driver rotates with `world_to_body` and integrates vz into z.
A keep-alive thread streams at 20 Hz. Take-off and landing use the high-level commander; the
streamed setpoints win while they flow (CRTP priority 2 > high-level 1, firmware commander.h),
and `land()` calls `send_notify_setpoint_stop()` to hand control back first.
Pose: log blocks from `stateEstimate` (x, y, z m; vx, vy, vz m/s, world; yaw deg) plus
`kalman.varX/varY` for sigma_xy. Blocks are split because a cflib log block holds 26 bytes.
Ranges: Multi-ranger `range.front/left/back/right` (uint16 mm) => body angles 0, +pi/2, pi,
-pi/2; readings >= 8000 mm mean no return (same rule as cflib utils/multiranger.py).
`range.up` is logged and exposed as `self.up_m`, not put in the horizontal scan.

Docs used (fetched 2026-11-09):
- Bitcraze coordinate system: https://www.bitcraze.io/documentation/system/platform/cf2-coordinate-system/
- Firmware log variables: https://www.bitcraze.io/documentation/repository/crazyflie-firmware/master/api/logs/
- cflib commander.py, log.py, platformservice.py, utils/multiranger.py:
  https://github.com/bitcraze/crazyflie-lib-python/tree/master/cflib
- Firmware src/modules/interface/commander.h (setpoint priorities)
- ../frames.md (Crazyflie section)

Check on the bench first:
1. Frame alignment: command Setpoint(+0.2, 0, 0) for 1 s. It must move along OUR +x. With flow
   deck only, CF +X is the take-off heading; set `frame_yaw_offset` (rad, ENU angle of CF +X)
   if it is not aligned with our ENU.
2. Yaw-rate sign: Setpoint(0, 0, 0, yaw_rate=+0.3) must turn the nose LEFT. cflib negates
   yawrate itself for firmware protocol <= 8; flip YAW_RATE_SIGN if it turns right.
3. Watchdog and ranges: stop calling send_setpoint() => driver sends zero after 0.5 s; kill the
   script and check what the firmware does without setpoints (timeout not checked in docs).
   Put a hand 0.3 m in front: ranges() shows about 0.3 at angle 0.

Not confirmed: firmware streaming-setpoint watchdog timeouts; whether `supervisor` arming is
required on your firmware (the driver calls it if cflib has it).
"""
from __future__ import annotations

import math
import threading
import time
from typing import Callable

try:
    from ._common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,
                          RangeScan, Setpoint, body_to_world, empty_scan, world_to_body, wrap_pi)
except ImportError:
    from _common import (CMD_TIMEOUT_S, RATE_HZ, JumpCounter, KeepAlive, OriginLatch, Pose,  # type: ignore
                         RangeScan, Setpoint, body_to_world, empty_scan, world_to_body, wrap_pi)

YAW_RATE_SIGN = 1.0          # flip after bench check 2
NO_RETURN_MM = 8000          # cflib Multiranger: >= 8000 mm => None
MULTIRANGER_MAX_M = 4.0      # VL53L1x up to 4 m (Bitcraze product docs, via lane 02 doc)
LOG_PERIOD_MS = 20           # 50 Hz
RANGE_BEAMS = (("range.front", 0.0), ("range.left", math.pi / 2),
               ("range.back", math.pi), ("range.right", -math.pi / 2))


def mm_to_range(mm: int) -> float:
    return math.inf if mm >= NO_RETURN_MM else mm / 1000.0


def cf_to_enu(v, offset: float):
    """Vector in the CF world frame => our ENU (CF +X points at ENU angle `offset`)."""
    return body_to_world(v, offset)


def enu_to_cf(v, offset: float):
    return world_to_body(v, offset)


class CrazyflieCflibAdapter:
    """Adapter for a Crazyflie via cflib and a Crazyradio. Construct, `connect()`,
    `takeoff()`, `start()`, then the planner loop; `land()` at the end."""

    def __init__(self, uri: str = "radio://0/80/2M/E7E7E7E7E7", scf=None,
                 mode: str = "world", frame_yaw_offset: float = 0.0,
                 range_source: Callable[[], RangeScan] | None = None,
                 rate_hz: float = RATE_HZ, cmd_timeout_s: float = CMD_TIMEOUT_S) -> None:
        if mode not in ("world", "hover"):
            raise ValueError("mode must be 'world' or 'hover'")
        self.uri, self.scf, self.mode = uri, scf, mode
        self.offset = frame_yaw_offset
        self.range_source = range_source
        self._keepalive = KeepAlive(self._send, rate_hz, cmd_timeout_s)
        self._origin = OriginLatch()
        self._jumps = JumpCounter()
        self._lock = threading.Lock()
        self._s: dict[str, float] = {}
        self._t_pose = 0.0
        self._t_range = 0.0
        self._z_target: float | None = None
        self.up_m = math.inf
        self.down_m = math.inf

    @property
    def cf(self):
        return self.scf.cf

    # --- lifecycle ------------------------------------------------------------
    def connect(self, reset_estimator: bool = True) -> None:
        if self.scf is None:
            import cflib.crtp                 # lazy: `import drivers` works without the SDK
            from cflib.crazyflie import Crazyflie
            from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
            cflib.crtp.init_drivers()
            self.scf = SyncCrazyflie(self.uri, cf=Crazyflie(rw_cache="./cache"))
            self.scf.open_link()
        from cflib.crazyflie.log import LogConfig
        blocks = [
            ("pos", ["stateEstimate.x", "stateEstimate.y", "stateEstimate.z", "stateEstimate.yaw"]),
            ("vel", ["stateEstimate.vx", "stateEstimate.vy", "stateEstimate.vz"]),
            ("var", ["kalman.varX", "kalman.varY"]),
            ("rng", ["range.front", "range.back", "range.left", "range.right", "range.up",
                     "range.zrange"]),
        ]
        for name, names in blocks:            # each block <= 26 bytes (cflib LogConfig.MAX_LEN)
            lc = LogConfig(name=name, period_in_ms=LOG_PERIOD_MS)
            for n in names:
                lc.add_variable(n)
            lc.data_received_cb.add_callback(self._on_log)
            try:
                self.cf.log.add_config(lc)    # KeyError if a variable is missing (no deck)
            except (KeyError, AttributeError) as e:
                if name in ("pos", "vel"):
                    raise
                print(f"crazyflie: log block {name!r} skipped: {e}")   # no Multi-ranger => no ranges
                continue
            lc.start()
        if reset_estimator:
            self.cf.param.set_value("kalman.resetEstimation", "1")
            time.sleep(0.1)
            self.cf.param.set_value("kalman.resetEstimation", "0")
            time.sleep(2.0)                   # let the estimator settle; not tuned
        sup = getattr(self.cf, "supervisor", None)
        if sup is not None and hasattr(sup, "send_arming_request"):
            sup.send_arming_request(True)

    def takeoff(self, height_m: float = 0.5, duration_s: float = 2.0) -> None:
        self.cf.high_level_commander.takeoff(height_m, duration_s)
        time.sleep(duration_s + 0.5)

    def start(self, set_origin_here: bool = True) -> None:
        p = self._raw()
        if set_origin_here:
            self._origin.set(p[0])
        self._z_target = self._s.get("stateEstimate.z", 0.0)
        self._keepalive.submit(Setpoint(0.0, 0.0, 0.0))
        self._keepalive.start()

    def land(self, duration_s: float = 2.0) -> None:
        self._keepalive.stop()
        self.cf.commander.send_notify_setpoint_stop()
        self.cf.high_level_commander.land(0.0, duration_s)
        time.sleep(duration_s + 0.5)

    # --- Adapter protocol -----------------------------------------------------
    def pose(self) -> Pose:
        pos, yaw, vel, sigma = self._raw()
        x, y, z = self._origin.apply(pos)
        return Pose(self._t_pose, x, y, z, vel[0], vel[1], vel[2], yaw,
                    quality=-1, reset_counter=self._jumps.update((x, y, z)),
                    sigma_xy=sigma)            # Kalman covariance; may be overconfident

    def ranges(self) -> RangeScan:
        if self.range_source is not None:
            return self.range_source()
        with self._lock:
            s, t = dict(self._s), self._t_range
        if "range.front" not in s:
            return empty_scan(time.monotonic())
        return RangeScan(t, [a for _, a in RANGE_BEAMS],
                         [mm_to_range(int(s[n])) for n, _ in RANGE_BEAMS], MULTIRANGER_MAX_M)

    def send_setpoint(self, sp: Setpoint) -> None:
        self._keepalive.submit(sp)

    # --- internals ------------------------------------------------------------
    def _send(self, sp: Setpoint, dt: float) -> None:
        yawrate = YAW_RATE_SIGN * math.degrees(sp.yaw_rate)
        if self.mode == "world":
            vx, vy, vz = enu_to_cf((sp.vx, sp.vy, sp.vz), self.offset)
            self.cf.commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)
            return
        yaw_cf = math.radians(self._s.get("stateEstimate.yaw", 0.0))
        f, l, _ = world_to_body(enu_to_cf((sp.vx, sp.vy, 0.0), self.offset), yaw_cf)
        if self._z_target is None:
            self._z_target = self._s.get("stateEstimate.z", 0.0)
        self._z_target = max(0.1, self._z_target + sp.vz * min(dt, 0.2))
        self.cf.commander.send_hover_setpoint(f, l, yawrate, self._z_target)

    def _raw(self):
        with self._lock:
            s = dict(self._s)
        if "stateEstimate.x" not in s or "stateEstimate.vx" not in s:
            raise RuntimeError("no stateEstimate log data yet: call connect() and wait")
        pos = cf_to_enu((s["stateEstimate.x"], s["stateEstimate.y"], s["stateEstimate.z"]),
                        self.offset)
        vel = cf_to_enu((s["stateEstimate.vx"], s["stateEstimate.vy"], s["stateEstimate.vz"]),
                        self.offset)
        yaw = wrap_pi(math.radians(s["stateEstimate.yaw"]) + self.offset)
        var = max(s.get("kalman.varX", math.nan), s.get("kalman.varY", math.nan))
        sigma = math.sqrt(var) if var == var and var >= 0 else None   # NaN-safe
        return pos, yaw, vel, sigma

    def _on_log(self, timestamp, data, logconf) -> None:
        now = time.monotonic()
        with self._lock:
            self._s.update(data)
            if "stateEstimate.x" in data:
                self._t_pose = now
            if "range.front" in data:
                self._t_range = now
                self.up_m = mm_to_range(int(data["range.up"]))
                self.down_m = mm_to_range(int(data["range.zrange"]))
