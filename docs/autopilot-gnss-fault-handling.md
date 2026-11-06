# Autopilot GNSS fault handling: PX4 EKF2 and ArduPilot EKF3 under spoofing

<!-- about: repo:px4/px4-autopilot, repo:ardupilot/ardupilot -->

What each autopilot's EKF does when GNSS goes wrong, read from the source at pinned tags and
checked in SITL by [samples/autopilot-spoof-response](../samples/autopilot-spoof-response/README.md)
(45 flights, 2026-11-06). Use it to choose parameters, and to decide what an external monitor
must do that the EKF cannot.

- PX4: tag `v1.17.0`, commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`. Paths are under
  `src/modules/ekf2/` unless given in full.
- ArduPilot: tag `Copter-4.6.3`, commit `92b0cd788ec29406f26c6f9c31d5ceedbd1cc538`. Paths
  are under `libraries/AP_NavEKF3/` unless given in full.

Line numbers are for those commits. Re-check them before quoting against another tag.

## The one mechanism that matters

Both EKFs do the same three things:

1. They test each GNSS sample against the filter's prediction (innovation gate, 5 sigma by
   default).
2. They skip samples that fail the test.
3. After a fixed time with no accepted GNSS position, if nothing else constrains position,
   they **reset the position state to the GNSS measurement**.

Step 3 exists so a vehicle with a bad IMU or a real GNSS jump does not dead-reckon away from a
good receiver forever. Against a spoofer it means a rejected spoof gets accepted after the
timeout, whole. A spoof that moves slowly and coherently (position and velocity together)
never fails step 1 at all, so it is fused directly.

The glitch flags only report step 2. Neither flag means "GNSS is not being used".

| | PX4 EKF2 v1.17.0 | ArduPilot EKF3 Copter-4.6.3 |
|---|---|---|
| Position gate | `EKF2_GPS_P_GATE` 5 SD, each axis separately (`params_gnss.yaml` 49-56; `EKF/aid_sources/gnss/gps_control.cpp` 361-367) | `EK3_POS_I_GATE` 500 = 5 SD, on the 2D sum of squares (`AP_NavEKF3.cpp` 185-191; `AP_NavEKF3_PosVelFusion.cpp` 813-815) |
| Velocity gate | `EKF2_GPS_V_GATE` 5 SD per axis (`params_gnss.yaml` 68-75; `gps_control.cpp` 312-320) | `EK3_VEL_I_GATE` 500, on the summed 2D/3D test (`AP_NavEKF3.cpp` 168-174; `AP_NavEKF3_PosVelFusion.cpp` 890) |
| Measurement noise used in the gate | `max(receiver hacc, EKF2_GPS_P_NOISE 0.5 m)`, capped at `EKF2_NOAID_NOISE` when GNSS is the only aiding (`gps_control.cpp` 346-357); velocity `max(sacc, EKF2_GPS_V_NOISE 0.3)` (309) | `EK3_POSNE_M_NSE` / receiver accuracy, scaled by `gpsNoiseScaler` (`AP_NavEKF3_PosVelFusion.cpp` 1004-1007) |
| Test ratio definition | `innov^2 / (gate^2 * innov_var)` per axis, reject if > 1 (`EKF/ekf.h` 1081, 1129-1135) | `(innovN^2 + innovE^2) / (gate^2 * (varN + varE))`, reject if >= 1 (`AP_NavEKF3_PosVelFusion.cpp` 813-816) |
| Timeout before reset-to-GNSS | `reset_timeout_max` = 7 s, compiled constant (`EKF/common.h` 480) | `posRetryTimeUseVel_ms` 10 s while GNSS velocity still passes, `posRetryTimeNoVel_ms` 7 s otherwise, compiled constants (`AP_NavEKF3.h` 472-476; `AP_NavEKF3_Control.cpp` 373-400) |
| Reset decision | `controlGnssPosFusion`: if fusion timed out and `isGnssPosResetAllowed()` => `resetHorizontalPositionToGnss`, else stop GNSS position and set `gnss_fault` (`gps_control.cpp` 189-205, 272-297, 442-450). Velocity: same at 135-145 | `FuseVelPosNED`: if `posTimeout` (or position variance > `EK3_GLITCH_RAD`^2) and (`!velAiding` or `gpsGoodToAlign`) => `ResetPosition` to GPS, P reset to (GLITCH_RAD/2)^2 (`AP_NavEKF3_PosVelFusion.cpp` 834-866); velocity at 910-920 |
| What blocks the reset | Another active horizontal **position** source (`ev_pos`, `aux_gpos`) in `EKF2_GPS_MODE 0`; any other horizontal **aiding**, velocity included (GNSS velocity, flow, EV velocity, airspeed+sideslip) in `EKF2_GPS_MODE 1` (`gps_control.cpp` 272-297; `EKF/estimator_interface.cpp` 596-649) | Only `posAiding` from range beacons. EV / flow do not block a GPS reset while the position source is GPS (`AP_NavEKF3_Control.cpp` 345-384). The fix is changing the source set |
| Glitch flag | `ESTIMATOR_STATUS.flags` bit 1024 `GPS_GLITCH` = any raw GNSS vel or pos test ratio > 1 on the latest sample, no hysteresis (`EKF/ekf_helper.cpp` 722-728; `src/modules/mavlink/streams/ESTIMATOR_STATUS.hpp` 88) | `EKF_STATUS_REPORT` `GPS_GLITCHING` (0x8000) = `!gpsAccuracyGood` with GPS as position source; innovations must fail for 1 s to set it and pass for 10 s to clear it (`AP_NavEKF3_Control.cpp` 790; `AP_NavEKF3_VehicleStatus.cpp` 299-317). Copter prints `GPS Glitch or Compass error` / `Glitch cleared` (`ArduCopter/events.cpp` 298-315) |
| Test ratios on MAVLink | `ESTIMATOR_STATUS.pos_horiz_ratio` = sqrt of the *filtered* (tau 0.5 s) ratio, which is clipped at 4, so it saturates at 2.0; NaN when GNSS position is not fused (`EKF/ekf_helper.cpp` 516-550; `EKF/ekf.h` 1076-1113) | `EKF_STATUS_REPORT.pos_horiz_variance` / `velocity_variance` = sqrt(test ratio) (`AP_NavEKF3_Outputs.cpp` 495-496) |
| Receiver-side spoof flag | `EKF2_GPS_CHECK` bit `kSpoofed` rejects samples flagged spoofed by the driver, in flight too (`EKF/aid_sources/gnss/gnss_checks.cpp` 82-108). `HIL_GPS` hard-codes `spoofing_state = 0` (`src/modules/mavlink/mavlink_receiver.cpp` ~2460) | No spoof-flag check in the `AP_NavEKF3` sources at this tag (searched for "spoof") |
| Multiple instances | Multi-EKF selector (`EKF2_MULTI_IMU`) picks a primary by test ratios (`EKF2Selector.cpp`); all instances see the same GNSS | Lanes per IMU; switch when primary error score > 1 or another lane is better by `EK3_ERR_THRESH` (`AP_NavEKF3.cpp` 909-1015, error score `AP_NavEKF3_Outputs.cpp` 62-67). With one GNSS every lane sees the same spoof; `EK3_AFFINITY` bit 0 only helps with two receivers |

## What the flights showed (summary)

From the sample's 45-flight sweep. One seed per cell, SITL, quad, survey at 10 m/s.

- **Step offset 20 m or 100 m**: PX4 flagged 0.2-7.2 s after onset, then reset onto the full
  offset at 7.3 s. ArduPilot flagged at 1.1 s, reset at 10.1 s and cleared the flag at
  20.1 s. Gates 3 SD / 300 changed nothing.
- **Position-only drag 3 m/s**: a reset sawtooth. PX4 jumped 24-28 m every ~10 s and
  ArduPilot 29-41 m every ~19 s, both ending 150 m off. This is the 108-152 m drift
  `golden-demo-px4` saw.
- **Coherent drag 0.1-5 m/s**: 96-110 % of the offset believed in every config. With default
  gates no flag ever went up at <= 1 m/s on either autopilot. The onset velocity step
  (>= 2 m/s on PX4) gave about 1 s of flag and then a reset onto the GNSS (PX4
  `ODOMETRY.reset_counter` +4 in one sample, consistent with the EKF-GSF yaw emergency reset
  in `gps_control.cpp` 105-118 / 394-432).
- **Large velocity steps cause failsafes, not rejection.** ArduPilot at 5 m/s (default) and
  >= 3 m/s (gates 300): `EKF variance` => `EKF Failsafe: changed to LAND Mode` 1.0-1.1 s after
  onset. PX4: `Failsafe: blind land` when the drag stopped at the cap (a reverse velocity
  step), and at onset with gates 3 at 2 m/s.
- **PX4 `EKF2_GPS_MODE 1`** refused the steps and the position drag (EKF error <= 5 m) and then
  blind-landed after 12-14 s, because the SITL quad had no other aiding source.

## Parameters a team should set

Pick by what you can fuse besides GNSS. Each row lists what you buy and what it costs in
availability.

**PX4**

- `EKF2_GPS_MODE 1` (dead-reckoning reset mode). The only setting that stops EKF2 from
  resetting onto a rejected GNSS while another horizontal aiding source runs. Measured: steps
  and position drags kept out of the state. Cost: with no other source the vehicle loses
  position after the 7 s timeout and blind-lands. It adds nothing against a coherent drag.
  Worth setting when you fuse flow, EV velocity or airspeed (fixed-wing). Untested here with a
  second source.
- `EKF2_GPS_P_GATE` / `EKF2_GPS_V_GATE` below 5. Flags earlier. Measured: no reduction in
  capture, and an extra LAND failsafe on a 2 m/s coherent drag. Do not use as spoof
  protection. Use it only if your monitor reads the flag and you accept more false flags in
  manoeuvres.
- `EKF2_GPS_CHECK` with the spoofed bit enabled, on a receiver that reports spoofing (u-blox
  M10 / F9 `spoofDetState`). Cheap, and it rejects at the source before the gate. Not
  verified in the hub: no receiver driver was in the loop.
- `EKF2_REQ_*` (EPH, SACC, NSATS...) apply at initial alignment. In flight only fix type,
  hacc/vacc > 50 m, sacc > 10 m/s and the spoof flag are checked (`gnss_checks.cpp` 82-108).
  A spoofer that reports good accuracy passes.
- External vision: with `ev_pos` fused alongside GNSS in mode 0, a GNSS position reset is
  blocked (`isGnssPosResetAllowed`). But EV position goes through a bias estimator while GNSS
  is active (`ev_pos_control.cpp` 211-233), so EV cannot pull the state off a spoof. It only
  stops the reset. Not measured.

**ArduPilot**

- No parameter disables the posTimeout reset to GPS. `EK3_GLITCH_RAD` (default 25 m) adds a
  second reset trigger (position variance > radius^2). `EK3_GLITCH_RAD 0` switches to
  clipping innovations instead of rejecting them, which pulls the state toward GNSS
  continuously. Both from source; not measured here.
- `EK3_POS_I_GATE` / `EK3_VEL_I_GATE` 300: earlier flag (3.9 s vs 7.1 s on a 3 m/s position
  drag), a shorter reset period (~14.5 s vs ~19.5 s) and an EKF failsafe on a 3 m/s coherent
  drag. Same capture.
- `FS_EKF_ACTION` / `FS_EKF_THRESH`: the EKF failsafe is what landed the 3-5 m/s coherent
  cases. It is the autopilot's only built-in reaction and it fires on velocity steps, not on
  slow drags.
- Source sets (`EK3_SRC1_*`, `EK3_SRC2_*`, `EK3_SRC_OPTIONS`) are the real tool: a second set
  with ExternalNav / optical flow position or velocity, selected by `MAV_CMD_SET_EKF_SOURCE_SET`,
  an RC switch (`RCx_OPTION 90`) or Lua (`ahrs:set_posvelyaw_source_set`).
- Two receivers with `EK3_AFFINITY` bit 0: a lane can follow the clean receiver. It only helps
  if the spoofer reaches one antenna. Not tested.

## What an external monitor must do that the EKF cannot

The EKF's only test is "does GNSS agree with my own prediction". The prediction is IMU
integration seeded from GNSS, so it inherits whatever GNSS told it, and after 7-10 s of
disagreement the EKF gives up and believes GNSS anyway. A monitor has to supply what the EKF
lacks:

1. **An independent reference that GNSS never touched.** VIO / flow velocity, visual or
   terrain geolocation, a second receiver with a different antenna, or the companion's own
   dead-reckoning started from a trusted fix. If the monitor's reference is the autopilot's
   EKF output, it tests GNSS against itself.
2. **Consistency tests that do not time out.** Solution separation with a protection level,
   and GNSS-velocity vs reference-velocity (the test that caught coherent drags in 3 s in
   `golden-demo` / `golden-demo-px4`). A slow coherent drag is invisible to a 5 SD innovation
   gate. It shows up only against a velocity source that does not move with it.
3. **Latching.** Once GNSS is excluded it stays excluded until a probation test clears it
   against the independent reference, not until a timer expires. That is exactly what EKF
   reset logic does not do.
4. **The onset as evidence.** A coherent spoof's only sharp feature is the velocity step when
   it starts (PX4 flagged it for ~1 s at >= 2 m/s). A monitor should log and act on a short
   glitch-flag burst, not wait for it to persist.
5. **Act on the estimator, not just alert.** Take GNSS out of the EKF before the 7 s (EKF2)
   or 10 s (EKF3) timeout, so the reset cannot happen, and give the EKF the replacement
   source in the same step.

## Switching sources safely

**PX4 v1.17 (no source sets).** Done by parameter, live on `parameter_update`, no reboot
(`samples/golden-demo-px4`).

- Order matters: `EKF2_GPS_CTRL 0` first, then `EKF2_EV_CTRL` (hpos + vel).
- With GNSS stopped, starting EV position resets EKF2's position to the EV measurement
  (`ev_pos_control.cpp` 220-226), which drops the spoof offset at once. The EV pose must be in
  EKF2's local origin frame: read `GPS_GLOBAL_ORIGIN` before sending. EV must arrive less than
  200 ms apart.
- If EV is enabled while GNSS is still active, EV runs through a bias estimator and cannot
  pull the state off the spoof.
- To come back: `EKF2_EV_CTRL 0`, then `EKF2_GPS_CTRL 7`. GNSS restart fuses without reset
  only if the test ratios are small (`gps_control.cpp` 210-236). Otherwise it resets onto
  GNSS. Re-enable only after the monitor's probation has cleared GNSS.
- INT32 params go bytewise in `PARAM_SET` (golden-demo-px4 pitfall).

**ArduPilot 4.6 (source sets).** `MAV_CMD_SET_EKF_SOURCE_SET 2` with set 2 = ExternalNav
position (and EV / flow velocity).

- A change of position source triggers a position reset to the new source
  (`AP_NavEKF3_PosVelFusion.cpp` 549-551, 628-630), so the offset accumulated before the
  switch is dropped.
- Switching **back** to set 1 resets onto GPS immediately (`AP_NavEKF3_PosVelFusion.cpp`
  608-610). Switching back while the spoof is still on teleports the EKF onto it. Gate the
  revert on the monitor clearing GNSS.
- Keep ExternalNav continuous: a ~10 s ExternalNav gap triggered `EKF Failsafe: changed to
  LAND` in `golden-demo` v1.
- `EK3_SRC_OPTIONS` bit 0 (fuse all velocities) would keep GNSS velocity fused in set 2;
  leave it off when GNSS is the suspect.

## Pitfalls

- `GPS_GLITCH` on PX4 has no hysteresis and reflects the latest sample. Integrate it over
  time, or read `pos_horiz_ratio`. That field is filtered and saturates at 2.0 (every
  rejected case in the sweep read exactly 2.0), so it shows "rejected", not "by how much".
- ArduPilot's `GPS_GLITCHING` needs 1 s of failure to appear and 10 s of passes to clear. In
  the step flights it stayed up 10 s after the EKF had already accepted the spoofed position.
- Neither EKF prints its reset-to-GNSS. On PX4 `ECL_WARN` is `PX4_DEBUG`
  (`EKF/estimator_interface.h` 45-49). Watch `ODOMETRY.reset_counter` (PX4,
  `EKF2.cpp` 1709-1711) or the jump in `GLOBAL_POSITION_INT`.
- Lane switches (`EKF3 lane switch N`) appeared at onset in most ArduPilot spoof flights.
  They are not a recovery: all lanes use the same GNSS.

## Tested configurations

Measured by [samples/autopilot-resilient-configs](../samples/autopilot-resilient-configs/README.md):
13 configs x coherent drag 0.3 / 1 / 3 m/s + a clean flight x 3 seeds = 156 SITL flights,
PX4 v1.17.0 SIH and ArduCopter 4.6.3, 2026-11-06. Same companions, survey and spoof model as
above. "Held" = mission completed, no failsafe, EKF error and true cross-track deviation both
<= 25 m. The second source in every config is simulated (VIO = truth + 0.1 m/s noise + fixed
0.05 / -0.03 m/s bias; replayed real visual geolocation), so these results are as good as that
source.

| Recipe | Files | Held 0.3 / 1 / 3 m/s | GNSS out after onset | Clean false alarms |
|---|---|---|---|---|
| ArduPilot: Lua GPS-vs-ExternalNav check, switch to source set 2 | `configs/ardupilot/lua-switch.parm` + `scripts/gnss_extnav_switch.lua` | 0/3, 3/3, 3/3 | 2.3-3.5 s at 1-3 m/s; 91 s in one 0.3 m/s flight | 0/3 |
| PX4: `EKF2_EV_CTRL 4` + `EKF2_GPS_MODE 1` + `EKF2_GPS_P_GATE 3` / `V_GATE 3` | `configs/px4/ev-vel-gpsmode1-gates3.params` | 0/3, 3/3, 3/3 | 14.9-15.1 s (1 m/s), 8.3-9.4 s (3 m/s) | 0/3 |
| PX4: same, 5 SD gates | `configs/px4/ev-vel-gpsmode1.params` | 0/3, 1/3, 3/3 | 29.7-93.3 s (1 m/s), 9.0-9.2 s (3 m/s) | 0/3 |
| ArduPilot: 2 receivers, 1 spoofed, `EK3_AFFINITY 1` | `configs/ardupilot/dual-gps-affinity.parm` | 0/3, 0/3, 3/3 | lane switch 0.1 s (3 m/s only) | 0/3 |
| ArduPilot: 2 receivers, `GPS_AUTO_SWITCH 2` | `configs/ardupilot/dual-gps-blend.parm` | 3/3, 0/3, 0/3 | never; believed exactly half | 0/3 |
| Reference, not onboard: companion monitor acting (PX4) | `configs/px4/companion-monitor.params` | 3/3, 3/3, 3/3 | 44-51 s, 3.0-5.0 s, 1.0 s | 0/3 |
| No effect: `EK3_SRC_OPTIONS 1`, `EK3_GLITCH_RAD 0`, PX4 `EKF2_EV_CTRL 4` in mode 0 | | 0/9 each | never | 0/3 |

What this adds to the sections above:

- **A Lua applet on ArduPilot is enough for 1-3 m/s.** It needs no extra binding: ExternalNav
  velocity is `ahrs:get_velocity_NED()` minus `ahrs:get_vel_innovations_and_variances_for_source(6)`,
  because EKF3 computes ExternalNav velocity innovations for reporting even while source set 1
  is active (`AP_NavEKF3_PosVelFusion.cpp` 520-528, innovation = state - observation at
  line 488). The GPS-vs-VIO velocity difference is the difference of the two innovation
  vectors. Dead-reckoning that velocity from the arming fix gives the position test. The
  switch resets EKF3 onto ExternalNav at once (position-source change), so the error after
  the switch is the reference's own (4.9-5.9 m at mission end).
- **`EKF2_GPS_MODE 1` becomes a real defence once a second velocity source is fused.** With EV
  velocity, a rejected GNSS position times out into `stopGnssPosFusion()` + `gnss_fault`
  instead of a reset (`gps_control.cpp` 189-205, 272-297), and GNSS stays out while it
  disagrees. Gates at 3 SD make a 1 m/s drag fail the velocity test from the onset; at 5 SD it
  is a coin toss. With no GNSS left the vehicle dead-reckons on VIO: fine for the ~100 s left
  in these missions, unbounded on a long flight.
- **Neither autopilot caught 0.3 m/s onboard.** A drag that slow never fails a velocity test and
  needs 80+ s to beat VIO drift on a position test. Only the external monitor with an absolute
  reference (visual geolocation, solution separation) excluded it, at 44-51 s.
- **Two receivers help only when one is clean.** Affinity switched lanes on a 3 m/s onset step
  and nothing slower; blending averages the spoof in. A spoofer in view of both antennas defeats
  both, so the second receiver needs a different defence (CRPA, authenticated signal).
- **`EK3_SRC_OPTIONS 1` with the Lua switch** gave the same errors as without it (end error
  5.0-5.8 m vs 4.9-5.9 m), so the warning in "Switching sources safely" did not show up in these
  flights. Leaving it off is still the simpler choice.
- **PX4 aux global position (`EKF2_AGP_CTRL 1`) with SIH's `sensor_agp_sim` is not usable as
  tested**: GNSS position fusion stopped before the attack in all 12 flights with
  `cs_gnss_hgt_fault` set, so those flights navigated on AGP alone (12-21 m deviation on clean
  flights). Cause not diagnosed.
