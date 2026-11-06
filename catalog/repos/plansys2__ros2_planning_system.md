# PlanSys2

`repo:plansys2/ros2_planning_system` - <https://github.com/plansys2/ros2_planning_system>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 495 | C++ | Apache-2.0 | 2026-10-30 | False | production | medium |

PDDL-based symbolic planning system for ROS 2: domain/problem management, plan generation with off-the-shelf planners and execution via behavior trees.

**Why it matters:** Turns high-level mission goals (visit, inspect, deliver) into executable action sequences, the missing layer above Nav2.

**Hackathon notes:** apt-installable; write a PDDL domain and wrap Nav2 goals as actions. Learning PDDL is the time cost.

**Concepts:** [Mission planning and routing](../../catalog/concepts/mission-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `pddl`, `task-planning`, `behavior-tree`, `ros2`

**Domains:** multi

## Related

- integrates_with: [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md)
- depends_on: [BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md)
- integrates_with: [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md) (integrates_with)
- [PlanSys2: A Planning System Framework for ROS2](../../catalog/resources/plansys2-paper.md) (has_code)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
