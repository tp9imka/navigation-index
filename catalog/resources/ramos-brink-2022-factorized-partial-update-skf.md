# Factorized Partial-Update Schmidt-Kalman Filter

`res:ramos-brink-2022-factorized-partial-update-skf` - paper - <https://doi.org/10.2514/1.G006449>

**By:** J. Humberto Ramos, Kevin M. Brink, Prashant Ganesh, John E. Hurtado - **Year:** 2022 - **Level:** advanced - **Access:** paywalled

Journal of Guidance, Control, and Dynamics 45(9) (abstract-level read via indexers). Applies the partial-update Schmidt-Kalman filter of Brink (2017) to UD covariance factors for numerical stability, in sequential and batch forms plus a multiplicative EKF variant. A FUSION 2023 follow-up adapts the update percentages from nonlinearity metrics.

## Key takeaways

- Partial-update percentages between 0 (consider) and 1 (full) are the standard knob a gate would drive
- The FUSION 2023 follow-up adapts them from nonlinearity, not from identifiability (abstract level)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `schmidt-kalman`, `partial-update`, `ud-factorization`, `consider-states`

## Referenced by

- [Reliable strategies for implementing model-based navigation on fixed-wing drones](../../catalog/resources/laupre-pirlet-skaloud-2023-reliable-vdm-navigation.md) (cites)

_Indexed by lane(s): innovation-pa-aero-adaptation_
