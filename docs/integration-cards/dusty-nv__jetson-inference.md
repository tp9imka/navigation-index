# jetson-inference (Hello AI World) - integration card
<!-- about: repo:dusty-nv/jetson-inference -->
One-line: TensorRT detection / segmentation / mono-depth on a Jetson camera stream in an afternoon, from Python or C++, with ROS nodes next door; good for onboard situational awareness and for the "perception box" of a demo stack.

| | |
|---|---|
| Install | Container (recommended): `git clone --recursive --depth=1 https://github.com/dusty-nv/jetson-inference && cd jetson-inference && docker/run.sh` (auto-picks `dustynv/jetson-inference:<L4T tag>`; listed tags r32.4.3 ... r36.3.0 = JetPack 4.4 ... 6.0 GA). ROS variant: `docker/run.sh --ros=humble` (noetic, foxy, galactic, humble, iron). Source: `git submodule update --init`, `sudo apt-get install git cmake libpython3-dev python3-numpy`, `mkdir build && cd build && cmake ../ && make && sudo make install && sudo ldconfig` (docs/building-repo-2.md). No pip package, no releases. |
| Runs on | NVIDIA Jetson (Nano, TX1/TX2, Xavier NX/AGX, Orin Nano/AGX) with JetPack 2.3 ... 6 (README system requirements; JetPack 6 on Orin). x86_64 with an NVIDIA GPU via the container + NVIDIA Container Runtime, WSL 2 possible (docs/aux-docker.md). CUDA + TensorRT required; no CPU fallback; no Apple Silicon. |
| Inputs | Stream URIs via `videoSource`: `csi://0`, `v4l2:///dev/video0`, `rtsp://`, `rtp://`, `webrtc://`, video and image files (docs/aux-streaming.md). Models: built-in names or your ONNX (`--model=x.onnx --labels=... --input-blob=input_0 --output-cvg=scores --output-bbox=boxes` for SSD-Mobilenet exported by `onnx_export.py`), TAO ETLT via `tao-converter`, legacy Caffe. |
| Outputs | Python: list of `Detection` objects from `detectNet.Detect` (box, class, confidence; fields in the API docs, not checked here); overlays on the CUDA image; class mask (segNet); depth field via `depthNet.GetDepthField()` (raw, typically 224x224, docs/depthnet.md). Output streams: display, files, `rtp://`, `rtsp`, `webrtc://`. ROS: `vision_msgs/Detection2DArray` on `detections` (ros_deep_learning README). |
| Key API / entry points | Python (`from jetson_inference import detectNet`, `from jetson_utils import videoSource, videoOutput`, confirmed in `python/examples/detectnet.py`): `detectNet(network, argv, threshold)`, `net.Detect(img, overlay="box,labels,conf")`, `net.GetNetworkFPS()`, `videoSource(uri, argv)`.`Capture()`, `videoOutput(uri, argv)`.`Render(img)`. Other classes: `imageNet`, `segNet`, `poseNet`, `actionNet`, `backgroundNet`, `depthNet`. CLIs: `detectnet`/`detectnet.py`, `segnet`, `depthnet`, `imagenet`, `posenet`. Training: `python/training/detection/ssd/train_ssd.py` + `onnx_export.py` (docs/pytorch-ssd.md). |
| Time to first result | Estimate: 1-2 h on a flashed Jetson with a matching JetPack (container pull + first-run TensorRT engine build, which docs say "will take a few minutes" per model). Half a day if JetPack does not match a container tag and you build from source. Custom SSD retrain: 1 day. |
| License | Code: MIT (GitHub; `LICENSE.md` is NVIDIA 2017 MIT text). Weights: see Gotchas - not covered by the code licence. |

## Minimal usage
From `python/examples/detectnet.py` and docs/detectnet-console-2.md, condensed. Not run.

```bash
docker/run.sh                      # inside the container; from a source build: cd jetson-inference/build/aarch64/bin
./detectnet.py --network=ssd-mobilenet-v2 images/peds_0.jpg images/test/output.jpg
./detectnet.py csi://0 rtp://<laptop-ip>:1234      # live camera, stream to ground station
```
```python
import sys
from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput
net = detectNet("ssd-mobilenet-v2", sys.argv, 0.5)   # positional, as in detectnet.py
cam = videoSource("csi://0", argv=sys.argv)
out = videoOutput("rtp://192.168.1.10:1234", argv=sys.argv)
while cam.IsStreaming():
    img = cam.Capture()
    if img is None: continue
    for d in net.Detect(img): print(d)
    out.Render(img)
```

Stated throughput (README table, segNet only, FP16, JetPack 4.2.1, MAX-N): `fcn-resnet18-cityscapes-512x256` 48 FPS on Nano / 480 FPS on Xavier; `-1024x512` 12 / 175 FPS; `fcn-resnet18-deepscene-576x320` 26 / 360 FPS. No detection throughput table; PeopleNet/DashCamNet input is 960x544 (docs/detectnet-tao.md).

## Wiring it into a nav stack
- ROS 2: [ros_deep_learning](../../catalog/repos/dusty-nv__ros_deep_learning.md) wraps the same nets as `video_source` / `detectnet` / `segnet` nodes publishing `vision_msgs/Detection2DArray`; feed tracks into a tracker or a C2 bridge such as the [MAVLink-to-TAK sample](../../samples/mavlink-to-tak-cot).
- Segmentation (DeepScene forest trail, Cityscapes) can produce a drivable / obstacle mask for a ground robot costmap ([Nav2](./ros-navigation__navigation2.md)); mono `depthNet` gives relative depth only, not metric.
- Newer models (VLMs, NanoOWL) and other packages are in [jetson-containers](../../catalog/repos/dusty-nv__jetson-containers.md) and [Jetson AI Lab](../../catalog/resources/nvidia-jetson-ai-lab.md).
- Scope: use for awareness, collision avoidance and C-UAS detection cues only.

## Gotchas
- **Weights licences are not the MIT code licence and are not stated in the repo.** 41 model URLs in `data/networks/models.json` point to `nvidia.box.com`; the README gives no licence per model. TAO models (PeopleNet, DashCamNet, TrafficCamNet, FaceDetect) are fetched with `tao-model-downloader.sh` from NGC and governed by their NGC model cards (not read here). Training-set licences flow through too (e.g. Cityscapes, MHP for segmentation weights; COCO for SSD). Check before shipping anything beyond a demo.
- Model download from Box links fails for some users (open issues #1836 "unable to download ResNet18-Tagging-VOC/resnet18.onnx", #1713). Pre-download on a good network before the event.
- JetPack must match a container tag; otherwise build from source (docs/aux-docker.md note). Clone the repo on the host even when using the container, because `docker/run.sh` mounts `data/` and model folders.
- Architecture set is dated (SSD-Mobilenet, DetectNet_v2, FCN-ResNet18); no YOLO path - maintainer pointed to TAO models instead (issue #1762). For modern detectors use Ultralytics export to TensorRT or Isaac ROS.
- Last commit 2025-10-16 (NumPy 2.0 fix); slow-moving. First run of each model builds a TensorRT engine (minutes).

## Alternatives
- [Ultralytics](../../catalog/repos/ultralytics__ultralytics.md) - modern YOLO with TensorRT/ONNX export on Jetson; AGPL-3.0, so licence check first.
- [Isaac ROS DNN inference](../../catalog/repos/nvidia-isaac-ros__isaac_ros_dnn_inference.md) - ROS 2 / NITROS TensorRT path if the stack is already Isaac ROS.
- [DepthAI](./luxonis__depthai.md) - push inference and metric stereo depth onto an OAK camera instead of the Jetson GPU.

Sources: README.md, LICENSE.md, docs/aux-docker.md, docs/building-repo-2.md, docs/detectnet-console-2.md, docs/detectnet-tao.md, docs/depthnet.md, docs/pytorch-ssd.md, docs/aux-streaming.md, python/examples/detectnet.py, data/networks/models.json, dusty-nv/ros_deep_learning README, issues #1713, #1762, #1836, commits list (read 2026-11-06).
