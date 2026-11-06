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
| `repo:ardupilot/ardupilot` | ArduCopter firmware, SITL, `sim_vehicle.py`, the vicon simulator, EKF3. |
| `repo:ardupilot/pymavlink` | MAVLink client used by `source_switch.py`. |
| `repo:ardupilot/mavproxy` | GCS that `sim_vehicle.py` starts (`--console --map`). |
| `repo:mavlink/mavlink` | `ardupilotmega.xml` defines `EKF_STATUS_REPORT` (193), `EKF_STATUS_FLAGS`, `MAV_CMD_SET_EKF_SOURCE_SET` (42007). |

## Files

- `ekf_flags.py` - stdlib decoder for `EKF_STATUS_REPORT` flags and variances.
- `test_ekf_flags.py` - 6 unit tests.
- `source_switch.py` - pymavlink flight script (sketch, needs SITL).

## Prerequisites

- An ArduPilot checkout with the SITL toolchain, set up per the ArduPilot wiki
  "Setting up SITL on Linux" (`Tools/environment_install/install-prereqs-ubuntu.sh -y`).
- `pip install pymavlink` (already present after install-prereqs).
- Python 3.10+. Only `ekf_flags.py` and its tests run on the stdlib alone.

## Run the stdlib part (verified)

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

The three flag values are hand-built examples (healthy GPS flight, constant-position
dead reckoning, GPS glitch), not values captured from SITL.

## Run the SITL flight (unverified sketch)

1. Start SITL with the vicon simulator on SERIAL5 (same arguments the autotest
   `GPSViconSwitching` uses):

   ```sh
   cd ardupilot/ArduCopter
   ../Tools/autotest/sim_vehicle.py -v ArduCopter -A "--serial5=sim:vicon:" --console --map
   ```

2. In another terminal, write the source-set parameters and reboot:

   ```sh
   python3 samples/ardupilot-ekf3-source-switch/source_switch.py --setup
   ```

   `SETUP_PARAMS` in `source_switch.py` is the full list. Key values: set 1 = GPS
   (`EK3_SRC1_POSXY=3`, `VELXY=3`, `POSZ=1` baro, `VELZ=3`, `YAW=1` compass), set 2 =
   ExternalNav (`EK3_SRC2_POSXY=6`, `VELXY=6`, `POSZ=1`, `VELZ=6`, `YAW=6`),
   `EK3_SRC_OPTIONS=0`, `RC8_OPTION=90`, `VISO_TYPE=2`, `SERIAL5_PROTOCOL=2`.

3. When MAVProxy shows the vehicle back up, fly:

   ```sh
   python3 samples/ardupilot-ekf3-source-switch/source_switch.py
   # or use the RC aux switch path instead of the MAVLink command:
   python3 samples/ardupilot-ekf3-source-switch/source_switch.py --switch-via rc
   ```

The script connects on `tcp:127.0.0.1:5762` (SITL SERIAL1) so it does not fight
MAVProxy for port 5760.

Expected (not observed here): MAVProxy prints `EKF3 IMU0 is using external nav data`
after the switch (that text is in `libraries/AP_NavEKF3/AP_NavEKF3_Control.cpp`), the
vehicle stays in GUIDED and flies the north leg with GPS off, and the CSV
`ekf_status_log.csv` shows variances staying below 0.5 in the `extnav-no-gps` phase.
For a contrast run, skip the source switch (comment out `v.set_source_set(2, via)`):
the EKF should lose `POS_HORIZ_ABS` and the vehicle fall into an EKF or GPS failsafe.

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
- `EKF_STATUS_REPORT` is requested explicitly with `MAV_CMD_SET_MESSAGE_INTERVAL`, so
  the script does not depend on `SRn_EXTRA3` stream rates.
