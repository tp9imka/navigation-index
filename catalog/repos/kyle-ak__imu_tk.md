# imu_tk

`repo:kyle-ak/imu_tk` - <https://github.com/Kyle-ak/imu_tk>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 557 | C++ | ? | 2023-06-22 | False | research-prototype | medium |

Tool for calibrating IMU intrinsics (misalignment, scale factors and biases of accelerometer and gyro) from a sequence of static poses, without a turntable.

**Why it matters:** Cheap way to improve MEMS IMU accuracy before deploying a filter.

**Hackathon notes:** Needs Ceres; collect static poses in many orientations with short rotations between.

**Concepts:** [Sensor calibration](../concepts/calibration.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `imu-intrinsics`, `multi-position`

**Domains:** multi

## Related

- alternative_to: [Kalibr](../repos/ethz-asl__kalibr.md)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
