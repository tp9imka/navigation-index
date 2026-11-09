# OMPL - Open Motion Planning Library

`repo:ompl/ompl` - <https://github.com/ompl/ompl>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,196 | C++ | NOASSERTION | 2026-11-06 | False | production | high |

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
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [PythonRobotics](../../catalog/repos/atsushisakai__pythonrobotics.md) (alternative_to)
- [terrain-navigation2](../../catalog/repos/ethz-asl__terrain-navigation2.md) (depends_on)
- [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md) (alternative_to)
- [edpl-ompl](../../catalog/repos/sauravag__edpl-ompl.md) (depends_on)
- [PathPlanning (zhm-real)](../../catalog/repos/zhm-real__pathplanning.md) (alternative_to)
- [Sampling-based Algorithms for Optimal Motion Planning](../../catalog/resources/karaman-frazzoli-rrtstar-ijrr-2011.md) (has_code)
- [Probabilistic roadmaps for path planning in high-dimensional configuration spaces](../../catalog/resources/kavraki-prm-1996.md) (has_code)
- [The Open Motion Planning Library (OMPL) website](../../catalog/resources/ompl-site.md) (explains)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-09._
