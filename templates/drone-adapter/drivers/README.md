# drivers: Adapter implementations for real platforms

Status of every driver: **unrun, written from docs.** No SDK was installed and no vehicle, SITL
or radio was touched. What did run is the smoke test below, on fake connection objects.
Each driver file starts with a docstring: the doc links used and the 3 things to check on the
bench first. Do those before any planner flight.

## Platform table

| Platform | Driver (class) | SDK pip name | Setpoint path | Pose source | Known traps |
|---|---|---|---|---|---|
| PX4 (SITL or real) | `px4_mavsdk.py` (`Px4MavsdkAdapter`) | `mavsdk` | Offboard `set_velocity_ned(VelocityNedYaw(n, e, d, yaw_deg))`, 20 Hz keep-alive started before `offboard.start()` | telemetry `position_velocity_ned()` + `attitude_euler()`, NED => ENU, minus A | VelocityNedYaw takes an absolute heading: the driver integrates yaw_rate into a heading target (capped 30 deg ahead of measured yaw). No ODOMETRY quality in MAVSDK telemetry => `quality=-1`. `distance_sensor()` has no sensor id (one beam). URL scheme differs between MAVSDK versions |
| ArduPilot Copter | `ardupilot_pymavlink.py` (`ArduPilotPymavlinkAdapter`) | `pymavlink` | GUIDED, `SET_POSITION_TARGET_LOCAL_NED`, `MAV_FRAME_LOCAL_NED`, mask 1479 (vel + yaw rate) or 3527 (vel only), 20 Hz | `LOCAL_POSITION_NED` + `ATTITUDE`, rates requested with `MAV_CMD_SET_MESSAGE_INTERVAL` | DISTANCE_SENSOR orientation: MAVLink text calls YAW_90 left, ArduPilot code treats it as 90 deg clockwise (right); driver follows ArduPilot (`ORIENT_SIGN`). OBSTACLE_DISTANCE defaults to north-aligned bins. Indoors the EKF needs an origin before LOCAL_POSITION_NED is usable. Stops after 3 s without commands |
| Crazyflie 2.x | `crazyflie_cflib.py` (`CrazyflieCflibAdapter`) | `cflib` | `send_velocity_world_setpoint(vx, vy, vz, yawrate_deg_s)` (mode "world") or `send_hover_setpoint` (mode "hover"), 20 Hz; take-off and land via high-level commander | log blocks `stateEstimate.x/y/z/yaw`, `stateEstimate.vx/vy/vz`, `kalman.varX/varY` => sigma_xy | Log block max 26 bytes => split blocks. CF world frame = take-off heading with flow deck only: set `frame_yaw_offset`. Yaw-rate sign on current firmware not confirmed (`YAW_RATE_SIGN`). Ranges `range.*` are mm, >= 8000 = no return. Must call `land()` (notify_setpoint_stop) to hand back to the high-level commander |
| DJI Tello / RoboMaster TT | `tello_djitellopy.py` (`TelloDjitellopyAdapter`) | `djitellopy` | `send_rc_control(lr, fb, ud, yaw)`, ints -100..100 stick values, 10 Hz | dead reckoning on `get_speed_x/y()` + `get_yaw()` + `get_height()`; `quality=10`, `sigma_xy=None` | rc values are stick deflection, not cm/s: `STICK_PER_MPS`, `STICK_PER_MPS_Z`, `STICK_PER_DEG_S`, `VEL_UNIT_M` default to None and the driver refuses to fly until set. Speed units and frame undocumented. No obstacle sensor: `ranges()` returns an empty scan (no beams), never "clear". Lands after 15 s without a command |

Every number in this table comes from the driver docstrings, which cite their sources, or from
[../frames.md](../frames.md).

## Shared behaviour (`_common.py`)

- **Keep-alive.** `send_setpoint()` only stores the setpoint. A thread re-sends the latest one at
  the driver rate. If the planner is silent for 0.5 s (`CMD_TIMEOUT_S`) it sends zero velocity.
- **Origin at A.** `start()` (PX4: `start_offboard()`) latches x and y. z stays the estimator's
  height above its own origin, usually the take-off floor, so goal z = 1.0 means 1 m up, as in
  the mock. `OriginLatch(keep_z=False)` makes z = 0 where you call `start()`.
- **reset_counter.** None of the four SDK paths exposes ODOMETRY `reset_counter`. `JumpCounter`
  counts position steps larger than 0.5 m between samples (`JUMP_M`). Heuristic only.
- **Pluggable ranges.** Every driver takes `range_source=callable` returning a `RangeScan`, for a
  depth camera or lidar on the companion.

## Use

```python
from drone_adapter.drivers import Px4MavsdkAdapter
from drone_adapter.example_loop import fly_to

ad = Px4MavsdkAdapter("udpin://0.0.0.0:14540")
ad.connect(); ad.arm_and_takeoff(1.0); ad.start_offboard()
fly_to(ad, (3.0, 0.0, 1.0), realtime=True)
ad.stop(land=True)
```

Install the SDK in a project venv only (`python3 -m venv .venv && .venv/bin/pip install mavsdk`),
never into the global interpreter.

## What ran

From the repo root: `sh templates/drone-adapter/drivers/results/run_smoke.sh`. Output on
2026-11-09 is in [results/2026-11-09-smoke-run.txt](results/2026-11-09-smoke-run.txt)
(synthetic input: fake connection objects). It shows: none of `mavsdk`, `pymavlink`, `cflib`,
`djitellopy` was importable on Python 3.12.10 or 3.14.6; all 7 files parse; each of the four
classes has `pose`, `ranges`, `send_setpoint`; `python3 -m unittest -v` inside
`templates/drone-adapter` ran 10 tests OK on both interpreters (5 existing, 5 in
`test_drivers_smoke.py`); the copied `drone_adapter.drivers` package imports and its 5 tests pass.

The smoke test checks conversions against frames.md (ENU east => NED (0, 1, 0), ENU yaw 0 =>
90 deg NED, CCW yaw rate => negative NED rate, mask 1479, Multi-ranger mm => m, Tello +y =>
negative lr stick). It does not prove any SDK call signature beyond what the docs say.

## Not verified

- Any SDK call against a real SDK, SITL or vehicle.
- PX4 behaviour when yaw is commanded as a moving heading target at 20 Hz.
- ArduPilot EKF origin requirement indoors; default stream rates without the interval requests.
- Crazyflie streaming-setpoint watchdog timeouts; whether supervisor arming is required.
- Tello stick-to-speed scale, rc signs, `get_yaw()` sign, `get_speed_*` units and frame.
