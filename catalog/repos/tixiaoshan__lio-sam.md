# LIO-SAM

`repo:tixiaoshan/lio-sam` - <https://github.com/TixiaoShan/LIO-SAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,971 | C++ | BSD-3-Clause | 2025-02-14 | False | research-prototype | high |

Tightly coupled LiDAR-inertial odometry via factor-graph smoothing, with optional GPS factors and loop closure.

**Why it matters:** Popular LIO with built-in GNSS factors; the template for LiDAR+INS+intermittent GNSS.

**Hackathon notes:** ROS 1 main branch, community ROS 2 branch. Needs a 9-axis IMU and careful extrinsics.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [tixiaoshan__lio-sam](../../docs/integration-cards/tixiaoshan__lio-sam.md) (integration-cards)

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `gtsam`, `factor-graph`, `gps`, `ros1`

**Domains:** ground

## Related

- depends_on: [GTSAM](../../catalog/repos/borglab__gtsam.md)
- alternative_to: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)
- integrates_with: [Scan Context](../../catalog/repos/gisbi-kim__scancontext.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GTSAM](../../catalog/repos/borglab__gtsam.md) (depends_on)
- [SC-LIO-SAM](../../catalog/repos/gisbi-kim__sc-lio-sam.md) (extends)
- [LeGO-LOAM](../../catalog/repos/robustfieldautonomylab__lego-loam.md) (alternative_to)
- [GLIO](../../catalog/repos/xikunliu-huskit__glio.md) (alternative_to)
- [LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping](../../catalog/resources/lio-sam-shan-2020.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
