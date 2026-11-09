# HDVIO: Improving Localization and Disturbance Estimation with Hybrid Dynamics VIO

`res:cioffi-2023-hdvio-hybrid-dynamics-vio` - paper - <https://arxiv.org/abs/2306.11429>

**By:** Giovanni Cioffi, Leonard Bauersfeld, Davide Scaramuzza - **Year:** 2023 - **Level:** advanced - **Access:** open

RSS 2023 (arXiv read in part). Adds a hybrid point-mass plus learned aerodynamic model, driven by thrust and IMU history, as preintegrated dynamics residuals in an optimisation-based VIO; the gap between predicted and actual motion becomes an external-force estimate. Evaluated on Blackbird, VID and NeuroBEM and in a known wind field.

## Key takeaways

- Reports up to 33% better motion and 40% better external-force estimates than the compared methods
- Requires vision; disturbance is a residual force, not an identified drag coefficient

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `hybrid-dynamics`, `external-force`, `rotor-thrust`, `wind`

## Related

- same_author: [HDVIO2.0: Wind and Disturbance Estimation with Hybrid Dynamics VIO](../../catalog/resources/cioffi-2025-hdvio2-wind-disturbance.md)
- uses: [NeuroBEM: Hybrid Aerodynamic Quadrotor Model](../../catalog/resources/bauersfeld-2021-neurobem.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
