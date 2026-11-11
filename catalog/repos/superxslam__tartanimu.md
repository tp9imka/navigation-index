# TartanIMU

`repo:superxslam/tartanimu` - <https://github.com/superxslam/TartanIMU>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 158 | Python | Apache-2.0 | 2026-09-12 | False | active-research | medium |

ResNet-LSTM inertial model pretrained on more than 100 hours of car, quadruped, drone and human data that predicts body-frame velocity from 6-axis IMU, with LoRA adaptation heads, pretrained weights on Hugging Face and an IROS 2026 challenge starter kit.

**Why it matters:** The first public IMU foundation model (CVPR 2025): a team can fine-tune on its own airframe instead of training from scratch.

**Build notes:** Apache-2.0 code; weights license on Hugging Face not checked. The README says the public release has the LSTM model only (the Transformer core is not included). pip install -e . then run inference on a CSV of IMU samples.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `imu-foundation-model`, `learned-inertial-odometry`, `lora`, `pytorch`

**Domains:** multi

## Related

- alternative_to: [AirIO](../../catalog/repos/air-io__air-io.md)
- alternative_to: [TLIO](../../catalog/repos/cathias__tlio.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [Tartan IMU: A Light Foundation Model for Inertial Positioning in Robotics](../../catalog/resources/zhao-2025-tartan-imu-foundation-model.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
