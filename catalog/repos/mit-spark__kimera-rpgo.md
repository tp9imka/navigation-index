# Kimera-RPGO

`repo:mit-spark/kimera-rpgo` - <https://github.com/MIT-SPARK/Kimera-RPGO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 575 | C++ | BSD-2-Clause | 2026-10-09 | False | active-research | medium |

Robust pose-graph optimization that rejects bad loop closures via pairwise consistency maximization on top of GTSAM.

**Why it matters:** Outlier-robust loop closure is what keeps a long GNSS-denied mission from corrupting its map; reusable outside Kimera.

**Hackathon notes:** Small library; feed it any odometry + loop closure edges. Good drop-in back end for a custom front end.

**Concepts:** [Visual SLAM](../concepts/visual-slam.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Swarms and multi-agent navigation](../concepts/multi-agent.md)

**Tags:** `pose-graph`, `pcm`, `outlier-rejection`, `gtsam`

**Domains:** multi

## Related

- depends_on: [GTSAM](../repos/borglab__gtsam.md)

## Referenced by

- [Kimera-VIO](../repos/mit-spark__kimera-vio.md) (depends_on)
- [Kimera: an Open-Source Library for Real-Time Metric-Semantic Localization and Mapping](../resources/kimera-rosinol-2019.md) (has_code)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
