# NeuroBEM quadrotor flight dataset

`res:neurobem-dataset` - dataset - <https://download.ifi.uzh.ch/rpg/NeuroBEM/>

**By:** UZH Robotics and Perception Group - **Year:** 2021 - **Level:** intermediate - **Access:** open

About 1 h 15 min of agile quadrotor flights in a Vicon hangar at 400 Hz: filtered linear and angular accelerations, body rates, per-motor speeds and their derivatives, battery voltage, and model-predicted forces. processed_data.zip is 657 MB, raw_data.zip 455 MB (HTTP Content-Length, 2026-11-09).

## Key takeaways

- Real motor speeds and mocap truth, the input set a drag/thrust virtual sensor needs
- Processed accelerations are fused with Vicon, so use raw_data for an honest IMU-only test
- No license stated on the page or Readme; ask before commercial reuse

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `dataset`, `rotor-speed`, `mocap`, `aerodynamics`

## Related

- part_of: [NeuroBEM: Hybrid Aerodynamic Quadrotor Model](../../catalog/resources/bauersfeld-2021-neurobem.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [NeuroBEM: Hybrid Aerodynamic Quadrotor Model](../../catalog/resources/bauersfeld-2021-neurobem.md) (uses)

_Indexed by lane(s): nav-differentiators_
