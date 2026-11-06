# cuVSLAM - integration card
<!-- about: repo:nvidia-isaac/cuvslam -->
GPU stereo / stereo-inertial / RGB-D visual odometry plus SLAM with map save, relocalization and optional visual place recognition, driven from Python on a Jetson or a CUDA laptop.

| | |
|---|---|
| Install | Python: download the wheel for your target from the [latest release](https://github.com/nvidia-isaac/cuVSLAM/releases/latest) (v17.0.1 on 2026-11-06), then `pip install cuvslam_cu12-*.whl` (system CUDA Toolkit) or `pip install "./cuvslam_cu12-<version>-<tags>.whl[cuda]"` (CUDA wheels from PyPI; not for Jetson Orin). C++: prebuilt `cuvslam-cpp-<ver>-<target>.tar.gz` or `cmake -S . -B build && cmake --build build --parallel $(nproc)` (CUDA >= 12.6 for the default `USE_CUNLS=ON`, TensorRT 8.6+ unless `-DUSE_TENSORRT=OFF`). ROS 2: separate repo [isaac_ros_visual_slam](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md). |
| Runs on | NVIDIA GPU only. Ubuntu 22.04 / 24.04, x86_64 with CUDA 12 or 13; Jetson Orin (JetPack 6.x, `cu12`) and Jetson Thor (JetPack 7.x, `cu13`). Wheels need CUDA; CMake has a `USE_CUDA` switch (default ON) but a CPU-only build is untested here and the license still limits use to NVIDIA platforms. No macOS / Apple Silicon, no AMD. ROS 2 only through Isaac ROS; no ROS 1 wrapper. |
| Inputs | Python: `Tracker.track(timestamp_ns, images, masks=None, depths=None)` with a list of numpy images captured at one instant (README: within 1 ms), plus `register_imu_measurement(sensor_index, ImuMeasurement(timestamp_ns, linear_accelerations, angular_velocities))`. Calibration as `cuvslam.Rig([Camera...], [ImuCalibration...])`; distortion models Pinhole, Fisheye (4 coeffs), Brown (k1,k2,k3,p1,p2), Polynomial (8). Camera frame in the examples: right-handed, X right, Y down, Z forward. ROS 2 node subscribes `visual_slam/image_<i>`, `visual_slam/camera_info_<i>` (sensor_msgs/Image, CameraInfo), `visual_slam/depth_0`, `visual_slam/imu` (sensor_msgs/Imu), optional `visual_slam/seg_mask_<i>` and `visual_slam/initial_pose`. |
| Outputs | `PoseEstimate.world_from_rig.pose` (rotation quaternion + translation), observations, landmarks, gravity estimate (Inertial mode), SLAM pose graph, saved map. ROS 2 publishes `visual_slam/tracking/odometry` (nav_msgs/Odometry), `visual_slam/tracking/vo_pose` (PoseStamped), `visual_slam/tracking/vo_pose_covariance`, `visual_slam/tracking/vo_path`, `visual_slam/tracking/slam_path`, `visual_slam/status`, plus `visual_slam/vis/*` clouds and markers. |
| Key API / entry points | `cuvslam.Rig`, `cuvslam.Camera`, `cuvslam.Distortion`; `cuvslam.Odometry.Config(odometry_mode=OdometryMode.{Multicamera,Inertial,RGBD,Mono,Multisensor}, ...)`; `cuvslam.Tracker(rig, Tracker.Mode.{OdometryOnlyRealtime,OdometryOnlyOffline,OdometryWithSlamRealtime,OdometryWithSlamOffline}, odom_cfg, slam_cfg)`; `Tracker.track(...)`, `Tracker.register_imu_measurement(...)`, `Tracker.odometry`, `Tracker.slam`; `Slam.save_map`, `Slam.localize_in_map`, `Slam.recognize_place_by_frame`, `Slam.get_pose_graph` (all confirmed in `python/src/cuvslam2.cpp`). |
| Time to first result | Estimate: 1-2 h on an x86 box or Orin that already has the right CUDA, most of it downloading EuRoC MH_01 (12 GB machine-hall zip). Add half a day if you must build from source or match CUDA/TensorRT for VPR. |
| License | GitHub metadata: NOASSERTION. LICENSE file: "NVIDIA Community License" (v. 2026-02-25), source and binaries. Commercial use and derivatives allowed, but the grant is "solely on systems with NVIDIA GPUs or CPUs" (NVIDIA Platforms). Section 10 adds export-control compliance. Not OSI open source. |

## Minimal usage
Not run. Adapted from `examples/euroc/track_euroc.py` (needs that folder's `dataset_utils.py`).

```python
import numpy as np
import cuvslam
from dataset_utils import prepare_frame_metadata_euroc, get_rig, load_frame

seq = "dataset/mav0"
mode = cuvslam.Odometry.OdometryMode.Inertial
cfg = cuvslam.Odometry.Config(odometry_mode=mode, rectified_stereo_camera=False)
tracker = cuvslam.Tracker(get_rig(seq), cuvslam.Tracker.Mode.OdometryOnlyOffline, cfg)

for f in prepare_frame_metadata_euroc(seq, mode):
    if f["type"] == "imu":
        m = cuvslam.ImuMeasurement()
        m.timestamp_ns = int(f["timestamp"])
        m.linear_accelerations = np.asarray(f["accel"])
        m.angular_velocities = np.asarray(f["gyro"])
        tracker.register_imu_measurement(0, m)
        continue
    est, _ = tracker.track(f["timestamp"], [load_frame(p) for p in f["images_paths"]])
    if est.world_from_rig is not None:
        print(f["timestamp"], est.world_from_rig.pose.translation)
```

## Wiring it into a nav stack
- ROS 2: run [isaac_ros_visual_slam](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) and remap camera driver topics onto `visual_slam/image_0`, `visual_slam/camera_info_0`, etc. `visual_slam/tracking/odometry` is the handoff to [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) or Nav2, and to [isaac_ros_nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) for mapping.
- Flight controller: feed the odometry to [MAVROS](../../catalog/repos/mavlink__mavros.md) (`odometry/out` or `vision_pose/pose`), which becomes MAVLink `ODOMETRY` / `VISION_POSITION_ESTIMATE` for PX4 EKF2 or ArduPilot EKF3. Convert from cuVSLAM's Y-down camera convention to the frame MAVROS expects first.
- Python without ROS: call `Tracker` directly and push poses out via [pymavlink](../../catalog/repos/ardupilot__pymavlink.md).
- Evaluate against ground truth with [evo](../../catalog/repos/michaelgrupp__evo.md) after dumping `[t, x, y, z, qx, qy, qz, qw]` per frame (TUM format).
- Calibrate first ([Kalibr](../../catalog/repos/ethz-asl__kalibr.md)). The README says no parameter tuning is expected, so calibration and sync are the main levers.

## Gotchas
- Platform lock: the license only covers NVIDIA hardware. A Raspberry Pi, Apple Silicon or AMD target is out both technically and legally.
- Wheel matrix is narrow. README lists cp310, cp311 and cp312-abi3, but the v17.0.1 release assets have no cp311 wheel, and the only Orin (`cu12` aarch64) wheel is cp310. Pin Python 3.10 on Orin. Install only one of `cuvslam-cu12` / `cuvslam-cu13`.
- Visual place recognition (`use_vpr`) needs TensorRT 10 (`libnvinfer10`), not bundled, and an AnyLoc engine built by `models/anyloc`, which downloads DINOv2 code and the `dinov2_vits14_pretrain.pth` checkpoint at configure time. cuVSLAM's docs do not state the checkpoint's license; upstream DINOv2 README says code and weights are Apache-2.0. An engine only loads in the TensorRT version that built it.
- Multi-camera calls must be hardware-synced; cycling cameras across `track()` calls is not supported (README). See TROUBLESHOOTING.md "Cameras that are not synchronized".
- `Multisensor` mode is experimental (README) and needs a cuNLS build; the release wheels include cuNLS.
- Open issue #47: Inertial mode shows pose jumps when short image blackouts are injected. Do not assume IMU will bridge dropped frames.
- Issue #16: the paper lists a 4-stereo setup as NA on AGX Orin; size multi-camera rigs on the Jetson you actually have.
- Building on Jetson needs `libcublas-dev-12-6 libcusolver-dev-12-6` (JetPack 6) since JetPack ships runtime libs only.

## Alternatives
- [OpenVINS](./rpng__open_vins.md) - CPU-only, GPL-3.0, runs on any ARM board; pick it when there is no NVIDIA GPU or you need online calibration.
- [ORB-SLAM3](./uz-slamlab__orb_slam3.md) - CPU, mono/stereo/RGB-D with IMU and multi-map; GPL-3.0; pick it for a hardware-neutral baseline.
- [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) or [Basalt](../../catalog/repos/vladyslavusenko__basalt.md) - CPU VIO alternatives when the license or GPU lock is a blocker.

Sources: `README.md`, `LICENSE`, `python/LICENSE`, `python/src/cuvslam2.cpp`, `examples/euroc/track_euroc.py`, `examples/euroc/README.md`, `models/anyloc/README.md`, `TROUBLESHOOTING.md` headings, release v17.0.1 asset list, issues #16 #47 (github.com/nvidia-isaac/cuVSLAM); `isaac_ros_cuvslam/src/visual_slam_node.cpp` (github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam); facebookresearch/dinov2 README license section.
