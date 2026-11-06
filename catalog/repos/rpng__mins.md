# MINS

`repo:rpng/mins` - <https://github.com/rpng/MINS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 812 | C++ | GPL-3.0 | 2026-10-23 | False | active-research | high |

Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.

**Why it matters:** Directly relevant to assured PNT: one estimator that degrades gracefully as individual sensors (including GNSS) drop out.

**Hackathon notes:** Start with the provided simulated data to see each sensor's contribution, then disable GNSS mid-run to demo a jamming scenario.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [rpng__mins](../../docs/integration-cards/rpng__mins.md) (integration-cards)
- [mins-2023](../../docs/paper-digests/mins-2023.md) (paper-digests)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `msckf`, `wheel-odometry`, `gnss`, `lidar`, `simulator`

**Domains:** ground

## Related

- extends: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [OpenVINS](../../catalog/repos/rpng__open_vins.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
