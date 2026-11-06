# robot_localization

`repo:cra-ros-pkg/robot_localization` - <https://github.com/cra-ros-pkg/robot_localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,983 | C++ | NOASSERTION | 2026-11-02 | False | production | high |

ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.

**Why it matters:** Fastest route to a working fused odometry on a ROS ground robot or drone; the usual baseline before writing a custom filter.

**Hackathon notes:** apt install on ROS 2; mostly YAML config. Common gotcha: frame conventions (REP-103/105) and double-counting velocities.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [cra-ros-pkg__robot_localization](../../docs/integration-cards/cra-ros-pkg__robot_localization.md) (integration-cards)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md)

**Tags:** `ekf`, `ukf`, `ros2`, `navsat`

**Domains:** ground, air

## Related

- alternative_to: [ethzasl_msf (Multi Sensor Fusion)](../../catalog/repos/ethz-asl__ethzasl_msf.md)
- integrates_with: [imu_tools](../../catalog/repos/ccnyroboticslab__imu_tools.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [imu_tools](../../catalog/repos/ccnyroboticslab__imu_tools.md) (integrates_with)
- [ethzasl_msf (Multi Sensor Fusion)](../../catalog/repos/ethz-asl__ethzasl_msf.md) (alternative_to)
- [fuse](../../catalog/repos/locusrobotics__fuse.md) (alternative_to)
- [ROSCon UK 2025 State Estimation workshop](../../catalog/repos/locusrobotics__roscon-uk-2025-se-workshop.md) (depends_on)
- [Navigating Using GPS Localization (Nav2 tutorial)](../../catalog/resources/nav2-gps-navigation-tutorial.md) (uses)
- [Smoothing Odometry using Robot Localization (Nav2 first-time robot setup guide)](../../catalog/resources/nav2-robot-localization-setup-guide.md) (uses)
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../../catalog/resources/nav2-roscon-uk-2025-state-estimation-workshop.md) (uses)
- [robot_localization package documentation](../../catalog/resources/robot-localization-docs.md) (has_code)
- [UGV GNSS outage on a real log: wheel odometry + IMU, innovation gate, drag detector](../../catalog/samples/ugv-gnss-outage-real.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
