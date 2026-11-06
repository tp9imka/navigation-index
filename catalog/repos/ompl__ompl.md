# OMPL - Open Motion Planning Library

`repo:ompl/ompl` - <https://github.com/ompl/ompl>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,192 | C++ | NOASSERTION | 2026-11-01 | False | production | high |

Library of sampling-based motion planners (RRT, RRT*, PRM, BIT*, informed variants, kinodynamic planners) with a clean state-space abstraction and Python bindings.

**Why it matters:** The reference implementation for sampling-based planning; underpins MoveIt and many UAV/UGV planners, so it is the quickest way to get a correct baseline planner.

**Hackathon notes:** pip wheels exist for the Python bindings; define a state validity checker against your occupancy grid or DEM and you have a planner in an afternoon.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [ompl__ompl](../../docs/integration-cards/ompl__ompl.md) (integration-cards)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `rrt`, `prm`, `sampling-based`, `python-bindings`

**Domains:** multi

## Related

- alternative_to: [PythonRobotics](../../catalog/repos/atsushisakai__pythonrobotics.md)
- integrates_with: [MoveIt 2](../../catalog/repos/moveit__moveit2.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [PythonRobotics](../../catalog/repos/atsushisakai__pythonrobotics.md) (alternative_to)
- [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md) (alternative_to)
- [The Open Motion Planning Library (OMPL) website](../../catalog/resources/ompl-site.md) (explains)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
