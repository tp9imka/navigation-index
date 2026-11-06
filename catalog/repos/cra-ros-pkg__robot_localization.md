# robot_localization

`repo:cra-ros-pkg/robot_localization` - <https://github.com/cra-ros-pkg/robot_localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,983 | C++ | NOASSERTION | 2026-11-02 | False | production | high |

ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.

**Why it matters:** Fastest route to a working fused odometry on a ROS ground robot or drone; the usual baseline before writing a custom filter.

**Hackathon notes:** apt install on ROS 2; mostly YAML config. Common gotcha: frame conventions (REP-103/105) and double-counting velocities.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [GNSS/INS integration](../concepts/gnss-ins.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md)

**Tags:** `ekf`, `ukf`, `ros2`, `navsat`

**Domains:** ground, air

## Related

- alternative_to: [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md)
- integrates_with: [imu_tools](../repos/ccnyroboticslab__imu_tools.md)

## Referenced by

- [imu_tools](../repos/ccnyroboticslab__imu_tools.md) (integrates_with)
- [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md) (alternative_to)
- [fuse](../repos/locusrobotics__fuse.md) (alternative_to)
- [ROSCon UK 2025 State Estimation workshop](../repos/locusrobotics__roscon-uk-2025-se-workshop.md) (depends_on)
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) (uses)
- [Nav2 first-time robot setup: Odometry and robot_localization](../resources/nav2-robot-localization-setup-guide.md) (uses)
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../resources/nav2-roscon-uk-2025-state-estimation-workshop.md) (uses)
- [robot_localization package documentation](../resources/robot-localization-docs.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
