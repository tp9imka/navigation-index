# KR Autonomous Flight

`repo:kumarrobotics/kr_autonomous_flight` - <https://github.com/kumarrobotics/kr_autonomous_flight>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 796 | C++ | NOASSERTION | 2026-04-18 | False | active-research | medium |

UPenn Kumar Robotics end-to-end autonomy stack for GPS-denied quadrotors: state estimation, mapping, planning and control in one system.

**Why it matters:** Full reference stack for flying without GNSS in forests and under canopy, from a lab with many field deployments.

**Hackathon notes:** Docker images help; large build. Use it to see how estimation and planning are glued, or reuse the planner.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Visual(-inertial) odometry](../concepts/vio.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `gps-denied`, `quadrotor`, `full-stack`

**Domains:** air

## Related

- alternative_to: [Fast-Planner](../repos/hkust-aerial-robotics__fast-planner.md)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
