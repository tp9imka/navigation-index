# Airspeed estimation for UAVs using only propeller feedback

`res:ntouros-2025-airspeed-propeller-feedback` - paper - <https://arxiv.org/abs/2507.03456>

**By:** Evangelos Ntouros, Pavel Kelley, Ewoud Smeur - **Year:** 2025 - **Level:** intermediate - **Access:** open

arXiv preprint, later in Aerospace Science and Technology per TU Delft listing (abstract read). Estimates fixed-wing airspeed from ESC-reported propeller power and rotational speed with a regularised analytical model; parameters are identified offline from logs with airspeed, or in flight from GPS velocity alone. Reports 5% normalised RMSE on unseen flight data.

## Key takeaways

- Propulsion telemetry as an airspeed sensor, the fixed-wing twin of rotor-drag velocity sensing
- In-flight identification from GPS velocity alone meets the same wind-vs-scale confounding this idea targets (not discussed in the abstract)

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `airspeed`, `propeller`, `esc-telemetry`, `fixed-wing`

_Indexed by lane(s): innovation-pa-aero-adaptation_
