# hdl_graph_slam

`repo:koide3/hdl_graph_slam` - <https://github.com/koide3/hdl_graph_slam>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,343 | C++ | BSD-2-Clause | 2024-07-16 | False | research-prototype | medium |

3D LiDAR graph SLAM with NDT/GICP scan matching odometry, loop detection and optional GPS, IMU and floor-plane constraints.

**Why it matters:** Simple, hackable graph SLAM that 4DRadarSLAM and others build on; GPS constraints make it handy for mixed GNSS/denied runs.

**Hackathon notes:** ROS 1; GLIM is the author's newer framework.

**Concepts:** [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [GNSS/INS integration](../concepts/gnss-ins.md)

**Tags:** `graph-slam`, `ndt`, `gicp`, `ros1`

**Domains:** ground

## Related

- alternative_to: [GLIM](../repos/koide3__glim.md)
- depends_on: [fast_gicp](../repos/koide3__fast_gicp.md)

## Referenced by

- [GLIM](../repos/koide3__glim.md) (alternative_to)
- [4DRadarSLAM](../repos/zhuge2333__4dradarslam.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
