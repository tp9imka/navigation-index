# Fast-Planner

`repo:hkust-aerial-robotics/fast-planner` - <https://github.com/hkust-aerial-robotics/fast-planner>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,443 | C++ | GPL-3.0 | 2024-10-24 | False | research-prototype | medium |

HKUST quadrotor planning framework: kinodynamic A* front-end plus B-spline optimization, with topological and perception-aware variants for fast flight in unknown environments.

**Why it matters:** Classic baseline that most later UAV planners compare against; modular enough to reuse its mapping (ESDF) and search components.

**Hackathon notes:** ROS1 + Gazebo-free lightweight sim; builds in minutes on Ubuntu 20.04. Expect NLopt dependency friction.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `kinodynamic-a-star`, `b-spline`, `esdf`, `ros1`

**Domains:** air

## Related

- extends: [FUEL - Fast UAV Exploration](../repos/hkust-aerial-robotics__fuel.md)
- alternative_to: [EGO-Planner](../repos/zju-fast-lab__ego-planner.md)

## Referenced by

- [FUEL - Fast UAV Exploration](../repos/hkust-aerial-robotics__fuel.md) (extends)
- [KR Autonomous Flight](../repos/kumarrobotics__kr_autonomous_flight.md) (alternative_to)
- [EGO-Planner](../repos/zju-fast-lab__ego-planner.md) (extends)
- [Robust and Efficient Quadrotor Trajectory Generation for Fast Autonomous Flight](../resources/zhou-fast-planner-paper.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
