# ArduPilot - integration card
<!-- about: repo:ardupilot/ardupilot -->
One-line: GPL autopilot with a scriptable EKF3 that can switch between GPS, external nav (VIO/mocap), optical flow, beacons and wheel encoders in flight, plus a SITL that can disable, jam or glitch its simulated GPS, so a GNSS-denied demo runs on a laptop.

| | |
|---|---|
| Install | `git clone --recurse-submodules https://github.com/ArduPilot/ardupilot && cd ardupilot && Tools/environment_install/install-prereqs-ubuntu.sh -y && . ~/.profile`, then `./waf configure --board sitl && ./waf copter`. Prereq scripts also exist for mac, arch, alpine, openSUSE and Windows (`Tools/environment_install/`). Stable tags: `Copter-4.6.3`, `Copter-4.7.2` (latest seen). |
| Runs on | Linux x86-64/arm64 is the main path. macOS works but see Gotchas. WSL2 is handled by `sim_vehicle.py` (forwards MAVLink to the Windows host). No GPU. ROS 2 via `ardupilot_ros`/DDS is optional. |
| Inputs | MAVLink from GCS/companion: `VISION_POSITION_ESTIMATE`, `VISION_SPEED_ESTIMATE`, `ODOMETRY` (VISO_TYPE=1), `GPS_INPUT`, `SET_GPS_GLOBAL_ORIGIN`, setpoints in GUIDED. Serial sensors (GPS, rangefinder, flow). Lua scripts on the SD card / `scripts/` dir in SITL. Units: MAVLink SI, local frames NED. |
| Outputs | MAVLink telemetry (`GLOBAL_POSITION_INT`, `EKF_STATUS_REPORT`, `GPS_RAW_INT`, ...), DataFlash `.bin` logs (EKF3 innovations `XKF*`), optional DDS topics. |
| Key API / entry points | `Tools/autotest/sim_vehicle.py -v copter --console --map [-L <loc>] [-A "<sitl args>"] [--add-param-file f.parm]`; EKF3 source params `EK3_SRC{1,2,3}_{POSXY,VELXY,POSZ,VELZ,YAW}` and `EK3_SRC_OPTIONS` (`libraries/AP_NavEKF/AP_NavEKF_Source.cpp`); RC aux option 90 = EKF source set; Lua `ahrs:set_posvelyaw_source_set(0..2)`, `ahrs:get_posvelyaw_source_set()`, `ahrs:get_vel_innovations_and_variances_for_source(src)`, `ahrs:handle_external_position_estimate(loc, acc_m, t_ms)`, `ahrs:set_origin(loc)` (`libraries/AP_Scripting/docs/docs.lua`); SITL GPS params `SIM_GPS1_ENABLE`, `SIM_GPS1_JAM`, `SIM_GPS1_GLTCH_{X,Y,Z}`, `SIM_GPS1_NUMSATS` (`libraries/SITL/SIM_GPS.cpp`); `VISO_TYPE` 0 None, 1 MAVLink, 2 IntelT265, 3 VOXL. |
| Time to first result | Estimate: 30-60 min to a flying SITL copter on a fresh Ubuntu box (prereq script + first waf build dominate). Another 1-2 h for the ExternalNav recipe below. Assumes x86-64 Ubuntu 22.04/24.04 and network access for submodules. |
| License | GPL-3.0 (GitHub metadata; README: GPLv3 or later). |

## Minimal usage
SITL copter, then turn it into a GNSS-denied ExternalNav vehicle using the simulated Vicon source. The parameter set is taken from the `VisionPosition` test in `Tools/autotest/arducopter.py` (master). Not run.

```bash
./Tools/autotest/sim_vehicle.py -v copter --console --map -A "--serial5=sim:vicon:"
```
In the MAVProxy console:
```
param set EK3_SRC1_POSXY 6
param set EK3_SRC1_VELXY 6
param set EK3_SRC1_POSZ 6
param set EK3_SRC1_VELZ 6
param set GPS1_TYPE 0
param set VISO_TYPE 1
param set SERIAL5_PROTOCOL 1
reboot
```
After reboot the EKF has no global origin. The autotest sends `SYSTEM_TIME` and sets the origin (`SET_GPS_GLOBAL_ORIGIN`) before takeoff; do the same from pymavlink or with the `ahrs-set-origin.lua` applet.

GNSS outage mid-flight instead of no GPS at all (master / 4.7 names): `param set SIM_GPS1_ENABLE 0` (4.6.x: `SIM_GPS_DISABLE 1`). Jamming: `SIM_GPS1_JAM 1` (4.6.x: `SIM_GPS_JAM`). Position glitch: `SIM_GPS1_GLTCH_X/Y` (4.6.x: `SIM_GPS_GLITCH_X/Y`).

## Wiring it into a nav stack
- External pose in: from ROS via [MAVROS](./mavlink__mavros.md) `~/vision_pose/pose` or `~/odometry/out`, from plain Python via [pymavlink](./ardupilot__pymavlink.md) `vision_position_estimate_send` (pattern in [vision_to_mavros](./thien94__vision_to_mavros.md) `t265_to_mavlink.py`). Feed it from [OpenVINS](./rpng__open_vins.md), [ORB-SLAM3](./uz-slamlab__orb_slam3.md) or a map-matcher such as [wildnav](./tiers__wildnav.md).
- Absolute fix from a map-matcher or other non-GNSS geolocation: Lua `ahrs:handle_external_position_estimate(location, accuracy_m, timestamp_ms)` (EKF3 only, altitude ignored), or `GPS_INPUT` via MAVROS `gps_input` plugin / MAVProxy `GPSInput` module.
- Source switching: three source sets (`EK3_SRC1/2/3_*`), switched by RC option 90, MAVLink, or Lua. `libraries/AP_Scripting/examples/ahrs-source.lua` votes between GPS, ExtNav and optical flow on GPS speed accuracy and ExtNav velocity innovation; `applets/ahrs-source-extnav-optflow.lua` is the packaged version. `applets/copter-deadreckon-home.lua` flies home on low GPS quality or EKF failsafe (Copter 4.3+).
- GCS / routing: [MAVProxy](./ardupilot__mavproxy.md) is launched by `sim_vehicle.py` (master TCP 5760, out UDP 127.0.0.1:14550 for instance 0). Add [mavlink-router](./mavlink-router__mavlink-router.md) when several clients need the link. [QGroundControl](./mavlink__qgroundcontrol.md) picks up UDP 14550.
- Catalog: [ArduPilot page](../../catalog/repos/ardupilot__ardupilot.md).

## Gotchas
- Parameter names moved between stable and master: SITL GPS went from `SIM_GPS_*` (4.6.x, `SIM_GPS_DISABLE`) to per-instance `SIM_GPS1_*` with `SIM_GPS1_ENABLE` (checked against tags `Copter-4.6.3` and `Copter-4.7.2`). Copy recipes only for your tag.
- ExternalNav without GPS needs an EKF origin set explicitly; without it the vehicle never reports a global position and AUTO/GUIDED with lat/lon targets fail. Open issue #67 on vision_to_mavros (`set_origin.py` failing) is the same trap.
- `EK3_SRC_OPTIONS` bit 3 (UsePerCoreEKFSources) maps core N to source set N. Default is one active source set across all cores.
- macOS: open issue #34890 (SITL fails to link on current Xcode, `-ld_classic` removed) and #19588 (SITL crash on Apple M1 arm64 without `--speedup`). Prefer a Linux VM/container on Apple Silicon.
- ArduRover GUIDED via MAVROS with ExternalNav and no GPS: closed issue #33049 reports `SET_POSITION_TARGET_LOCAL_NED` not working; check before you build a rover demo on it.
- Lua scripting needs `SCR_ENABLE=1`, a reboot, and enough `SCR_HEAP_SIZE` (the dead-reckon applet asks for 80000+).
- GPL-3.0: modified firmware you distribute must ship source.

## Alternatives
- [PX4](./px4__px4-autopilot.md): BSD-licensed, EKF2 with bitmask aiding control, ROS 2 native over uXRCE-DDS, SIH for a no-Gazebo simulator.
- For a pure estimator without an autopilot: [robot_localization](./cra-ros-pkg__robot_localization.md) or [GTSAM](./borglab__gtsam.md).

Sources: `README.md`, `libraries/AP_NavEKF/AP_NavEKF_Source.cpp`, `libraries/AP_Scripting/docs/docs.lua`, `libraries/AP_Scripting/examples/ahrs-source.lua`, `applets/copter-deadreckon-home.lua`, `applets/ahrs-set-origin.lua`, `libraries/SITL/SIM_GPS.cpp` and `SITL.cpp` (master, Copter-4.6.3, Copter-4.7.2), `libraries/AP_VisualOdom/AP_VisualOdom.cpp`, `Tools/autotest/arducopter.py` (`VisionPosition`), `Tools/autotest/sim_vehicle.py`, repo tree listing, issue search (#34890, #19588, #33049).
