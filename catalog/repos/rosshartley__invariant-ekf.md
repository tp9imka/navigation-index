# invariant-ekf (Hartley InEKF)

`repo:rosshartley/invariant-ekf` - <https://github.com/RossHartley/invariant-ekf>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 571 | C++ | BSD-3-Clause | 2019-08-17 | False | archived | medium |

C++ library implementing the invariant EKF for aided inertial navigation, including contact-aided legged-robot state estimation.

**Why it matters:** Reference InEKF implementation; invariant filters behave better than standard EKF under large initial errors.

**Hackathon notes:** Last push 2019; still compiles with Eigen. Pairs with the Hartley 2019 paper.

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `inekf`, `lie-group`, `legged`

**Domains:** ground

## Related

- extends: [DRIFT](../repos/umich-curly__drift.md)
- alternative_to: [iekf (contagon)](../repos/contagon__iekf.md)

## Referenced by

- [iekf (contagon)](../repos/contagon__iekf.md) (alternative_to)
- [AI-IMU Dead-Reckoning](../repos/mbrossar__ai-imu-dr.md) (alternative_to)
- [DRIFT](../repos/umich-curly__drift.md) (extends)
- [The invariant extended Kalman filter as a stable observer](../resources/barrau-bonnabel-invariant-ekf.md) (explains)
- [Contact-Aided Invariant Extended Kalman Filtering for Robot State Estimation](../resources/hartley-contact-aided-inekf.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
