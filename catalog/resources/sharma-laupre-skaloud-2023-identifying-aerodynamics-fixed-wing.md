# Identifying Aerodynamics of Small Fixed-Wing Drones Using Inertial Measurements for Model-Based Navigation

`res:sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing` - paper - <https://navi.ion.org/content/70/4/navi.611>

**By:** Aman Sharma, Gabriel Francois Laupre, Jan Skaloud - **Year:** 2023 - **Level:** advanced - **Access:** open

NAVIGATION 70(4), open access. Calibrates the aerodynamic coefficients of a vehicle-dynamic-model (VDM) navigation filter from flight data with three decoupled estimators (wind, then moment, then force coefficients). Wind is estimated with a partial-update Schmidt-Kalman filter; a recursively built observability Gramian is tracked in its eigenbasis and only directions whose information increment exceeds a threshold are updated, the rest are kept as considered states. The calibration runs offline on smoothed PPK data; the identified parameters are then used in a VDM-EKF during simulated 2-min GNSS outages on two fixed-wing drones (21 and 44 parameters).

## Key takeaways

- Closest prior art for identifiability-gated parameter updates: observability-Gramian increment test plus Schmidt consider states
- Offline only: the paper states the algorithm in its current form cannot calibrate in real time
- Random initial parameters made the VDM filter diverge, so a calibration step before navigation is required
- No improvement over INS/GNSS with the high-grade STIM318 IMU over the tested outage lengths

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `vdm`, `fixed-wing`, `schmidt-kalman`, `observability-gramian`, `partial-update`, `aerodynamic-identification`, `wind`

## Related

- cites: [Assessment of VDM-based autonomous navigation of a UAV under operational conditions](../../catalog/resources/khaghani-skaloud-2018-vdm-navigation.md)
- same_author: [Reliable strategies for implementing model-based navigation on fixed-wing drones](../../catalog/resources/laupre-pirlet-skaloud-2023-reliable-vdm-navigation.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Reliable strategies for implementing model-based navigation on fixed-wing drones](../../catalog/resources/laupre-pirlet-skaloud-2023-reliable-vdm-navigation.md) (same_author)

_Indexed by lane(s): innovation-pa-aero-adaptation_
