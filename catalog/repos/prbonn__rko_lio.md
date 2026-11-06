# RKO-LIO

`repo:prbonn/rko_lio` - <https://github.com/PRBonn/rko_lio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 687 | C++ | MIT | 2026-10-18 | False | active-research | high |

LiDAR-inertial odometry aiming to work without sensor-specific modelling or heavy tuning.

**Why it matters:** Recent (2025-2026) LIO from the KISS-ICP group; good for unknown hardware.

**Hackathon notes:** `pip install "rko_lio[all]"` then `rko_lio -v /path/to/bags` runs on ROS 1 or ROS 2 bags with a rerun viewer; a ROS 2 node is also available. You must supply IMU and LiDAR extrinsics if the bag's TF tree lacks them. No loop closure - see rko_slam for that.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [prbonn__rko_lio](../../docs/integration-cards/prbonn__rko_lio.md) (integration-cards)

**Concepts:** [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `imu`, `pip`, `ros2`, `2025`

**Domains:** ground

## Related

- alternative_to: [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md)
- alternative_to: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
