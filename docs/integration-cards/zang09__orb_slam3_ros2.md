# ORB_SLAM3_ROS2 - integration card
<!-- about: repo:zang09/orb_slam3_ros2 -->
Thin ROS 2 wrapper that feeds camera (and IMU) topics into ORB-SLAM3 for MONO, STEREO, RGBD and STEREO-INERTIAL modes; useful to watch ORB-SLAM3 track live ROS 2 data, but it publishes no pose, so you must patch it before anything downstream can use the result.

| | |
|---|---|
| Install | No releases. First build ORB-SLAM3 from the author's fork [zang09/ORB-SLAM3-STEREO-FIXED](https://github.com/zang09/ORB-SLAM3-STEREO-FIXED) (GPL-3.0). Then `sudo apt install ros-$ROS_DISTRO-vision-opencv ros-$ROS_DISTRO-message-filters`, `cd ~/colcon_ws/src && git clone https://github.com/zang09/ORB_SLAM3_ROS2.git orbslam3_ros2` (add `-b humble` for Humble), edit two hard-coded paths, then `colcon build --symlink-install --packages-select orbslam3`. Paths to edit: `CMakeLists.txt` line 5 `set(ENV{PYTHONPATH} "/opt/ros/foxy/lib/python3.8/site-packages/")` and `CMakeModules/FindORB_SLAM3.cmake` line 8 `set(ORB_SLAM3_ROOT_DIR "~/Install/ORB_SLAM/ORB_SLAM3")`. |
| Runs on | Linux, CPU. `main`: tested Ubuntu 20.04, ROS 2 Foxy, OpenCV 4.2.0. Branch `humble`: Ubuntu 22.04, Humble, OpenCV 4.5.4 (README on that branch). Nothing for Jazzy. |
| Inputs | Relative topic names (remap them): `camera` (MONO, sensor_msgs/Image); `camera/left`, `camera/right` (STEREO, message_filters sync; STEREO-INERTIAL, separate buffers); `camera/rgb`, `camera/depth` (RGBD); `imu` (sensor_msgs/Imu, STEREO-INERTIAL). ORB vocabulary `vocabulary/ORBvoc.txt.tar.gz` (~42 MB, extract first) and an ORB-SLAM3 YAML from `config/` (EuRoC, KITTI, TUM, TUM-VI, RealSense D435i / T265 for mono, stereo, rgb-d, stereo-inertial, plus `monocular-inertial` and `rgb-d-inertial` configs with no matching node). |
| Outputs | No ROS topics, no TF. On shutdown each node calls `SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt")` into the working directory, plus the ORB-SLAM3 Pangolin viewer while running. |
| Key API / entry points | `ros2 run orbslam3 mono VOCAB YAML`, `ros2 run orbslam3 stereo VOCAB YAML BOOL_RECTIFY`, `ros2 run orbslam3 rgbd VOCAB YAML`, `ros2 run orbslam3 stereo-inertial VOCAB YAML BOOL_RECTIFY [BOOL_EQUALIZE]`. Node classes in `src/<mode>/*-node.cpp` (`MonocularSlamNode`, `StereoSlamNode`, `RgbdSlamNode`, `StereoInertialNode`) call `ORB_SLAM3::System::TrackMonocular / TrackStereo / TrackRGBD`, which return the camera pose you would publish. |
| Time to first result | Estimate: half a day to a day, most of it building ORB-SLAM3, Pangolin and Sophus against the right OpenCV; the README's EuRoC bag demo also needs ROS 1 Noetic + `ros1_bridge` (or convert the bag with `rosbags`). |
| License | No LICENSE file in the repo and no licence in GitHub metadata. It links ORB-SLAM3 (GPL-3.0), so any distributed build is GPL-3.0-bound in practice; the wrapper code itself has no grant. The README says it is modified from `curryc/ros2_orbslam3`. |

## Minimal usage
Not run. From README (STEREO-INERTIAL on EuRoC via ros1_bridge).

```sh
tar -xzf ~/colcon_ws/src/orbslam3_ros2/vocabulary/ORBvoc.txt.tar.gz -C ~/colcon_ws/src/orbslam3_ros2/vocabulary
source ~/colcon_ws/install/local_setup.bash
ros2 run orbslam3 stereo-inertial \
  ~/colcon_ws/src/orbslam3_ros2/vocabulary/ORBvoc.txt \
  ~/colcon_ws/src/orbslam3_ros2/config/stereo-inertial/EuRoC.yaml true
# ROS 1 side: rosbag play V1_02_medium.bag /cam0/image_raw:=/camera/left /cam1/image_raw:=/camera/right /imu0:=/imu
```

## Wiring it into a nav stack
- To make it useful: in each node, take the `Sophus::SE3f` returned by `Track*()` (camera-from-world), invert it, and publish nav_msgs/Odometry plus a TF. Then it can feed [MAVROS](./mavlink__mavros.md) `vision_pose` / [vision_to_mavros](./thien94__vision_to_mavros.md), or [robot_localization](./cra-ros-pkg__robot_localization.md). Open issues #23 and #32 ask for exactly this.
- `KeyFrameTrajectory.txt` is TUM format: evaluate with [evo](./michaelgrupp__evo.md).
- Core algorithm details, licensing and dataset configs: [ORB-SLAM3 card](./uz-slamlab__orb_slam3.md).

## Gotchas
- No pose output (above). This is the main thing to know before choosing it.
- Hard-coded Foxy PYTHONPATH and ORB-SLAM3 path in CMake; the build fails or picks the wrong install until you edit them.
- OpenCV version must match what ORB-SLAM3 was built with (README troubleshooting, issue #2 comment). Missing `sophus/se3.hpp`: `sudo make install` in ORB-SLAM3's `Thirdparty/Sophus/build`.
- Crashes on Humble reported and open: #20 (mono segfault), #24 (RGB-D "double free or corruption"), #11 (RealSense D455 segfault).
- No monocular-inertial or RGBD-inertial node despite shipping those configs (#21 asks for it).
- Maintenance: last `main` commit 2023-02, last `humble` commit 2023-06.

## Alternatives
- [RTAB-Map ROS](./introlab__rtabmap_ros.md) - maintained ROS 2 visual/LiDAR SLAM from apt with proper topics, TF and localization mode.
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) - stereo(-inertial) VIO with ROS 2 odometry output on NVIDIA GPUs.
- [OpenVINS](./rpng__open_vins.md) - VIO with a ROS 2 node that publishes odometry; filter-based, no loop closure map.

Sources: `README.md` (branches `main` and `humble`), branches list, commit log, repo tree, `CMakeLists.txt`, `CMakeModules/FindORB_SLAM3.cmake`, `src/monocular/monocular-slam-node.cpp`, `src/stereo/stereo-slam-node.cpp`, `src/rgbd/rgbd-slam-node.cpp`, `src/stereo-inertial/stereo-inertial-node.cpp`, `vocabulary/` listing, issues #11 #20 #21 #23 #24 #32 (github.com/zang09/ORB_SLAM3_ROS2); GitHub metadata of zang09/ORB-SLAM3-STEREO-FIXED.
