# PX4 EKF2 drag fusion, wind process noise and IMU bias inhibit (source, v1.16.0)

`res:px4-ekf2-drag-wind-source-v1-16` - doc - <https://github.com/PX4/PX4-Autopilot/blob/v1.16.0/src/modules/ekf2/EKF/aid_sources/drag/drag_fusion.cpp>

**By:** PX4 Dev Team - **Year:** 2025 - **Level:** advanced - **Access:** open

Source read at v1.16.0 (drag_fusion.cpp differs at v1.17.0 only in parameter names). Ekf::fuseDrag applies the full gain K = P H / S to all states behind a 5-sigma innovation gate, with fixed EKF2_BCOEF_X/Y and EKF2_MCOEF. Wind gains are zeroed only when the wind flag is off; predictCovariance keeps adding wind process noise up to the initial-uncertainty cap. updateIMUBiasInhibit inhibits accel-bias learning on heuristics (high manoeuvre level, clipping, fake position axis alignment) and leaves gyro conditions as a TODO. The offline mc_wind_estimator_tuning.py fits the coefficients and its readme says it assumes no wind.

## Key takeaways

- No measured-identifiability gate on wind or drag coefficients; coefficients fixed, wind keeps random-walking during drag-only flight
- Heuristic excitation gating exists for accel bias only
- Offline coefficient fit assumes still air

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `ekf2`, `drag-fusion`, `wind`, `bias-inhibit`, `source-code`

## Related

- part_of: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- explains: [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)

_Indexed by lane(s): innovation-pa-aero-adaptation_
