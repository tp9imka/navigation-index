# A Nonlinear Model-Based Wind Velocity Observer for Unmanned Aerial Vehicles

`res:borup-fossen-johansen-2016-wind-velocity-observer` - paper - <https://torarnj.folk.ntnu.no/NOLCOS16_final_submission.pdf>

**By:** Kasper T. Borup, Thor I. Fossen, Tor A. Johansen - **Year:** 2016 - **Level:** advanced - **Access:** open

NOLCOS 2016 (author PDF read). An exponentially stable nonlinear wind observer for fixed-wing UAVs combining an aircraft model with a GNSS-aided INS; also estimates the pitot scale factor. The model-free predecessor needs persistently exciting yaw and pitch motion; this observer removes the PE requirement by relying on an aerodynamic model.

## Key takeaways

- States the trade explicitly: model-free wind and pitot-scale estimation needs persistent excitation, model-based does not
- Requires GNSS-aided INS; not a GNSS-denied method

**Concepts:** [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `wind-estimation`, `airspeed-scale`, `persistent-excitation`, `fixed-wing`, `nonlinear-observer`

## Related

- same_author: [Moving Horizon Estimation of Air Data Parameters for UAVs](../../catalog/resources/wenz-johansen-2019-mhe-air-data.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Moving Horizon Estimation of Air Data Parameters for UAVs](../../catalog/resources/wenz-johansen-2019-mhe-air-data.md) (same_author)

_Indexed by lane(s): innovation-pa-aero-adaptation_
