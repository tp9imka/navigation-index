# AI-IO: An Aerodynamics-Inspired Real-Time Inertial Odometry for Quadrotors

`res:cui-2026-ai-io-aerodynamics-inertial-odometry` - paper - <https://arxiv.org/abs/2603.00597>

**By:** Jiahao Cui, Feng Yu, Linzuo Zhang, Yu Hu, Danping Zou - **Year:** 2026 - **Level:** advanced - **Access:** open

ICRA 2026 paper (arXiv Feb 2026). Argues rotor speed is the missing physical input in learned inertial odometry because rotor drag ties body velocity to measurable quantities, feeds IMU plus rotor speed to a transformer velocity estimator, and fuses its output in an uncertainty-aware EKF. Releases a real quadrotor dataset with IMU, rotor speed and ground truth.

## Key takeaways

- Abstract: adding rotor speed improves velocity prediction accuracy by 36.9%
- Abstract: the transformer adds a further 22.4% over previous results
- Code and data MIT-licensed on GitHub

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial-odometry`, `rotor-speed`, `rotor-drag`, `icra-2026`

## Related

- has_code: [AI-IO](../../catalog/repos/sjtu-visys-team__ai-io.md)
- cites: [DIDO: Deep Inertial Quadrotor Dynamical Odometry](../../catalog/resources/zhang-2022-dido-quadrotor-dynamical-odometry.md)
- cites: [AirIO: Learning Inertial Odometry with Enhanced IMU Feature Observability](../../catalog/resources/airio-paper.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)

_Indexed by lane(s): nav-differentiators_
