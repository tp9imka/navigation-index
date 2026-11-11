# Qualcomm AI Hub Models

`repo:qualcomm/ai-hub-models` - <https://github.com/qualcomm/ai-hub-models>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,258 | Python | BSD-3-Clause | 2026-11-07 | False | production | medium |

Collection of models exported for Qualcomm devices, each with a perf.yaml of measured on-device latency and memory per runtime (TFLite, QNN, ONNX) and precision. Includes SuperPoint (the MIT rpautrat version), ResNet, depth models and more.

**Why it matters:** Published per-device latency for nav-relevant networks on Qualcomm silicon, including the RB3 Gen 2 robotics kit. It is the cheapest source of a cited NPU number.

**Build notes:** Read src/qai_hub_models/models/<model>/perf.yaml for numbers. No QRB5165 (RB5 / VOXL 2) entry as of 2026-11-09; the closest robotics board is the RB3 Gen 2 Vision Kit. Profiling on hosted devices needs a free Qualcomm account.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md)

**Tags:** `qualcomm`, `npu`, `benchmark`, `superpoint`, `tflite`, `qnn`

**Domains:** multi

## Related

- same_org: [AIMET (AI Model Efficiency Toolkit)](../../catalog/repos/qualcomm__aimet.md)
- alternative_to: [ncnn](../../catalog/repos/tencent__ncnn.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [AIMET (AI Model Efficiency Toolkit)](../../catalog/repos/qualcomm__aimet.md) (same_org)
- [ncnn](../../catalog/repos/tencent__ncnn.md) (alternative_to)
- [Qualcomm AI Hub: SuperPoint on-device performance](../../catalog/resources/qualcomm-ai-hub-superpoint.md) (has_code)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-09._
