# MAVROS - integration card
<!-- about: repo:mavlink/mavros -->
One-line: MAVLink-to-ROS 2 bridge for PX4 and ArduPilot; the standard way to push a ROS VIO/SLAM pose or a synthetic GPS fix into an autopilot and get telemetry back as ROS topics.

| | |
|---|---|
| Install | `sudo apt install ros-${ROS_DISTRO}-mavros ros-${ROS_DISTRO}-mavros-extras` then `sudo ros2 run mavros install_geographiclib_datasets.sh` (mandatory). Default branch is `ros2`. |
| Runs on | ROS 2 Humble and newer (README). Linux; any arch with ROS 2 binaries (amd64, arm64 incl. Jetson/RPi). |
| Inputs | `fcu_url` (`udp://:14540@`, `udp://127.0.0.1:14550@127.0.0.1:14557`, `serial:///dev/ttyACM0:921600`, `tcp://...`). ROS topics into plugins, e.g. `~/vision_pose/pose` (`geometry_msgs/PoseStamped`), `~/vision_pose/pose_cov`, `~/odometry/out` (`nav_msgs/Odometry`), `~/gps_input/gps_input` (`mavros_msgs/GPSINPUT`), `~/mocap/pose`, `~/vision_speed/*`. ROS side in ENU/FLU (REP 103/147); MAVROS converts to NED/FRD. |
| Outputs | `/mavros/state`, `/mavros/imu/data`, `/mavros/global_position/*`, `/mavros/local_position/*`, `~/odometry/in`, `/mavros/gpsstatus/*`, services for arm/mode/takeoff/missions/params. |
| Key API / entry points | Launch files (`mavros/launch/`): `node.launch`, `px4.launch` + `px4_pluginlists.yaml`/`px4_config.yaml`, `apm.launch` + `apm_pluginlists.yaml`/`apm_config.yaml`, `apm_with_terrain.launch`, `multi_uas.launch`. Plugins of interest in `mavros_extras`: `vision_pose_estimate` (=> `VISION_POSITION_ESTIMATE`), `odom` (=> `ODOMETRY`), `gps_input` (=> `GPS_INPUT`, `gps_rate` default 5 Hz), `fake_gps`, `mocap_pose_estimate`, `optical_flow`, `landing_target`, `adsb`, `open_drone_id`. `libmavconn` is usable without ROS. |
| Time to first result | Estimate: 20-30 min with ROS 2 already installed: apt install, datasets, launch against SITL, `ros2 topic echo /mavros/state`. |
| License | Triple BSD / GPLv3 / LGPLv3 (`LICENSE.md`); GitHub shows NOASSERTION. |

## Minimal usage
From README (ROS 2). Not run.

```bash
sudo apt install ros-${ROS_DISTRO}-mavros ros-${ROS_DISTRO}-mavros-extras
sudo ros2 run mavros install_geographiclib_datasets.sh
# PX4 SITL
ros2 launch mavros px4.launch fcu_url:=udp://:14540@
# ArduPilot SITL (sim_vehicle.py MAVProxy output on 14550)
ros2 launch mavros apm.launch fcu_url:=udp://127.0.0.1:14550@
ros2 topic echo /mavros/state
```
Vision pose in (from `docs/plugins/extras/vision_pose_estimate.md`): publish `geometry_msgs/PoseStamped` in ENU on `/mavros/vision_pose/pose`, or set `tf/listen: true` with `tf/frame_id` / `tf/child_frame_id` to let the plugin read TF (rate limit default 10 Hz).

## Wiring it into a nav stack
- VIO/SLAM: [OpenVINS](./rpng__open_vins.md), [RTAB-Map](./introlab__rtabmap.md), [ORB-SLAM3](./uz-slamlab__orb_slam3.md), [cuVSLAM](./nvidia-isaac__cuvslam.md) => `odometry/out` or `vision_pose/pose` => [ArduPilot](./ardupilot__ardupilot.md) (`VISO_TYPE=1`, `EK3_SRC1_*=6`) or [PX4](./px4__px4-autopilot.md) (`EKF2_EV_CTRL`). The [vision_to_mavros](./thien94__vision_to_mavros.md) node handles the TF rotation for T265-style cameras.
- Absolute fix from map-matching as GPS: `gps_input` plugin => ArduPilot `GPS1_TYPE=14`. For PX4 prefer ROS 2 direct to `/fmu/in/aux_global_position` ([px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md)) since PX4 `main` has no `GPS_INPUT` handler.
- PX4 + ROS 2 can skip MAVROS entirely via uXRCE-DDS ([px4_ros_com](./px4__px4_ros_com.md)); MAVROS remains the path for ArduPilot and for mixed fleets.
- Fused output into [robot_localization](./cra-ros-pkg__robot_localization.md) or [Nav2](./ros-navigation__navigation2.md) from `/mavros/local_position/odom`.
- LLM access to the same topics: [ros-mcp-server](./robotmcp__ros-mcp-server.md), [ROSA](./nasa-jpl__rosa.md).
- Catalog: [MAVROS page](../../catalog/repos/mavlink__mavros.md).

## Gotchas
- Skipping `install_geographiclib_datasets.sh` makes the node fail at start (README calls it mandatory).
- Frames: publish ENU/FLU on the ROS side; double conversion (feeding already-NED data) is the most common "drone flies away" bug. Check by walking the camera north and watching `/mavros/local_position/pose`.
- Rate: autopilots want vision at 15-30 Hz or more; `tf/rate_limit` defaults to 10 Hz for the TF-listen mode.
- Plugin blacklists: closed issue #1917 notes some plugins still loaded when blacklisted; verify with `ros2 node info`.
- ROS 1 (`master` branch, Noetic) still exists but docs on the default branch are ROS 2.

## Alternatives
- [px4_ros_com](./px4__px4_ros_com.md) + uXRCE-DDS: PX4 only, no MAVLink hop, uORB-native messages.
- [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md): ArduPilot's own DDS/ROS 2 path.
- [pymavlink](./ardupilot__pymavlink.md) when there is no ROS at all.

Sources: `README.md`, `LICENSE.md`, `mavros/launch/` listing, `mavros_extras/src/plugins/` listing, `docs/plugins/extras/{vision_pose_estimate,odom,gps_input}.md`, issue search.
