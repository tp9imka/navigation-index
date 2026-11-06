# jetson-containers - integration card
<!-- about: repo:dusty-nv/jetson-containers -->
One-line: prebuilt and buildable Docker images for NVIDIA Jetson (PyTorch, TensorRT tooling, OpenCV with CUDA, ROS 1/2, DeepStream, VLMs) matched to your JetPack/L4T version. It saves the day you would otherwise lose compiling CUDA wheels on the device.

| | |
|---|---|
| Install | On the Jetson: `git clone https://github.com/dusty-nv/jetson-containers && bash jetson-containers/install.sh` (README). The script runs `pip3 install -r requirements.txt` with the host pip (installing `python3-pip` through apt if missing) and symlinks `autotag` and `jetson-containers` into `/usr/local/bin` (install.sh). Optional `sudo bash jetson-containers/install.sh --pypi` adds a local devpi + APT cache. You can skip the tools entirely: `sudo docker run --runtime nvidia -it --rm --network=host dustynv/l4t-pytorch:r36.2.0` (README). No PyPI package. |
| Runs on | NVIDIA Jetson with Docker and the NVIDIA container runtime. The README says only JetPack 6.2 (CUDA 12.6) and JetPack 7 (CUDA 13.x) are "tested and supported". Ubuntu 24.04 containers exist for JP6/JP7. ARM SBSA (GH200/GB200) is also supported. The older stack is on the `legacy` branch. Builds happen on the device and need a lot of disk (see Gotchas). |
| Inputs | Package names to build or run (`pytorch`, `ros:humble-desktop`, `torch2trt`, `opencv`, `onnxruntime`, `deepstream`, `isaac-ros`...), `CUDA_VERSION`, `LSB_RELEASE` and `ROS_DISTRO` environment variables, host directories mounted into `/data`. |
| Outputs | Local Docker images (or images pulled from `dustynv/*` on Docker Hub). `jetson-containers run` wraps `docker run` with `--runtime nvidia`, a `/data` cache mount, display/audio and V4L2/CSI camera devices (docs/run.md). |
| Key API / entry points | `jetson-containers build --name=<img> <pkg> [<pkg>...]` (combine packages, e.g. `pytorch transformers ros:humble-desktop`), `jetson-containers run [docker args] <image> [cmd]`, `autotag <pkg>` (finds an image compatible with your L4T locally, in the registry, or by building it), `CUDA_VERSION=12.6 jetson-containers build <pkg>`. ROS distros in `packages/physicalAI/ros/version.py`: ROS 1 `melodic`, `noetic`; ROS 2 `foxy`, `galactic`, `humble`, `iron`, `jazzy`, with the default picked from `LSB_RELEASE` (24.04 => jazzy, 22.04 => humble). |
| Time to first result | Estimate: 30-60 min to a running `l4t-pytorch` container on a flashed Orin with a supported JetPack (mostly pull time). Building a combined image such as PyTorch + ROS 2 + OpenCV-CUDA from source can take several hours on-device if the wheels are not cached. Check the pip server first. |
| License | Repo code: **MIT** (LICENSE.md, NVIDIA 2026). GitHub metadata says NOASSERTION. The **images bundle third-party software under its own licences**, including NVIDIA's proprietary JetPack/CUDA/TensorRT components (NVIDIA EULAs) and whatever each package pulls (some AGPL/GPL, model weights with their own terms). The MIT licence covers the build scripts only. |

## Minimal usage

Not run. From the README "Getting Started" and docs/run.md.

```bash
git clone https://github.com/dusty-nv/jetson-containers
bash jetson-containers/install.sh
jetson-containers run $(autotag l4t-pytorch)                          # interactive, GPU, /data mounted
jetson-containers run --volume $PWD:/ws $(autotag pytorch) python3 /ws/infer.py
jetson-containers build --name=navperc pytorch opencv ros:humble-desktop
```

## Wiring it into a nav stack

- Onboard perception box: one image with PyTorch + TensorRT + OpenCV-CUDA + ROS 2 Humble. Run the detector ([Ultralytics](./ultralytics__ultralytics.md) export, [jetson-inference](./dusty-nv__jetson-inference.md), [torch2trt](./nvidia-ai-iot__torch2trt.md)) and VIO/feature matching ([LightGlue ONNX](./fabio-sim__lightglue-onnx.md)) there, and publish ROS topics to the autopilot bridge ([MAVROS](./mavlink__mavros.md), [px4_ros_com](./px4__px4_ros_com.md), [micro-XRCE-DDS agent](./eprosima__micro-xrce-dds-agent.md)).
- Use `--network=host` (the default in the README examples) so DDS discovery and MAVLink UDP work across containers on the same Jetson.
- Bake the final image the evening before and `docker save` it. A venue network that blocks Docker Hub or the jetson-ai-lab pip index will stop a rebuild.

Catalog page: [catalog/repos/dusty-nv__jetson-containers.md](../../catalog/repos/dusty-nv__jetson-containers.md). Concepts: [edge-ai](../../catalog/concepts/edge-ai.md), [ros](../../catalog/concepts/ros.md).

## Gotchas

- JetPack must match. `autotag` looks for an L4T-compatible tag, and mismatches show up as "CUDA not available" inside the container (#1495, open: building pytorch gives cuda not available) or broken torchvision (#1387, open: torchvision fails on L4T 36.3.0). Anything older than JetPack 6.2 is outside the stated support. Use the `legacy` branch or the older `dustynv/*:r35.x` tags at your own risk.
- Orin Nano: limited RAM and storage. Open issues include #1330 (gemma_vlm does not compile on Orin Nano), #1558 (Whisper build fails on Orin Nano JP 6.2.1) and #1316 (`ros:humble-desktop` build fails on Orin Nano Super looking for an RTI Connext package). Move Docker's data root to NVMe and add swap per docs/setup.md before building.
- `install.sh` runs host `pip3 install` and `sudo ln` into `/usr/local/bin`. That changes the host Python, so run it only on a dedicated Jetson.
- Builds pull wheels from `pypi.jetson-ai-lab.io` (README status badge). If that index is down, builds fall back to compiling from source.
- The README troubleshooting section lists `InvalidDefaultArgInFrom ... BASE_IMAGE` from corrupted Docker caches. The fix is `docker image prune` / `docker buildx prune`.

## Alternatives

- [jetson-inference](./dusty-nv__jetson-inference.md) - its own `docker/run.sh` container when you only need TensorRT detection/segmentation, not a custom stack.
- Ultralytics JetPack images (`docker/Dockerfile-jetson-jetpack6` in [Ultralytics](./ultralytics__ultralytics.md)) - quicker if YOLO is the only workload and AGPL is acceptable.
- NVIDIA NGC L4T base images (not indexed) - minimal and official, but you build PyTorch/ROS on top yourself.

Sources: `gh api repos/dusty-nv/jetson-containers` (NOASSERTION, default branch master, pushed 2026-11-02), LICENSE.md, README.md, install.sh, docs/run.md, `packages/physicalAI/ros/version.py`, repo tree (packages list incl. `packages/ml/pytorch/torch2trt`, `packages/cv/deepstream`, `packages/physicalAI/isaac-ros`), issues #1495, #1387, #1330, #1558, #1316.
