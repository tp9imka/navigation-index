# allan_variance_ros

`repo:ori-drs/allan_variance_ros` - <https://github.com/ori-drs/allan_variance_ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 695 | C++ | BSD-3-Clause | 2025-01-23 | False | production | high |

ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.

**Why it matters:** Needed to get realistic IMU noise values for any filter or VIO setup.

**Hackathon notes:** Record a few hours of static IMU data before the event; the analysis itself is quick.

**Concepts:** [Sensor calibration](../concepts/calibration.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `allan-variance`, `imu-noise`, `kalibr`

**Domains:** multi

## Related

- alternative_to: [imu_utils](../repos/gaowenliang__imu_utils.md)
- integrates_with: [Kalibr](../repos/ethz-asl__kalibr.md)

## Referenced by

- [allantools](../repos/aewallin__allantools.md) (alternative_to)
- [Kalibr](../repos/ethz-asl__kalibr.md) (integrates_with)
- [imu_utils](../repos/gaowenliang__imu_utils.md) (alternative_to)
- [allan-variance (Python)](../repos/nmayorov__allan-variance.md) (alternative_to)
- [kalibr_allan (archived)](../repos/rpng__kalibr_allan.md) (alternative_to)
- [Kalibr wiki: IMU Noise Model](../resources/kalibr-imu-noise-model-wiki.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
