# Gazebo Sim (gz-sim) - integration card
<!-- about: repo:gazebosim/gz-sim -->
One-line: the physics + sensor simulator behind PX4 and ArduPilot SITL and Nav2 demos, with IMU, NavSat (GNSS), magnetometer, altimeter, air pressure, cameras and LiDAR, so you can fly or drive a vehicle and cut its GNSS on cue.

| | |
|---|---|
| Install | Binary per the gazebosim.org getting-started guide (README defers there): e.g. Harmonic on Ubuntu 24.04 via the OSRF apt repo (`sudo apt install gz-harmonic`). With ROS 2, install the matching `ros-$ROS_DISTRO-ros-gz` packages. Library-only install: gazebosim.org/api/sim/9/install.html. Usually you get it indirectly from PX4 (`make px4_sitl gz_x500`) or `ardupilot_gazebo`. |
| Runs on | Ubuntu (CI: Noble amd64), macOS via Homebrew, Windows via Conda (server and GUI in separate terminals, `gz sim -s` / `gz sim -g`). GPU strongly preferred for camera / depth sensors (OGRE 2); headless server (`gz sim -s`) works without a display for non-rendering sensors. |
| Inputs | SDF world and model files (`.sdf`), models from Gazebo Fuel, plugin (system) configuration in SDF, `<spherical_coordinates>` for the world's geodetic origin, commands over gz-transport topics/services (`gz topic`, `gz service`), ROS 2 topics through `ros_gz_bridge`. |
| Outputs | gz-transport messages: `gz.msgs.IMU`, `gz.msgs.NavSat` (lat, lon, alt, velocity), `gz.msgs.Magnetometer`, `gz.msgs.Altimeter`, `gz.msgs.FluidPressure`, `gz.msgs.Image`, `gz.msgs.LaserScan`, poses, odometry. Bridged to ROS 2 as `sensor_msgs/Imu`, `sensor_msgs/NavSatFix`, etc. Logs/recordings via the `log` system. |
| Key API / entry points | CLI: `gz sim <world.sdf>`, `gz sim -s -r` (headless, run), `gz topic -l/-e`, `gz service`. Systems (SDF `<plugin filename=...>`): `gz-sim-imu-system`, `gz-sim-navsat-system`, `gz-sim-magnetometer-system`, `gz-sim-altimeter-system`, `gz-sim-air-pressure-system`, `gz-sim-sensors-system` (rendering sensors), `gz-sim-multicopter-motor-model-system`, `gz-sim-multicopter-control-system`, `gz-sim-odometry-publisher-system`, `gz-sim-wind-effects-system`. Python: `from gz.sim import TestFixture, World, world_entity` with `fixture.on_post_update(cb)` and `fixture.server().run(blocking, iterations, paused)`. Example worlds: `examples/worlds/spherical_coordinates.sdf`, `quadcopter.sdf`, `sensors.sdf`. |
| Time to first result | Estimate: 30-60 min to a running PX4 `gz_x500` with GNSS, assuming Ubuntu 22.04/24.04 with a working GPU driver and the PX4 toolchain. Plan more on macOS / VMs (see Gotchas). |
| License | Apache-2.0 |

## Minimal usage

From the README and `examples/worlds/spherical_coordinates.sdf` header comments. Not run.

```bash
gz sim spherical_coordinates.sdf          # world with gz-sim-navsat-system and a WGS84 origin
gz topic -l                               # find the navsat / imu topics
gz service -s /world/spherical_coordinates/set_spherical_coordinates \
  --reqtype gz.msgs.SphericalCoordinates --reptype gz.msgs.Boolean --timeout 2000 \
  --req "surface_model: EARTH_WGS84, latitude_deg: 35.6, longitude_deg: 140.1, elevation: 10.0"
```

With PX4 (from the [PX4 SITL GPS denial sample](../../samples/px4-sitl-gps-denial/)):

```bash
cd PX4-Autopilot && make px4_sitl gz_x500     # HEADLESS=1 for no GUI
```

## Wiring it into a nav stack

- Autopilots: PX4 launches gz-sim itself (`gz_x500`, `gz_x500_vision`, ...) and reads its IMU/GNSS/baro/mag; ArduPilot uses [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md). GNSS denial is then injected in the autopilot (PX4 `failure gps off`), see [PX4 SITL GPS denial](../../samples/px4-sitl-gps-denial/) and [ArduPilot EKF3 source switch](../../samples/ardupilot-ekf3-source-switch/).
- ROS 2: [ros_gz](../../catalog/repos/gazebosim__ros_gz.md) `parameter_bridge` maps `gz.msgs.NavSat` => `sensor_msgs/NavSatFix` and `gz.msgs.IMU` => `sensor_msgs/Imu`, which feed [robot_localization](./cra-ros-pkg__robot_localization.md) and [Nav2](./ros-navigation__navigation2.md).
- Camera frames for visual localization (e.g. the [LightGlue geolocalization sample](../../samples/visual-geolocalization-lightglue/)) come from `gz-sim-sensors-system` cameras; draping a georeferenced orthophoto onto a ground plane needs a heightmap / textured model you build yourself (e.g. from [GDAL](./osgeo__gdal.md) outputs).
- Spoofing-style tests: the navsat system reports truth plus SDF-configured noise; shifting the world origin with `set_spherical_coordinates` at runtime is a crude way to fake a position jump (my suggestion, untested).
- For RL or fast swarm logic without rendering, [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md) is lighter.

## Gotchas

- Version matching: each ROS 2 distro has a recommended Gazebo release (Humble => Fortress, Jazzy => Harmonic per gazebosim.org docs); mixing needs source builds of `ros_gz`. PX4 docs pin which Gazebo they support. Pick versions before the event.
- Old tags are named `ignition-gazebo6_*` (Fortress era); package and plugin names changed from `ignition-gazebo-*` / `ign` to `gz-sim-*` / `gz`. Tutorials mix both.
- Mixed Debian + source installs break `gz` CLI tools; README workaround: set `GZ_CONFIG_PATH` to every install's `share/gz`.
- Apple Silicon and ARM VMs: crashes on start reported (issues #1362 "Crash on M1 chip instantly even using docker", #1841 ARM64 Ubuntu VM, #1987 macOS GUI segfault). Software rendering via Mesa llvmpipe showed black viewports (#1116). Use a native Linux x86 box with a real GPU if cameras matter.
- NavSat needs the world to define `<spherical_coordinates>` and the `gz-sim-navsat-system` plugin loaded, otherwise nothing is published (related crash #2163).
- Windows: `gz sim` alone does not work; run server and GUI separately (README).

## Alternatives

- [isaac-sim/isaacsim](../../catalog/repos/isaac-sim__isaacsim.md): photoreal RTX rendering and synthetic data, needs a strong NVIDIA GPU.
- [microsoft/airsim](../../catalog/repos/microsoft__airsim.md) / [iamaisim/projectairsim](../../catalog/repos/iamaisim__projectairsim.md): Unreal-based drone sim with better imagery for vision work; AirSim is archived.
- [cyberbotics/webots](../../catalog/repos/cyberbotics__webots.md): easier install, cross-platform, smaller autopilot ecosystem.

Sources: `gh api repos/gazebosim/gz-sim/readme`; `src/systems` listing; `examples/worlds/spherical_coordinates.sdf`; `examples/scripts/python_api/testFixture.py`; tags list; issue searches ("navsat", "macos gui"); vault sample `samples/px4-sitl-gps-denial/README.md`. Catalog: [record](../../catalog/repos/gazebosim__gz-sim.md).
