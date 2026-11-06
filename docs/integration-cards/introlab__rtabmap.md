# RTAB-Map - integration card
<!-- about: repo:introlab/rtabmap -->
Graph SLAM with appearance-based loop closure for RGB-D, stereo and 2D/3D LiDAR, with a GUI, a SQLite map database, localization-only mode and Nav2-ready occupancy grids; the fastest path to "map once, relocalize later" on a ground robot.

| | |
|---|---|
| Install | ROS: `sudo apt install ros-$ROS_DISTRO-rtabmap-ros` (rtabmap_ros README). Standalone app: release 0.24.2 (2026-10-25) ships macOS Apple Silicon `.dmg` (Sequoia / Tahoe, OpenCV 4 or 5) and Windows `.exe` / `.zip` (CPU and CUDA 13.0 builds); Linux via apt or source. Docker: `introlab3it/rtabmap`, `introlab3it/rtabmap_ros`. Source: CMake with PCL >= 1.7 and OpenCV required, ~50 optional deps toggled by `WITH_*` options. |
| Runs on | Linux, Windows, macOS, Android, iOS (CI badges in README). CPU by default; optional CUDA paths via OpenCV CUDA modules, CudaSift, Torch (SuperPoint) or ONNX Runtime. ROS binaries (README table): ROS 1 Noetic (EOL), ROS 2 Humble, Jazzy, Kilted, Lyrical, Rolling (Iron EOL). Jetson: builds from source on aarch64; 51 issues mention Jetson (e.g. #740 symbol lookup error, #1430 Nano install help). |
| Inputs | ROS 2 `rtabmap` node (rtabmap_sync subscribers): `rgb/image`, `rgb/camera_info`, `depth/image` (sensor_msgs/Image, CameraInfo), or stereo / `rgbd_image(s)`; `scan` (LaserScan), `scan_cloud` (PointCloud2), `odom` (nav_msgs/Odometry) or TF odom, `odom_info`, `imu` (sensor_msgs/Imu), `gps/fix` (NavSatFix), `global_pose` (PoseWithCovarianceStamped), `initialpose`, AprilTag / ArUco detections, `landmark_detections`. Separate odometry nodes in `rtabmap_odom`: `rgbd_odometry`, `stereo_odometry`, `icp_odometry`. Standalone tools read EuRoC, KITTI and TUM-format folders. |
| Outputs | `map` (nav_msgs/OccupancyGrid), `grid_prob_map`, `cloud_map`, `cloud_obstacles`, `cloud_ground` (PointCloud2), OctoMap topics, `elevation_map` (GridMap), `localization_pose` (PoseWithCovarianceStamped), `mapData`, `mapGraph`, `info` (rtabmap_msgs), `mapPath`, `global_path`, `landmarks`; TF `map` => `odom`. Database (SQLite) at `database_path`, `~/.ros/rtabmap.db` by default in `rtabmap.launch.py` (the bare node saves nothing if unset), reusable for localization and export (`rtabmap-export`, `rtabmap-databaseViewer`). |
| Key API / entry points | ROS 2: `ros2 launch rtabmap_launch rtabmap.launch.py ...`, examples in `rtabmap_examples/launch/` (`realsense_d435i_infra.launch.py`, `realsense_d435i_stereo.launch.py`, `zed.launch.py`, `lidar3d.launch.py`, `vlp16_zed.launch.py`, `depthai.launch.py`, `euroc_datasets.launch.py`). CLI tools (`tools/`): `rtabmap` (GUI), `rtabmap-console`, `rtabmap-euroc_dataset`, `rtabmap-kitti_dataset`, `rtabmap-rgbd_dataset`, `rtabmap-reprocess`, `rtabmap-export`, `rtabmap-info`, `rtabmap-report`. C++: `rtabmap::Rtabmap`, `rtabmap::Odometry`, parameters listed in the API docs. |
| Time to first result | Estimate: 30-60 min from apt on Humble/Jazzy with a RealSense D435i (`realsense_d435i_infra.launch.py`) or a EuRoC folder via `rtabmap-euroc_dataset`; 15 min with the macOS / Windows app on a recorded database. Source build with optional deps: half a day or more. |
| License | GitHub metadata: NOASSERTION. LICENSE file: BSD 3-clause text (copyright Mathieu Labbe / IntRoLab). Build-dependent: see licensing gotchas below. |

## Minimal usage
Not run. EuRoC stereo from the tool's own usage text (`tools/EurocDataset/main.cpp`):

```sh
rtabmap-euroc_dataset \
  --Rtabmap/PublishRAMUsage true --Rtabmap/DetectionRate 2 \
  --RGBD/LinearUpdate 0 --RGBD/AngularUpdate 0 --Mem/STMSize 30 \
  ~/EuRoC/V1_03_difficult
# writes rtabmap.db in the sequence folder; open with rtabmap-databaseViewer
```

ROS 2 with a D435i (example file header):

```sh
sudo apt install ros-$ROS_DISTRO-rtabmap-ros ros-$ROS_DISTRO-realsense2-camera
ros2 launch rtabmap_examples realsense_d435i_infra.launch.py
```

## Wiring it into a nav stack
- Odometry in: run its own `rgbd_odometry` / `icp_odometry`, or feed a better front end (`odom` topic) from [OpenVINS](./rpng__open_vins.md), [cuVSLAM](./nvidia-isaac__cuvslam.md), [FAST-LIO2](./hku-mars__fast_lio.md) or [KISS-ICP](./prbonn__kiss-icp.md). RTAB-Map then only does loop closure, the graph and maps.
- Odometry approaches can also be compiled in: CMake options `WITH_OPENVINS`, `WITH_ORB_SLAM`, `WITH_VINS_FUSION`, `WITH_OKVIS`, `WITH_MSCKF_VIO`, `WITH_CUVSLAM`, `WITH_LOAM`, `WITH_FLOAM`, `WITH_LIOSAM` (all OFF by default).
- Maps out: `map` => [Nav2](../../catalog/repos/ros-navigation__navigation2.md) map server / costmaps; `localization_pose` => [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) as an absolute pose; `map` => `odom` TF serves the usual REP-105 chain.
- GNSS-denied relocalization: map once, then relaunch with `localization:=true` (`rtabmap.launch.py` sets `Mem/IncrementalMemory false`, `Mem/InitWMWithAllNodes true`) on the same `database_path`. `gps/fix` can be added as graph priors when GNSS is available.
- UAV: [MAVROS](../../catalog/repos/mavlink__mavros.md) `vision_pose/pose` from `map` => `base_link` TF for external vision.

## Gotchas
- License depends on the build, and the default CMake options pull in non-BSD code. Defaults ON: `WITH_TORO` (CMake summary labels TORO "Creative Commons Attribution-NonCommercial-ShareAlike"), `WITH_VERTIGO` (GPLv3), `WITH_ORB_OCTREE` (GPLv3), `WITH_MADGWICK` (GPL). Optional GPL / restricted: SuperPoint via Torch (GPLv3, `WITH_TORCH`), cvsba (GPLv2), CCCoreLib (GPLv2), libfovis (GPLv2), libviso2 / dvo_core / ORB_SLAM / VINS-Fusion / OpenVINS (GPLv3), msckf_vio (Penn Software License), cuVSLAM (NVIDIA license). Read the `--` license block that CMake prints at configure time and turn off what you cannot ship. Whether the apt binaries were built with TORO/Vertigo is not checked here.
- SURF / SIFT: need OpenCV `xfeatures2d`; CMake labels a build with OpenCV `nonfree` as "Non commercial". SURF requires an OpenCV built with `OPENCV_ENABLE_NONFREE`. SIFT moved into main OpenCV from 4.4.0 (issue #596 discusses SIFT availability with a free OpenCV 4.4). Use ORB / GFTT-BRIEF or SuperPoint/ONNX to stay clear.
- The `rtabmap-euroc_dataset` usage text prints `rtabmap-kitti_dataset` as the program name (copy-paste in `main.cpp`); the binary is `rtabmap-euroc_dataset`.
- Image QoS: the D435i example forces reliable QoS because "with best effort, a lost fragment of a large image drops the whole image" (launch file comment).
- Sync: RGB and depth must share timestamps (or use `approx_sync`); mismatched clocks are the common "no data received" cause.
- Memory management (`Mem/STMSize`, `Rtabmap/TimeThr`) trades loop-closure recall for bounded compute on long runs; defaults suit indoor ground robots.

## Alternatives
- [Cartographer](../../catalog/repos/cartographer-project__cartographer.md) - 2D/3D LiDAR SLAM with pure localization; Apache-2.0; less active.
- [ORB-SLAM3](./uz-slamlab__orb_slam3.md) - camera-only SLAM with atlas relocalization when no depth or LiDAR is present; GPL-3.0.
- [cuVSLAM](./nvidia-isaac__cuvslam.md) plus [isaac_ros_nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - GPU visual SLAM and 3D reconstruction on Jetson.

Sources: `README.md`, `LICENSE`, `CMakeLists.txt` (options and license summary), `tools/` listing, `tools/EurocDataset/main.cpp` and `CMakeLists.txt`, `tools/*/CMakeLists.txt` output names, release 0.24.2 assets, issues #596 #740 #1430 (github.com/introlab/rtabmap); `README.md`, `rtabmap_slam/src/CoreWrapper.cpp`, `rtabmap_util/src/MapsManager.cpp`, `rtabmap_sync/src/impl/CommonDataSubscriberDepth.cpp`, `rtabmap_examples/launch/realsense_d435i_infra.launch.py`, `rtabmap_launch/launch/rtabmap.launch.py`, repo tree (github.com/introlab/rtabmap_ros, branch `ros2`).
