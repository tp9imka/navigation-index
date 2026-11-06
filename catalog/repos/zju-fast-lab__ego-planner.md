# EGO-Planner

`repo:zju-fast-lab/ego-planner` - <https://github.com/zju-fast-lab/ego-planner>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,730 | C++ | GPL-3.0 | 2025-03-08 | False | research-prototype | medium |

ESDF-free gradient-based local planner for quadrotors from ZJU FAST Lab: optimizes B-spline trajectories using collision terms computed only where the trajectory hits obstacles.

**Why it matters:** Lightweight onboard replanning for small drones flying through clutter; widely reused baseline for agile UAV navigation in unknown environments.

**Hackathon notes:** ROS1 (Noetic) with a bundled simulator; runs on a laptop. Porting to ROS 2 / PX4 needs a bridge. Good for a demo of reactive flight in a random forest map.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `quadrotor`, `b-spline`, `local-planner`, `ros1`

**Domains:** air

## Related

- extends: [EGO-Swarm](../repos/zju-fast-lab__ego-planner-swarm.md)
- extends: [Fast-Planner](../repos/hkust-aerial-robotics__fast-planner.md)
- same_org: [GCOPTER](../repos/zju-fast-lab__gcopter.md)

## Referenced by

- [Fast-Planner](../repos/hkust-aerial-robotics__fast-planner.md) (alternative_to)
- [EGO-Swarm](../repos/zju-fast-lab__ego-planner-swarm.md) (extends)
- [GCOPTER](../repos/zju-fast-lab__gcopter.md) (same_org)
- [EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors](../resources/zhou-ego-planner-paper.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
