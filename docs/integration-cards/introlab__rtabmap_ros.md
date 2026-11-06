# rtabmap_ros - integration card
<!-- about: repo:introlab/rtabmap_ros -->
The ROS 2 (and ROS 1) wrapper around [RTAB-Map](./introlab__rtabmap.md): odometry nodes (RGB-D, stereo, ICP LiDAR), the `rtabmap` SLAM node with a persistent SQLite map, a localization-only mode and Nav2-ready outputs, all from `apt`; the shortest path to a mapped-then-relocalizing ground or low-altitude robot in ROS 2.

| | |
|---|---|
| Install | `sudo apt install ros-$ROS_DISTRO-rtabmap-ros` (README table: Humble, Jazzy, Kilted, Lyrical, Rolling; Noetic EOL on `master`; Iron EOL). Source (default branch `ros2`): `sudo apt remove ros-$ROS_DISTRO-rtabmap*`, then in `~/ros2_ws`: `git clone https://github.com/introlab/rtabmap.git src/rtabmap`, `git clone --branch ros2 https://github.com/introlab/rtabmap_ros.git src/rtabmap_ros`, `rosdep update && rosdep install --from-paths src --ignore-src -r -y`, `export MAKEFLAGS="-j6"`, `colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release` (add `-DRTABMAP_SYNC_MULTI_RGBD=ON -DRTABMAP_SYNC_USER_DATA=ON` for multi-camera / user data). Docker: `introlab3it/rtabmap_ros`. Latest GitHub release 0.23.13 (2026-10-04). |
| Runs on | Linux with ROS 2 Humble or newer (README: "ROS 2 Humble minimum required"). CPU by default; GPU options come from how the core rtabmap library is built (see the RTAB-Map card). Buildfarm binaries are amd64 per the README badges; aarch64 availability not checked here. |
| Inputs | `rtabmap.launch.py` args: `rgb_topic` (default `/camera/rgb/image_rect_color`), `depth_topic`, `camera_info_topic`, `stereo` + `stereo_namespace`, `rgbd_sync`, `subscribe_scan` + `scan_topic` (`/scan`, LaserScan), `subscribe_scan_cloud` + `scan_cloud_topic` (`/scan_cloud`, PointCloud2), `imu_topic` (`/imu/data`), `gps_topic` (`/gps/fix`, NavSatFix), `tag_topic` (`/detections`), `fiducial_topic`, `odom_topic` (`odom`), `frame_id` (`base_link`). External odometry is accepted in place of the built-in odometry nodes. |
| Outputs | Occupancy grid on `map_topic` (`map`), point cloud / OctoMap / grid_map outputs, `localization_pose`, graph and info topics (`rtabmap_msgs`), TF `map` => `odom` (`publish_tf_map`), and from the odometry nodes nav_msgs/Odometry plus TF `odom` => `base_link` (`publish_tf_odom`). Database at `database_path` (default `~/.ros/rtabmap.db`). Full topic list on the [RTAB-Map card](./introlab__rtabmap.md). |
| Key API / entry points | `ros2 launch rtabmap_launch rtabmap.launch.py` with `localization:=true|false`, `visual_odometry`, `icp_odometry`, `rtabmap_args:="-d"` (delete DB on start), `qos`, `approx_sync`, `rtabmap_viz`, `rviz`. Odometry executables (`rtabmap_odom`): `rgbd_odometry`, `stereo_odometry`, `icp_odometry` (also composable nodes; `guess_frame_id` takes a wheel/EKF odom frame as the registration prior). SLAM node: `rtabmap_slam rtabmap` with services `set_mode_localization` / `set_mode_mapping`. Sync nodes `rgbd_sync`, `stereo_sync`, `rgbdx_sync`. Examples in `rtabmap_examples/launch/`: `lidar3d.launch.py`, `lidar3d_assemble.launch.py`, `vlp16_zed.launch.py`, `realsense_d435i_*.launch.py`, `zed.launch.py`, `depthai*.launch.py`, `euroc_datasets.launch.py`. Nav2 plugin package `rtabmap_costmap_plugins` (voxel layer that follows the robot in z, for drones). |
| Time to first result | Estimate: 30-60 min with apt on Humble/Jazzy and a supported RGB-D/stereo camera or a VLP-16 bag via `lidar3d.launch.py`; a day for a source build with custom core options. |
| License | LICENSE file: BSD-3-Clause. README notes the core RTAB-Map library may be built with components under other licences (SIFT/SURF, g2o, GTSAM, etc.; see the RTAB-Map card's licensing gotchas). No weights shipped. |

## Minimal usage
Not run. From `rtabmap_examples/launch/lidar3d.launch.py` header and launch args.

```sh
sudo apt install ros-$ROS_DISTRO-rtabmap-ros
# mapping (this example deletes ~/.ros/rtabmap.db on start when localization is false)
ros2 launch rtabmap_examples lidar3d.launch.py lidar_topic:=/velodyne_points frame_id:=velodyne imu_topic:=/imu/data
# later, localize in the saved map
ros2 launch rtabmap_examples lidar3d.launch.py lidar_topic:=/velodyne_points frame_id:=velodyne localization:=true
```

RGB-D with the generic launch:

```sh
ros2 launch rtabmap_launch rtabmap.launch.py rtabmap_args:="-d" \
  rgb_topic:=/camera/color/image_raw depth_topic:=/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/color/camera_info frame_id:=base_link approx_sync:=true qos:=1
```

## Wiring it into a nav stack
- Nav2: `map` (OccupancyGrid) and `map` => `odom` TF replace AMCL + map_server; `rtabmap_demos` has Nav2 examples. [Nav2 card](./ros-navigation__navigation2.md).
- Wheel + IMU first: fuse with [robot_localization](./cra-ros-pkg__robot_localization.md) and pass that frame as `guess_frame_id` to `icp_odometry` / `rgbd_odometry` (the `rtabmap_odom` README calls it the highest-value parameter for a wheeled robot).
- External LiDAR or visual odometry instead of the built-in nodes: `visual_odometry:=false icp_odometry:=false odom_topic:=<topic>`, e.g. from [RKO-LIO](./prbonn__rko_lio.md), [KISS-ICP](./prbonn__kiss-icp.md) or [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md).
- GNSS: the launch file feeds `gps_topic` (NavSatFix) to the SLAM node as an asynchronous input (`rtabmap_slam` README diagram). How it constrains the graph was not checked in source; open issues ask exactly that (#247 mapping deviates from GPS odometry, #1392 "Does RTAB map use GPS to filter the odom?", #521 GPS heading as `global_pose`), so validate before relying on it.
- Autopilot: `localization_pose` or the map-frame odometry => [MAVROS](./mavlink__mavros.md) / [vision_to_mavros](./thien94__vision_to_mavros.md).

## Gotchas
- DDS drops: with Fast DDS (ROS 2 default) the nodes subscribe best effort when `qos=0`, and large images or clouds get silently dropped. README fix: `qos:=1` and `export FASTDDS_BUILTIN_TRANSPORTS=LARGE_DATA` on every machine (or switch to Cyclone DDS). README measured D435i RGB-D odometry going from 17.5 Hz to 27 Hz with both.
- The database persists: restarting without `-d` / `delete_db_on_start` continues the old map as a new session. The `lidar3d` example passes `-d` in mapping mode, so re-running it in mapping mode wipes your map.
- Localization mode needs the robot to see a previously mapped place before it relocalizes; open issues #1416 and #766 show LiDAR-only relocalization and localization drift questions.
- Building from source while the apt rtabmap is installed mixes libraries; README says remove the binaries first. Use `MAKEFLAGS=-j6` or fewer on machines with < 16 GB RAM.
- Parameters are mostly documented in the ROS 1 wiki and the core parameter reference; names are unchanged in ROS 2.
- 557 open issues on GitHub (metadata at time of writing): search before debugging.

## Alternatives
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) - GPU stereo VIO on Jetson/NVIDIA; no occupancy map.
- [LIO-SAM](./tixiaoshan__lio-sam.md) - LiDAR-inertial with a GPS factor; no localization-only mode or database.
- [ORB-SLAM3](./uz-slamlab__orb_slam3.md) - visual(-inertial) SLAM with atlas relocalization, but no ROS 2 outputs out of the box (see [ORB_SLAM3_ROS2](./zang09__orb_slam3_ros2.md)).

Sources: `README.md` (branch `ros2`), `LICENSE`, branches list, release 0.23.13, `rtabmap_launch/launch/rtabmap.launch.py`, `rtabmap_examples/launch/` listing and `lidar3d.launch.py`, `rtabmap_odom/README.md`, `rtabmap_slam/README.md`, issues #247 #521 #766 #1392 #1416 (github.com/introlab/rtabmap_ros); existing card `introlab__rtabmap.md`.
