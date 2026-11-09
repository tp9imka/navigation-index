# Assessment of VDM-based autonomous navigation of a UAV under operational conditions

`res:khaghani-skaloud-2018-vdm-navigation` - paper - <https://infoscience.epfl.ch/record/255356>

**By:** Mehran Khaghani, Jan Skaloud - **Year:** 2018 - **Level:** advanced - **Access:** open

Robotics and Autonomous Systems 106 (2018). Replaces the INS process model with a fixed-wing vehicle dynamic model (VDM) and treats IMU, barometer and GNSS as observations, tested on a real small fixed-wing flight and in Monte Carlo simulation.

## Key takeaways

- Abstract: roughly one to two orders of magnitude better accuracy over 3-minute GNSS outages vs INS-based integration
- No extra hardware needed: the model is the added sensor
- No public code or flight data found

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `vehicle-dynamic-model`, `fixed-wing`, `gnss-outage`, `epfl`

## Related

- same_author: [Fixed-Wing Micro UAV Open Data With Digicam And Raw INS/GNSS - IGN Flight 8](../../catalog/resources/skaloud-2021-ign-flight8-fixed-wing-data.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Autonomous Navigation of Small UAVs Based on Vehicle Dynamic Model](../../catalog/resources/khaghani-skaloud-2016-vdm-navigation-small-uavs-eurocow.md) (same_author)
- [Reliable strategies for implementing model-based navigation on fixed-wing drones](../../catalog/resources/laupre-pirlet-skaloud-2023-reliable-vdm-navigation.md) (cites)
- [Error characteristics of a model-based integration approach for fixed-wing unmanned aerial vehicles](../../catalog/resources/mwenegoha-2021-vdm-error-characteristics-fixed-wing.md) (cites)
- [Identifying Aerodynamics of Small Fixed-Wing Drones Using Inertial Measurements for Model-Based Navigation](../../catalog/resources/sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing.md) (cites)
- [Fixed-Wing Micro UAV Open Data With Digicam And Raw INS/GNSS - IGN Flight 8](../../catalog/resources/skaloud-2021-ign-flight8-fixed-wing-data.md) (same_author)
- [Semi-Aerodynamic Model Aided Invariant Kalman Filtering for UAV Full-State Estimation](../../catalog/resources/ye-2023-semi-aerodynamic-model-aided-iekf.md) (cites)

_Indexed by lane(s): nav-differentiators_
