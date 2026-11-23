# TensorRT (open-source components)

`repo:nvidia/tensorrt` - <https://github.com/NVIDIA/TensorRT>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 13,479 | C++ | Apache-2.0 | 2026-11-18 | False | production | high |

Open parts of NVIDIA's inference SDK: parsers, plugins, samples and the trtexec / Polygraphy tools for building and profiling engines from ONNX.

**Why it matters:** On a Jetson this is how a matcher or VPR backbone gets from 'works in PyTorch' to a fixed, measurable latency. trtexec timings are the numbers to quote.

**Build notes:** JetPack already ships TensorRT; this repo is for samples and Polygraphy. Export ONNX, run `trtexec --onnx=model.onnx --fp16`, record mean and p99 latency. Engines are tied to the GPU and TensorRT version: rebuild on the target.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `tensorrt`, `jetson`, `onnx`, `int8`, `fp16`, `trtexec`

**Domains:** multi

## Related

- alternative_to: [torch2trt](../../catalog/repos/nvidia-ai-iot__torch2trt.md)
- integrates_with: [LightGlue-ONNX](../../catalog/repos/fabio-sim__lightglue-onnx.md)
- integrates_with: [Jetson Benchmarks](../../catalog/repos/nvidia-ai-iot__jetson_benchmarks.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Jetson Benchmarks](../../catalog/repos/nvidia-ai-iot__jetson_benchmarks.md) (depends_on)
- [jetson-stats (jtop)](../../catalog/repos/rbonghi__jetson_stats.md) (integrates_with)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-23._
