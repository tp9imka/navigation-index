# Isaac ROS Visual SLAM (isaac_ros_cuvslam) - integration card
<!-- about: repo:nvidia-isaac-ros/isaac_ros_visual_slam, repo:nvidia-isaac/cuvslam -->
ROS 2 wrapper around NVIDIA's GPU stereo / multi-camera / RGB-D visual(-inertial) odometry and SLAM ([cuVSLAM](./nvidia-isaac__cuvslam.md)); drop-in `nav_msgs/Odometry` + TF for GNSS-denied flight or driving on Jetson.

| | |
|---|---|
| Install | Isaac ROS 5.0 (release `v5.0-0`, 2026-09-22) targets ROS 2 Lyrical. Binary (docs quickstart): set up the Isaac ROS apt repo / dev environment, then `sudo apt-get install -y ros-lyrical-isaac-ros-cuvslam` (plus `ros-lyrical-isaac-ros-examples ros-lyrical-isaac-ros-realsense` for the RealSense example). Source: clone into `${ISAAC_ROS_WS}/src`, `rosdep install --from-paths ${ISAAC_ROS_WS}/src/isaac_ros_visual_slam/isaac_ros_cuvslam --ignore-src -y`, `colcon build --symlink-install --packages-up-to isaac_ros_cuvslam`. The cuVSLAM library is a git submodule (`cuvslam` => github.com/nvidia-isaac/cuVSLAM); needs `git lfs`. |
| Runs on | Docs getting-started page: Jetson AGX Thor or AGX Orin with JetPack 7.2, or x86_64 Ubuntu 24.04 with an Ampere or newer NVIDIA GPU (8 GB+), CUDA 13.2+, 32 GB+ disk; DGX Spark also listed. No CPU-only path. |
| Inputs | Per camera `i`: `visual_slam/image_i` (sensor_msgs/Image) and `visual_slam/camera_info_i`; optional `visual_slam/imu` (sensor_msgs/Imu), `visual_slam/depth_0` (RGB-D mode), `visual_slam/seg_mask_i` (dynamic-object masks), `visual_slam/initial_pose`. Params: `num_cameras` (2), `tracking_mode` (0 multicamera, 1 VIO with IMU, 2 RGB-D), `rectified_images` (true), `camera_optical_frames`, `imu_frame`, IMU noise (`gyro_noise_density`, `accel_random_walk`, ...), `map_frame`/`odom_frame`/`base_frame` (`map`/`odom`/`base_link`). |
| Outputs | `visual_slam/tracking/odometry` (nav_msgs/Odometry), `visual_slam/tracking/vo_pose` (PoseStamped), `vo_pose_covariance` (PoseWithCovarianceStamped), `vo_path` and `slam_path` (nav_msgs/Path), `visual_slam/status` (`isaac_ros_visual_slam_interfaces/VisualSlamStatus`), diagnostics, TF `map` => `odom` => `base_link` (toggles `publish_map_to_odom_tf`, `publish_odom_to_base_tf`), `visual_slam/vis/*` debug clouds. Services `visual_slam/reset`, `save_map`, `load_map`, `localize_in_map`, `set_slam_pose`, `get_all_poses`. |
| Key API / entry points | Component `nvidia::isaac_ros::visual_slam::VisualSlamNode` in package `isaac_ros_cuvslam`. Launch files in `isaac_ros_cuvslam/launch/`: `isaac_ros_visual_slam.launch.py` (standalone container), `isaac_ros_visual_slam_core.launch.py`, `_realsense.launch.py`, `_realsense_rgbd.launch.py`, `_realsense_mask.launch.py`, `_multi_realsense.launch.py`, `_isaac_sim.launch.py`. Docs also use `ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=realsense_stereo_rect,cuvslam`. Interfaces package `isaac_ros_visual_slam_interfaces` (srv: FilePath, GetAllPoses, LocalizeInMap, Reset, SetSlamPose). |
| Time to first result | Estimate: 1-2 h on a Jetson already flashed with JetPack 7.2 and an Isaac ROS apt setup, using a RealSense or a provided rosbag; a day if you start from flashing. |
| License | Wrapper `LICENSE`: Apache-2.0 (`package.xml` Apache-2.0). The cuVSLAM library underneath is under the "NVIDIA Community License": use only on NVIDIA platforms, not OSI open source, export-control clause (see [cuVSLAM card](./nvidia-isaac__cuvslam.md)). |

## Minimal usage
Not run. From the isaac_ros_cuvslam docs quickstart and `launch/isaac_ros_visual_slam.launch.py`.

```sh
sudo apt-get install -y ros-lyrical-isaac-ros-cuvslam ros-lyrical-isaac-ros-examples ros-lyrical-isaac-ros-realsense
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=realsense_stereo_rect,cuvslam
# or standalone, then remap your camera driver onto visual_slam/image_0, image_1, camera_info_0, camera_info_1
ros2 launch isaac_ros_cuvslam isaac_ros_visual_slam.launch.py
rviz2 -d $(ros2 pkg prefix isaac_ros_cuvslam --share)/rviz/default.cfg.rviz
ros2 topic echo /visual_slam/tracking/odometry
```

## Wiring it into a nav stack
- PX4 / ArduPilot external vision: `visual_slam/tracking/odometry` => [MAVROS](./mavlink__mavros.md) `odometry/out` (MAVLink `ODOMETRY`), or => [px4_ros_com](./px4__px4_ros_com.md) `VehicleOdometry` over XRCE-DDS. Turn off `publish_map_to_odom_tf` if another node owns `map` => `odom`. Frame conversion helper: [vision_to_mavros](./thien94__vision_to_mavros.md).
- Fusion: feed into [robot_localization](./cra-ros-pkg__robot_localization.md) with GNSS/IMU so GNSS can correct drift when available and VSLAM carries through outages.
- Mapping: [isaac_ros_nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) consumes the pose for a 3D ESDF and Nav2 costmap ([Navigation2](./ros-navigation__navigation2.md)).
- Map reuse: `save_map` / `load_map` + `localize_in_map` for repeat missions in a known area.

## Gotchas
- Package renamed 2026-09-21: `isaac_ros_visual_slam` => `isaac_ros_cuvslam` (README "Latest"). Old launch commands (`ros2 launch isaac_ros_visual_slam ...`) and apt names from pre-5.0 tutorials no longer match; topic names stay `visual_slam/...` and the interfaces package is unchanged.
- 5.0 is Lyrical + JetPack 7.2 + CUDA 13.2. Jetson Orin Nano on JetPack 7 failed to start the container (#223, closed); older Jetsons need an older Isaac ROS release (4.x, Jazzy).
- #229: node intermittently stops publishing odometry/status after 60-360 s while inputs keep flowing (3.2.6, AGX Orin). Watch `visual_slam/status` and restart on silence.
- #226: drift while stationary on Orin Nano + D435i; #143: tilted camera mounts; #213: empty gravity topic with Isaac Sim IMU. IMU noise params and extrinsics matter in VIO mode.
- `rectified_images` defaults to true; feeding raw fisheye/distorted images without setting it gives bad tracking.
- Not usable off NVIDIA hardware (licence and CUDA).

## Alternatives
- [cuVSLAM](./nvidia-isaac__cuvslam.md) Python/C++ directly - same engine without ROS, for offline evaluation or non-ROS stacks.
- [OpenVINS](./rpng__open_vins.md) - CPU, open source (GPL-3.0) VIO with better transparency on non-NVIDIA hardware.
- [RTAB-Map](./introlab__rtabmap.md) - CPU RGB-D/stereo/LiDAR SLAM with long-term map management.

Sources: `README.md`, `LICENSE`, `.gitmodules`, `isaac_ros_cuvslam/package.xml`, `isaac_ros_cuvslam/launch/` listing and `isaac_ros_visual_slam.launch.py`, `isaac_ros_cuvslam/src/visual_slam_node.cpp`, `isaac_ros_visual_slam_interfaces/srv` and `msg` listings, releases v4.5-0 v4.6-0 v5.0-0, issues #141 #143 #177 #213 #220 #223 #226 #227 #229 (github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam); nvidia-isaac-ros.github.io `repositories_and_packages/isaac_ros_visual_slam/isaac_ros_cuvslam/` and `getting_started/` pages; github.com/nvidia-isaac/cuVSLAM `LICENSE`.
