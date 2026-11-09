# HDVIO2.0: Wind and Disturbance Estimation with Hybrid Dynamics VIO

`res:cioffi-2025-hdvio2-wind-disturbance` - paper - <https://arxiv.org/abs/2504.00969>

**By:** Giovanni Cioffi, Leonard Bauersfeld, Davide Scaramuzza - **Year:** 2025 - **Level:** advanced - **Access:** open

IEEE T-RO 2025. Extends hybrid-dynamics VIO with rotational dynamics: two TCNs predict residual thrust and torque from commands and gyro history, and the optimizer estimates wind and external disturbances with the full state.

## Key takeaways

- Abstract reports real flights in winds up to 25 km/h; no accuracy figure in the abstract
- Wind is the state that limits model-aided dead reckoning; this estimates it onboard
- Code GPL/AGPL, ROS Noetic

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `hybrid-dynamics`, `wind-estimation`, `t-ro`

## Related

- has_code: [HDVIO2.0](../../catalog/repos/uzh-rpg__hdvio2.0.md)
- uses: [NeuroBEM: Hybrid Aerodynamic Quadrotor Model](../../catalog/resources/bauersfeld-2021-neurobem.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_
