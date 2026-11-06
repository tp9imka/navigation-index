# LightGlue-ONNX - integration card
<!-- about: repo:fabio-sim/lightglue-onnx -->
One-line: exports extractor + LightGlue as one ONNX graph and runs it on ONNX Runtime (CPU, CUDA, TensorRT, OpenVINO) or pure TensorRT - the deployment path for LightGlue on Jetson-class or x86 GPU hardware without PyTorch at runtime.

| | |
|---|---|
| Install | `git clone https://github.com/fabio-sim/LightGlue-ONNX && cd LightGlue-ONNX`, then (README, uv): inference only `uv sync`; CPU export `uv sync --group export --extra torch-cpu`; CUDA export+inference `uv sync --no-group cpu --group cuda --group export --extra torch-cuda`; TensorRT CLI add `--group trt`. Prebuilt models: GitHub release `v3.0` (2026-07-19) ships `raco_aliked_lightglue_pipeline_k{512..3584}.onnx`; `v2.0` (2024-07-17) ships `superpoint_lightglue_pipeline*.onnx` and `disk_lightglue_pipeline*.onnx` (incl. `.trt.onnx`, `.fp8.onnx`). `pyproject.toml`: version 3.0.0, `requires-python = ">=3.12,<3.15"`, pins `onnxruntime==1.27.0`, `torch==2.13.0`, `tensorrt-cu13==10.16.1.11`. |
| Runs on | Inference via ONNX Runtime on any OS for CPU. CUDA, TensorRT and GPU-preprocess dependency groups are marked `platform_system == 'Linux' and platform_machine == 'x86_64'` in `pyproject.toml`, so the uv groups do not cover Jetson (aarch64) - there you would use JetPack's own TensorRT/onnxruntime with the exported `.onnx` (not verified here). Devices in source (`config.py` `InferenceDevice`): `cpu`, `cuda`, `tensorrt`, `openvino`. README: "By default, inference uses CUDA when available and falls back to CPU". Browser WebGPU demo: `uv run python web/serve.py`. |
| Inputs | Image pair (file paths on the CLI), resized to `-h/-w` given at export or inference; image dims must suit the extractor (`input_dim_divisor`: superpoint 8, disk 16, raco_aliked 32, from `config.py`). Export can mark batch/height/width dynamic by setting them to 0. Fixed `--num-keypoints` per exported model. |
| Outputs | ONNX graph outputs keypoints and matches for the pair (end-to-end pipeline); CLI `infer`/`trtexec` write a match visualization (`-o`) and can `--profile`. |
| Key API / entry points | CLI `lightglue-onnx` (`lightglue_dynamo.cli:main`, typer): `export EXTRACTOR [-o PATH] [-b] [-h] [-w] [--num-keypoints N] [--opset 16..20] [--fp16]`; `infer MODEL IMG0 IMG1 EXTRACTOR [-h] [-w] [-d cpu|cuda|tensorrt|openvino] [--fp16] [--preprocessing opencv|cuda]`; `trtexec MODEL_OR_ENGINE IMG0 IMG1 EXTRACTOR [--fp16] [--precision-constraints none|prefer|obey]`. `EXTRACTOR` in source: `superpoint` (default), `disk`, `raco_aliked`. FP8: `lightglue_dynamo/scripts/quantize.py`. Kornia also wraps these models as `kornia.feature.OnnxLightGlue` (README changelog). |
| Time to first result | Estimate: 15-30 min on Linux x86-64 with CPU or a CUDA GPU using a prebuilt release model and `uv run lightglue-onnx infer`. 1-3 h for a first TensorRT engine on Jetson (JetPack version matching, engine build), assuming JetPack TensorRT is recent enough. |
| License | Repo code: Apache-2.0 (GitHub metadata, `pyproject.toml`). Exported models embed the extractor weights, so the extractor's license follows the `.onnx`: `lightglue_dynamo/models/superpoint.py` carries the Magic Leap "CONFIDENTIAL" header and downloads `superpoint_v1.pth` (non-commercial research license, SuperPointPretrainedNetwork LICENSE). `raco_aliked` pulls `cvg/RaCo` `raco.pth` (cvg/RaCo GitHub metadata: Apache-2.0) and ALIKED `aliked-n16.pth` (Shiaoming/ALIKED: BSD-3-Clause). DISK: Apache-2.0 per cvg/LightGlue README. |

## Minimal usage
Not run. Adapted from README example commands; uses the v3.0 prebuilt RaCo-ALIKED model (cleanest license of the three extractors).

```shell
git clone https://github.com/fabio-sim/LightGlue-ONNX && cd LightGlue-ONNX
uv sync                                   # CPU onnxruntime
mkdir -p weights && gh release download v3.0 -R fabio-sim/LightGlue-ONNX \
  -p 'raco_aliked_lightglue_pipeline_k1024.onnx' -D weights
uv run lightglue-onnx infer weights/raco_aliked_lightglue_pipeline_k1024.onnx \
  drone_frame.jpg map_tile.jpg raco_aliked -h 1024 -w 1024 -d cpu -o matches.png
```

## Wiring it into a nav stack
- Same role as [LightGlue](./cvg__lightglue.md) (frame-to-tile matching => homography => lat/lon), but as a deployable artifact: export once on a workstation, copy the `.onnx` to the vehicle computer, build a TensorRT engine there, call it from a ROS 2 node or plain Python with onnxruntime.
- On NVIDIA Jetson inside ROS 2, the generic ONNX/TensorRT inference nodes in [isaac_ros_dnn_inference](../../catalog/repos/nvidia-isaac-ros__isaac_ros_dnn_inference.md) are a possible host; no integration exists in either repo, so expect glue code for pre/post-processing.
- Pair with [XFeat](./verlab__accelerated_features.md) as a CPU fallback on boards without a usable GPU, and with retrieval ([AnyLoc](./anyloc__anyloc.md), [MixVPR](../../catalog/repos/amaralibey__mixvpr.md)) upstream.
- Output to the autopilot as for any vision fix: [MAVROS](../../catalog/repos/mavlink__mavros.md) / [non-GPS MAVLink position](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md), after inlier gating.

## Gotchas
- License follows the weights inside the ONNX: the default `export`/`infer` extractor is `superpoint`, and the older release assets are SuperPoint-based. Maintainer (issue #24): the repo "inherits the original repository's license (Apache License, Version 2.0)" and defers the SuperPoint question to LightGlue; LightGlue's own maintainer says Apache does not cover `superpoint_v1.pth` (cvg/LightGlue issue #38). Prefer `raco_aliked` or `disk`.
- No "open SuperPoint" shortcut: SuperPoint-Open features fed to the SuperPoint-trained LightGlue gave zero matches (issue #39).
- Jetson history: issue #50 reports 19 s for `infer.py` on a Jetson AGX via onnxruntime; maintainer: TensorRT through ONNX Runtime "has some problems", use pure TensorRT (`trtexec`, TensorRT Python) instead. Issue #53: JetPack 6.0 brings TensorRT 8.6. The current pins target TensorRT 10.16 / CUDA 13 on x86-64; compatibility of new exports with older JetPack TensorRT is not stated.
- TensorRT conversion errors are a recurring theme (closed issues #65, #66 "Internal Error (/lightglue/ArgMax)", #78, #98, #106). Use the provided `.trt.onnx` variants or the `trtexec` command path rather than hand-rolled conversion.
- `--num-keypoints` and (optionally) image size are baked in at export; mismatched `-h/-w` at inference or non-divisible sizes break things. Export several keypoint budgets (the v3.0 release does k512..k3584) and pick per platform.
- Python >=3.12 required by `pyproject.toml`; older JetPack Python versions will need a separate env or a container.
- The v3.0 speedup plots link to a blog post whose URL says an LLM ("gpt-5-6-sol") discovered the TensorRT optimizations; treat them as the author's measurements, not independently reproduced.

## Alternatives
- [LightGlue](./cvg__lightglue.md) in PyTorch with `matcher.compile()` - simpler when PyTorch is available on the target.
- [XFeat](./verlab__accelerated_features.md) - CPU-real-time, no export step needed, lower accuracy.
- [AirSLAM](../../catalog/repos/sair-lab__airslam.md) - already ships a TensorRT point-line front end inside a SLAM system, if you want VO rather than map registration.

Sources: fabio-sim/LightGlue-ONNX README.md, pyproject.toml, lightglue_dynamo/cli.py, lightglue_dynamo/config.py, lightglue_dynamo/models/superpoint.py, lightglue_dynamo/models/raco.py, lightglue_dynamo/models/aliked.py, directory listings; releases (v0.1.3, v1.0.0, v2.0, v3.0); issues #24, #39, #50, #53 (plus search hits #65, #66, #78, #98, #106); cvg/LightGlue issue #38; GitHub metadata for fabio-sim/LightGlue-ONNX, cvg/RaCo, Shiaoming/ALIKED via `gh api` (2026-11-06).
