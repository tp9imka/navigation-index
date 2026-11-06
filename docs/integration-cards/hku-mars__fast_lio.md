# FAST-LIO2 - integration card
<!-- about: repo:hku-mars/fast_lio -->
Tightly coupled LiDAR-inertial odometry (iterated EKF + ikd-Tree) that gives a drift-limited pose and a registered point cloud from a Livox, Velodyne or Ouster plus IMU, on CPU, including ARM boards.

| | |
|---|---|
| Install | ROS 1 (`main` branch): install and source `livox_ros_driver` first, then `cd ~/<ws>/src && git clone https://github.com/hku-mars/FAST_LIO.git && cd FAST_LIO && git submodule update --init && cd ../.. && catkin_make`. ROS 2 (`ROS2` branch, maintained by Ericsii): install and source `livox_ros_driver2`; the branch README clones the fork `git clone https://github.com/Ericsii/FAST_LIO.git --recursive`, then `rosdep install --from-paths src --ignore-src -y && colcon build --symlink-install` (upstream `-b ROS2` should be equivalent, not checked). Docker image for ROS 1 in README: `kenny0407/marslab_fastlio2:latest` (third-party image). No tagged releases. Deps: PCL >= 1.8, Eigen >= 3.3.4. |
| Runs on | Linux CPU. ROS 1 >= Melodic on `main`; ROS 2 >= Foxy, Humble recommended, Ubuntu >= 20.04 on `ROS2`. README lists ARM support: Khadas VIM3, NVIDIA TX2, Raspberry Pi 4B (8 GB). No GPU use (closed issue #426 asked for Jetson GPU acceleration). Ubuntu >= 16.04. |
| Inputs | LiDAR on `common.lid_topic` (default `/livox/lidar`): `livox_ros_driver(2)/CustomMsg` when `preprocess.lidar_type` = 1 (AVIA), otherwise `sensor_msgs/PointCloud2` (types VELO16 = 2, OUST64 = 3, MID360 = 4 on the ROS 2 branch). Points must carry per-point time (`time` for Velodyne, `t` for Ouster; set `preprocess.timestamp_unit` SEC/MS/US/NS). IMU on `common.imu_topic` (default `/livox/imu`), `sensor_msgs/Imu`, 6 or 9 axis. Extrinsic `mapping.extrinsic_T` / `extrinsic_R` = LiDAR pose in IMU frame (rotation matrix only). |
| Outputs | `/Odometry` (nav_msgs/Odometry, `frame_id` `camera_init`, `child_frame_id` `body`), TF `camera_init` => `body`, `/path`, `/cloud_registered` (world frame), `/cloud_registered_body`, `/cloud_effected`, `/Laser_map` (all PointCloud2). Optional `PCD/scans.pcd` when `pcd_save_en` is set. ROS 2 adds a `map_save` service (std_srvs/Trigger). |
| Key API / entry points | ROS 1 launch: `mapping_avia.launch`, `mapping_horizon.launch`, `mapping_mid360.launch`, `mapping_ouster64.launch`, `mapping_velodyne.launch`, `mapping_marsim.launch`. ROS 2: `ros2 launch fast_lio mapping.launch.py config_file:=<avia|horizon|mid360|ouster64|velodyne>.yaml` (default `mid360.yaml`; `config_path` overrides the directory). Node `LaserMappingNode` in `src/laserMapping.cpp`; preprocessing in `src/preprocess.cpp` (enum `LID_TYPE`). Key params: `preprocess.lidar_type`, `scan_line`, `blind`, `mapping.extrinsic_est_en`, `common.time_sync_en`, `filter_size_map`. |
| Time to first result | Estimate: 2-3 h on ROS 1 Noetic or ROS 2 Humble x86 with the README Avia bag (Google Drive) or NCLT bag; ROS 2 users must convert the ROS 1 bags first (README). Own sensor: add a few hours for extrinsics and timestamp fields. |
| License | GitHub metadata: GPL-2.0; LICENSE file is GNU GPL v2. No weights. |

## Minimal usage
Not run. ROS 2 branch README, Livox Avia bag.

```sh
cd <ros2_ws>/src && git clone https://github.com/Ericsii/FAST_LIO.git --recursive
cd .. && rosdep install --from-paths src --ignore-src -y && colcon build --symlink-install && source install/setup.bash
ros2 launch fast_lio mapping.launch.py config_file:=avia.yaml
ros2 bag play <converted_avia_bag>
```

ROS 1: `roslaunch fast_lio mapping_velodyne.launch` then `rosbag play <bag>`.

## Wiring it into a nav stack
- Drivers: Livox via [livox_ros_driver2](../../catalog/repos/livox-sdk__livox_ros_driver2.md) in CustomMsg mode (`msg_MID360_launch.py`), not the PointCloud2 launch.
- Pose: `/Odometry` => [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) or [MAVROS](../../catalog/repos/mavlink__mavros.md) `odometry/out` (MAVLink `ODOMETRY`). Rename or statically connect `camera_init` / `body` to your `odom` / `base_link`; the names are hard-coded.
- Map: `/cloud_registered` feeds OctoMap, Nav2 costmaps ([navigation2](../../catalog/repos/ros-navigation__navigation2.md)) or a voxel mapper.
- No loop closure and no relocalization in a prior map. Add [FAST_LIO_LOCALIZATION](../../catalog/repos/hviktortsoi__fast_lio_localization.md) for map-based relocalization or a scan-context pose graph ([Scan Context](../../catalog/repos/gisbi-kim__scancontext.md)).
- LiDAR-IMU extrinsic and time offset: [LiDAR_IMU_Init](../../catalog/repos/hku-mars__lidar_imu_init.md).

## Gotchas
- `livox_ros_driver2` (ROS 2) or `livox_ros_driver` (ROS 1) is a hard build dependency even if you only use a Velodyne or Ouster (`package.xml`, `find_package(livox_ros_driver2 REQUIRED)`).
- "Failed to find match for field 'time'" means the cloud lacks per-point timestamps, so motion undistortion silently degrades (README note B; 17 issues, e.g. #45, #115 on KITTI, #410 Hesai).
- Livox must use the CustomMsg launch; the PointCloud2 launch lacks per-point time (README).
- Sync matters: README says hardware-sync LiDAR and IMU; `time_sync_en` is a crude software fallback.
- README recommends `extrinsic_est_en: false` when the extrinsic is known.
- Open ROS 2 issues: #458 startup lag when IMU starts before LiDAR, #449 misses when stationary over 5 minutes with `map_en`.
- ROS 2 branch is a community fork; parity with `main` is not guaranteed.
- GPL-2.0 copyleft.

## Alternatives
- [KISS-ICP](./prbonn__kiss-icp.md) - LiDAR-only, no IMU, no extrinsics, `pip install`; pick it when the IMU is missing or uncalibrated.
- [Point-LIO](../../catalog/repos/hku-mars__point-lio.md) for aggressive motion / IMU saturation, [Faster-LIO](../../catalog/repos/gaoxiang12__faster-lio.md) for lower CPU.
- [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md), [DLIO](../../catalog/repos/vectr-ucla__direct_lidar_inertial_odometry.md) or [GLIM](../../catalog/repos/koide3__glim.md) when you need loop closure / GNSS factors or GPU acceleration (GLIM).

Sources: `README.md` (`main` and `ROS2` branches), `LICENSE`, `src/laserMapping.cpp` (both branches), `src/preprocess.h`, `package.xml`, `CMakeLists.txt`, `launch/mapping.launch.py` and `launch/` listing (github.com/hku-mars/FAST_LIO); issues #45 #115 #410 #426 #449 #458.
