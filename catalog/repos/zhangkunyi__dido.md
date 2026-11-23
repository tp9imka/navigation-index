# DIDO

`repo:zhangkunyi/dido` - <https://github.com/zhangkunyi/DIDO>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 64 | Python | ? | 2022-10-08 | False | research-prototype | medium |

Code and data for Deep Inertial Quadrotor Dynamical Odometry: networks de-bias the accelerometer and gyro, learn a dynamics residual and regress velocity/position, and two EKF stages (rotation, translation) fuse them. Dataset folders hold per-sequence HDF5 files with IMU and mocap ground truth for circle and figure-eight flights.

**Why it matters:** Early open example of mixing quadrotor dynamics with learned inertial estimates in a filter; its data is also the second benchmark used by AI-IO.

**Build notes:** No LICENSE file in the repo, so reuse rights are unclear: use the data for evaluation only and ask the authors before shipping anything derived. Indoor mocap flights only.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `learned-inertial-odometry`, `quadrotor-dynamics`, `ekf`, `hdf5`

**Domains:** air

## Related

- integrates_with: [AI-IO](../../catalog/repos/sjtu-visys-team__ai-io.md)

## Referenced by

- [AI-IO](../../catalog/repos/sjtu-visys-team__ai-io.md) (evaluated_on)
- [DIDO: Deep Inertial Quadrotor Dynamical Odometry](../../catalog/resources/zhang-2022-dido-quadrotor-dynamical-odometry.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-23._
