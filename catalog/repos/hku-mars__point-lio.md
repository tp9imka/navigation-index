# Point-LIO

`repo:hku-mars/point-lio` - <https://github.com/hku-mars/Point-LIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,376 | C++ | NOASSERTION | 2026-06-13 | False | active-research | medium |

High-bandwidth LiDAR-inertial odometry that updates the state point by point, tolerating aggressive motion and IMU saturation.

**Why it matters:** Handles violent motion (agile drones, vibration) where frame-based LIO breaks.

**Hackathon notes:** Same ecosystem as FAST-LIO; try when FAST-LIO diverges on aggressive motion.

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `point-wise`, `high-bandwidth`, `ros1`

**Domains:** air

## Related

- alternative_to: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)

## Referenced by

- [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md) (alternative_to)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
