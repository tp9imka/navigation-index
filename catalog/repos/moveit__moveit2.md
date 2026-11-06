# MoveIt 2

`repo:moveit/moveit2` - <https://github.com/moveit/moveit2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,102 | C++ | BSD-3-Clause | 2026-10-28 | False | production | low |

Motion planning framework for ROS 2 manipulators: kinematics, collision checking, planners (OMPL, Pilz, STOMP) and real-time servoing.

**Why it matters:** Relevant when a vehicle carries an arm or gimbal-like mechanism; outside pure navigation but the ROS 2 standard for manipulation planning.

**Hackathon notes:** Binary install via apt; use the MoveIt Setup Assistant for a new robot. Overkill unless your platform has an arm.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `manipulation`, `ompl`, `ros2`, `motion-planning`

**Domains:** ground

## Related

- integrates_with: [Nav2 (ROS 2 Navigation)](../repos/ros-navigation__navigation2.md)

## Referenced by

- [OMPL - Open Motion Planning Library](../repos/ompl__ompl.md) (integrates_with)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
