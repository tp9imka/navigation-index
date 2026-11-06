# RKO-LIO - integration card
<!-- about: repo:prbonn/rko_lio -->
LiDAR-inertial odometry that aims to "just work" without sensor-specific modelling: `pip install` and run on a ROS 1/2 bag in minutes, or `apt install` a ROS 2 node; the quickest way to get IMU-aided LiDAR odometry on unfamiliar hardware.

| | |
|---|---|
| Install | Python: `pip install "rko_lio[all]"` (or `pip install rko_lio rosbags "rerun-sdk>=0.31"`). PyPI name `rko-lio`, latest 0.4.0 (GitHub release v0.4.0, 2026-09-01); `master` `pyproject.toml` already says 0.4.2, unreleased. ROS 2: `sudo apt install ros-$ROS_DISTRO-rko-lio` (README: Humble, Jazzy, Kilted, Lyrical, Rolling). Source: clone into a colcon workspace, `rosdep install --from-paths src --ignore-src -r -y && colcon build --packages-select rko_lio` (add `--cmake-args -DRKO_LIO_FETCH_CONTENT_DEPS=ON` if rosdep cannot supply deps). |
| Runs on | CPU only. `requires-python >= 3.10`. PyPI 0.4.0 wheels: CPython 3.10-3.14 (and 3.14t) on manylinux x86_64, manylinux aarch64, macOS 11 x86_64 and arm64, win_amd64. Closed issue #100 (Jetson Orin, Humble, source build, odometry drifting) ended with the reporter switching to Zenoh RMW. |
| Inputs | Python CLI: a directory of ROS 1 `*.bag` files or a ROS 2 bag (`metadata.yaml`), via `rosbags`; or the `raw` dataloader (`transforms.yaml` with 4x4 extrinsics, `imu.csv`/`.txt`, `lidar/<ns>.ply` per scan). Topics and frames autodetected or set with `--imu`, `--lidar`, `--base_frame`, `--imu_frame`, `--lidar_frame`. Extrinsics from the bag TF tree, or a config file with `extrinsic_imu2base_quat_xyzw_xyz` and `extrinsic_lidar2base_quat_xyzw_xyz` (both required if TF is missing). ROS 2 node: `imu_topic` (sensor_msgs/Imu), `lidar_topic` (sensor_msgs/PointCloud2 with per-point timestamps), `base_frame`, all required unless autodetect is on. Python API timestamps are integer nanoseconds. |
| Outputs | CLI: `<run_name>_tum.txt` trajectory (TUM format) under `results/` or `--log_dir`; optional deskewed scans as `.ply` (`--dump_deskewed`); Rerun visualization with `-v`. ROS 2: `rko_lio/odom` (nav_msgs/Odometry, `odom_topic`), TF `odom` => `base_frame` (`invert_odom_tf` option), optional `rko_lio/deskewed_scan`, `rko_lio/local_map` (PointCloud2), `rko_lio/lidar_acceleration` (AccelStamped), `rko_lio/reset_count` (std_msgs/UInt32, transient local). `dump_results` / `results_dir` parameters write results from the node too. |
| Key API / entry points | CLI `rko_lio <data_path> [-v] [--config f.yaml] [--dataloader rosbag|raw] [--imu T] [--lidar T] [--base_frame F] [-o log_dir] [-n run_name] [--dump_config] [--dump_deskewed]` (entry point `rko_lio.cli:app`). Python `rko_lio.lio.LIO(config)` with `.add_imu_measurement(acceleration, angular_velocity, time_ns, extrinsic_imu2base=None)`, `.register_scan(scan_nx3, timestamps_ns, extrinsic_lidar2base=None, start_time_ns=None, end_time_ns=None)`, `.pose`, `.map_point_cloud`, `.poses_with_timestamps`. ROS 2: `ros2 launch rko_lio odometry.launch.py [autodetect:=false imu_topic:=... lidar_topic:=... base_frame:=base_link] [config_file:=f.yaml] [rviz:=true]`; C++ targets: `online_node_component` and siblings (composable components) plus an `offline_node` executable for bags (`rko_lio/ros/CMakeLists.txt`). Configs: `config/ros_default.yaml`, `leg_kilo.yaml`, `oxford_spires.yaml`. |
| Time to first result | Estimate: 10-20 min with pip and a bag that has a TF tree with IMU and LiDAR frames; 30 min via apt on a supported ROS 2 distro. |
| License | LICENSE file: MIT (Meher V.R. Malladi). Fetched deps (TBB, Eigen, Sophus etc.) under their own licences. No weights. |

## Minimal usage
Not run. From README.

```sh
pip install "rko_lio[all]"
rko_lio --dump_config                 # writes a default config to edit
rko_lio -v /path/to/bag_dir           # ROS 1 *.bag dir or ROS 2 bag with metadata.yaml
rko_lio --config cfg.yaml --imu /imu/data --lidar /points --base_frame base_link /path/to/bag_dir
```

ROS 2:

```sh
sudo apt install ros-$ROS_DISTRO-rko-lio
ros2 launch rko_lio odometry.launch.py autodetect:=false \
  imu_topic:=/imu/data lidar_topic:=/points base_frame:=base_link
ros2 launch rko_lio odometry.launch.py -s   # list all launch options
```

## Wiring it into a nav stack
- `rko_lio/odom` => [robot_localization](./cra-ros-pkg__robot_localization.md) as an odometry input next to wheel odom and GNSS, or => [MAVROS](./mavlink__mavros.md) `odometry/out` for PX4/ArduPilot external vision.
- Loop closure and drift correction: the README points to `PRBonn/rko_slam` (early). [KISS-SLAM](./prbonn__kiss-slam.md) is the LiDAR-only sibling with closures.
- Same lab and output conventions as [KISS-ICP](./prbonn__kiss-icp.md); the `_tum.txt` output goes straight into [evo](./michaelgrupp__evo.md).

## Gotchas
- Extrinsics are mandatory. Convention is `transform_<from>2<to>` (vector in `from` frame to `to` frame); getting the direction wrong is the likely first failure.
- Point clouds need per-point timestamps for deskew; `lidar_timestamps.force_absolute` / `force_relative` and `multiplier_to_seconds` parameters exist for drivers with odd time fields.
- Topic and frame autodetection in the launch file is marked experimental in the README.
- Defaults to `max_num_threads: 1` in the ROS node (`base_node.cpp`); raise it on multi-core hosts.
- No GNSS or global factor: pure odometry, so it drifts over long runs. Recent closed issues cover jerky first metres (#139), jitter when stationary (#122) and a reset on registration failure (#176).

## Alternatives
- [FAST-LIO2](./hku-mars__fast_lio.md) - the common LIO baseline, more tuning per sensor; GPL-2.0.
- [LIO-SAM](./tixiaoshan__lio-sam.md) - when you want a GPS factor and loop closure in the same node and have a 9-axis IMU.
- [KISS-ICP](./prbonn__kiss-icp.md) - when no IMU is available.

Sources: `README.md`, `LICENSE`, `pyproject.toml`, `rko_lio/python/rko_lio/cli.py`, `rko_lio/python/rko_lio/lio.py`, `rko_lio/python/rko_lio/lio_pipeline.py`, `rko_lio/python/rko_lio/dataloaders/raw.py`, `rko_lio/ros/base_node.cpp`, `rko_lio/ros/base_node.hpp`, repo tree (`launch/`, `config/`), release v0.4.0, PyPI JSON for `rko-lio`, issues #100 #122 #139 #176 (github.com/PRBonn/rko_lio).
