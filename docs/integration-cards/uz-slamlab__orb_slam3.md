# ORB-SLAM3 - integration card
<!-- about: repo:uz-slamlab/orb_slam3 -->
CPU feature-based SLAM for mono / stereo / RGB-D, with or without IMU, with loop closure, relocalization and a multi-map atlas; the reference baseline for GNSS-denied visual drift.

| | |
|---|---|
| Install | `git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git ORB_SLAM3 && cd ORB_SLAM3 && chmod +x build.sh && ./build.sh` (builds bundled DBoW2, g2o, Sophus, extracts `Vocabulary/ORBvoc.txt.tar.gz`, produces `lib/libORB_SLAM3.so` and `Examples/*`). Needs Pangolin, OpenCV (CMake: `find_package(OpenCV 4.4)`, fails if not found), Eigen >= 3.1.0. Tag `v1.0-release` (README "V1.0, December 22th, 2021"); last push 2024-07-24. |
| Runs on | Linux CPU; README tested Ubuntu 16.04 / 18.04 and asks for "a powerful computer (e.g. i7)". CMake sets `-march=native` and `-std=c++11`. ROS 1 examples tested on Melodic only; no upstream ROS 2 (use [orb_slam3_ros2](../../catalog/repos/zang09__orb_slam3_ros2.md)). No GPU path. Jetson / aarch64: possible but unsupported (see Gotchas). |
| Inputs | Images as `cv::Mat` plus timestamps (seconds, double) and optional `std::vector<IMU::Point>` per frame. Settings YAML (camera model pinhole or Kannala-Brandt fisheye, intrinsics, stereo/IMU extrinsics, IMU noise, ORB params), see `Calibration_Tutorial.pdf`. Datasets: EuRoC ASL folders, TUM-VI, TUM RGB-D, KITTI via `Examples/*`. ROS 1 nodes (`Examples_old/ROS/ORB_SLAM3/src`): `/camera/image_raw`, `/camera/left/image_raw`, `/camera/right/image_raw`, `/camera/rgb/image_raw`, `/camera/depth_registered/image_raw` (sensor_msgs/Image), `/imu` (sensor_msgs/Imu). |
| Outputs | `Track*` returns `Sophus::SE3f` camera pose (Tcw). Trajectory files via `SaveTrajectoryTUM`, `SaveTrajectoryEuRoC`, `SaveTrajectoryKITTI`, `SaveKeyFrameTrajectory*`. Atlas save/load. The upstream ROS 1 nodes publish nothing (no publishers in `ros_stereo_inertial.cc`); poses only show in the Pangolin viewer unless you add a publisher. |
| Key API / entry points | `ORB_SLAM3::System(voc_file, settings_file, System::eSensor, bUseViewer=true, initFr=0, strSequence="")`; `TrackMonocular(im, t, vImuMeas={})`, `TrackStereo(imLeft, imRight, t, vImuMeas={})`, `TrackRGBD(im, depth, t, vImuMeas={})`; `ActivateLocalizationMode()`, `GetTrackingState()`, `isLost()`, `Shutdown()`, `SaveTrajectoryEuRoC(file)` (all in `include/System.h`). Binaries per sensor/dataset, e.g. `Examples/Stereo-Inertial/stereo_inertial_euroc`, `Examples/Monocular-Inertial/mono_inertial_euroc`, `Examples/Stereo-Inertial/stereo_inertial_realsense_D435i`. |
| Time to first result | Estimate: half a day on Ubuntu 20.04/22.04 x86 including Pangolin build and compile fixes, then minutes per EuRoC sequence. Jetson or ROS 2: add 1 day. |
| License | GitHub metadata: GPL-3.0. README: GPLv3; closed-source commercial licence on request from the authors (orbslam at unizar dot es). `Dependencies.md`: bundled DBoW2/DLib and g2o are BSD, Sophus MIT. No learned weights; `ORBvoc.txt` vocabulary ships in-repo. |

## Minimal usage
Not run. Stereo-inertial on one EuRoC sequence (ASL folder layout).

```sh
./Examples/Stereo-Inertial/stereo_inertial_euroc \
  Vocabulary/ORBvoc.txt Examples/Stereo-Inertial/EuRoC.yaml \
  ~/EuRoC/MH01 Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt dataset-MH01_stereoi
```

Argument order from the usage string in `stereo_inertial_euroc.cc`: vocabulary, settings, then (sequence folder, timestamps file) pairs, then an optional output name. It writes `f_<name>.txt` (all frames) and `kf_<name>.txt` (keyframes) and constructs `System` with the viewer off.

## Wiring it into a nav stack
- ROS 2: use [orb_slam3_ros2](../../catalog/repos/zang09__orb_slam3_ros2.md) (README tested Ubuntu 20.04 / Foxy, OpenCV 4.2, against a patched ORB-SLAM3 fork) or add a `nav_msgs/Odometry` publisher in your own node around `System::TrackStereo`.
- Pose handoff: convert Tcw to Twc, publish as odometry, then [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) or [MAVROS](../../catalog/repos/mavlink__mavros.md) `vision_pose/pose` => MAVLink `VISION_POSITION_ESTIMATE`. [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md) shows the frame-alignment step.
- Calibration: [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) output maps to the settings YAML (fields differ; transcribe by hand).
- Scoring: TUM/EuRoC trajectory files go straight into [evo](../../catalog/repos/michaelgrupp__evo.md).

## Gotchas
- README says `build_ros.sh` builds `Examples/ROS/ORB_SLAM3`, but the ROS sources now live in `Examples_old/ROS/ORB_SLAM3`; `build_ros.sh` still `cd`s into `Examples/ROS/ORB_SLAM3`, which does not exist. Fix the path or use a wrapper.
- README's Mono-Inertial command reads `rosrun ORB_SLAM3 Mono ...`; the ROS CMakeLists builds it as `Mono_Inertial`.
- README points at `euroc_examples` / `tum_vi_examples` scripts, which are not in the repo tree on master. Call the `Examples/*/..._euroc` binaries directly.
- C++ standard: CMake forces C++11 but newer Pangolin needs C++14+ (open #599, #374). Under C++17, `mnFullBAIdx++` on a `bool` fails to compile (open #550). Common fix: set C++14 and change that member to `int`.
- OpenCV floor is 4.4 in CMake, while the ROS 2 wrapper asks for OpenCV 4.2 and a fork; pick one OpenCV for both.
- Jetson Orin Nano / Ubuntu 22.04 aarch64 build failure at `Tracking.cc` (open #996); `-march=native` and Pangolin/GL on Jetson add friction (#400, #159).
- Upstream is quiet; 72 issues match "segmentation fault" (e.g. #592 LocalMapping in stereo-inertial). Monocular-inertial init needs motion with rotation and acceleration.
- GPL-3.0 copyleft for any distributed derivative; commercial use requires the authors' separate licence.

## Alternatives
- [OpenVINS](./rpng__open_vins.md) - lighter filter-based VIO with online calibration, ROS 2 Humble in CI; no loop closure in core.
- [cuVSLAM](./nvidia-isaac__cuvslam.md) - on Jetson / NVIDIA GPUs; maintained, Python API, map save and relocalization.
- [ORB-SLAM2](../../catalog/repos/raulmur__orb_slam2.md) for visual-only without IMU, or [DROID-SLAM](../../catalog/repos/princeton-vl__droid-slam.md) for learned dense SLAM on a desktop GPU.

Sources: `README.md`, `Dependencies.md`, `CMakeLists.txt`, `build_ros.sh`, `include/System.h`, `Examples/Stereo-Inertial/stereo_inertial_euroc.cc`, `Examples_old/ROS/ORB_SLAM3/CMakeLists.txt`, `Examples_old/ROS/ORB_SLAM3/src/ros_stereo_inertial.cc`, repo tree (github.com/UZ-SLAMLab/ORB_SLAM3); issues #159 #374 #400 #550 #592 #599 #996; zang09/ORB_SLAM3_ROS2 README.
