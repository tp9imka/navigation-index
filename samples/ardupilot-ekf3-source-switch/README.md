# ArduPilot EKF3 source-set switch under GPS denial (SITL)

## Goal

Show the ArduPilot way of surviving GPS loss: EKF3 holds up to three sensor "source
sets" (`EK3_SRC1_*`, `EK3_SRC2_*`, `EK3_SRC3_*`) and can switch between them in flight.
This sample flies an ArduCopter SITL on GPS (set 1), switches to an external-nav source
(set 2, the SITL vicon simulator), cuts the simulated GPS, flies a 15 m leg without it,
restores GPS, switches back, and returns home. `EKF_STATUS_REPORT` is logged the whole
time so you can see what the EKF thinks of its own position.

## Repos used

| Repo | Why |
|---|---|
| `repo:ardupilot/ardupilot` | ArduCopter firmware, SITL, the vicon simulator, EKF3. |
| `repo:ardupilot/pymavlink` | MAVLink client used by `source_switch.py`. |
| `repo:ardupilot/mavproxy` | Optional GCS if you start SITL with `sim_vehicle.py --console --map` instead of Docker. |
| `repo:mavlink/mavlink` | `ardupilotmega.xml` defines `EKF_STATUS_REPORT` (193), `EKF_STATUS_FLAGS`, `MAV_CMD_SET_EKF_SOURCE_SET` (42007). |

## Files

- `ekf_flags.py` - stdlib decoder for `EKF_STATUS_REPORT` flags and variances.
- `test_ekf_flags.py` - 6 unit tests.
- `source_switch.py` - pymavlink flight script. `--setup` writes the parameters and
  reboots; the second run flies. `--no-switch` is the contrast run (GPS cut, no source
  switch). Writes a CSV with flags, variances, GPS fix type and local north/east.

## Prerequisites

- Docker, for the SITL: `samples/sitl-docker` builds ArduCopter `Copter-4.6.3` headless
  (no `sim_vehicle.py`, no MAVProxy) with the vicon simulator on SERIAL5.
- Python 3.10+ with `pymavlink` (ran with pymavlink 2.4.50 on python3.12). Only
  `ekf_flags.py` and its tests run on the stdlib alone.

## Run the stdlib part

```sh
cd samples/ardupilot-ekf3-source-switch
python3 -m unittest -v test_ekf_flags
python3 ekf_flags.py 0x033f 0x0081 0x833f
```

Observed output (python3.14.7, 2026-11-06):

```
Ran 6 tests in 0.000s

OK
0x033f: ATTITUDE | VELOCITY_HORIZ | VELOCITY_VERT | POS_HORIZ_REL | POS_HORIZ_ABS | POS_VERT_ABS | PRED_POS_HORIZ_REL | PRED_POS_HORIZ_ABS
0x0081: ATTITUDE | CONST_POS_MODE
0x833f: ATTITUDE | VELOCITY_HORIZ | VELOCITY_VERT | POS_HORIZ_REL | POS_HORIZ_ABS | POS_VERT_ABS | PRED_POS_HORIZ_REL | PRED_POS_HORIZ_ABS | GPS_GLITCHING
```

The three flag values above are hand-built examples. `0x033f` and `0x00a7` / `0x0025`
also show up in the real SITL runs below.

## Run the SITL flight (ran 2026-11-06)

```sh
docker build -f samples/sitl-docker/Dockerfile.ardupilot -t nav-sitl-ardupilot:copter-4.6.3 samples/sitl-docker
docker run --rm -d --name ap -p 5760:5760 -p 5762:5762 -p 5763:5763 nav-sitl-ardupilot:copter-4.6.3

cd samples/ardupilot-ekf3-source-switch
python3 source_switch.py --connect tcp:127.0.0.1:5762 --setup   # params + reboot
python3 source_switch.py --connect tcp:127.0.0.1:5762            # fly, ~100 s
```

Or `docker compose up -d ardupilot` from `samples/sitl-docker`. Recreate the container
(`docker rm -f ap` + `docker run`) before each flight: a run ends in RTL, and a fresh
container plus `--setup` is the clean start.

`SETUP_PARAMS` in `source_switch.py` is the full list. Set 1 = GPS (`EK3_SRC1_POSXY=3`,
`VELXY=3`, `POSZ=1` baro, `VELZ=3`, `YAW=1` compass), set 2 = ExternalNav
(`EK3_SRC2_POSXY=6`, `VELXY=6`, `POSZ=1`, `VELZ=6`, `YAW=6`), `EK3_SRC_OPTIONS=0`,
`RC8_OPTION=90`, `VISO_TYPE=2`, `SERIAL5_PROTOCOL=2`.

Observed (ArduCopter Copter-4.6.3 SITL in Docker on linux/arm64, pymavlink 2.4.50,
abridged: one EKF line per second, repeated lines cut):

```
command MAV_CMD_SET_MESSAGE_INTERVAL => MAV_RESULT_ACCEPTED   (x4)
command MAV_CMD_SET_EKF_SOURCE_SET => MAV_RESULT_ACCEPTED
  STATUSTEXT: Arm: AHRS: waiting for home        (16 pre-arm refusals over ~25 s, also
  STATUSTEXT: Arm: Gyros inconsistent             "Accels inconsistent" and
  STATUSTEXT: Arm: VisOdom: yaw diff 10.8 deg (>10)   while SITL settles)
  STATUSTEXT: EKF3 IMU0 origin set
  STATUSTEXT: VisOdom: yaw shifted 2 to 355 deg
  STATUSTEXT: Arming motors
armed
command MAV_CMD_NAV_TAKEOFF => MAV_RESULT_ACCEPTED
  [gps] gps_fix=6 ne=(0.0,-0.0) flags=0x033f pos=abs vel=0.01(good) pos_h=0.00(good) pos_v=0.00(good) mag=0.02(good)
command MAV_CMD_SET_EKF_SOURCE_SET => MAV_RESULT_ACCEPTED
param SIM_GPS_DISABLE = 1
  [extnav-no-gps] gps_fix=1 ne=(0.3,-0.0) flags=0x033f pos=abs vel=0.06(good) pos_h=0.02(good) pos_v=0.00(good) mag=0.03(good)
  [extnav-no-gps] gps_fix=1 ne=(8.1,-0.0) flags=0x033f pos=abs vel=0.06(good) pos_h=0.01(good) pos_v=0.00(good) mag=0.02(good)
  [extnav-no-gps] gps_fix=1 ne=(15.5,0.0) flags=0x033f pos=abs vel=0.01(good) pos_h=0.00(good) pos_v=0.00(good) mag=0.02(good)
  [extnav-no-gps] gps_fix=1 ne=(15.0,-0.0) flags=0x033f pos=abs vel=0.01(good) pos_h=0.00(good) pos_v=0.00(good) mag=0.02(good)
param SIM_GPS_DISABLE = 0
  [gps-back-extnav] gps_fix=6 ne=(15.0,-0.0) flags=0x033f pos=abs vel=0.01(good) pos_h=0.00(good) pos_v=0.00(good) mag=0.02(good)
command MAV_CMD_SET_EKF_SOURCE_SET => MAV_RESULT_ACCEPTED
  [gps-restored] gps_fix=6 ne=(15.0,-0.0) flags=0x033f pos=abs vel=0.01(good) pos_h=0.00(good) pos_v=0.00(good) mag=0.00(good)
RTL commanded; EKF log written to ekf_status_log.csv
```

How to read it: `gps_fix=1` is GPS_RAW_INT "no fix" after `SIM_GPS_DISABLE=1` (this is
4.6, so the script fell back from `SIM_GPS1_ENABLE`). With source set 2 the EKF keeps
`POS_HORIZ_ABS` (flags `0x033f`) and all normalized variances stay under 0.1 for the
whole 30 s, and the copter flies the 15 m north leg and holds it. The CSV had 330 rows
(51 gps, 152 extnav-no-gps, 51 gps-back-extnav, 76 gps-restored at 5 Hz). No
"using external nav" STATUSTEXT appeared on the in-flight source switch; that text was
seen only at EKF start (see `samples/vio-to-mavlink-bridge`).

### Contrast run: GPS cut without the source switch

```sh
python3 source_switch.py --connect tcp:127.0.0.1:5762 --no-switch --log ekf_noswitch.csv
```

Observed (same setup, fresh container, abridged):

```
param SIM_GPS_DISABLE = 1
  [gps-only-no-gps] gps_fix=1 ne=(0.7,0.0) flags=0x033f pos=abs ...
  [gps-only-no-gps] gps_fix=1 ne=(15.3,0.0) flags=0x033f pos=abs ...
  [gps-only-no-gps] gps_fix=1 ne=(15.4,0.0) flags=0x0025 pos=NONE ...
  [gps-only-no-gps] STATUSTEXT: EKF variance
  [gps-only-no-gps] STATUSTEXT: EKF Failsafe: changed to LAND Mode
  [gps-only-no-gps] STATUSTEXT: EKF3 IMU0 stopped aiding
  [gps-only-no-gps] gps_fix=1 ne=(14.5,0.2) flags=0x00a7 pos=NONE ...
  [gps-only-no-gps] STATUSTEXT: SmartRTL deactivated: bad position
param SIM_GPS_DISABLE = 0
  [gps-back] STATUSTEXT: EKF3 IMU0 is using GPS
  [gps-back] STATUSTEXT: Disarming motors
  [gps-back] STATUSTEXT: EKF Failsafe Cleared
  [gps-back] gps_fix=6 ne=(17.3,-2.1) flags=0x033f pos=abs ...
```

On GPS only, the EKF coasts for ~6 s (position still flagged absolute while it dead
reckons), then drops horizontal position (`0x0025`, later `0x00a7` = CONST_POS_MODE),
the EKF failsafe switches to LAND, and the copter lands and disarms. When GPS returns
the local position jumps from (14.5, 0.2) to (17.3, -2.1): about 3.6 m of
dead-reckoning error the EKF had not reported. The variance fields stayed "good" the
whole time, so watch the flags, not only the variances.

Not run: `--switch-via rc` (RC8 aux switch path).

## How the two switch paths work

- `MAV_CMD_SET_EKF_SOURCE_SET` (42007, param1 = 1..3) is an ArduPilot-dialect command,
  covered by the autotest `MAV_CMD_SET_EKF_SOURCE_SET` in
  `Tools/autotest/arducopter.py`.
- `RCx_OPTION=90` ("EKF Pos Source") maps a 3-position switch to sets 1/2/3 at
  low/mid/high PWM. In SITL the script fakes the switch with `RC_CHANNELS_OVERRIDE` and
  resends it every loop because overrides expire (`RC_OVERRIDE_TIME`).

## Disabling simulated GPS: parameter name depends on version

- ArduPilot 4.6 and older: `SIM_GPS_DISABLE=1` (in `libraries/SITL/SITL.cpp` on the
  `ArduPilot-4.6` and `Copter-4.5` branches).
- ArduPilot 4.7 and master: per-GPS groups, `SIM_GPS1_ENABLE=0`
  (`libraries/SITL/SIM_GPS.cpp`).

`set_sim_gps()` probes for `SIM_GPS1_ENABLE` first and falls back to `SIM_GPS_DISABLE`.
The autotest `GPSViconSwitching` instead sets `GPS1_TYPE=0` (driver off), which also
works on real hardware.

## Extending it in a hackathon

- Replace the vicon simulator with your own pose source through
  `samples/vio-to-mavlink-bridge` (`VISO_TYPE=1`).
- Add set 3 with optical flow (`EK3_SRC3_VELXY=5`, `SIM_FLOW_ENABLE=1`, `FLOW_TYPE=10`
  plus a SITL rangefinder) and fall back GPS => vision => flow.
- Automate the switch onboard with the Lua examples in `libraries/AP_Scripting/examples`
  (`ahrs-source.lua`, `ahrs-source-gps-optflow.lua`), which pick a source set from
  innovations instead of a human or GCS command.
- Inject GPS spoofing rather than loss (SITL `SIM_GPS1_GLTCH` on 4.7/master, `SIM_GPS_GLITCH` on 4.6,
  a lat/lon/alt offset vector) and watch `GPS_GLITCHING`.

## Pitfalls

- `SIM_GPS_DISABLE` does not exist on master. Probe, as the script does.
- `EK3_SRC_OPTIONS` defaults to FuseAllVelocities; the ArduPilot transition wiki page
  recommends 0 when switching between GPS and external nav.
- Switch source sets before the GPS drops, not after: the EKF needs the new source
  healthy and aligned. Yaw source changes (compass => ExternalNav) cause a yaw reset.
- ExternalNav without GPS has no global origin on a cold start. Here GPS sets it at
  boot; without GPS you must send `SET_GPS_GLOBAL_ORIGIN` first.
- The variance values in `EKF_STATUS_REPORT` are normalized test ratios, not m^2;
  the 0.5 / 0.8 thresholds come from the comment in `ardupilotmega.xml`.
- pymavlink requests no telemetry streams. The first version of this script waited for
  `GLOBAL_POSITION_INT` that never came on SERIAL1; it now requests every message it
  reads with `MAV_CMD_SET_MESSAGE_INTERVAL`.
- Arming fails for ~20-30 s after SITL boot. `arducopter_arm()` + `motors_armed_wait()`
  from pymavlink sends once and then blocks forever; `Vehicle.arm()` retries and prints
  the pre-arm reasons.
- `Arm: Logging failed` in Docker means the Docker VM disk is full.
