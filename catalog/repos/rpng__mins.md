# MINS

`repo:rpng/mins` - <https://github.com/rpng/MINS>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 812 | C++ | GPL-3.0 | 2026-10-23 | False | active-research | high |

Multi-sensor aided inertial navigation that fuses IMU with camera, LiDAR, GNSS and wheel odometry, including online spatial/temporal calibration and a multi-sensor simulator.

**Why it matters:** Directly relevant to assured PNT: one estimator that degrades gracefully as individual sensors (including GNSS) drop out.

**Hackathon notes:** Start with the provided simulated data to see each sensor's contribution, then disable GNSS mid-run to demo a jamming scenario.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual(-inertial) odometry](../concepts/vio.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Sensor calibration](../concepts/calibration.md)

**Tags:** `msckf`, `wheel-odometry`, `gnss`, `lidar`, `simulator`

**Domains:** ground

## Related

- extends: [OpenVINS](../repos/rpng__open_vins.md)

## Referenced by

- [OpenVINS](../repos/rpng__open_vins.md) (extends)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
