# Observability-based Rules for Designing Consistent EKF SLAM Estimators

`res:huang-mourikis-roumeliotis-2010-observability-consistent-ekf` - paper - <https://experts.umn.edu/en/publications/observability-based-rules-for-designing-consistent-ekf-slam-estim/>

**By:** Guoquan Huang, Anastasios I. Mourikis, Stergios I. Roumeliotis - **Year:** 2010 - **Level:** advanced - **Access:** paywalled

IJRR 29(5) (abstract read). Proves that linearising at the latest estimates gives the EKF a larger observable subspace than the true nonlinear system, so covariance shrinks in directions without information. Proposes OC-EKF and first-estimates-Jacobian (FEJ) EKF.

## Key takeaways

- Spurious information from relinearisation is a known source of overconfidence; an information gate built on the filter's own Jacobians inherits it
- Use FEJ-style or fixed linearisation points when computing the gate's information increment

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `fej`, `ekf-consistency`, `observability`

_Indexed by lane(s): innovation-pa-aero-adaptation_
