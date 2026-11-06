# imu_tools - integration card
<!-- about: repo:ccnyroboticslab/imu_tools -->
apt-installable ROS 1/ROS 2 nodes that turn raw `sensor_msgs/Imu` (plus optional magnetometer) into an orientation quaternion (Madgwick or complementary filter), plus an RViz IMU display. The standard first stage before robot_localization.

| | |
|---|---|
| Install | Binaries: `sudo apt-get install ros-<distro>-imu-tools` (README: released into all current ROS 1 and ROS 2 distros). Source: `git clone -b <distro> https://github.com/CCNYRoboticsLab/imu_tools.git` into a workspace, `rosdep install`, `colcon build` (ROS 2) or `catkin_make` (ROS 1). Branches exist per distro, including `humble`, `jazzy`, `kilted`, `rolling` (default) and `noetic`. |
| Runs on | Any ROS-supported platform (C++, CPU only). Same code paths on x86 and ARM/Jetson. |
| Inputs | `imu/data_raw` (`sensor_msgs/Imu`, gyro rad/s, accel m/s^2; orientation field ignored) and, when `use_mag` is true, `imu/mag` (`sensor_msgs/MagneticField`). Topic names are relative, so remap or push into a namespace. Madgwick `use_mag` defaults to true; complementary `use_mag` defaults to false. |
| Outputs | `imu/data` (`sensor_msgs/Imu` with orientation filled; Madgwick can also remove gravity from accel with `remove_gravity_vector`). Debug topics `imu/rpy/filtered`, `imu/rpy/raw` (Madgwick) when `publish_debug_topics`; complementary also publishes `imu/steady_state` (`std_msgs/Bool`) when bias estimation is on. Optional TF `fixed_frame` (default `odom`) => IMU frame when `publish_tf` (Madgwick default true, complementary default false). |
| Key API / entry points | Madgwick: executable `imu_filter_madgwick_node`, component `ImuFilterMadgwickRos`, launch `ros2 launch imu_filter_madgwick imu_filter.launch.py` (node name `imu_filter`, params `config/imu_filter.yaml`), also `imu_filter_component.launch.py`. Params: `gain` (0.1), `zeta` (gyro drift gain), `world_frame` (`enu` default, `ned`, `nwu`), `use_mag`, `mag_bias_x/y/z`, `declination`, `yaw_offset`, `stateless`, `constant_dt`, `orientation_stddev`, `time_jump_threshold`. Complementary: executable `complementary_filter_node`, launch `ros2 launch imu_complementary_filter complementary_filter.launch.py` (node `complementary_filter_gain_node`), params `gain_acc`, `gain_mag`, `bias_alpha`, `do_bias_estimation`, `do_adaptive_gain`. RViz plugin `rviz_imu_plugin`. |
| Time to first result | Estimate: 10 min with the apt package and a live IMU or a bag with `imu/data_raw`. |
| License | Split: `LICENSE` says `imu_filter_madgwick` is GPL-3.0-or-later (`LICENSE.gplv3`), everything else BSD-3-Clause (`LICENSE.bsd`). GitHub metadata shows NOASSERTION because of the split. Sample bags in `imu_filter_madgwick/sample/` carry no separate licence. |

## Minimal usage
Not run. ROS 2 (from launch files and source):

```sh
sudo apt install ros-humble-imu-tools
ros2 launch imu_filter_madgwick imu_filter.launch.py      # expects imu/data_raw (+ imu/mag)
# or without magnetometer, explicit remap:
ros2 run imu_filter_madgwick imu_filter_madgwick_node --ros-args \
  -p use_mag:=false -p world_frame:=enu -p publish_tf:=false \
  -r imu/data_raw:=/camera/imu
ros2 topic echo /imu/data --field orientation
```

## Wiring it into a nav stack
- `imu/data` => [robot_localization](./cra-ros-pkg__robot_localization.md) `imu0` (orientation + angular velocity) next to wheel odometry, VIO or GNSS. Set `publish_tf:=false` so this node does not fight the EKF over `odom` => `base_link`.
- RealSense / OAK IMUs publish gyro and accel without orientation; this node fills it before [RTAB-Map](./introlab__rtabmap.md) or Nav2.
- MAVLink side: flight controllers already estimate attitude; use this only on companion-computer IMUs, not to replace the autopilot EKF.
- Characterise the IMU first with [allan_variance_ros](./ori-drs__allan_variance_ros.md) if you need noise numbers for a downstream filter; this package does not output covariances beyond a fixed `orientation_stddev`.

## Gotchas
- `world_frame` default is `enu` in ROS 2 and must match what downstream expects; ArduPilot/PX4 are NED. Invalid values silently fall back to `enu` with a warning (`imu_filter_ros.cpp`).
- Madgwick defaults `use_mag: true`; IMU and mag go through an `ApproximateTime` synchronizer, so with no `imu/mag` publisher nothing is published. Issue #211 (closed): Z axis flips if the magnetometer stops publishing for some seconds.
- Yaw without a magnetometer is unobservable and starts at an arbitrary value (open issues #73, #205); output drifts or skews over time on some IMUs (open #179, #184, #193 RealSense).
- `fixed_frame` TF lookup errors (`"odom" ... does not exist`, closed #194) when `publish_tf` is on but nothing else defines the frame.
- Licensing: the Madgwick package is GPL-3.0; use `imu_complementary_filter` (BSD) if you ship a closed binary.
- The README now also advertises a third-party UKF ("FusionCore"); it is not part of this repo and not evaluated here.

## Alternatives
- [xioTechnologies Fusion](./xiotechnologies__fusion.md) - newer Madgwick-family AHRS in C with Python bindings, no ROS needed, MIT.
- [ahrs](../../catalog/repos/mayitzin__ahrs.md) - pure-Python collection of AHRS filters for offline comparison.
- [robot_localization](./cra-ros-pkg__robot_localization.md) alone can integrate raw gyro, but it does not estimate tilt from accel the way these filters do.

Sources: `README.md`, `LICENSE`, `imu_filter_madgwick/launch/imu_filter.launch.py`, `imu_filter_madgwick/config/imu_filter.yaml`, `imu_filter_madgwick/src/imu_filter_ros.cpp`, `imu_filter_madgwick/CMakeLists.txt`, `imu_complementary_filter/launch/complementary_filter.launch.py`, `imu_complementary_filter/config/filter_config.yaml`, `imu_complementary_filter/src/complementary_filter_ros.cpp`, branch list, issues #73 #179 #184 #193 #194 #205 #211 (github.com/CCNYRoboticsLab/imu_tools).
