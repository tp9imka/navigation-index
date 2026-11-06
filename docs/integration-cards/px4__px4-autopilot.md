# PX4 Autopilot - integration card
<!-- about: repo:px4/px4-autopilot -->
One-line: BSD autopilot whose EKF2 takes GNSS, external vision, optical flow and an "auxiliary global position" (map-matching, pseudolites, LEO) through per-source bitmask params, with a lightweight SIH simulator and a failure-injection command that turns GPS off, stuck or wrong mid-flight.

| | |
|---|---|
| Install | `git clone https://github.com/PX4/PX4-Autopilot --recursive && bash ./PX4-Autopilot/Tools/setup/ubuntu.sh` then reboot/re-login. Latest stable release seen: `v1.17.0` (2026-05-13). |
| Runs on | Ubuntu 22.04/24.04 x86-64 is the documented path. Gazebo (gz) SITL needs a GPU-capable desktop; SIH needs no 3D simulator. ROS 2 Humble/Jazzy for the uXRCE-DDS bridge. |
| Inputs | MAVLink (`mavlink_receiver.cpp`): `VISION_POSITION_ESTIMATE`, `ODOMETRY`, `OPTICAL_FLOW_RAD`, `SET_GPS_GLOBAL_ORIGIN`, `LANDING_TARGET`, `HIL_GPS`, and on `main` `GLOBAL_POSITION_SENSOR` (=> aux global position). `GPS_INPUT` has no handler on `main`. ROS 2 via uXRCE-DDS `/fmu/in/*`: `vehicle_visual_odometry`, `vehicle_mocap_odometry` (`px4_msgs/VehicleOdometry`), `aux_global_position` (`AuxGlobalPosition`), `sensor_optical_flow`, `distance_sensor`, on `main` also `sensor_gnss`. Frames NED/FRD. |
| Outputs | uORB topics (`vehicle_odometry`, `estimator_status_flags`, ...), `/fmu/out/*` ROS 2 topics, MAVLink telemetry, ULog `.ulg` logs (review with [flight_review](../../catalog/repos/px4__flight_review.md)). |
| Key API / entry points | `make px4_sitl gz_x500` (also `gz_x500_vision`, `gz_x500_flow`, `gz_x500_mono_cam_down`, `gz_x500_lidar_down`); SIH: `make px4_sitl sihsim_quadx` on v1.17.0, `make px4_sitl_sih sihsim_quadx` on `main`; pxh shell: `listener <topic>`, `uorb top`, `failure gps off|stuck|wrong [-i n]`, `param set`; EKF2 params `EKF2_GPS_CTRL` (bits lon/lat, alt, 3D vel, dual-antenna heading), `EKF2_EV_CTRL` (hpos, vpos, vel, yaw), `EKF2_OF_CTRL`, `EKF2_BARO_CTRL`, `EKF2_HGT_REF`, `EKF2_GPS_MODE` / `EKF2_AGP*_MODE` (0 automatic, 1 dead-reckoning), aux global position `EKF2_AGP_CTRL` (v1.17.0) or `EKF2_AGP0..3_CTRL` + `EKF2_AGP0..3_ID` (`main`); `SYS_FAILURE_EN=1` to allow injection. |
| Time to first result | Estimate: 45-90 min from clean Ubuntu to a SIH or gz quad in QGC (setup script + first build). SIH saves the Gazebo install. Assumes x86-64 Ubuntu and a normal network. |
| License | BSD-3-Clause. |

## Minimal usage
GNSS loss in SIH, then fly on dead reckoning or vision. From `docs/en/sim_sih/index.md` and `docs/en/debug/failure_injection.md`. Not run.

```bash
make px4_sitl sihsim_quadx                 # v1.17.0; on main: make px4_sitl_sih sihsim_quadx
# optional faster than real time (main docs): PX4_SIM_SPEED_FACTOR=10 make px4_sitl_sih sihsim_quadx
```
In the `pxh>` shell:
```
param set SYS_FAILURE_EN 1
commander takeoff
failure gps off          # or: failure gps wrong   (offset/spoof-like), failure gps stuck
listener estimator_status_flags
failure gps ok           # clears the injection
```
Same from Python: `examples/failure_injection.py` in [MAVSDK-Python](./mavlink__mavsdk-python.md) (`drone.failure.inject(FailureUnit.SENSOR_GPS, FailureType.OFF, instance=0)`).

Vision-aided Gazebo variant: `make px4_sitl gz_x500_vision` publishes external-vision odometry from the model; `failure vio off|stuck` is applied to it on gz.

## Wiring it into a nav stack
- VIO/SLAM pose => `/fmu/in/vehicle_visual_odometry` (ROS 2) or `ODOMETRY` (MAVLink via [MAVROS](./mavlink__mavros.md) `odometry/out`). Set `EKF2_EV_CTRL` bits and `EKF2_EV_DELAY`. Frame and quaternion helpers: [px4_ros_com](./px4__px4_ros_com.md) `frame_transforms.h`.
- Map-matching / visual geolocation (lat/lon + std dev) => `/fmu/in/aux_global_position` (`AuxGlobalPosition`: `lat`, `lon`, `alt`, `eph`, `epv`, `source` enum GNSS/VISION/PSEUDOLITES/TERRAIN/MAGNETIC/ESTIMATOR/LEO). The clean C++ wrapper is `GlobalPositionMeasurementInterface` in [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md). Producers: [wildnav](./tiers__wildnav.md), [AnyLoc](./anyloc__anyloc.md), [TERCOM nav](./mzahana__tercom_nav.md).
- Custom flight behaviour on GNSS loss (hold, return on dead reckoning) as a ROS 2 external mode with px4-ros2-interface-lib rather than a firmware fork.
- GCS: [QGroundControl](./mavlink__qgroundcontrol.md) on UDP 14550; MAVSDK on 14540 (per SIH docs).
- Catalog: [PX4 page](../../catalog/repos/px4__px4-autopilot.md).

## Gotchas
- `main` and `v1.17.0` differ in exactly the places a GNSS-denied demo touches: SIH build target (`px4_sitl_sih` vs `px4_sitl`), AGP params (multi-instance `EKF2_AGP0_*` vs single `EKF2_AGP_*`), `GLOBAL_POSITION_SENSOR` MAVLink ingress (only on `main`), `/fmu/in/sensor_gnss` (only on `main`). Pin one and read docs from that tag.
- `EKF2_AGP*_CTRL` bit 1 (vertical) is reserved and not fused; altitude only matters when the origin is first set (param description; closed issue #29153 on the bitmask behaviour).
- Failure injection: PX4 ACKs failure types the active simulator does not apply. Per the docs table, SIH ignores `vio` and `airspeed`; `optical_flow` is rejected everywhere.
- ROS 2 message definitions must match the firmware (`px4_msgs` branch = PX4 release) or you get silent topic mismatches; see the px4_ros_com and interface-lib cards.
- macOS: several gz build issues (#21157, #27026 closed; #28657 open, gz optical_flow plugin vs OpenCV 5). Use Ubuntu or SIH.

## Alternatives
- [ArduPilot](./ardupilot__ardupilot.md): EKF3 source sets switchable from Lua, richer SITL GPS fault params (jam, glitch), GPL.
- Simulators without the autopilot: [Gazebo gz-sim](./gazebosim__gz-sim.md), [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md).

Sources: `README.md`, `src/modules/ekf2/params_{gnss,external_vision,aux_global_position,optical_flow,barometer}.yaml` and `module.yaml` (main and v1.17.0), `msg/versioned/AuxGlobalPosition.msg`, `src/modules/uxrce_dds_client/dds_topics.yaml` (main and v1.17.0), `src/modules/mavlink/mavlink_receiver.cpp` (main and v1.17.0), `docs/en/debug/failure_injection.md`, `docs/en/sim_sih/index.md` (main and v1.17.0), `ROMFS/px4fmu_common/init.d-posix/airframes/` listing, releases API, issue search.
