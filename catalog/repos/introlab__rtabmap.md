# RTAB-Map

`repo:introlab/rtabmap` - <https://github.com/introlab/rtabmap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,080 | C++ | NOASSERTION | 2026-11-04 | False | production | high |

Graph-based SLAM library and app supporting RGB-D, stereo and LiDAR, with memory management for large-scale loop closure and map reuse.

**Why it matters:** Practical all-rounder with GUI, database and localization modes; easiest way to get a working 3D map on a ground robot.

**Hackathon notes:** Install via apt binaries (ROS) or the standalone app. Supports phone/iPad LiDAR capture. Save a map, then switch to localization mode.

**Concepts:** [Visual SLAM](../concepts/visual-slam.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Place recognition and loop closure](../concepts/place-recognition.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `rgbd`, `stereo`, `lidar`, `database`, `gui`

**Domains:** ground, air, dismounted

## Related

- integrates_with: [rtabmap_ros](../repos/introlab__rtabmap_ros.md)
- alternative_to: [Cartographer](../repos/cartographer-project__cartographer.md)

## Referenced by

- [Cartographer](../repos/cartographer-project__cartographer.md) (alternative_to)
- [rtabmap_ros](../repos/introlab__rtabmap_ros.md) (depends_on)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
