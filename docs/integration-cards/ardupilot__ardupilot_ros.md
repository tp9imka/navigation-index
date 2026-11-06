# ardupilot_ros - integration card
<!-- about: repo:ardupilot/ardupilot_ros -->
One-line: ArduPilot's ROS 2 example workspace package that flies an Iris copter in a Gazebo maze on 2D-lidar Cartographer SLAM instead of GPS, plus Nav2 goal navigation; the shortest reference for "external odometry into ArduPilot EKF3 over DDS".

| | |
|---|---|
| Install | No releases or binaries. In a ROS 2 workspace next to [ardupilot_gz](../../catalog/repos/ardupilot__ardupilot_gz.md): `cd ~/ros2_ws/src && git clone https://github.com/ArduPilot/ardupilot_ros.git`, then `rosdep install --from-paths src --ignore-src -r --skip-keys gazebo-ros-pkgs` and `colcon build --packages-up-to ardupilot_ros ardupilot_gz_bringup` (README). ardupilot_gz itself comes from `vcs import --input https://raw.githubusercontent.com/ArduPilot/ardupilot_gz/main/ros2_gz.repos --recursive src`, which also brings ArduPilot, `micro_ros_agent` (humble) and `ros_gz`. |
| Runs on | ROS 2 Humble on Ubuntu (default branch `humble`; the `jazzy` branch README still says Humble and was last committed 2024-11-02). README lists Gazebo Garden; ardupilot_gz README now says Harmonic (default) or Jetty and the ardupilot_ros README adds the Gazebo rosdep sources for Harmonic-on-Humble. Needs a GPU-capable desktop for Gazebo. |
| Inputs | Sim: 2D `scan` (lidar), `/odometry`, `/imu` from the Gazebo bridge. Cartographer node remaps `/odom` => `/odometry` (`launch/cartographer.launch.py`). Nav2 `cmd_vel` (Twist) => `twist_stamper` => `ap/cmd_vel` (TwistStamped). |
| Outputs | Cartographer TF `map` => `odom` => `base_link` (`config/cartographer.lua`: `provide_odom_frame = true`, `tracking_frame = imu_link`), occupancy grid at 0.05 m. ArduPilot consumes `odom` => `base_link` from `/ap/tf` as visual odometry. |
| Key API / entry points | Packages: `ardupilot_cartographer`, `ardupilot_gui`, `ardupilot_ros` (meta). Launch: `ardupilot_cartographer cartographer.launch.py` (args `use_sim_time` default true, `rviz` default true; nodes `cartographer_ros/cartographer_node`, `cartographer_occupancy_grid_node`), `navigation.launch.py` (Nav2 bringup with `config/navigation.yaml` + `twist_stamper`), `twist_stamper.launch.py`; `ros2 run ardupilot_cartographer joy_controller` (keyboard); `ardupilot_gui ardupilot_gui.launch.py sysid:=<n>`. Sim world: `ardupilot_gz_bringup iris_maze.launch.py` (from ardupilot_gz). |
| Time to first result | Estimate: 2-4 h for the first full build of the ardupilot_gz + ardupilot_ros workspace and a SLAM map in RViz; another 1-2 h if the EKF does not accept the vision input (see gotchas). Assumes Ubuntu 22.04 with ROS 2 Humble and Gazebo already installed. |
| License | GPL-3.0 (GitHub; `package.xml` says GPLv3+). |

## Minimal usage
From `ardupilot_cartographer/README.md`. Not run.

```bash
cd ~/ros2_ws && source install/setup.bash
ros2 launch ardupilot_gz_bringup iris_maze.launch.py rviz:=false     # SITL + Gazebo + micro_ros_agent (udp4 2019)
ros2 launch ardupilot_cartographer cartographer.launch.py rviz:=false
ros2 launch ardupilot_cartographer navigation.launch.py              # optional Nav2

# EKF3 params (README, via MAVProxy or any GCS):
#   AHRS_EKF_TYPE=3 EK2_ENABLE=0 EK3_ENABLE=1
#   EK3_SRC1_POSXY=6 EK3_SRC1_POSZ=1 EK3_SRC1_VELXY=6 EK3_SRC1_VELZ=6 EK3_SRC1_YAW=6
#   VISO_TYPE=1   ARMING_CHECK=388598 (optional, disables GPS checks in SITL)
mavproxy.py --console --map --aircraft test --master=:14550
#   mode guided / arm throttle / takeoff 2.5
```

Check the vision path before flying: `ros2 topic echo /ap/tf` must show `odom` => `base_link`, and MAVProxy must not print `VisOdom: not healthy`.

## Wiring it into a nav stack
- External odometry path (ArduPilot `libraries/AP_DDS/AP_DDS_External_Odom.cpp`): AP_DDS subscribes `/ap/tf`, keeps only transforms with `frame_id == "odom"` and `child_frame_id == "base_link"`, converts FLU => NED and feeds `AP_VisualOdom::handle_pose_estimate`. Any odometry source works if it publishes that transform there: swap Cartographer for [KISS-ICP](./prbonn__kiss-icp.md), [FAST-LIO](./hku-mars__fast_lio.md), [RTAB-Map](./introlab__rtabmap.md), [OpenVINS](./rpng__open_vins.md) or [cuVSLAM](./nvidia-isaac__cuvslam.md).
- Transport: [Micro XRCE-DDS Agent](./eprosima__micro-xrce-dds-agent.md) (as `micro_ros_agent udp4 -p 2019` in SITL).
- MAVLink alternative for the same EKF input: [vision_to_mavros](./thien94__vision_to_mavros.md) + [MAVROS](./mavlink__mavros.md) sending `VISION_POSITION_ESTIMATE`, which also carries covariance.
- Planning on top: [Nav2](./ros-navigation__navigation2.md) via `navigation.launch.py`. Sim: [Gazebo gz-sim](./gazebosim__gz-sim.md), [ardupilot_gz](../../catalog/repos/ardupilot__ardupilot_gz.md). Mapping engine: [Cartographer](../../catalog/repos/cartographer-project__cartographer.md).
- Ground truth / scoring: record `/ap/pose/filtered` vs Gazebo pose and compare with [evo](./michaelgrupp__evo.md).
- Catalog: [ardupilot_ros page](../../catalog/repos/ardupilot__ardupilot_ros.md).

## Gotchas
- `/tf` vs `/ap/tf`: since ArduPilot PR #25384 the DDS client listens on `/ap/tf`, while Cartographer publishes `/tf`. Issue #24 ("VisOdom: not Healthy") is exactly this; the fix suggested there is a `topic_tools relay` from `/tf` to `/ap/tf`. `cartographer.launch.py` on `humble` has no such relay, and the only relay found in ardupilot_gz `robot.launch.py` is `gz/tf` => `tf`. Add it yourself.
- Multi-vehicle namespacing in ardupilot_gz broke this package (open #43); the fix (PR #47, `namespace` launch arg) is still open, unmerged. With `DDS_USE_NS=1` topics move under a per-vehicle namespace.
- No covariance: the DDS path sends position/angle error 0; tune `VISO_POS_M_NSE` / `VISO_YAW_M_NSE` (ArduPilot params) instead of relying on SLAM covariance.
- Firmware must include visual odometry; closed #26: some boards' prebuilt firmware lacks `VISO_TYPE`, use custom.ardupilot.org with visual odometry enabled.
- Cartographer config is 2D (`use_trajectory_builder_2d = true`, `TRAJECTORY_BUILDER_2D.max_range = 30`); `EK3_SRC1_POSZ=1` keeps height on the baro. Not a 3D or outdoor recipe as shipped.
- README asks for a real-copter backup EKF source set (GPS/non-GPS transitions); the SITL params disable GPS checks.
- GPL-3.0 launch/config code; low risk for a hackathon.

## Alternatives
- [vision_to_mavros](./thien94__vision_to_mavros.md): MAVLink route into the same ArduPilot EKF3 ExternalNAV, works with older firmware and non-DDS links.
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) / [px4_ros_com](./px4__px4_ros_com.md): the PX4 equivalent if your team runs PX4.
- [RTAB-Map](./introlab__rtabmap.md): richer SLAM (visual + lidar, loop closure, 3D) to plug into the same `/ap/tf` input.

Sources: `README.md`, `ardupilot_cartographer/README.md`, `ardupilot_cartographer/launch/cartographer.launch.py`, `launch/navigation.launch.py`, `launch/twist_stamper.launch.py`, `config/cartographer.lua`, `ardupilot_cartographer/package.xml`, repo tree, branch list and last commits (`humble`, `jazzy`, `main`); ArduPilot `libraries/AP_DDS/README.md`, `AP_DDS_External_Odom.cpp`; ardupilot_gz `README.md`, `ros2_gz.repos`, `ardupilot_gz_bringup/launch/iris_maze.launch.py`, `launch/robots/iris_lidar.launch.py`, `launch/robots/robot.launch.py`; issues #24, #26, #43 and PR #47.
