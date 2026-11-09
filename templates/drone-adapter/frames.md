# Frame conventions per platform

The planner always works in local **ENU** (x east, y north, z up, origin at point A) with body
**FLU** (x forward, y left, z up), yaw in rad CCW from +x. Each driver converts at its own
boundary with the helpers in `adapter.py`. Nothing here was flown or run against an SDK; it is
read from the sources listed at the bottom. "Not confirmed" means check it on the bench on Day 1.

## Summary

| Platform | World / body frame | Velocity command | Yaw in the command | What the driver converts |
|---|---|---|---|---|
| PX4 (MAVSDK Offboard) | NED / FRD | `VelocityNedYaw(north_m_s, east_m_s, down_m_s, yaw_deg)` | Absolute heading, deg, 0 = north, CW positive | `enu_to_ned(v)`; yaw rate => integrate a heading target, then `degrees(yaw_enu_to_ned(...))` |
| ArduPilot (GUIDED) | NED / FRD | `SET_POSITION_TARGET_LOCAL_NED`, frame `MAV_FRAME_LOCAL_NED` (1), velocity-only mask 3527 | Yaw rate in rad/s, CW positive, with mask 1479 | `enu_to_ned(v)`; `yaw_rate_enu_to_ned(r)` |
| Crazyflie (cflib) | Right-handed, Z up; X set by the positioning system or the take-off heading / body FLU | `commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)`, m/s | Yaw rate in deg/s | Usually none for vectors; `degrees(r)` for yaw rate; a fixed yaw offset if the CF frame is not aligned with our ENU |
| Tello (djitellopy) | No world frame / body, axes right, forward, up | `send_rc_control(lr, fb, ud, yaw)`, ints -100..100 | Yaw stick -100..100 | `world_to_body(v, yaw)`, then lr = -left, fb = forward, ud = up, scaled to stick units |

## PX4

- **Frames.** PX4 uses NED for the local/world frame and FRD for the body frame on all topics unless
  a message says otherwise. ROS uses ENU and FLU. ENU => NED swaps x and y and negates z; FLU => FRD
  negates y and z (PX4 ROS 2 user guide, frame conventions section; docs, read in full).
  `adapter.enu_to_ned` and `adapter.flu_to_frd` implement exactly these.
- **MAVSDK velocity command.** `Offboard.VelocityNedYaw` has `north_m_s`, `east_m_s`, `down_m_s`
  and `yaw_deg`, where yaw is in degrees, 0 = north, positive clockwise seen from above (MAVSDK C++
  API reference; docs, read in full). It takes an **absolute heading, not a yaw rate.** Our
  `Setpoint` carries `yaw_rate`, so the driver keeps a heading target `psi += yaw_rate * dt` in ENU
  and sends `math.degrees(yaw_enu_to_ned(psi))`. Not confirmed: that MAVSDK-Python exposes the same
  fields (it wraps the same API definition, but the Python page was not read). The body-frame
  variant `VelocityBodyYawspeed` (forward, right, down, yaw rate) was not read this pass.
- **ROS 2 path.** `TrajectorySetpoint` fields are all NED and need ENU => NED before sending
  (PX4 ROS 2 user guide; docs). `px4_ros_com` ships a `frame_transforms` library for this.
- **Raw MAVLink.** PX4 accepts `SET_POSITION_TARGET_LOCAL_NED` only with `MAV_FRAME_LOCAL_NED` or
  `MAV_FRAME_BODY_NED`, and velocity-only setpoints are supported for multicopters (PX4 Offboard
  mode page; docs, read in full). Whether PX4 honours the yaw-rate bit together with a
  velocity-only setpoint was not checked.
- **Keep-alive.** PX4 needs a setpoint stream of at least 2 Hz before switching into Offboard and
  leaves Offboard after `COM_OF_LOSS_T` without one (PX4 Offboard mode page; docs). Our 20 Hz loop
  is well above that; the driver must keep sending even when the planner has nothing new.
- **Origin.** PX4 local positions are relative to the EKF origin, not point A. The driver stores the
  pose at A on start and subtracts it, then applies `ned_to_enu`. Heading from telemetry is NED
  (0 = north, CW) => `yaw_ned_to_enu`.
- **Health.** Map ODOMETRY `quality` and `reset_counter` into `Pose` (see
  `docs/research/close-area-nav/03-close-area-localization.md`: `quality` -1 failed, 0 unknown,
  1-100). Not checked whether PX4 re-publishes the external-vision `reset_counter` to the companion.

## ArduPilot

- **Command.** In GUIDED, Copter accepts `SET_POSITION_TARGET_LOCAL_NED`. With
  `MAV_FRAME_LOCAL_NED` (1), x is north, y is east, z is down, positions are offsets from the EKF
  origin. `type_mask` 3527 (0x0DC7) = use velocity only; 1479 = velocity plus yaw rate. The page's
  example sends 0.174 with "rotate clock-wise at 10deg/sec", so yaw rate is rad/s, CW positive
  (ArduPilot dev docs, "Copter Commands in Guided Mode"; docs, read in full).
  `MAV_FRAME_BODY_OFFSET_NED` (9) makes velocities forward, right, down relative to heading.
- **Conversion.** `vx_ned, vy_ned, vz_ned = enu_to_ned((sp.vx, sp.vy, sp.vz))`,
  `yaw_rate = yaw_rate_enu_to_ned(sp.yaw_rate)`.
- **Keep-alive.** Re-send velocity commands at least every second; the vehicle stops after 3 s
  without one (same page). The 20 Hz loop covers it.
- **Pose.** Same origin rule as PX4. Which telemetry message to read (`LOCAL_POSITION_NED`,
  `ODOMETRY`) and its default stream rate were not checked this pass.

## Crazyflie

- **Frames.** The global frame is right-handed with Z up (aligned with gravity). With an external
  positioning system (Lighthouse, mocap, UWB) its origin and axes come from that system's
  calibration. Without one (flow deck dead reckoning), the take-off position is the origin and the
  take-off heading is +X. The body frame is x forward, y left, z up (FLU). Positive yaw turns the
  nose left, so yaw is CCW like ENU. The reported Euler pitch has the opposite sign to the pitch
  inside the estimator quaternion (Bitcraze "The Coordinate System of the Crazyflie 2.x"; docs,
  read in full).
- **What "ENU-like" means here.** The CF global frame matches our ENU axes only if the positioning
  system was calibrated with X east, or if the drone takes off at A facing +x of our frame. Otherwise
  the driver applies one fixed yaw rotation (`world_to_body` / `body_to_world` with the offset angle)
  at the boundary. Check this on Day 1 by commanding +x and watching which way it moves.
- **Command.** `cflib` `Commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)`: velocities in
  m/s in the world frame, yaw rate in deg/s. With firmware protocol version 8 or older, cflib sends
  a legacy packet and negates `yawrate` itself (cflib `commander.py`; code, read the function). The
  sign convention of `yawrate` on current firmware was not confirmed; test it.
- **Pose and ranges.** Not checked this pass: the log variable names for position, velocity and
  yaw, their units, and the streaming-setpoint watchdog timeout. Multi-ranger deck: 5 x VL53L1x
  (front, back, left, right, up), up to 4 m (Bitcraze product docs, via lane 02 doc). Front,
  left, back, right map to body angles 0, +pi/2, pi, -pi/2 in `RangeScan`.

## Tello

- **Command.** `djitellopy` `Tello.send_rc_control(left_right_velocity, forward_backward_velocity,
  up_down_velocity, yaw_velocity)`; each value is an int clamped to -100..100 and sent as the SDK
  text command `rc a b c d` without an acknowledgement (djitellopy `tello.py`; code, read the
  function). The same order (a left/right, b forward/backward, c up/down, d yaw, -100..100) is
  quoted from the Tello SDK 2.0 user guide on the TelloPilots forum (forum; the PDF itself was not
  read).
- **Units correction.** `rc` values are **stick deflection, not cm/s.** The cm/s units in the SDK
  belong to `go`, `curve` and `speed` (`set_speed` docstring: 10-100 cm/s; code). The mapping from
  stick value to m/s is not documented in what was read => calibrate on the bench (fly `rc 0 50 0 0`
  for 2 s, measure distance) and set a per-axis scale in the driver.
- **Body axes.** Positive `a` = right, positive `b` = forward, positive `c` = up, positive `d` =
  clockwise yaw. These are common usage, **not confirmed** in docs read this pass.
- **Conversion.** `f, l, u = world_to_body((sp.vx, sp.vy, sp.vz), pose.yaw)`, then
  `a = -k_xy * l`, `b = k_xy * f`, `c = k_z * u`, `d = -k_yaw * degrees(sp.yaw_rate)`, all rounded
  to int. Needs a yaw estimate for `world_to_body`.
- **Pose.** The Tello reports no position. State fields include `vgx`, `vgy`, `vgz` and `yaw` (deg),
  but djitellopy does not document the velocity units or frame (code, read the getters).
  Position must come from mission pads (EDU / TT), an external system, or dead reckoning; set
  `quality` low and `sigma_xy=None` unless you measure it.
- **Ranges.** No obstacle sensor on Tello; `ranges()` returns all `math.inf`. RoboMaster TT forward
  ToF: not verified (lane 02 doc).
- **Keep-alive.** The Tello auto-lands after 15 s without a command (Tello SDK, via lane 02 doc).

## Sources

| Source | Type | Read |
|---|---|---|
| [PX4 ROS 2 user guide, frame conventions](https://docs.px4.io/main/en/ros2/user_guide.html) | docs | frame section in full |
| [PX4 Offboard mode](https://docs.px4.io/main/en/flight_modes/offboard.html) | docs | full |
| [MAVSDK Offboard::VelocityNedYaw](https://mavsdk.mavlink.io/main/en/cpp/api_reference/structmavsdk_1_1_offboard_1_1_velocity_ned_yaw.html) | docs | full |
| [ArduPilot Copter commands in Guided mode](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html) | docs | full |
| [Bitcraze Crazyflie 2.x coordinate system](https://www.bitcraze.io/documentation/system/platform/cf2-coordinate-system/) | docs | full |
| [cflib commander.py](https://github.com/bitcraze/crazyflie-lib-python/blob/master/cflib/crazyflie/commander.py) | code | `send_velocity_world_setpoint` and neighbours |
| [djitellopy tello.py](https://github.com/damiafuentes/DJITelloPy/blob/master/djitellopy/tello.py) | code | `send_rc_control`, `set_speed`, state getters |
| [TelloPilots thread quoting SDK 2.0 `rc`](https://tellopilots.com/threads/is-continuous-movement-available.3485/) | forum | search snippet only |
| `docs/research/close-area-nav/02-sims-platforms-competitions.md`, `03-close-area-localization.md` | hub docs | full |

All fetched on 2026-11-09. Content was rephrased for compliance with licensing restrictions.
