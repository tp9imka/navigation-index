# ArduPilot EKF3 drag fusion and wind-state gating (source, Copter-4.6.3)

`res:ardupilot-ekf3-drag-wind-source-copter-4-6-3` - doc - <https://github.com/ArduPilot/ardupilot/blob/Copter-4.6.3/libraries/AP_NavEKF3/AP_NavEKF3_AirDataFusion.cpp>

**By:** ArduPilot Dev Team - **Year:** 2025 - **Level:** advanced - **Access:** open

Source read at tag Copter-4.6.3. FuseDragForces fuses body-frame drag with fixed coefficients (EK3_DRAG_BCOEF_X/Y, EK3_DRAG_MCOEF) and computes Kalman gains only for the two wind states. setAidingMode sets windStateIsObservable from source types (GPS position or velocity, flow, beacons, body odometry); CovariancePrediction treats wind as truth (zero variance, no process noise) during drag dead reckoning or when wind is not observable. A source-type freeze rule, not a measured-identifiability test.

## Key takeaways

- Drag coefficients are never adapted online
- Drag fusion corrects wind only; velocity and position are not corrected by drag in this code
- Wind freezes on a source-type rule at GNSS loss

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `ekf3`, `drag-fusion`, `wind`, `source-code`, `dead-reckoning`

## Related

- part_of: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- explains: [Windspeed Estimation and Baro Compensation (ArduCopter)](../../catalog/resources/ardupilot-copter-wind-estimation-docs.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [ArduPilot PR 33326: zero wind cross-covariances when treating wind as truth](../../catalog/resources/ardupilot-pr-33326-wind-truth-cross-covariance.md) (explains)

_Indexed by lane(s): innovation-pa-aero-adaptation_
