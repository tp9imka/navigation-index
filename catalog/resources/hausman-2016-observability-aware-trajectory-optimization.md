# Observability-Aware Trajectory Optimization for Self-Calibration with Application to UAVs

`res:hausman-2016-observability-aware-trajectory-optimization` - paper - <https://arxiv.org/abs/1604.07905>

**By:** Karol Hausman, James Preiss, Gaurav S. Sukhatme, Stephan Weiss - **Year:** 2016 - **Level:** advanced - **Access:** open

arXiv preprint. Plans quadrotor trajectories that maximise an observability measure of chosen calibration states, using the empirical local observability Gramian (finite-difference perturbations of the simulated sensor model) and Krener-Ide style measures based on its condition number or smallest singular value. Simulated GPS-IMU quadrotor only.

## Key takeaways

- Empirical local observability Gramian is cheap to compute numerically for nonlinear models
- Reported about 2x lower position RMSE and 4x lower GPS-IMU transform error than a minimum-energy planner (simulation)
- Plans excitation; does not gate a running filter's updates

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `observability-gramian`, `active-calibration`, `trajectory-optimization`, `quadrotor`

## Related

- same_author: [Trajectory Optimization for Self-Calibration and Navigation](../../catalog/resources/preiss-2017-trajectory-optimization-self-calibration.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Trajectory Optimization for Self-Calibration and Navigation](../../catalog/resources/preiss-2017-trajectory-optimization-self-calibration.md) (same_author)

_Indexed by lane(s): innovation-pa-aero-adaptation_
