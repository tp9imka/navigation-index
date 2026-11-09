# Belief Control Barrier Functions for Risk-aware Control

`res:vahs-belief-cbf-2023` - paper - <https://arxiv.org/abs/2309.06499>

**By:** Matti Vahs, Christian Pek, Jana Tumova - **Year:** 2023 - **Level:** advanced - **Access:** open

Peer-reviewed (IEEE RA-L 8(12):8565-8572, 2023, doi 10.1109/LRA.2023.3330662, confirmed via Crossref in docs/research/close-area-nav/05-cbf-baselines-faithful.md). Defines control barrier functions on the EKF belief (mean and covariance) so a controller keeps the robot in a safe set with a chosen confidence. The barrier uses the predicted covariance growth between updates and a margin for the jump at the next measurement update. Crazyflie hardware tests under varying sensing; control rates up to 1 kHz.

## Key takeaways

- Strongest prior art for clearance inflated by live covariance
- Brakes before the margin grows: covariance prediction plus an update-jump margin (Theorem 3); a plain sqrt(lambda_max) inflation is a weaker copy
- Gaussian belief only, faults not modelled

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `control-barrier-function`, `belief`, `ekf`, `quadrotor`, `peer-reviewed`

## Referenced by

- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Risk-Aware Robot Control in Dynamic Environments Using Belief Control Barrier Functions](../../catalog/resources/han-vahs-sample-based-bcbf-cdc2025.md) (same_author)

_Indexed by lane(s): close-area-innovation_
