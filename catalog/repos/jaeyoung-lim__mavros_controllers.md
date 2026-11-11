# mavros_controllers

`repo:jaeyoung-lim/mavros_controllers` - <https://github.com/Jaeyoung-Lim/mavros_controllers>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 509 | C++ | BSD-3-Clause | 2022-09-03 | False | research-prototype | medium |

Geometric trajectory-tracking controllers for PX4 multirotors over MAVROS, sending body-rate and thrust setpoints in offboard mode, with trajectory publisher nodes.

**Why it matters:** A worked example of closing your own tracking loop around PX4 from a companion computer, the integration path most guidance demos need.

**Build notes:** License BSD-3-Clause (gh api). Last push 2022-09-03. ROS 1 + MAVROS. For a ROS 2 build use px4-ros2-interface-lib or the PX4 ROS 2 offboard example; copy this repo's control law rather than its plumbing.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `px4`, `offboard`, `geometric-control`, `mavros`, `bsd-3-clause`

**Domains:** air

## Related

- depends_on: [MAVROS](../../catalog/repos/mavlink__mavros.md)
- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- alternative_to: [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
