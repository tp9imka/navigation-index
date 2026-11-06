# imu_x_fusion

`repo:cggos/imu_x_fusion` - <https://github.com/cggos/imu_x_fusion>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,127 | C++ | GPL-3.0 | 2025-03-28 | False | educational | high |

Loosely coupled IMU + GNSS / 6-DoF odometry fusion with multiple estimators side by side (ESKF, IEKF, UKF variants, MAP).

**Why it matters:** Lets you compare filter variants on the same inputs with little code.

**Hackathon notes:** ROS package; swap estimator by config to compare behaviour.

**Concepts:** [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `eskf`, `iekf`, `ukf`, `comparison`

**Domains:** ground

## Related

- alternative_to: [imu_gps_localization](../../catalog/repos/ydsf16__imu_gps_localization.md)
- alternative_to: [gps_imu_fusion](../../catalog/repos/shelfcol__gps_imu_fusion.md)

## Referenced by

- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [gps_imu_fusion](../../catalog/repos/shelfcol__gps_imu_fusion.md) (alternative_to)
- [imu_gps_localization](../../catalog/repos/ydsf16__imu_gps_localization.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
