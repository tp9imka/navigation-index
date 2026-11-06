# AuvEstimator

`repo:alliwong/auvestimator` - <https://github.com/alliWong/AuvEstimator>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3 | Python | ? | 2021-05-14 | False | research-prototype | medium |

Work-in-progress AUV state estimator fusing DVL, IMU and barometer two ways, a 15-state EKF and a GTSAM factor graph with custom DVL and barometer factors, with ROS 1 (Kinetic/Melodic, Python 2.7) wrappers.

**Why it matters:** Small, readable DVL-aided INS example to start a GNSS-free underwater nav filter from.

**Hackathon notes:** Dormant since 2021; treat as a starting template, not a dependency. No LICENSE file, so all rights reserved by default.

**Concepts:** [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `ekf`, `dvl`, `imu`, `auv`

**Domains:** underwater

## Related

- integrates_with: [Water Linked DVL Python](../../catalog/repos/waterlinked__dvl-python.md)
- alternative_to: [SMARC navigation](../../catalog/repos/halajun__smarc_navigation.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [SMARC navigation](../../catalog/repos/halajun__smarc_navigation.md) (alternative_to)
- [USBL Simulator](../../catalog/repos/maximilian-nitsch__usbl-simulator.md) (integrates_with)
- [Water Linked DVL Python](../../catalog/repos/waterlinked__dvl-python.md) (integrates_with)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
