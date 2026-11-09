# Observability-aware Self-Calibration of Visual and Inertial Sensors for Ego-Motion Estimation

`res:schneider-2019-observability-aware-vi-self-calibration` - paper - <https://arxiv.org/abs/1901.07242>

**By:** Thomas Schneider, Mingyang Li, Cesar Cadena, Juan Nieto, Roland Siegwart - **Year:** 2019 - **Level:** advanced - **Access:** open

IEEE Sensors Journal (arXiv preprint read). A background process scores trajectory segments with information-theoretic metrics, keeps the most informative ones in a database across sessions, and updates calibration only from those segments. Compared against an EKF that jointly estimates motion and calibration.

## Key takeaways

- Information-gated calibration updates exist for visual-inertial extrinsics and intrinsics
- Segment selection runs beside the estimator, not inside a navigation filter during sensor loss
- Cites Bahnemann et al. for active multirotor model identification

**Concepts:** [Sensor calibration](../../catalog/concepts/calibration.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `information-gating`, `self-calibration`, `informative-segments`

## Related

- cites: [Sampling-based Motion Planning for Active Multirotor System Identification](../../catalog/resources/bahnemann-2017-active-multirotor-system-identification.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
