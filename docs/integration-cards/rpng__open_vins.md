# OpenVINS - integration card
<!-- about: repo:rpng/open_vins -->
CPU-only MSCKF visual-inertial odometry with online camera/IMU calibration and a built-in simulator, so a team can produce a VIO trajectory before any hardware arrives.

| | |
|---|---|
| Install | From `docs/gs-installing.dox`: `sudo apt-get install libeigen3-dev libboost-all-dev libceres-dev`, then in a workspace `git clone https://github.com/rpng/open_vins/` and `catkin build` (ROS 1) or `colcon build` (ROS 2). ROS-free CMake build also supported (`docs/gs-installing-free.dox`). Dockerfiles in repo root: `Dockerfile_ros1_{16,18,20}_04`, `Dockerfile_ros2_{18,20,22}_04`. Latest release v2.7 (2023-06-20). |
| Runs on | Linux, CPU only (OpenCV 3/4 with contrib for ArUco, Eigen3, Ceres, Boost). ROS 1 Kinetic / Melodic / Noetic; ROS 2 Dashing / Galactic per docs, Humble in CI (`Dockerfile_ros2_22_04` is `FROM osrf/ros:humble-desktop`). Jazzy / 24.04 not in CI. Jetson / aarch64: builds reported by users, no official guidance (see Gotchas). No GPU path. |
| Inputs | `sensor_msgs/Imu` on `topic_imu` (default `/imu0`), `sensor_msgs/Image` on `topic_camera<i>` (default `/cam<i>/image_raw`); topic names can also come from the `rostopic` field of the Kalibr-style `kalibr_imucam_chain.yaml` / `kalibr_imu_chain.yaml` next to `estimator_config.yaml`. Mono, stereo, or N mono cameras (`max_cameras`, `use_stereo`). |
| Outputs | ROS 2 (in node namespace, default `ov_msckf`): `odomimu` (nav_msgs/Odometry, `frame_id` `global`, `child_frame_id` `imu`), `poseimu` (PoseWithCovarianceStamped), `pathimu`, `points_msckf` / `points_slam` / `points_aruco` (PointCloud2), `loop_pose` / `loop_feats` / `loop_extrinsic` / `loop_intrinsics` for a secondary loop-closure node; TF `global` => `imu` and `imu` => `cam<i>`. Optional state dump to text (`save_total_state`). |
| Key API / entry points | Executables `run_subscribe_msckf`, `run_simulation` (confirmed in `ov_msckf/cmake/ROS2.cmake`). Launch `ov_msckf/launch/subscribe.launch.py` (args `config`, `config_path`, `max_cameras`, `use_stereo`, `verbosity`, `rviz_enable`), ROS 1 `subscribe.launch`, `serial.launch`, `simulation.launch`. C++: `ov_msckf::VioManager::feed_measurement_imu(const ov_core::ImuData&)`, `feed_measurement_camera(const ov_core::CameraData&)`, `get_state()`, `initialized()` (`ov_msckf/src/core/VioManager.h`). Evaluation tools in `ov_eval`. |
| Time to first result | Estimate: 1-2 h with the provided Docker image and the EuRoC V1_01_easy bag; simulator run (`run_simulation` with `config/rpng_sim`) in under 1 h, no dataset download. Own sensor: add a day for Kalibr camera-IMU calibration and config. |
| License | GitHub metadata: GPL-3.0; LICENSE file is GNU GPL v3. No model weights. |

## Minimal usage
Not run. From `docs/gs-tutorial.dox` (ROS 2) and the ROS 2 CI workflow.

```sh
# simulator, no data needed
ros2 run ov_msckf run_simulation src/open_vins/config/rpng_sim/estimator_config.yaml

# EuRoC bag (ROS 2 format) with the shipped config
ros2 launch ov_msckf subscribe.launch.py config:=euroc_mav
ros2 bag play V1_01_easy
```

ROS 1: `roslaunch ov_msckf subscribe.launch config:=euroc_mav` and `rosbag play V1_01_easy.bag`.

## Wiring it into a nav stack
- Camera drivers => remap to `/cam0/image_raw`, `/cam1/image_raw`, `/imu0`, or set the `rostopic` fields in the config chain. Calibrate with [Kalibr](../../catalog/repos/ethz-asl__kalibr.md); IMU noise via [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md) or [kalibr_allan](../../catalog/repos/rpng__kalibr_allan.md).
- `/ov_msckf/odomimu` => [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) for fusion with wheel odom / GNSS, or => [MAVROS](../../catalog/repos/mavlink__mavros.md) `odometry/out` for PX4/ArduPilot external vision. Frame names are hard-coded `global` / `imu`; add a static TF or relay to match your `odom` / `base_link`.
- Loop closure is not in the core estimator: the `loop_*` topics are meant for the secondary pose-graph repo `rpng/ov_secondary` (README).
- Score runs with `ov_eval` or [evo](../../catalog/repos/michaelgrupp__evo.md).
- Multi-sensor extension (GNSS, LiDAR, wheel): [MINS](../../catalog/repos/rpng__mins.md).

## Gotchas
- Development is slow: last release v2.7 in 2023; ROS 2 CI stops at Humble. Expect to patch for Jazzy.
- Open issue #553 (Humble): stereo trajectory diverges nondeterministically with "image received out of order" and kilometer-scale positions. Check bag playback rate and timestamps.
- Open issue #540: divergence right after initialization with very large IMU values; usually IMU noise / extrinsic / time-offset config. Static vs dynamic init matter: hold the sensor still or excite it as the config expects.
- Jetson: open #514 (segfault on Orin Nano with some configs), #506 (boost::filesystem link error in Isaac ROS dev container), #350 (diverges on Xavier NX with EuRoC). Budget time for real-time tuning on small ARM boards (lower feature count, `max_cameras`).
- OpenCV must include contrib (ArUco) if you build OpenCV from source (docs). Open #510: ArUco compile issue on Humble + OpenCV 4.
- GPL-3.0: linking it into a distributed product makes that product GPL.

## Alternatives
- [cuVSLAM](./nvidia-isaac__cuvslam.md) - if the platform is a Jetson; GPU stereo-inertial plus SLAM and relocalization, NVIDIA-only license.
- [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) - optimization-based VIO with loop closure and GPS fusion, ROS 1 upstream.
- [Basalt](../../catalog/repos/vladyslavusenko__basalt.md) or [Kimera-VIO](../../catalog/repos/mit-spark__kimera-vio.md) - other CPU VIO options; [MSCKF-VIO](../../catalog/repos/kumarrobotics__msckf_vio.md) for a minimal stereo MSCKF.

Sources: `README.md`, `LICENSE`, `docs/gs-installing.dox`, `docs/gs-tutorial.dox`, `.github/workflows/build_ros1.yml`, `build_ros2.yml`, `Dockerfile_ros2_22_04`, `ov_msckf/src/ros/ROS2Visualizer.cpp`, `ov_msckf/launch/subscribe.launch.py`, `ov_msckf/cmake/ROS2.cmake`, `ov_msckf/src/core/VioManager.h`, release v2.7, issues #350 #506 #510 #514 #540 #553 (github.com/rpng/open_vins).
