# LightGlue-ONNX

`repo:fabio-sim/lightglue-onnx` - <https://github.com/fabio-sim/LightGlue-ONNX>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 822 | Python | Apache-2.0 | 2026-07-30 | False | production | high |

ONNX export and inference of LightGlue matching with SuperPoint, DISK and ALIKED extractors (including RaCo-ALIKED-LightGlue+), with TensorRT, OpenVINO and FP8 quantization workflows.

**Why it matters:** Fast learned matching on embedded hardware for visual geolocalization and VO.

**Hackathon notes:** Download prebuilt ONNX models from Releases and run with onnxruntime-gpu or TensorRT; for export, the repo now uses uv (uv sync with export/cuda/trt groups) and a lightglue-onnx CLI.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [fabio-sim__lightglue-onnx](../../docs/integration-cards/fabio-sim__lightglue-onnx.md) (integration-cards)

**Concepts:** [Onboard / edge AI perception](../concepts/edge-ai.md), [Feature detection and matching](../concepts/feature-matching.md), [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md)

**Tags:** `lightglue`, `onnx`, `tensorrt`, `openvino`

**Domains:** air, ground

## Related

- extends: [LightGlue](../repos/cvg__lightglue.md)

## Referenced by

- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../resources/honeywell-vision-aided-navigation.md) (alternative_to)
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../resources/inertial-labs-vins.md) (alternative_to)
- [Theseus Visual Navigation System (YC launch)](../resources/theseus-visual-navigation-system.md) (alternative_to)
- [Twist Robotics OSCAR visual navigation module (Ukraine)](../resources/twist-robotics-oscar.md) (alternative_to)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
