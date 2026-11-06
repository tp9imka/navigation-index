# fuse

`repo:locusrobotics/fuse` - <https://github.com/locusrobotics/fuse>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 885 | C++ | NOASSERTION | 2026-08-19 | False | production | medium |

ROS framework for sensor fusion as factor-graph optimization: plugin sensor models, motion models and publishers on top of Ceres, supporting both smoothing and fixed-lag estimation.

**Why it matters:** A more flexible alternative to robot_localization EKF when you need delayed measurements, robust losses or custom constraints.

**Hackathon notes:** Use the fuse tutorials or the ROSCon UK 2025 workshop Docker image; plugin config in YAML. Ceres dependency builds slowly.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md)

**Tags:** `factor-graph`, `ceres`, `fixed-lag`, `ros2`

**Domains:** ground, multi

## Related

- same_org: [ROSCon UK 2025 State Estimation workshop](../repos/locusrobotics__roscon-uk-2025-se-workshop.md)
- alternative_to: [robot_localization](../repos/cra-ros-pkg__robot_localization.md)

## Referenced by

- [ROSCon UK 2025 State Estimation workshop](../repos/locusrobotics__roscon-uk-2025-se-workshop.md) (depends_on)
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../resources/nav2-roscon-uk-2025-state-estimation-workshop.md) (uses)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
