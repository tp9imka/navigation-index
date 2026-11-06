# VINS-Mono

`repo:hkust-aerial-robotics/vins-mono` - <https://github.com/HKUST-Aerial-Robotics/VINS-Mono>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,071 | C++ | GPL-3.0 | 2024-08-14 | False | research-prototype | medium |

Optimization-based monocular visual-inertial estimator with sliding-window bundle adjustment, online initialization, loop closure and pose-graph reuse.

**Why it matters:** The canonical one-camera-plus-IMU estimator; works on light UAV payloads where stereo or LiDAR is too heavy.

**Hackathon notes:** ROS 1 only and no longer maintained; run in a Melodic/Noetic container. Sensitive to time sync and initialization motion.

## Deep dives

- [vins-mono-qin-2017](../../docs/paper-digests/vins-mono-qin-2017.md) (paper-digests)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `sliding-window`, `ceres`, `ros1`, `loop-closure`

**Domains:** air

## Related

- alternative_to: [VINS-Fusion](../repos/hkust-aerial-robotics__vins-fusion.md)

## Referenced by

- [VINS-Fusion](../repos/hkust-aerial-robotics__vins-fusion.md) (extends)
- [VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator](../resources/vins-mono-qin-2017.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
