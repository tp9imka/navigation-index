# CoLRIO

`repo:pengyu-team/co-lrio` - <https://github.com/PengYu-Team/Co-LRIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 |  | ? | 2025-03-27 | False | research-prototype | low |

Placeholder repo: it only holds a README pointing to zhongshp/Co-LRIO, where the code lives. CoLRIO is ROS 2 centralized lidar-ranging-inertial state estimation for robotic swarms that offloads optimization to a server and uses UWB inter-robot ranges (ICRA 2024).

**Why it matters:** Shows how UWB ranging tightens swarm state estimation when GNSS is out.

**Hackathon notes:** Use zhongshp/Co-LRIO (Apache-2.0, C++). ROS 2 Foxy and GTSAM 4.2a8; build is sensitive to versions.

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `uwb`, `lidar`, `swarm`, `gtsam`

**Domains:** ground, air, multi

## Related

- same_org: [DCL-SLAM](../../catalog/repos/zhongshp__dcl-slam.md)

## Referenced by

- [DCL-SLAM](../../catalog/repos/zhongshp__dcl-slam.md) (same_org)
- [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
