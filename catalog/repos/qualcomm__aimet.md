# AIMET (AI Model Efficiency Toolkit)

`repo:qualcomm/aimet` - <https://github.com/qualcomm/aimet>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2,748 | Python | NOASSERTION | 2026-11-21 | False | production | low |

Qualcomm's quantization and compression library for PyTorch and ONNX models: post-training quantization, quantization-aware training and accuracy debugging, aimed at INT8 deployment on Snapdragon NPUs.

**Why it matters:** Qualcomm flight boards (RB5, VOXL 2) need INT8 models for the NPU. AIMET is the vendor path to get there without large accuracy loss.

**Build notes:** Repo moved from quic/aimet to qualcomm/aimet. License file is BSD-3-style (GitHub reports NOASSERTION). Only worth the setup if the team has a Qualcomm board in hand.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `quantization`, `int8`, `qualcomm`, `npu`, `pytorch`

**Domains:** multi

## Related

- same_org: [Qualcomm AI Hub Models](../../catalog/repos/qualcomm__ai-hub-models.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Qualcomm AI Hub Models](../../catalog/repos/qualcomm__ai-hub-models.md) (same_org)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-23._
