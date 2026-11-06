# Aerostack2

`repo:aerostack2/aerostack2` - <https://github.com/aerostack2/aerostack2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 406 | C++ | BSD-3-Clause | 2026-11-05 | False | active-research | medium |

ROS 2 framework for autonomous single and multi-aerial-robot systems with behaviours, state estimation plugins and platform adapters (Gazebo and a multirotor simulator in this repo; PX4, Crazyflie and DJI adapters in separate as2_platform_* repos).

**Why it matters:** One of the few ROS 2 native UAV mission frameworks that spans simulation to several real autopilots, good for multi-drone mission demos.

**Hackathon notes:** Binary packages for Humble; Python mission API lets you script takeoff/goto/land for several drones quickly.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `ros2`, `behaviour-trees`, `multi-uav`, `upm`, `aerostack2`, `uav`, `mission-api`, `behavior-tree`, `px4`

**Domains:** air, multi

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- alternative_to: [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md)
- integrates_with: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)
- integrates_with: [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md)
- alternative_to: [MRS UAV System](../../catalog/repos/ctu-mrs__mrs_uav_system.md)
- integrates_with: [PlanSys2](../../catalog/repos/plansys2__ros2_planning_system.md)
- depends_on: [BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md)

## Referenced by

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MRS UAV System](../../catalog/repos/ctu-mrs__mrs_uav_system.md) (alternative_to)
- [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md) (alternative_to)
- [PlanSys2](../../catalog/repos/plansys2__ros2_planning_system.md) (integrates_with)
- [Race Against the Machine dataset](../../catalog/repos/tii-racing__drone-racing-dataset.md) (alternative_to)
- [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md) (integrates_with)
- [Aerostack2: A Software Framework for Developing Multi-robot Aerial Systems](../../catalog/resources/aerostack2-paper.md) (has_code)
- [CVAR-UPM Drone Team - A2RL](../../catalog/resources/cvar-upm-a2rl-team.md) (uses)

_Indexed by lane(s): autopilots, domains-swarm, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
