# Stonefish - integration card
<!-- about: repo:patrykcieslak/stonefish -->
C++ marine robotics simulator (Bullet physics extended with geometry-based hydrodynamics, custom OpenGL 4.3 underwater rendering) with a nav-relevant sensor set: IMU, INS, DVL, GPS (dropped underwater), pressure, compass, multibeam, FLS, SSS, MSIS, cameras. Use it for AUV / USV dead-reckoning and DVL-aided nav scenarios where GNSS is absent by physics.

| | |
|---|---|
| Install | Latest release v1.5 (2025-06-10); `master` `CMakeLists.txt` says `VERSION 1.6.0`. Deps (README): `sudo apt install libglm-dev libsdl2-dev libfreetype6-dev` (glm >= 0.9.9.0), plus OpenGL. Build: `git clone https://github.com/patrykcieslak/stonefish && cd stonefish && mkdir build && cd build && cmake .. && make -j8 && sudo make install`. CMake options `BUILD_TESTS` (OFF, builds demo apps in `Tests/`) and `EMBED_RESOURCES` (OFF). ROS 2: clone `patrykcieslak/stonefish_ros2` (GPL-3.0) into a colcon workspace; its README requires "the same version as the ROS2 package". |
| Runs on | Linux (developed and tested on Ubuntu). No Windows build; macOS not supported (no OpenGL 4.3). Needs a GPU with OpenGL 4.3 and vendor drivers; README calls it CPU heavy. |
| Inputs | Scenario XML (`.scn`) parsed by `ScenarioParser` / the ROS node, or a C++ `SimulationManager` subclass that builds the scene in code. Geodetic origin via the `NED` class. |
| Outputs | Sensor samples per sensor class (`Library/include/sensors/scalar/`: `Accelerometer`, `Gyroscope`, `IMU`, `INS`, `DVL`, `GPS`, `Pressure`, `Compass`, `Odometry`, `Pose`, `Profiler`, `Multibeam`, `Current`, encoders, force/torque; `vision/`: `ColorCamera`, `DepthCamera`, `ThermalCamera`, `EventBasedCamera`, `OpticalFlowCamera`, `SegmentationCamera`, `FLS`, `SSS`, `MSIS`, `Multibeam2`). Via stonefish_ros2: ROS 2 topics per sensor defined in the scenario. `GPS` samples are `[lat, lon, north, east]`; underwater it records `BT_LARGE_FLOAT` placeholders instead of a fix (`GPS.cpp`). |
| Key API / entry points | C++: `sf::SimulationManager` (override scene building), `sf::GraphicalSimulationApp` / `sf::ConsoleSimulationApp` (headless), `sf::SimulationApp(title, dataDirPath, sim)`, `app.Run()`, `sf::RenderSettings`, `sf::HelperSettings`, `sf::ScenarioParser`, `sf::GPS(name, frequency, history)` + `setNoise(nedStdDev)`. ROS 2: launch `stonefish_simulator.launch.py` / `stonefish_simulator_nogpu.launch.py` with args `simulation_data`, `scenario_desc`, `simulation_rate`, `window_res_x`, `window_res_y`. Example apps: `Tests/UnderwaterTest`, `FlyingTest`, `FloatingTest`, `LearningTest`. |
| Time to first result | Estimate: 30-60 min to build the library and run a `Tests/` demo on Ubuntu with a working GPU driver; 1-2 h more for stonefish_ros2 with a scenario file. |
| License | `COPYING.txt`: GPL-3.0 (library and stonefish_ros2). Linking your code into a distributed binary inherits GPL. |

## Minimal usage
Not run. From README and `CMakeLists.txt`.

```sh
sudo apt install libglm-dev libsdl2-dev libfreetype6-dev
git clone https://github.com/patrykcieslak/stonefish && cd stonefish
cmake -S . -B build -DBUILD_TESTS=ON && cmake --build build -j8
sudo cmake --install build
# demo app binaries land under build/ (exact path not checked)
```

ROS 2 (include in your own launch, per stonefish_ros2 README):

```sh
ros2 launch stonefish_ros2 stonefish_simulator.launch.py \
  simulation_data:=<pkg>/data scenario_desc:=<pkg>/scenarios/auv.scn simulation_rate:=100.0
```

## Wiring it into a nav stack
- IMU + DVL + pressure => an INS/DVL filter ([robot_localization](./cra-ros-pkg__robot_localization.md), [fuse](./locusrobotics__fuse.md) or [GTSAM](./borglab__gtsam.md)); surface GPS fixes reset drift when the vehicle surfaces.
- Sonar and camera outputs feed terrain / feature-based nav research; nav-only consumers can ignore rendering.
- Benchmark with [evo](./michaelgrupp__evo.md) against the simulator's ground-truth `Odometry`/`Pose` sensors.

## Gotchas
- GPU/OpenGL 4.3 is mandatory for the default app; open issue #90 asks for a headless mode for sensing. `ConsoleSimulationApp` and the `_nogpu` launch exist, but which sensors work without rendering was not checked.
- GPS model is simple: 2D Gaussian noise in N/E (`setNoise`), height not simulated (converted with down = 0), no multipath, jamming or spoofing.
- Library and ROS package versions must match; open issue #91 reports a compile error on ROS 2 Humble in `ROS2Interface.cpp`.
- Single maintainer, unfunded (README); open issues on multi-robot scenes (#80) and simulation-speed control for RL (#81).

## Alternatives
- [DAVE](../../catalog/repos/field-robotics-lab__dave.md) or [UUV Simulator](../../catalog/repos/uuvsimulator__uuv_simulator.md) - Gazebo-based underwater, plays with [ros_gz](./gazebosim__ros_gz.md).
- [HoloOcean (ROS)](../../catalog/repos/byu-holoocean__holoocean-ros.md) - Unreal-based underwater sim.
- [VRX](../../catalog/repos/osrf__vrx.md) - surface vessels on Gazebo.

Sources: `README.md`, `COPYING.txt`, `CMakeLists.txt`, `Library/include/core/` listing, `Library/include/core/SimulationApp.h`, `Library/include/sensors/scalar/` and `vision/` listings, `Library/include/sensors/scalar/GPS.h`, `Library/src/sensors/scalar/GPS.cpp`, `Tests/` listing, `Tests/UnderwaterTest/main.cpp`, release v1.5, issues #80 #81 #90 #91 (github.com/patrykcieslak/stonefish); `README.md`, `launch/stonefish_simulator.launch.py` (github.com/patrykcieslak/stonefish_ros2).
