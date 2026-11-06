# DepthAI - integration card
<!-- about: repo:luxonis/depthai -->
One-line: drive a Luxonis OAK camera from Python so stereo depth, on-camera detection with metric XYZ, IMU and (v3) stereo-inertial VIO come out of one USB/PoE device; the index id points at a repo that is now mostly a signpost, the live code is `luxonis/depthai-core`.

| | |
|---|---|
| Install | `pip install depthai` (PyPI 3.12.0, `requires_python >=3.9`, MIT; wheels for manylinux_2_28 x86_64 and aarch64, macOS 11 arm64 and x86_64, win_amd64 - PyPI JSON 2026-11-06). Examples: clone `luxonis/depthai-core`, `python3 examples/python/install_requirements.py`. Legacy demo app: `git clone --recursive -b main https://github.com/luxonis/depthai.git`, `python3 install_requirements.py`, or Docker `luxonis/depthai:latest` (README on `main`). |
| Runs on | Host: Linux x86_64/aarch64 (incl. Raspberry Pi 64-bit, Jetson with glibc >= 2.28), macOS (Apple Silicon wheel), Windows. Needs an OAK device: RVC2 (OAK-D, OAK-D Lite/Pro/S2, OAK-1) or RVC4 (OAK4). Inference runs on the camera, so no host GPU/CUDA. ROS via [depthai-ros](../../catalog/repos/luxonis__depthai-ros.md). |
| Inputs | Camera sockets (`CAM_A` color, `CAM_B`/`CAM_C` mono stereo pair), on-board IMU (`ACCELEROMETER_RAW`, `GYROSCOPE_RAW`, rotation vector), models as NN Archives from the Luxonis model zoo (`dai.NNModelDescription("yolov6-nano")` + platform `RVC2`/`RVC4`) or legacy `.blob` (RVC2). Record/replay for offline runs (`examples/python/RecordReplay`). |
| Outputs | `ImgFrame` (color, mono, rectified, depth in mm), `SpatialImgDetections` (bbox, `labelName`, `confidence`, `spatialCoordinates.x/y/z` in mm, camera frame), IMU packets, point clouds, `BasaltVIO.transform` pose stream, encoded video (H.264/H.265/MJPEG). |
| Key API / entry points | v3 (confirmed in `depthai-core` examples): `dai.Pipeline()` (context manager, implicit default device), `p.create(dai.node.Camera).build(socket, sensorFps=...)`, `cam.requestOutput((w, h))`, `p.create(dai.node.Depth).build(dai.node.Depth.Algorithm.AUTO, fps, (640, 400))`, `p.create(dai.node.SpatialDetectionNetwork).build(cam, depth, modelDescription)`, `dai.getModelFromZoo(desc)` / `dai.NNArchive(path)`, `p.create(dai.node.IMU).enableIMUSensor([...], 200)`, `p.create(dai.node.BasaltVIO)` with inputs `left`, `right`, `imu` and output `transform`, `dai.node.HostNode` for host-side processing, `p.run()` / `p.start()`. v2 API (`ColorCamera`, `MonoCamera`, `XLinkOut`, `dai.Device(pipeline)`) is on `depthai-core` branch `v2_stable` / `depthai-python`. |
| Time to first result | Estimate: 15-30 min from `pip install depthai` to the spatial detection example on an OAK-D (first run downloads the model from the zoo). Basalt VIO example: 1-2 h incl. Rerun viewer setup. Assumes USB3 and Linux udev access already working. |
| License | GitHub metadata: none (default branch `readme` holds only a README). `LICENSE` on the `main` branch: MIT. `depthai-core`: MIT. Model weights: see Gotchas. |

## Repo layout (read this first)
- `luxonis/depthai` default branch `readme` is a placeholder: "Looking for old depthai repository contents? Check `main` branch!". `main` holds the v2-era demo app (`depthai_demo.py`, `calibrate.py`, `depthai_sdk`, `resources/nn`), still receiving calibration fixes (2026-09).
- `luxonis/depthai-core` (C++ with Python bindings, latest release v3.12.0 on 2026-11-04) is the library. Its README: "You're viewing the `v3.x.y` branch"; v2 is on `v2_stable`; migration in `V2V3PortinGuide.md` (`ColorCamera`/`MonoCamera` deprecated for `Camera`, explicit `XLinkOut` removed, `.dap` standalone packages unsupported).
- `luxonis/depthai-python` is v2 only; its README says v3 bindings live in `depthai-core`.
- Models: v3 uses the Luxonis model zoo via `dai.getModelFromZoo` / `NNModelDescription` (downloads `.tar.xz` NN Archives, e.g. `yolov6-nano-r2-288x512.tar.xz` per `examples/python/ModelZoo/model_zoo.py`). v2 used `.blob` files compiled with [blobconverter](https://github.com/luxonis/blobconverter) (MIT, last push 2025-12; README requires an OpenVINO 2022.3 build to self-host).

## Minimal usage
Condensed from `depthai-core/examples/python/SpatialDetectionNetwork/spatial_detection.py`. Not run.

```python
import depthai as dai
with dai.Pipeline() as p:
    cam = p.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A, sensorFps=20)
    depth = p.create(dai.node.Depth).build(dai.node.Depth.Algorithm.AUTO, 20, (640, 400))
    nn = p.create(dai.node.SpatialDetectionNetwork).build(cam, depth, dai.NNModelDescription("yolov6-nano"))
    nn.setDepthLowerThreshold(100); nn.setDepthUpperThreshold(5000)
    q = nn.out.createOutputQueue()
    p.start()
    while p.isRunning():
        for d in q.get().detections:
            c = d.spatialCoordinates
            print(d.labelName, round(d.confidence, 2), c.x, c.y, c.z)  # mm, camera frame
```

`createOutputQueue()` / `q.get()` / `isRunning()` is the host-queue pattern from `examples/python/DetectionNetwork/detection_network.py`; this exact combination was not run. Stereo-inertial odometry: `examples/python/VSLAM/basalt_vio.py` (640x400 stereo at 60 FPS + IMU at 200 Hz into `BasaltVIO`, pose to a Rerun node); `basalt_vio_rtabmap_slam.py` adds RTAB-Map.

## Wiring it into a nav stack
- ROS 2: [depthai-ros](../../catalog/repos/luxonis__depthai-ros.md) publishes images, depth, IMU and detections; feed depth to [Nav2](./ros-navigation__navigation2.md) costmaps, stereo + IMU to [OpenVINS](../../catalog/repos/rpng__open_vins.md) or [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md).
- Without ROS: `BasaltVIO.transform` => convert to NED / ENU => [VIO-to-MAVLink bridge sample](../../samples/vio-to-mavlink-bridge) => PX4/ArduPilot `VISION_POSITION_ESTIMATE` / `ODOMETRY` for GNSS-denied flight. Related upstream projects in the index: [Basalt](../../catalog/repos/vladyslavusenko__basalt.md), [RTAB-Map](../../catalog/repos/introlab__rtabmap.md).
- Score the VIO track with [evo](./michaelgrupp__evo.md) by logging poses as TUM lines.
- Spatial detections give metric bearing + range in the camera frame: usable for obstacle avoidance and C-UAS detection cues.

## Gotchas
- **Model weights licences are separate and not stated in depthai-core.** The zoo default in the examples is `yolov6-nano`; upstream YOLOv6 (meituan/YOLOv6) is GPL-3.0 on GitHub. Many legacy `resources/nn` models on `depthai@main` are OpenVINO Open Model Zoo models (licence per model card, not checked). Check each model card before reuse.
- BasaltVIO runs on the host CPU (`class BasaltVIO : public NodeCRTP<ThreadedHostNode, BasaltVIO>` in `include/depthai/basalt/BasaltVIO.hpp`) and is optional at build time (`DEPTHAI_BASALT_SUPPORT` defaults OFF in `cmake/depthaiOptions.cmake`). The PyPI wheel CI (`.github/workflows/python-main.yml`) sets `DEPTHAI_BUILD_BASALT: ON` for Linux and macOS jobs and `OFF` for Windows, so expect no `BasaltVIO` on Windows wheels (inferred from CI, not tested). Open issues: drift under rotation on OAK-D-S2 (#1931), race condition (#1510), compilation errors (#1493).
- Beta nodes (`dai.beta.node`) run on-device only on RVC4; on RVC2 they fall back to the host (README).
- v2 and v3 APIs are not compatible; most forum answers, blog posts and older `depthai-experiments` code are v2. Check which one a snippet targets before copying.
- Docker / Linux needs USB device access: the README's Docker command uses `--privileged -v /dev/bus/usb:/dev/bus/usb --device-cgroup-rule='c 189:* rmw'`.
- No throughput numbers are stated in the READMEs read; measure on your device.

## Alternatives
- [jetson-inference](./dusty-nv__jetson-inference.md) - run detection on a Jetson GPU with any USB/CSI camera; no metric depth without a stereo camera.
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) - GPU VIO/SLAM on Jetson if you already have Jetson + stereo camera and need a more mature tracker than on-host Basalt.
- [Ultralytics](../../catalog/repos/ultralytics__ultralytics.md) - train custom detectors; export then convert for the OAK (AGPL-3.0, licence check).

Sources: luxonis/depthai README (branches `readme` and `main`), `main` LICENSE, branch list; luxonis/depthai-core README.md, V2V3PortinGuide.md, cmake/depthaiOptions.cmake, include/depthai/basalt/BasaltVIO.hpp, examples/README.md, examples/python/DetectionNetwork/detection_network.py, examples/python/{SpatialDetectionNetwork/spatial_detection.py, VSLAM/basalt_vio.py, ModelZoo/model_zoo.py, ModelZoo/mymodel.yaml, install_requirements.py}, bindings/python/setup.py, .github/workflows/python-main.yml, release v3.12.0, issues #1493, #1510, #1931; luxonis/depthai-python README; luxonis/blobconverter README; meituan/YOLOv6 GitHub licence; PyPI JSON for depthai 3.12.0 (read 2026-11-06).
