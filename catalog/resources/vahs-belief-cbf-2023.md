# Belief Control Barrier Functions for Risk-aware Control

`res:vahs-belief-cbf-2023` - paper - <https://arxiv.org/abs/2309.06499>

**By:** Matti Vahs, Christian Pek, Jana Tumova - **Year:** 2023 - **Level:** advanced - **Access:** open

Defines control barrier functions on the EKF belief (mean and covariance) so a controller keeps the robot in a safe set with a chosen confidence. Quadrotor tests under disturbances and varying sensing; control rates up to 1 kHz. arXiv preprint, no venue on the page.

## Key takeaways

- Strongest prior art for clearance inflated by live covariance
- Gaussian belief only, faults not modelled

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `control-barrier-function`, `belief`, `ekf`, `quadrotor`

_Indexed by lane(s): close-area-innovation_
