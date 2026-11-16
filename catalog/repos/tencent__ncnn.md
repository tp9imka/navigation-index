# ncnn

`repo:tencent/ncnn` - <https://github.com/Tencent/ncnn>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 24,053 | C++ | NOASSERTION | 2026-11-16 | False | production | medium |

Dependency-free C++ inference engine tuned for ARM CPUs (NEON) with optional Vulkan GPU. Its benchmark/README.md lists per-board latency for a fixed model set, including Raspberry Pi 5 and Jetson AGX Orin.

**Why it matters:** The practical CPU-only inference path on a Raspberry Pi 5 or other ARM companion, and a published per-board baseline to compare against.

**Build notes:** BSD-3 for ncnn itself, with third-party components under their own terms (LICENSE.txt). Run `benchncnn` on your board to reproduce the README numbers before porting your own model via pnnx.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `inference`, `arm`, `neon`, `vulkan`, `raspberry-pi`, `benchmark`

**Domains:** multi

## Related

- alternative_to: [Qualcomm AI Hub Models](../../catalog/repos/qualcomm__ai-hub-models.md)
- alternative_to: [Hailo Raspberry Pi 5 examples](../../catalog/repos/hailo-ai__hailo-rpi5-examples.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Qualcomm AI Hub Models](../../catalog/repos/qualcomm__ai-hub-models.md) (alternative_to)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
