# Safe Control for Nonlinear Systems Under Faults and Attacks Via Control Barrier Functions

`res:zhang-li-clark-2025-ft-cbf` - paper - <https://arxiv.org/abs/2207.05146>

**By:** Hongchao Zhang, Zhouchi Li, Andrew Clark - **Year:** 2025 - **Level:** advanced - **Access:** open

Peer-reviewed (IEEE Transactions on Automatic Control 2025, doi 10.1109/TAC.2025.3571338). Fault-tolerant CBFs: one EKF per sensor fault pattern, each omitting that pattern's sensors, and a CBF constraint for every estimate with its own error bound. When the constraints conflict, estimates are dropped by a solution-separation-style test against pair-excluded filters, then by largest residual. Wheeled-robot sensor-attack and Boeing 747 actuator-failure case studies in simulation.

## Key takeaways

- Safety filter margin from a bank of fault-excluded estimators, not one covariance: the mechanism of the close-area innovation claim C (integrity-aware safety-filter margin)
- Exclusion uses separation thresholds and pair-excluded filters, close to ARAIM-style subset exclusion
- When no consistent set is found it drops the largest-residual estimates instead of declaring unavailable
- Simulation only, ground robot and aircraft lateral dynamics; no multirotor, no range-sensor barrier

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `control-barrier-function`, `fault-tolerant`, `safety-filter`, `integrity`, `peer-reviewed`

## Related

- cites: [Control Barrier Functions for Safe CPS Under Sensor Faults and Attacks](../../catalog/resources/clark-li-zhang-2020-ft-cbf-cdc.md)

## Referenced by

- [Barrier Certificate based Safe Control for LiDAR-based Systems under Sensor Faults and Attacks](../../catalog/resources/zhang-cheng-niu-clark-2022-lidar-barrier-faults.md) (same_author)

_Indexed by lane(s): pl-margin-prior-art_
