# depthai-core - integration card
<!-- about: repo:luxonis/depthai-core -->
One-line: the C++17 library (with the Python bindings built from the same tree) behind every Luxonis OAK camera; use it directly when you need C++ on a companion computer, host-side Basalt VIO or RTAB-Map SLAM nodes wired to the camera's stereo + IMU, or a build you control. For the Python-first view, the model zoo and spatial detection, see the [DepthAI card](./luxonis__depthai.md).

| | |
|---|---|
| Install | Python: `pip install depthai` (PyPI 3.12.0, `requires_python >=3.9`, wheels manylinux_2_28 x86_64/aarch64, macOS 11 arm64/x86_64, win_amd64; PyPI JSON read 2026-11-06). C++ (README): `git clone https://github.com/luxonis/depthai-core && cd depthai-core && git submodule update --init --recursive`, then `cmake -S . -B build -D'BUILD_SHARED_LIBS=ON' -D'CMAKE_INSTALL_PREFIX=<dir>'` and `cmake --build build --target install --parallel N`; consume with `find_package(depthai CONFIG REQUIRED)` + `target_link_libraries(app PRIVATE depthai::core)`. `add_subdirectory` integration is not supported (README). Needs CMake >= 3.20, C++17 compiler, `libudev-dev` on Linux; OpenCV 4 optional (examples, record/replay), PCL optional. Dependencies are fetched through an internal vcpkg bootstrap (`DEPTHAI_BOOTSTRAP_VCPKG ON`). VIO/SLAM need `-DDEPTHAI_BASALT_SUPPORT=ON -DDEPTHAI_RTABMAP_SUPPORT=ON` (both default OFF in `cmake/depthaiOptions.cmake`). Latest release v3.12.0 (2026-11-04). Prebuilt Windows library under Releases; template project luxonis/depthai-core-example. |
| Runs on | Host: Linux x86_64/aarch64, macOS, Windows (C++ and wheels). Android: not supported on v3 (README; v2 only). Device: RVC2 (OAK-D family) and RVC4 (OAK4) over USB or Ethernet; a v3 pipeline can also run on the RVC4 itself (`dai.DeviceInfo.local()`). No host GPU required. ROS via [depthai-ros](../../catalog/repos/luxonis__depthai-ros.md). |
| Inputs | Camera sockets `CAM_A` (colour), `CAM_B`/`CAM_C` (mono stereo pair), on-board IMU (`ACCELEROMETER_RAW`, `GYROSCOPE_RAW`, rotation vector), device calibration (EEPROM), NN Archives / model zoo, holistic record/replay via `DEPTHAI_RECORD` / `DEPTHAI_REPLAY` env vars. |
| Outputs | `ImgFrame` (colour, mono, rectified, depth), `IMUData`, `TrackedFeatures` (on-device `FeatureTracker`), `PointCloudData`, `SpatialImgDetections`, `Odometry` from `BasaltVIO.transform` (transform + `velocity`, `getTranslation()`, `getQuaternion()`), `TransformData` from `RTABMapSLAM.transform` and `odomCorrection` (map => odom), `RTABMapSLAM.occupancyGridMap` (`MapData`), `obstaclePCL` / `groundPCL`. Frame conventions of the VIO/SLAM outputs are not stated in the headers read. |
| Key API / entry points | C++ (headers under `include/depthai/`): `dai::Pipeline`, `pipeline.create<dai::node::Camera>()->build(dai::CameraBoardSocket::CAM_B, std::nullopt, fps)`, `cam->requestOutput(std::make_pair(w, h))`, `dai::node::StereoDepth` / `dai::node::Depth`, `dai::node::IMU::enableIMUSensor({...}, 200)`, `dai::node::FeatureTracker`, `dai::node::BasaltVIO` (inputs `left`, `right`, `imu`; outputs `transform`, `passthrough`; `setImuUpdateRate`, `setConfigPath`, `setLocalTransform`, `setImuExtrinsics`, `setAccelNoiseStd`, `setGyroNoiseStd`), `dai::node::RTABMapVIO` (inputs rect, depth, optional `features`, `imu`; output `transform`; `setParams(std::map<string,string>)`, `setUseFeatures`), `dai::node::RTABMapSLAM` (rect, depth, `features`, `odom` => `transform`, `odomCorrection`, `occupancyGridMap`), `output.createOutputQueue(size, blocking)` + `queue->get<T>()`, `pipeline.start()`, `isRunning()`, `wait()`. Python mirrors these 1:1 (`dai.node.BasaltVIO`, etc.; bindings in `bindings/python/src`). |
| Time to first result | Estimate: Python VIO 1-2 h from `pip install depthai` to `examples/python/VSLAM/basalt_vio.py` on an OAK-D with IMU (plus Rerun viewer). C++ from source: half a day, dominated by the vcpkg dependency build (more with Basalt/RTAB-Map ON; the README warns about OOM kills on parallel builds). Assumes a supported OAK with IMU and working USB udev rules. |
| License | MIT (GitHub metadata). Bundled third-party ports (Basalt, RTAB-Map, etc. under `cmake/ports/`) and zoo model weights carry their own licences; not reviewed here. |

## Minimal usage
C++ Basalt VIO, condensed from `examples/cpp/VSLAM/basalt_vio.cpp` with the Rerun node replaced by an output queue (pattern from `examples/cpp/IMU/imu_gyroscope_accelerometer.cpp`). Not run; needs a build with `DEPTHAI_BASALT_SUPPORT=ON`.

```cpp
#include "depthai/depthai.hpp"
#include <iostream>
int main() {
    dai::Pipeline p;
    auto left  = p.create<dai::node::Camera>()->build(dai::CameraBoardSocket::CAM_B, std::nullopt, 60);
    auto right = p.create<dai::node::Camera>()->build(dai::CameraBoardSocket::CAM_C, std::nullopt, 60);
    auto imu   = p.create<dai::node::IMU>();
    auto vio   = p.create<dai::node::BasaltVIO>();
    imu->enableIMUSensor({dai::IMUSensor::ACCELEROMETER_RAW, dai::IMUSensor::GYROSCOPE_RAW}, 200);
    imu->setBatchReportThreshold(1); imu->setMaxBatchReports(10);
    left->requestOutput(std::make_pair(640, 400))->link(vio->left);
    right->requestOutput(std::make_pair(640, 400))->link(vio->right);
    imu->out.link(vio->imu);
    auto q = vio->transform.createOutputQueue(8, false);
    p.start();
    while(p.isRunning()) {
        auto o = q->get<dai::Odometry>();
        auto t = o->getTranslation(); auto r = o->getQuaternion();
        std::cout << t.x << " " << t.y << " " << t.z << " " << r.qx << " " << r.qy << " " << r.qz << " " << r.qw << "\n";
    }
}
```
Python equivalent: `examples/python/VSLAM/basalt_vio.py`; VIO + SLAM: `basalt_vio_rtabmap_slam.py` / `.cpp`. `Quaterniond` fields `qx, qy, qz, qw` per `include/depthai/common/Quaterniond.hpp`.

## Wiring it into a nav stack
- GNSS-denied odometry without ROS: `BasaltVIO.transform` (or `RTABMapVIO`) => convert to NED/ENU and the vehicle body frame => [VIO-to-MAVLink bridge sample](../../samples/vio-to-mavlink-bridge/) => PX4/ArduPilot `ODOMETRY` / `VISION_POSITION_ESTIMATE` ([pymavlink](./ardupilot__pymavlink.md), [vision_to_mavros](./thien94__vision_to_mavros.md) for the ROS route).
- Map + loop closure: feed VIO into `RTABMapSLAM.odom`; use `odomCorrection` as the map => odom correction and `occupancyGridMap` for planning ([Nav2](./ros-navigation__navigation2.md) if on ROS). Upstream projects: [Basalt](../../catalog/repos/vladyslavusenko__basalt.md), [RTAB-Map](./introlab__rtabmap.md).
- Alternative estimators: export synced stereo + IMU (or record with `DEPTHAI_RECORD`) into [OpenVINS](./rpng__open_vins.md) or [cuVSLAM](./nvidia-isaac__cuvslam.md) and compare tracks with [evo](./michaelgrupp__evo.md).
- Concept pages: [VIO](../../catalog/concepts/vio.md), [visual SLAM](../../catalog/concepts/visual-slam.md).

## v3 vs v2 (short)
- This repo's `main` is v3 (`v3.x.y`); v2 lives on branch `v2_stable`, and v2 Python bindings are the separate luxonis/depthai-python repo. Porting guide: `V2V3PortinGuide.md`.
- v3 adds the unified `Camera` node (replacing `ColorCamera`/`MonoCamera`), implicit host queues (`createOutputQueue`, no explicit `XLinkOut`), host nodes in the same pipeline (`ThreadedHostNode`), VIO/SLAM nodes, multi-device pipelines (`pipeline.addDevice(...)`), RVC4 support and the model zoo. v2 and v3 code are not source-compatible.

## Gotchas
- **VIO/SLAM run on the host CPU, not the camera**: `BasaltVIO`, `RTABMapVIO` and `RTABMapSLAM` all derive from `NodeCRTP<ThreadedHostNode, ...>` in their headers. On-device pieces are depth, `FeatureTracker`, IMU and NN. Budget companion-computer CPU accordingly.
- Basalt/RTAB-Map are off by default in a source build. In the wheel CI (`.github/workflows/python-main.yml`) the Windows job sets `DEPTHAI_BUILD_BASALT: OFF` (RTAB-Map ON), other jobs ON; expect no `BasaltVIO` on Windows wheels (inferred from CI, not tested).
- **Telemetry and network calls by default** (README): anonymised usage telemetry (`DEPTHAI_TELEMETRY=0` to disable), startup notifications fetched from `depthai-releases.luxonis.com` (`DEPTHAI_DISABLE_STARTUP_NOTIFICATIONS=1`), model-zoo internet check (`DEPTHAI_ZOO_INTERNET_CHECK=0`), crash dump collection (`DEPTHAI_DISABLE_CRASHDUMP_COLLECTION`). Set these for air-gapped or sensitive setups. `DEPTHAI_FETCH_ARTIFACTS` (CMake, default ON) downloads device firmware at build time.
- `DEPTHAI_AUTOCALIBRATION` can flash a new stereo calibration to EEPROM by default when enabled; leave it unset unless you mean it.
- Open issues: Basalt VIO drift under rotation on OAK-D-S2 (#1931), race condition (#1510), compile errors with Basalt (#1493), `RTABMapSLAM` crash with occupancy grid disabled (#1738), custom Basalt source build (#1527), macOS Sequoia build failure (#1333).
- vcpkg integration as a consumer uses a custom branch (README); `DEPTHAI_VCPKG_INTERNAL_ONLY=OFF` makes the library non-installable outside vcpkg.
- Low-memory hosts (Raspberry Pi, small Jetson): use `cmake --build build --parallel 2` per README troubleshooting.

## Alternatives
- [DepthAI card](./luxonis__depthai.md) - same library from the Python side; start there unless you need C++.
- [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) / [cuVSLAM](./nvidia-isaac__cuvslam.md) - GPU VIO on Jetson with any calibrated stereo + IMU.
- [OpenVINS](./rpng__open_vins.md) - research-grade MSCKF VIO you can tune and inspect; feed it OAK stereo + IMU via depthai-ros.

Sources: `gh api repos/luxonis/depthai-core` (MIT, default branch `main`, pushed 2026-11-06), releases (v3.12.0, v3.11.0, v3.10.0), README.md, repo tree, cmake/depthaiOptions.cmake, .github/workflows/python-main.yml, include/depthai/basalt/BasaltVIO.hpp, include/depthai/rtabmap/{RTABMapVIO.hpp, RTABMapSLAM.hpp}, include/depthai/pipeline/datatype/{Odometry.hpp, TransformData.hpp}, include/depthai/common/Quaterniond.hpp, examples/cpp/VSLAM/{basalt_vio.cpp, CMakeLists.txt, rerun_node.hpp}, examples/cpp/IMU/imu_gyroscope_accelerometer.cpp, examples/python/VSLAM/basalt_vio.py, existing card luxonis__depthai.md, issue search (#1333, #1493, #1510, #1527, #1738, #1931), PyPI JSON for depthai (read 2026-11-06).
