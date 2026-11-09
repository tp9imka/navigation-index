# Reliable strategies for implementing model-based navigation on fixed-wing drones

`res:laupre-pirlet-skaloud-2023-reliable-vdm-navigation` - paper - <https://doi.org/10.1017/S0373463323000267>

**By:** Gabriel Laupre, Lucas Pirlet, Jan Skaloud - **Year:** 2023 - **Level:** advanced - **Access:** open

The Journal of Navigation, open access (CC BY). Makes a roughly 50-state VDM navigation filter numerically stable on real fixed-wing flights with UD factorisation plus partial Schmidt-Kalman updates. During initialisation, model-parameter states move gradually from considered to full states over a ramp; during a GNSS outage, all VDM parameter error states and position are placed in considered mode by a fixed rule. Validated on four real flights of one small fixed-wing drone.

## Key takeaways

- Phase-based freezing (consider all model parameters during GNSS outage) already exists and is tested on real flights
- With partial updates, horizontal errors were lower than with full updates in all compared 2-min outages but one (heading error case)
- Twelve 2-min outages: VDM max horizontal error more than 10x lower than inertial coasting in 3 cases, more than 5x in 3, 1.5-2.5x in 6
- 6-min outage: about 250 m max horizontal error for VDM vs about 4.5 km for inertial coasting
- Authors note that straight constant-velocity missions may not give enough observability to refine aerodynamic coefficients

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `vdm`, `fixed-wing`, `schmidt-kalman`, `consider-states`, `gnss-outage`, `real-flight`

## Related

- same_author: [Identifying Aerodynamics of Small Fixed-Wing Drones Using Inertial Measurements for Model-Based Navigation](../../catalog/resources/sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing.md)
- cites: [Assessment of VDM-based autonomous navigation of a UAV under operational conditions](../../catalog/resources/khaghani-skaloud-2018-vdm-navigation.md)
- cites: [Factorized Partial-Update Schmidt-Kalman Filter](../../catalog/resources/ramos-brink-2022-factorized-partial-update-skf.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Identifying Aerodynamics of Small Fixed-Wing Drones Using Inertial Measurements for Model-Based Navigation](../../catalog/resources/sharma-laupre-skaloud-2023-identifying-aerodynamics-fixed-wing.md) (same_author)

_Indexed by lane(s): innovation-pa-aero-adaptation_
