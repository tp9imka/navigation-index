# AI-IO

`repo:sjtu-visys-team/ai-io` - <https://github.com/SJTU-ViSYS-team/AI-IO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 87 | Python | MIT | 2026-07-27 | False | active-research | high |

Learned inertial odometry for quadrotors that feeds rotor speeds alongside IMU data into a transformer velocity regressor, then fuses the predicted velocity in an uncertainty-aware EKF. Ships its own real flight dataset with IMU, rotor speed and ground truth, and also reads the DIDO dataset.

**Why it matters:** The most recent open code that treats the propulsion system as a sensor: the paper (ICRA 2026) reports rotor speed improves velocity prediction accuracy by 36.9%. MIT license makes it usable for a product prototype.

**Hackathon notes:** Dataset is a 363 MB GitHub release asset (AI-IO_dataset.tar.gz) plus a 0.9 MB checkpoint, so it downloads in minutes. Train/eval scripts are single commands; training time and GPU need not measured here. Use its velocity output as a pseudo-measurement in an existing EKF; an IMU-only ablation gives the rotor-speed delta.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `learned-inertial-odometry`, `rotor-speed`, `quadrotor`, `transformer`, `ekf`, `pytorch`

**Domains:** air

## Related

- evaluated_on: [DIDO](../../catalog/repos/zhangkunyi__dido.md)
- alternative_to: [AirIO](../../catalog/repos/air-io__air-io.md)
- alternative_to: [Learned Inertial Odometry for Drone Racing](../../catalog/repos/uzh-rpg__learned_inertial_model_odometry.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [DIDO](../../catalog/repos/zhangkunyi__dido.md) (integrates_with)
- [AI-IO: An Aerodynamics-Inspired Real-Time Inertial Odometry for Quadrotors](../../catalog/resources/cui-2026-ai-io-aerodynamics-inertial-odometry.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
