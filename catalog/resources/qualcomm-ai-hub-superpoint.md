# Qualcomm AI Hub: SuperPoint on-device performance

`res:qualcomm-ai-hub-superpoint` - report - <https://aihub.qualcomm.com/models/superpoint>

**By:** Qualcomm - **Year:** 2026 - **Level:** intro - **Access:** open

Qualcomm's measured latency for SuperPoint (the MIT-licensed rpautrat implementation, 640x480 input) per device, runtime and precision. Same data as perf.yaml in the ai-hub-models repo. Vendor numbers.

## Key takeaways

- QCS8550 (proxy), float, QNN: 16.13 ms; W8A8 TFLite: 20.207 ms (vendor)
- RB3 Gen 2 Vision Kit, W8A8 TFLite: 580.219 ms with 40 of 156 layers on CPU (vendor)
- No QRB5165 (RB5 / VOXL 2) entry
- Uses the license-clean SuperPoint, not the Magic Leap weights

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md)

**Tags:** `qualcomm`, `npu`, `superpoint`, `benchmark`, `vendor-claim`

## Related

- has_code: [Qualcomm AI Hub Models](../../catalog/repos/qualcomm__ai-hub-models.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
