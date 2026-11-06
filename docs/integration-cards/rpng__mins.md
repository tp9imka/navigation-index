# MINS - integration card
<!-- about: repo:rpng/mins -->
One-line: tightly coupled MSCKF-style filter fusing IMU with any mix of cameras, LiDARs, wheel odometry and GNSS (with online calibration), plus a multi-sensor simulator, so you can switch GNSS off mid-run and show the other sensors holding the solution.

| | |
|---|---|
| Install | ROS 1: `mkdir -p ws/src && cd ws/src && git clone https://github.com/rpng/MINS && cd .. && catkin build && source devel/setup.bash` (README). ROS 2: follow `Dockerfile_humble_22_04` / `Dockerfile_jazzy_24_04` / `Dockerfile_lyrical_26_04` (README points there). ROS-free: `cmake -S MINS/mins -B build/mins -DCMAKE_BUILD_TYPE=Release -DENABLE_ROS=OFF -DENABLE_ARUCO_TAGS=OFF && cmake --build build/mins` with `libeigen3-dev libopencv-dev` (from `Dockerfile_rosfree_ubuntu_24_04`). |
| Runs on | CI badges: ROS 1 Melodic/Noetic, ROS 2 Humble/Jazzy/Lyrical, ROS-free Ubuntu 22.04/24.04/26.04, macOS arm64, Windows x64. README "Dependency" section still says tested on Ubuntu 18/20. CPU only. |
| Inputs | ROS bags or live topics: IMU, camera images, `sensor_msgs/PointCloud2`, `nav_msgs/Odometry` (wheel), `sensor_msgs/NavSatFix` (GNSS, e.g. `/gps/fix` in the KAIST config), PoseStamped/TransformStamped (VICON). Configs: one `config.yaml` that includes `config_imu.yaml`, `config_gps.yaml`, `config_camera.yaml`, `config_lidar.yaml`, `config_wheel.yaml`, `config_estimator.yaml`, `config_init.yaml`, ... GNSS block: `enabled`, `max_n`, `noise`, `chi2_mult`, `do_calib_ext`, `do_calib_dt`, per-receiver `pGinI` lever arm and `timeoffset`. |
| Outputs | Pose/path topics for RViz (ROS), estimated calibration; evaluation toolbox `mins_eval` for accuracy, consistency, timing. |
| Key API / entry points | ROS 1: `roslaunch mins simulation.launch cam_enabled:=true lidar_enabled:=true`, `roslaunch mins rosbag.launch config:=kaist/kaist_LC path_gt:=urban30.txt path_bag:=urban30.bag`, `roslaunch mins subscribe.launch config:=euroc_mav rosbag:=...`. ROS 2: `ros2 run mins simulation mins/config/simulation/config.yaml`, `ros2 run mins subscribe mins/config/euroc_mav/config.yaml`. ROS-free executables (`cmake/ROS1.cmake`): `mins_cli <config.yaml>` (simulation), `mins_bag <config.yaml> [bag | /dev/stdin]` (`mins_bag` is also built by `cmake/ROS2.cmake`). Updaters live in `mins/src/update/{cam,gps,lidar,wheel,vicon}`. |
| Time to first result | Estimate: 1-2 h for the simulation run inside the provided Docker image (build time dominates); half a day for a KAIST bag (download + config). Own robot: days (extrinsics, time offsets, noise). Assumes x86 Linux with Docker. |
| License | GPL-3.0 (GitHub and README). |

## Minimal usage
From README and `Dockerfile_rosfree_ubuntu_24_04`. Not run.

```bash
git clone https://github.com/rpng/MINS && cd MINS
docker build -f Dockerfile_rosfree_ubuntu_24_04 -t mins .
docker run --rm -it mins ./build/mins/mins_cli src/MINS/mins/config/simulation/config.yaml
# ROS 2 alternative: ros2 run mins simulation mins/config/simulation/config.yaml, then rviz2
```

GNSS denial demo: in `config/simulation/config_gps.yaml` GNSS ships with `enabled: false`; enable it, run once with GNSS, then rerun with GNSS disabled or on a bag where the `/gps/fix` topic stops partway, and compare paths.

## Wiring it into a nav stack
- Real data: KAIST Complex Urban configs (`config/kaist/kaist_C`, `kaist_L`, `kaist_LC`) with converted bags mirrored on Hugging Face (README); see [KAIST dataset page](../../catalog/resources/kaist-complex-urban-dataset.md). EuRoC and TUM-VI configs for VIO-only.
- GNSS input is `NavSatFix`; produce it from a u-blox with [pyubx2](./semuconsulting__pyubx2.md) or a ROS driver. GNSS initialization is controlled by `init_distance` and `init_closed_form` in `config_gps.yaml` (semantics not read in source).
- Output to [Nav2](./ros-navigation__navigation2.md) needs a small adapter to Odometry/TF; to PX4/ArduPilot via a VIO-to-MAVLink bridge (see [samples/vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge)).
- Simulation upstream: its own simulator, or [Gazebo gz-sim](./gazebosim__gz-sim.md) recorded to a bag.
- Built on [OpenVINS](../../catalog/repos/rpng__open_vins.md) (`ov_core` in `thirdparty/`). Catalog: [MINS page](../../catalog/repos/rpng__mins.md).

## Gotchas
- GPS is disabled in the default simulation config; many first runs show only IMU+camera/LiDAR.
- OpenCV must match the one `cv_bridge` was built against, or you get a segfault (comment in `mins/CMakeLists.txt`).
- `mins_bag` reads ROS 1 bags without ROS; bz2/lz4-compressed chunks need BZip2/LZ4 found at configure time, otherwise only uncompressed bags open.
- Non-ROS1/ROS2 builds fall through to `ROS1.cmake`, which builds the ROS-free targets when catkin is not found; pass `-DENABLE_ROS=OFF` to force that path on a machine that also has ROS 1.
- Issues: own-hardware bring-up (#14, closed), KAIST urban30 result questions (#48, open), no zero-velocity update (#42, open), Livox LiDAR support (#39, open), no map-based relocalization (#34, closed).
- GPL-3.0 plus OpenVINS (GPL-3.0): derivative code must stay GPL.
- Very active recently (commits through 2026-10 adding ROS-free bag streaming); pin a commit.

## Alternatives
- [OpenVINS](../../catalog/repos/rpng__open_vins.md): camera+IMU only, better documented, same group.
- [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md): LiDAR-inertial factor graph with GPS factors (ROS 1 main).
- [robot_localization](./cra-ros-pkg__robot_localization.md): loosely coupled, config-only, enough if you have wheel odom + IMU + GNSS and no vision.

Sources: `ReadMe.md`, `mins/CMakeLists.txt`, `mins/cmake/ROS1.cmake`, `Dockerfile_rosfree_ubuntu_24_04`, `mins/config/simulation/config.yaml`, `mins/config/simulation/config_gps.yaml`, `mins/config/kaist/kaist_LC/config_gps.yaml`, `mins/src/io/RosMsgs.h`, `mins/src/run_simulation_cli.cpp`, `mins/src/run_bag_cli.cpp`, recent commits, issue search (sorted by comments).
