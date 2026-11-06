# LeGO-LOAM

`repo:robustfieldautonomylab/lego-loam` - <https://github.com/RobustFieldAutonomyLab/LeGO-LOAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,770 | C++ | BSD-3-Clause | 2024-08-17 | False | archived | low |

Lightweight ground-optimized LiDAR odometry and mapping that segments ground to speed up feature extraction on UGVs.

**Why it matters:** Classic UGV LiDAR SLAM for rough terrain on modest compute.

**Hackathon notes:** ROS 1 only, unmaintained, tuned for Velodyne VLP-16. Use LIO-SAM or KISS-ICP instead unless reproducing baselines.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md)

**Tags:** `loam`, `ground-segmentation`, `ros1`

**Domains:** ground

## Related

- alternative_to: [LIO-SAM](../repos/tixiaoshan__lio-sam.md)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
