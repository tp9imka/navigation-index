# RTAB-Map

`repo:introlab/rtabmap` - <https://github.com/introlab/rtabmap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,080 | C++ | NOASSERTION | 2026-11-04 | False | production | high |

Graph-based SLAM library and app supporting RGB-D, stereo and LiDAR, with memory management for large-scale loop closure and map reuse.

**Why it matters:** Practical all-rounder with GUI, database and localization modes; easiest way to get a working 3D map on a ground robot.

**Hackathon notes:** Install via apt binaries (ROS) or the standalone app. Supports phone/iPad LiDAR capture. Save a map, then switch to localization mode.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [introlab__rtabmap](../../docs/integration-cards/introlab__rtabmap.md) (integration-cards)

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `rgbd`, `stereo`, `lidar`, `database`, `gui`

**Domains:** ground, air, dismounted

## Related

- integrates_with: [rtabmap_ros](../../catalog/repos/introlab__rtabmap_ros.md)
- alternative_to: [Cartographer](../../catalog/repos/cartographer-project__cartographer.md)

## Referenced by

- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [drone_navigation - ROS 2 + PX4 + RTAB-Map diploma](../../catalog/repos/bolotnaya-glesenb__drone_navigation.md) (depends_on)
- [Cartographer](../../catalog/repos/cartographer-project__cartographer.md) (alternative_to)
- [rtabmap_ros](../../catalog/repos/introlab__rtabmap_ros.md) (depends_on)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
