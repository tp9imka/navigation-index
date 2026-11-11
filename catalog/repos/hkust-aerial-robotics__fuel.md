# FUEL - Fast UAV Exploration

`repo:hkust-aerial-robotics/fuel` - <https://github.com/hkust-aerial-robotics/fuel>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,519 | C++ | GPL-3.0 | 2024-11-19 | False | research-prototype | medium |

Frontier-information-structure based autonomous exploration for quadrotors, combining global tour planning over frontiers with local viewpoint refinement.

**Why it matters:** Autonomous mapping of unknown buildings or terrain without GNSS or prior map, a core reconnaissance capability.

**Build notes:** Bundled sim; pairs naturally with a VIO/LiDAR odometry source from other lanes.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `exploration`, `frontier`, `quadrotor`

**Domains:** air

## Related

- extends: [Fast-Planner](../../catalog/repos/hkust-aerial-robotics__fast-planner.md)
- extends: [RACER - multi-UAV exploration](../../catalog/repos/robotics-star-lab__racer.md)

## Referenced by

- [mav_active_3d_planning](../../catalog/repos/ethz-asl__mav_active_3d_planning.md) (alternative_to)
- [Fast-Planner](../../catalog/repos/hkust-aerial-robotics__fast-planner.md) (extends)
- [GBPlanner (CERBERUS)](../../catalog/repos/ntnu-arl__gbplanner_ros.md) (alternative_to)
- [RACER - multi-UAV exploration](../../catalog/repos/robotics-star-lab__racer.md) (extends)
- [Close-area search for B: frontier, nominal-first, lawnmower and random-walk arms when B is a region or unknown, then A* to the detected B](../../catalog/samples/close-area-explore.md) (explains)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-09._
