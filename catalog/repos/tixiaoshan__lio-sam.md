# LIO-SAM

`repo:tixiaoshan/lio-sam` - <https://github.com/TixiaoShan/LIO-SAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,971 | C++ | BSD-3-Clause | 2025-02-14 | False | research-prototype | high |

Tightly coupled LiDAR-inertial odometry via factor-graph smoothing, with optional GPS factors and loop closure.

**Why it matters:** Popular LIO with built-in GNSS factors; the template for LiDAR+INS+intermittent GNSS.

**Hackathon notes:** ROS 1 main branch, community ROS 2 branch. Needs a 9-axis IMU and careful extrinsics.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `gtsam`, `factor-graph`, `gps`, `ros1`

**Domains:** ground

## Related

- depends_on: [GTSAM](../repos/borglab__gtsam.md)
- alternative_to: [FAST-LIO / FAST-LIO2](../repos/hku-mars__fast_lio.md)
- integrates_with: [Scan Context](../repos/gisbi-kim__scancontext.md)

## Referenced by

- [GTSAM](../repos/borglab__gtsam.md) (depends_on)
- [SC-LIO-SAM](../repos/gisbi-kim__sc-lio-sam.md) (extends)
- [LeGO-LOAM](../repos/robustfieldautonomylab__lego-loam.md) (alternative_to)
- [GLIO](../repos/xikunliu-huskit__glio.md) (alternative_to)
- [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](../resources/lio-sam-shan-2020.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
