# ROG-Map

`repo:hku-mars/rog-map` - <https://github.com/hku-mars/ROG-Map>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 633 | C++ | GPL-3.0 | 2025-03-13 | False | active-research | low |

Robocentric occupancy grid that slides with the vehicle and keeps an inflated map and frontier information, designed for LiDAR-based high-speed planning. It is the map module inside the SUPER planner.

**Why it matters:** Shows the map design that LiDAR drone planners use in practice: a bounded local window, incremental inflation and explicit unknown handling, instead of a global octree.

**Build notes:** License GPL-3.0, last push 2025-03-13 (gh api). ROS 1 only on main. Paper is an arXiv preprint (2302.14819). Read for the sliding-window idea; a 48h team can reproduce it as a numpy ring buffer.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md)

**Tags:** `occupancy-grid`, `robocentric`, `lidar`, `ros1`, `c++`, `gpl-3.0`

**Domains:** air

## Related

- integrates_with: [SUPER](../../catalog/repos/hku-mars__super.md)
- integrates_with: [FAST-LIO / FAST-LIO2](../../catalog/repos/hku-mars__fast_lio.md)

## Referenced by

- [SUPER](../../catalog/repos/hku-mars__super.md) (depends_on)

_Indexed by lane(s): close-area-planning_

_GitHub metadata fetched 2026-11-23._
