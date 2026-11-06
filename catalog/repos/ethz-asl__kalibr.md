# Kalibr

`repo:ethz-asl/kalibr` - <https://github.com/ethz-asl/kalibr>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5,801 | C++ | NOASSERTION | 2024-03-30 | False | production | medium |

ETH ASL calibration toolbox for multi-camera and camera-IMU systems (extrinsics and time offset), plus IMU intrinsics and rolling-shutter calibration.

**Why it matters:** Standard way to calibrate a camera-IMU rig before running any VIO.

**Hackathon notes:** Use the Docker image to avoid ROS 1 build pain; print an AprilGrid target in advance.

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `camera-imu`, `extrinsics`, `time-offset`, `aprilgrid`, `ros1`

**Domains:** multi

## Related

- alternative_to: [iKalibr](../../catalog/repos/unsigned-long__ikalibr.md)
- integrates_with: [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md)
- integrates_with: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- integrates_with: [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md)

## Referenced by

- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [cuckoo_time_translator](../../catalog/repos/ethz-asl__cuckoo_time_translator.md) (same_org)
- [imu_tk](../../catalog/repos/kyle-ak__imu_tk.md) (alternative_to)
- [allan_variance_ros](../../catalog/repos/ori-drs__allan_variance_ros.md) (integrates_with)
- [iKalibr](../../catalog/repos/unsigned-long__ikalibr.md) (alternative_to)
- [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md) (integrates_with)
- [Kalibr wiki: IMU Noise Model](../../catalog/resources/kalibr-imu-noise-model-wiki.md) (part_of)
- [Kalibr wiki: camera-IMU calibration tutorials](../../catalog/resources/kalibr-wiki.md) (has_code)

_Indexed by lane(s): ins-fusion, slam_

_GitHub metadata fetched 2026-11-06._
