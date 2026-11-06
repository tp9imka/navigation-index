# Autoware Universe

`repo:autowarefoundation/autoware_universe` - <https://github.com/autowarefoundation/autoware_universe>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,807 | C++ | Apache-2.0 | 2026-11-06 | False | production | medium |

The broad package collection of Autoware with experimental and production-candidate modules, including localization add-ons such as YabLoc, landmark-based localizers and the pose estimator arbiter.

**Why it matters:** Holds Autoware's extra localization modules; the core NDT scan matcher and EKF localizer have moved to autoware_core.

**Hackathon notes:** Pick packages and run them standalone with rosbags; autoware_ndt_scan_matcher and autoware_ekf_localizer now live in autoware_core, not here.

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `autoware`, `localization`, `ekf`, `ndt`

**Domains:** ground

## Related

- same_org: [Autoware](../../catalog/repos/autowarefoundation__autoware.md)

## Referenced by

- [Autoware](../../catalog/repos/autowarefoundation__autoware.md) (depends_on)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
