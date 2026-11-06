# AI-IMU Dead-Reckoning

`repo:mbrossar/ai-imu-dr` - <https://github.com/mbrossar/ai-imu-dr>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,009 | Python | MIT | 2025-01-08 | False | research-prototype | high |

Car dead reckoning from IMU only, using an invariant EKF whose noise covariances are adapted by a neural network, evaluated on KITTI.

**Why it matters:** Ground vehicle navigation through GNSS outages using only the IMU.

**Hackathon notes:** PyTorch; KITTI raw data needed. Clear demo of IMU-only drift reduction.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [mbrossar__ai-imu-dr](../../docs/integration-cards/mbrossar__ai-imu-dr.md) (integration-cards)
- [brossard-ai-imu-dr](../../docs/paper-digests/brossard-ai-imu-dr.md) (paper-digests)

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `inekf`, `learned-covariance`, `kitti`

**Domains:** ground

## Related

- same_org: [Denoise IMU Gyro](../../catalog/repos/mbrossar__denoise-imu-gyro.md)
- alternative_to: [invariant-ekf (Hartley InEKF)](../../catalog/repos/rosshartley__invariant-ekf.md)

## Referenced by

- [3. Inertial navigation and sensor fusion](../../docs/primer/03-inertial-and-fusion.md) (mentions)
- [Denoise IMU Gyro](../../catalog/repos/mbrossar__denoise-imu-gyro.md) (same_org)
- [AI-IMU Dead-Reckoning](../../catalog/resources/brossard-ai-imu-dr.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
