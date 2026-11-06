# VINS-Mono

`repo:hkust-aerial-robotics/vins-mono` - <https://github.com/HKUST-Aerial-Robotics/VINS-Mono>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,071 | C++ | GPL-3.0 | 2024-08-14 | False | research-prototype | medium |

Optimization-based monocular visual-inertial estimator with sliding-window bundle adjustment, online initialization, loop closure and pose-graph reuse.

**Why it matters:** The canonical one-camera-plus-IMU estimator; works on light UAV payloads where stereo or LiDAR is too heavy.

**Hackathon notes:** ROS 1 only and no longer maintained; the README targets Ubuntu 16.04 / ROS Kinetic with Ceres 1.14, and the bundled Docker image is ROS Kinetic. Sensitive to time sync and initialization motion.

## Deep dives

- [vins-mono-qin-2017](../../docs/paper-digests/vins-mono-qin-2017.md) (paper-digests)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `sliding-window`, `ceres`, `ros1`, `loop-closure`

**Domains:** air

## Related

- alternative_to: [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md)

## Referenced by

- [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) (extends)
- [MVIO - monocular visual-inertial odometry in C++](../../catalog/repos/rusaub__mvio.md) (alternative_to)
- [VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator](../../catalog/resources/vins-mono-qin-2017.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
