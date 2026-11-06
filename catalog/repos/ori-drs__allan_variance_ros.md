# allan_variance_ros

`repo:ori-drs/allan_variance_ros` - <https://github.com/ori-drs/allan_variance_ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 695 | C++ | BSD-3-Clause | 2025-01-23 | False | production | high |

ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.

**Why it matters:** Needed to get realistic IMU noise values for any filter or VIO setup.

**Hackathon notes:** Record a few hours of static IMU data before the event; the analysis itself is quick.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [ori-drs__allan_variance_ros](../../docs/integration-cards/ori-drs__allan_variance_ros.md) (integration-cards)

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `allan-variance`, `imu-noise`, `kalibr`

**Domains:** multi

## Related

- alternative_to: [imu_utils](../../catalog/repos/gaowenliang__imu_utils.md)
- integrates_with: [Kalibr](../../catalog/repos/ethz-asl__kalibr.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [allantools](../../catalog/repos/aewallin__allantools.md) (alternative_to)
- [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) (integrates_with)
- [imu_utils](../../catalog/repos/gaowenliang__imu_utils.md) (alternative_to)
- [allan-variance (Python)](../../catalog/repos/nmayorov__allan-variance.md) (alternative_to)
- [kalibr_allan (archived)](../../catalog/repos/rpng__kalibr_allan.md) (alternative_to)
- [Kalibr wiki: IMU Noise Model](../../catalog/resources/kalibr-imu-noise-model-wiki.md) (explains)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
