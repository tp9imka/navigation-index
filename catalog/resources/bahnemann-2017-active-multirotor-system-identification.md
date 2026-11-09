# Sampling-based Motion Planning for Active Multirotor System Identification

`res:bahnemann-2017-active-multirotor-system-identification` - paper - <https://arxiv.org/abs/1612.05143>

**By:** Rik Bahnemann, Michael Burri, Enric Galceran, Roland Siegwart, Juan Nieto - **Year:** 2017 - **Level:** advanced - **Access:** open

ICRA 2017 (arXiv preprint read at abstract level). Plans maximally informative multirotor trajectories for identifying inertia and aerodynamic coefficients, approximating belief dynamics with an EKF inside a sampling-based (RRBT) planner. Reports about 4x faster parameter convergence and lower uncertainty in simulation and on a real vehicle.

## Key takeaways

- Some multirotor parameters only become observable under specific motions
- Active excitation for aero identification exists; it is planned offline, not triggered by a navigation filter

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `active-identification`, `multirotor`, `aerodynamic-coefficients`, `rrbt`

## Referenced by

- [Observability-aware Self-Calibration of Visual and Inertial Sensors for Ego-Motion Estimation](../../catalog/resources/schneider-2019-observability-aware-vi-self-calibration.md) (cites)

_Indexed by lane(s): innovation-pa-aero-adaptation_
