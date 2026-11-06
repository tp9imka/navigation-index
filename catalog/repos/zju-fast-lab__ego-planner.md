# EGO-Planner

`repo:zju-fast-lab/ego-planner` - <https://github.com/zju-fast-lab/ego-planner>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,730 | C++ | GPL-3.0 | 2025-03-08 | False | research-prototype | medium |

ESDF-free gradient-based local planner for quadrotors from ZJU FAST Lab: optimizes B-spline trajectories using collision terms computed only where the trajectory hits obstacles.

**Why it matters:** Lightweight onboard replanning for small drones flying through clutter; widely reused baseline for agile UAV navigation in unknown environments.

**Hackathon notes:** ROS1 (Ubuntu 16.04-20.04) with a bundled simulator; runs on a laptop. A ROS 2 port lives in the ego-planner-swarm ros2_version branch, and upstream recommends EGO-Swarm over this repo; PX4 needs a bridge. Good for a demo of reactive flight in a random forest map.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `quadrotor`, `b-spline`, `local-planner`, `ros1`

**Domains:** air

## Related

- extends: [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md)
- extends: [Fast-Planner](../../catalog/repos/hkust-aerial-robotics__fast-planner.md)
- same_org: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)

## Referenced by

- [Fast-Planner](../../catalog/repos/hkust-aerial-robotics__fast-planner.md) (alternative_to)
- [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md) (extends)
- [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md) (same_org)
- [EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors](../../catalog/resources/zhou-ego-planner-paper.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
