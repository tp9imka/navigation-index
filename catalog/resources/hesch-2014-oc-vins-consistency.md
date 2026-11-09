# Consistency Analysis and Improvement of Vision-aided Inertial Navigation

`res:hesch-2014-oc-vins-consistency` - paper - <https://www-users.cse.umn.edu/~stergios/papers/TRO_2014_OC_VINS_Joel_Dimitris_Sean.pdf>

**By:** Joel A. Hesch, Dimitrios G. Kottas, Sean L. Bowman, Stergios I. Roumeliotis - **Year:** 2014 - **Level:** advanced - **Access:** open

IEEE T-RO 30(1):158-176. Shows that standard EKF-based VINS gains spurious information along unobservable directions (global yaw and position), so its covariance shrinks too fast and the filter becomes overconfident. Proposes observability-constrained VINS (OC-VINS) for both SLAM and MSCKF, tested in simulation and on real data.

## Key takeaways

- A plain EKF VIO is overconfident by construction, not just by tuning
- Yaw about gravity is unobservable; a covariance that says otherwise is wrong
- OC / FEJ style fixes are what OpenVINS and similar stacks ship

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `consistency`, `nees`, `observability`, `msckf`, `oc-vins`

## Related

- same_author: [Observability-based Rules for Designing Consistent EKF SLAM Estimators](../../catalog/resources/huang-mourikis-roumeliotis-2010-observability-consistent-ekf.md)
- explains: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

_Indexed by lane(s): close-area-localization_
