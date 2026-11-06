# Ceres Solver

`repo:ceres-solver/ceres-solver` - <https://github.com/ceres-solver/ceres-solver>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,604 | C++ | NOASSERTION | 2026-11-04 | False | production | medium |

Google's nonlinear least-squares and general optimization library with automatic differentiation and robust loss functions.

**Why it matters:** Used as the solver under many VIO and GNSS/INS optimizers (VINS-Fusion, OB_GINS); good for writing your own sliding-window estimator.

**Hackathon notes:** Solid but you write the residuals yourself. Pair with an existing IMU preintegration residual (e.g. from OB_GINS) rather than deriving from scratch.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `nonlinear-least-squares`, `autodiff`, `bundle-adjustment`

**Domains:** multi

## Related

- alternative_to: [GTSAM](../repos/borglab__gtsam.md)
- integrates_with: [OB_GINS](../repos/i2nav-whu__ob_gins.md)
- integrates_with: [VINS-Fusion](../repos/hkust-aerial-robotics__vins-fusion.md)

## Referenced by

- [GTSAM](../repos/borglab__gtsam.md) (alternative_to)
- [OB_GINS](../repos/i2nav-whu__ob_gins.md) (depends_on)
- [g2o](../repos/rainerkuemmerle__g2o.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
