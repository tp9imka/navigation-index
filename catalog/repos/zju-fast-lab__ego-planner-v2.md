# EGO-Planner-v2 (Swarm Playground)

`repo:zju-fast-lab/ego-planner-v2` - <https://github.com/ZJU-FAST-Lab/EGO-Planner-v2>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 751 | C++ | GPL-3.0 | 2023-10-16 | False | research-prototype | medium |

Codebase of the 'Swarm of micro flying robots in the wild' work: MINCO-based local trajectory optimisation with obstacle, dynamic-feasibility and inter-agent constraints, plus a lightweight simulator.

**Why it matters:** The current state of the ZJU B-spline / MINCO planner family that EGO-Planner and Fast-Planner started; shows how a full onboard planner is wired for real flights in clutter.

**Build notes:** License GPL-3.0 (gh api). Last push 2023-10-16. ROS 1 Noetic. Its bundled simulator runs without Gazebo, which makes a clutter-avoidance demo feasible in a day if the team already knows ROS. Needs a good pose: pair with the hub's VIO samples, and say so if the demo uses ground-truth odometry.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `minco`, `local-planner`, `swarm`, `multirotor`, `c++`, `gpl-3.0`

**Domains:** air

## Related

- extends: [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md)
- extends: [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md)
- same_org: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [Geometrically Constrained Trajectory Optimization for Multicopters](../../catalog/resources/wang-minco-gcopter-2021.md) (uses)
- [Swarm of micro flying robots in the wild](../../catalog/resources/zhou-swarm-wild-scirobotics-2022.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-23._
