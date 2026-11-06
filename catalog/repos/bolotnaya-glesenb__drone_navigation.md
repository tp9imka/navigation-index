# drone_navigation - ROS 2 + PX4 + RTAB-Map diploma

`repo:bolotnaya-glesenb/drone_navigation` - <https://github.com/BOLOTNAYA-GLESENb/drone_navigation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-06-07 | False | educational | medium |

Diploma project: autonomous quadcopter navigation in PX4 SITL + Gazebo with ROS 2, RTAB-Map visual SLAM for mapping and localisation, A* global planning, VFH plus a custom 3D manoeuvre for obstacle avoidance, and YOLO person detection. README in Russian.

**Why it matters:** An integrated sim stack that wires SLAM, planning and avoidance to PX4, which is the glue most teams lose time on.

**Hackathon notes:** Needs a working ROS 2 + PX4 SITL + Gazebo setup (hours, not minutes). Reuse the node layout and the SLAM-to-planner wiring.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `lang:ru`, `ros2`, `px4`, `rtab-map`, `gazebo`, `a-star`, `vfh`

**Domains:** air

## Related

- depends_on: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- depends_on: [RTAB-Map](../../catalog/repos/introlab__rtabmap.md)
- depends_on: [Ultralytics YOLO](../../catalog/repos/ultralytics__ultralytics.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
