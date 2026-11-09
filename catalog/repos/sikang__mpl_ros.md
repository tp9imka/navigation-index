# mpl_ros (motion primitive library)

`repo:sikang/mpl_ros` - <https://github.com/sikang/mpl_ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | research-prototype | low |

ROS wrapper and examples for search-based kinodynamic planning: graph search over short constant-jerk or constant-acceleration motion primitives with a minimum-time-plus-effort cost.

**Why it matters:** Reference implementation of kinodynamic search for quadrotors, the same idea as Fast-Planner's front end. The output is already dynamically feasible, so no separate smoothing pass is needed.

**Hackathon notes:** License Apache-2.0, last push 2025-04-17 (gh api). ROS 1 catkin build. Kinodynamic search in Python is slow in 3D; prefer geometric A* + min-snap unless the team needs aggressive flight.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `kinodynamic`, `motion-primitives`, `lqmt`, `ros1`, `c++`, `apache-2.0`

**Domains:** air

## Related

- same_org: [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md)
- alternative_to: [Fast-Planner](../../catalog/repos/hkust-aerial-robotics__fast-planner.md)

## Referenced by

- [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md) (same_org)
- [Search-based motion planning for quadrotors using linear quadratic minimum time control](../../catalog/resources/liu-mpl-lqmt-iros-2017.md) (has_code)

_Indexed by lane(s): close-area-planning_
