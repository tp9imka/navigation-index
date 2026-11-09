# PyPose

`repo:pypose/pypose` - <https://github.com/pypose/pypose>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,621 | Python | Apache-2.0 | 2026-11-06 | False | active-research | medium |

PyTorch library for differentiable robotics on Lie groups: IMU pre-integration, EKF/UKF modules and second-order optimizers that can sit inside a training loop.

**Why it matters:** The base AirIO and AirIMU are built on; lets a team train a learned inertial or dynamics model end to end through the filter.

**Hackathon notes:** Apache-2.0, pip install pypose. Use pp.module.IMUPreintegrator to propagate and plug a learned velocity in as an EKF update.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `lie-group`, `imu-preintegration`, `pytorch`, `differentiable`

**Domains:** multi

## Related

- integrates_with: [AirIO](../../catalog/repos/air-io__air-io.md)
- integrates_with: [AirIMU](../../catalog/repos/haleqiu__airimu.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
