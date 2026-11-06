# 4DRadarSLAM

`repo:zhuge2333/4dradarslam` - <https://github.com/zhuge2333/4DRadarSLAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 316 | C++ | GPL-3.0 | 2023-11-01 | False | research-prototype | medium |

4D radar SLAM with scan-to-scan registration, loop closure and pose-graph optimization, released with an NTU 4D radar dataset.

**Why it matters:** One of the few full SLAM pipelines for 4D imaging radar, the all-weather sensor for ground vehicles.

**Hackathon notes:** ROS 1; structured like hdl_graph_slam. Test on their dataset first.

**Concepts:** [Radar navigation and odometry](../../catalog/concepts/radar-nav.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `4d-radar`, `gicp`, `pose-graph`, `ros1`

**Domains:** ground

## Related

- extends: [hdl_graph_slam](../../catalog/repos/koide3__hdl_graph_slam.md)
- alternative_to: [CFEAR Radarodometry](../../catalog/repos/dan11003__cfear_radarodometry.md)

## Referenced by

- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [CFEAR Radarodometry](../../catalog/repos/dan11003__cfear_radarodometry.md) (alternative_to)
- [4D Millimeter-Wave Radar in Autonomous Driving: A Survey](../../catalog/resources/han-4d-mmwave-radar-survey-2023.md) (cites)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
