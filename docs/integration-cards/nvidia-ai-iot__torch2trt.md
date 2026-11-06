# torch2trt - integration card
<!-- about: repo:nvidia-ai-iot/torch2trt -->
One-line: one call (`torch2trt(model, [x])`) turns a PyTorch module into a TensorRT engine wrapped as a `TRTModule`. Useful for a small custom network on a Jetson. It is largely unmaintained and tied to older TensorRT APIs, so try ONNX => `trtexec` first.

| | |
|---|---|
| Install | No PyPI package (`pypi.org/pypi/torch2trt/json` returns 404, checked 2026-11-06). From source: `git clone https://github.com/NVIDIA-AI-IOT/torch2trt && cd torch2trt && python setup.py install` (setup.py `version='0.5.0'`). Optional plugins library: `cmake -B build . && cmake --build build --target install && ldconfig`. `python setup.py install --plugins` builds the deprecated PyTorch-dependent plugins. Optional contrib (QAT): `scripts/build_contrib.sh`. Prebuilt on Jetson: the `torch2trt` package in [jetson-containers](./dusty-nv__jetson-containers.md) (`packages/ml/pytorch/torch2trt`, which clones master and applies a `flattener.py` patch). |
| Runs on | NVIDIA GPU with the TensorRT Python API. On Jetson that comes with JetPack. On desktop install TensorRT per the NVIDIA guide (README). CUDA PyTorch required. No CPU, no Apple Silicon. Repo `docker/` has 21-06, 21-08, 21-09 and `l4t-35.1.0` Dockerfiles, so it is dated. |
| Inputs | A `torch.nn.Module` in eval mode on CUDA plus a list of example CUDA tensors. Options in the `torch2trt()` signature (`torch2trt/torch2trt.py`): `fp16_mode`, `int8_mode` + `int8_calib_dataset`, `max_workspace_size`, `use_onnx`, `default_device_type` / `dla_core` / `gpu_fallback` (DLA on Xavier/Orin), `min_shapes` / `max_shapes` / `opt_shapes` (dynamic shapes), `input_names` / `output_names`, `onnx_opset`. |
| Outputs | `TRTModule` (a `torch.nn.Module`) that runs the engine on torch CUDA tensors. Save it with `torch.save(model_trt.state_dict(), 'x.pth')` and load it with `TRTModule().load_state_dict(torch.load('x.pth'))`. |
| Key API / entry points | `from torch2trt import torch2trt, TRTModule, tensorrt_converter`; `torch2trt(module, inputs, ...)`; `TRTModule`; `@tensorrt_converter('torch.nn.ReLU.forward')` to register a custom layer converter (the function receives a `ConversionContext` with `ctx.method_args`, `ctx.method_return`, `ctx.network`). Model benchmark script `test.sh`. |
| Time to first result | Estimate: 30 min inside a matching jetson-containers image for a torchvision classifier. Unknown for a modern detector: unsupported ops need hand-written converters or `use_onnx=True`. |
| License | **MIT** (LICENSE.md, NVIDIA 2019). TensorRT itself is under NVIDIA's proprietary licence. The models you convert keep their own licences: an engine built from AGPL [Ultralytics](./ultralytics__ultralytics.md) weights is still AGPL. |

## Minimal usage

Not run. From the README.

```python
import torch
from torch2trt import torch2trt, TRTModule
from torchvision.models import resnet18

model = resnet18(weights=None).eval().cuda()
x = torch.ones((1, 3, 224, 224)).cuda()
model_trt = torch2trt(model, [x], fp16_mode=True)
print(torch.max(torch.abs(model(x) - model_trt(x))))      # sanity check vs PyTorch
torch.save(model_trt.state_dict(), "resnet18_trt.pth")

m = TRTModule(); m.load_state_dict(torch.load("resnet18_trt.pth"))
```

## Wiring it into a nav stack

- Use it for small custom networks on the companion computer: a learned place-recognition encoder for [visual geolocalization](../../catalog/concepts/visual-geolocalization.md), a terrain-patch classifier, or a CNN feature extractor feeding a filter. The output stays a PyTorch-callable module, so the rest of a ROS 2 Python node is unchanged.
- Run it inside a [jetson-containers](./dusty-nv__jetson-containers.md) image so JetPack, TensorRT and torch versions agree.
- For feature matchers, [LightGlue ONNX](./fabio-sim__lightglue-onnx.md) already provides TensorRT paths. For detectors, export ONNX ([Ultralytics](./ultralytics__ultralytics.md) `format=engine`) or use [jetson-inference](./dusty-nv__jetson-inference.md).
- Engines are device- and version-specific. Build on the target Jetson, never on a desktop GPU.

Catalog page: [catalog/repos/nvidia-ai-iot__torch2trt.md](../../catalog/repos/nvidia-ai-iot__torch2trt.md). Concepts: [edge-ai](../../catalog/concepts/edge-ai.md).

## Gotchas

- Maintenance: last commit 2024-05-03, last push 2024-08-17 (GitHub metadata). The README warns the converter "has limited coverage of TensorRT / PyTorch" and was made mainly for JetBot.
- TensorRT 10 broke the old builder API: #920 (open, 2024: `INetworkDefinition` has no attribute `add_convolution`) and #557 (open: `Builder` has no attribute `max_workspace_size`). Current JetPack 6 images carry TensorRT 10.x (for example, Ultralytics issue #26655 reports TRT 10.3 on JetPack 6), so expect failures on current JetPack unless the jetson-containers patch covers your ops.
- Unconverted ops: #325 (open: `Tensor` has no attribute `_trt`) is the classic symptom of an op without a converter. Write a `@tensorrt_converter` or switch to `use_onnx=True`.
- Detector reports: #697 (open: YOLOX-S works, tiny/nano do not), #428 (open: demo fails on Jetson Nano), #669 (open: README example errors).
- The default `max_workspace_size=1<<25` (32 MB) is small for big models. Raise it if the build fails or picks slow tactics.

## Alternatives

- ONNX export + `trtexec` / TensorRT Python API (not indexed) - the maintained path. Prefer it for anything beyond a toy network.
- [jetson-inference](./dusty-nv__jetson-inference.md) - ready TensorRT pipelines for detection, segmentation and depth with camera I/O.
- Torch-TensorRT (`packages/ml/pytorch/torch_tensorrt` in [jetson-containers](./dusty-nv__jetson-containers.md), not indexed) - NVIDIA's maintained PyTorch => TensorRT compiler.

Sources: `gh api repos/nvidia-ai-iot/torch2trt` (MIT, pushed 2024-08-17), commits (latest 2024-05-03), LICENSE.md, README.md, setup.py, `torch2trt/__init__.py`, `torch2trt/torch2trt.py` (`torch2trt()` signature), `docker/` listing, PyPI JSON (404), jetson-containers `packages/ml/pytorch/torch2trt/{Dockerfile,install.sh}`, issues #920, #557, #325, #697, #428, #669.
