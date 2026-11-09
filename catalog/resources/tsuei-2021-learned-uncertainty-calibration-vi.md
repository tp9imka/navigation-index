# Learned Uncertainty Calibration for Visual Inertial Localization

`res:tsuei-2021-learned-uncertainty-calibration-vi` - paper - <https://arxiv.org/abs/2110.02136>

**By:** Stephanie Tsuei, Stefano Soatto, Paulo Tabuada, Mark B. Milam - **Year:** 2021 - **Level:** advanced - **Access:** open

ICRA 2021. Observes that EKF means are accurate while covariances are not, and that the covariance error in visual-inertial localization is systematic. Learns a nonlinear map from the reported covariance to an empirically calibrated one, tested in simulation and on a real-world VIO system.

## Key takeaways

- VIO covariance error is systematic, so it can be calibrated from logged flights
- Implies a cheap fix: fit an inflation from Day 1 recordings against a reference

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `covariance-calibration`, `uncertainty`, `ekf`, `xivo`

## Related

- same_author: [Quantifying VIO Uncertainty](../../catalog/resources/tsuei-soatto-2023-quantifying-vio-uncertainty.md)

## Referenced by

- [Quantifying VIO Uncertainty](../../catalog/resources/tsuei-soatto-2023-quantifying-vio-uncertainty.md) (same_author)

_Indexed by lane(s): close-area-localization_
