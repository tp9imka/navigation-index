# Autoware

`repo:autowarefoundation/autoware` - <https://github.com/autowarefoundation/autoware>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 12,220 | Dockerfile | Apache-2.0 | 2026-11-04 | False | production | medium |

Meta-repository for Autoware, the open-source ROS 2 autonomous driving stack covering localization (NDT, EKF), perception, planning and control.

**Why it matters:** The biggest open ground-vehicle autonomy stack; its localization modules are a mature map-based alternative when GNSS is degraded.

**Hackathon notes:** Heavy: use the Docker images and the planning simulator. For a hackathon, lift single packages such as NDT scan matcher or the EKF localizer.

**Concepts:** [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Path and motion planning](../concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `autoware`, `ndt`, `ros2`, `av`

**Domains:** ground

## Related

- depends_on: [Autoware Universe](../repos/autowarefoundation__autoware_universe.md)
- integrates_with: [AWSIM](../repos/autowarefoundation__awsim.md)
- alternative_to: [Baidu Apollo](../repos/apolloauto__apollo.md)

## Referenced by

- [Baidu Apollo](../repos/apolloauto__apollo.md) (alternative_to)
- [Autoware Universe](../repos/autowarefoundation__autoware_universe.md) (same_org)
- [AWSIM](../repos/autowarefoundation__awsim.md) (integrates_with)
- [Autoware documentation](../resources/autoware-docs.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
