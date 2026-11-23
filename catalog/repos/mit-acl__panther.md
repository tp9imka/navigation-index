# PANTHER

`repo:mit-acl/panther` - <https://github.com/mit-acl/panther>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 244 | C++ | BSD-3-Clause | 2022-11-01 | False | research-prototype | low |

Perception-aware trajectory planner for multirotors in dynamic environments: jointly optimises translation and yaw so the camera keeps moving obstacles in view while avoiding them.

**Why it matters:** Example of coupling yaw (sensor pointing) with the trajectory; the same trick applies to keeping a downward or forward camera on matchable terrain.

**Build notes:** License BSD-3-Clause (gh api). Last push 2022-11-01. ROS Noetic, CGAL, CasADi from source and an HSL linear solver behind a registration form. Not a 48h install; read for the formulation.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `perception-aware`, `yaw-planning`, `dynamic-obstacles`, `casadi`, `bsd-3-clause`

**Domains:** air

## Related

- same_org: [MADER](../../catalog/repos/mit-acl__mader.md)
- depends_on: [CasADi](../../catalog/repos/casadi__casadi.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [LA-Planner](../../catalog/repos/robotics-star-lab__la-planner.md) (alternative_to)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-23._
