# px4_ros_com - integration card
<!-- about: repo:px4/px4_ros_com -->
One-line: PX4's ROS 2 example package (listeners, offboard control in C++ and Python) plus `frame_transforms.h`, the NED/ENU and FRD/FLU conversion helpers you need when you publish VIO into `/fmu/in/vehicle_visual_odometry` by hand.

| | |
|---|---|
| Install | In a colcon workspace: `git clone https://github.com/PX4/px4_msgs src/px4_msgs && git clone https://github.com/PX4/px4_ros_com src/px4_ros_com && colcon build`. Run the [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md) (`MicroXRCEAgent udp4 -p 8888`) next to PX4 SITL. Install details are delegated to the PX4 uXRCE-DDS and ROS 2 guide (README). |
| Runs on | ROS 2 (Humble/Jazzy per PX4 docs), Linux. Depends directly on `px4_msgs`. |
| Inputs | PX4 uORB topics bridged as `/fmu/out/*` (e.g. `sensor_combined`, `vehicle_gps_position`, `vehicle_odometry`, `vehicle_status`). |
| Outputs | Example publishers to `/fmu/in/offboard_control_mode`, `/fmu/in/trajectory_setpoint`, `/fmu/in/vehicle_command`, `debug_vect`. |
| Key API / entry points | Nodes in `src/examples/`: `listeners/sensor_combined_listener.cpp`, `listeners/vehicle_gps_position_listener.cpp`, `offboard/offboard_control.cpp`, `offboard/offboard_control_srv.cpp`, `offboard_py/offboard_control.py`, `advertisers/debug_vect_advertiser.cpp`; launch `launch/sensor_combined_listener.launch.py`, `launch/offboard_control_launch.yaml`. Library `px4_ros_com::frame_transforms` (`include/px4_ros_com/frame_transforms.h`): `ned_to_enu_orientation`, `enu_to_ned_orientation`, `aircraft_to_baselink_orientation`, `baselink_to_aircraft_orientation`, `px4_to_ros_orientation`, `ros_to_px4_orientation`, `transform_static_frame(vec, StaticTF)`, `quaternion_from_euler`, `quaternion_get_yaw`, `covariance_urt_to_array`. |
| Time to first result | Estimate: 30-45 min to see `ros2 launch px4_ros_com sensor_combined_listener.launch.py` print IMU data from PX4 SITL. Assumes ROS 2 installed and PX4 SITL building. |
| License | BSD-3-Clause. |

## Minimal usage
Not run.

```bash
MicroXRCEAgent udp4 -p 8888 &          # agent
make px4_sitl gz_x500                  # in PX4-Autopilot; starts the uXRCE-DDS client
source install/setup.bash
ros2 launch px4_ros_com sensor_combined_listener.launch.py
ros2 topic echo /fmu/out/vehicle_odometry
```
VIO in (sketch): convert your ENU/FLU pose with `ros_to_px4_orientation` / `transform_static_frame(..., StaticTF::ENU_TO_NED)`, fill `px4_msgs::msg::VehicleOdometry` (`pose_frame = POSE_FRAME_NED`, position, quaternion, variances), publish to `/fmu/in/vehicle_visual_odometry`, set `EKF2_EV_CTRL` on PX4.

## Wiring it into a nav stack
- Same transport as [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md), which wraps the visual-odometry and aux-global-position publishing with validation; prefer that for new navigation inputs and keep px4_ros_com for its frame helpers and listener examples.
- Producers: [OpenVINS](./rpng__open_vins.md), [cuVSLAM](./nvidia-isaac__cuvslam.md), [KISS-ICP](./prbonn__kiss-icp.md). Consumers of `/fmu/out/vehicle_odometry`: [robot_localization](./cra-ros-pkg__robot_localization.md), [Nav2](./ros-navigation__navigation2.md), evaluation with [evo](./michaelgrupp__evo.md).
- Autopilot: [PX4](./px4__px4-autopilot.md) only. For ArduPilot use [MAVROS](./mavlink__mavros.md).
- Catalog: [px4_ros_com page](../../catalog/repos/px4__px4_ros_com.md).

## Gotchas
- `px4_msgs` must match the PX4 firmware version; open issues #145 (optical flow message mismatch) and #143 (ask for version tags matching PX4 releases) show the pain. PX4 `main` also has a message translation node for version skew.
- PX4 publishes `/fmu/out/*` with best-effort QoS; a default reliable subscriber receives nothing. The examples set a sensor-data QoS profile; copy it.
- Last push 2025-11; examples lag PX4 `main` features (no aux global position example here).
- Topic names on newer PX4 can carry a version suffix (see the interface-lib card); check `ros2 topic list` before hard-coding.

## Alternatives
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) for modes and validated navigation inputs.
- [MAVROS](./mavlink__mavros.md) for MAVLink-based ROS 2 access to either autopilot.

Sources: `README.md`, repo tree, `include/px4_ros_com/frame_transforms.h`, PX4 `src/modules/uxrce_dds_client/dds_topics.yaml`, issue search (#145, #143).
