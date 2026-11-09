# NeuroBEM: Hybrid Aerodynamic Quadrotor Model

`res:bauersfeld-2021-neurobem` - paper - <https://rpg.ifi.uzh.ch/NeuroBEM.html>

**By:** Leonard Bauersfeld, Elia Kaufmann, Philipp Foehn, Sihao Sun, Davide Scaramuzza - **Year:** 2021 - **Level:** advanced - **Access:** open

RSS 2021. Combines blade-element-momentum theory with a learned residual to model quadrotor forces and torques at speeds up to 65 km/h, and releases the mocap flight data used to fit it.

## Key takeaways

- First-principles rotor model plus a small learned residual
- Data includes per-motor speed at 400 Hz
- Basis for the dynamics model in HDVIO

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `blade-element-momentum`, `aerodynamics`, `quadrotor`, `rss-2021`

## Related

- uses: [NeuroBEM quadrotor flight dataset](../../catalog/resources/neurobem-dataset.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [HDVIO: Improving Localization and Disturbance Estimation with Hybrid Dynamics VIO](../../catalog/resources/cioffi-2023-hdvio-hybrid-dynamics-vio.md) (uses)
- [HDVIO2.0: Wind and Disturbance Estimation with Hybrid Dynamics VIO](../../catalog/resources/cioffi-2025-hdvio2-wind-disturbance.md) (uses)
- [NeuroBEM quadrotor flight dataset](../../catalog/resources/neurobem-dataset.md) (part_of)

_Indexed by lane(s): nav-differentiators_
