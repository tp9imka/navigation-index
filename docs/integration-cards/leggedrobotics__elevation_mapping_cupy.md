# elevation_mapping_cupy - integration card
<!-- about: repo:leggedrobotics/elevation_mapping_cupy -->
GPU (CuPy) robot-centric elevation mapping from point clouds with drift compensation, visibility cleanup, a small learned traversability filter and plugin layers, published as `grid_map_msgs/GridMap`; ROS 2 Jazzy on the `ros2` branch.

| | |
|---|---|
| Install | ROS 2 (branch `ros2`, release v2.2.0 2026-07-20, `package.xml` 2.2.0): `mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src && git clone -b ros2 https://github.com/leggedrobotics/elevation_mapping_cupy.git && cd .. && rosdep install --from-paths src --ignore-src -r -y && colcon build --packages-up-to semantic_sensor elevation_mapping_cupy --symlink-install`. Pinned environment: `docker/run.sh` (with `Dockerfile.x64`). ROS 1: default branch `main` is still catkin (`package.xml` 2.0.0, `catkin build elevation_mapping_cupy`, Docker in `docker/`). |
| Runs on | `ros2` README: Ubuntu 24.04, ROS 2 Jazzy, Python 3, NVIDIA GPU with CUDA 12. x86 Dockerfile only in repo; Jetson is user-reported territory (issues #124, #137, #72). |
| Inputs | `PointCloud2` subscribers configured per robot (`subscribers: lidar: {topic_name: /points, data_type: pointcloud}`), TF from `map_frame` (default `odom`) to `base_frame` (default `base_link`), sensor frames via TF. v2.1.0 notes say PointCloud2 is the supported surface on Jazzy; image/semantic fusion was removed from the supported path, then semantic workflows came back in v2.2.0 notes. |
| Outputs | `grid_map_msgs/GridMap` publishers configured by `publishers:` (layers e.g. `elevation`, `traversability`, `variance`, optional `observation_age`), services `/elevation_mapping_cupy/clear_map` (std_srvs/Trigger), `save_map` / `load_map` (grid_map_msgs/ProcessFile), `masked_replace` (grid_map_msgs/SetGridMap). |
| Key API / entry points | `ros2 launch elevation_mapping_cupy synthetic_depth_demo.launch.py` (self-contained), `ros2 launch elevation_mapping_cupy elevation_mapping.launch.py robot_config:=<setup>/base.yaml`. Config: `config/core/core_param.yaml` (resolution 0.1 m, map_length 20 m, frames, `use_chainer: false` => PyTorch backend), `config/core/plugin_config.yaml`, `config/setups/<robot>/`. ROS 1: `roslaunch elevation_mapping_cupy turtlesim_simple_example.launch` (TurtleBot3 waffle). |
| Time to first result | Estimate: 1-2 h for the Docker path and synthetic demo on an x86 + NVIDIA machine; longer on Jetson. |
| License | `LICENSE`: MIT. Traversability filter weights ship in-repo as `elevation_mapping_cupy/config/core/weights.dat`, no separate licence stated (repo MIT applies by default). |

## Minimal usage
Not run. From the `ros2` README.

```sh
git clone -b ros2 https://github.com/leggedrobotics/elevation_mapping_cupy.git ~/ros2_ws/src/elevation_mapping_cupy
cd ~/ros2_ws && rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-up-to semantic_sensor elevation_mapping_cupy --symlink-install
source install/setup.bash
ros2 launch elevation_mapping_cupy synthetic_depth_demo.launch.py
```

Minimal robot config (README):

```yaml
subscribers:
  lidar: {topic_name: /points, data_type: pointcloud}
publishers:
  elevation_map: {layers: [elevation, traversability, variance], basic_layers: [elevation], fps: 5.0}
```

## Wiring it into a nav stack
- Pose: it reads TF `map_frame` => `base_frame`, so any odometry that publishes TF works: [KISS-ICP](./prbonn__kiss-icp.md), [FAST-LIO](./hku-mars__fast_lio.md), [Isaac ROS Visual SLAM](./nvidia-isaac-ros__isaac_ros_visual_slam.md), or [robot_localization](./cra-ros-pkg__robot_localization.md).
- Output is [grid_map](./anybotics__grid_map.md); convert traversability to OccupancyGrid for [Navigation2](./ros-navigation__navigation2.md), or query it from an [OMPL](./ompl__ompl.md) validity checker.
- Plane segmentation (`convex_plane_decomposition_ros`) is ROS 1 only on `main`; ROS 2 port is open issue #139.

## Gotchas
- Two lines of code: `main` (ROS 1, catkin) and `ros2` (Jazzy). Releases v2.x target `ros2` / `release/jazzy`, not the default branch. Clone with `-b ros2`.
- v2.2.0 release notes: the remote GPU CI runner is not registered, validation was run locally on an RTX 4090; "A representative raw Ouster bag was not available"; they ask you to measure latency on your target. Performance numbers in those notes are RTX 4090 only.
- Jetson: #137 reports gradual FPS degradation on Orin AGX with a Livox MID360; #124 Orin docker, #141 "ros2 docker not working", #122 "ROS 2 Branch Many Issues".
- Default `map_frame` is `odom`; drift compensation assumes a mostly consistent odometry frame, large jumps (loop closure in the same frame) smear the map.
- Requires CuPy + PyTorch matching your CUDA; this is where most installs break, hence the Docker path.

## Alternatives
- [elevation_mapping](../../catalog/repos/leggedrobotics__elevation_mapping.md) - CPU predecessor, ROS 1.
- [isaac_ros_nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - GPU 3D TSDF/ESDF + 2D costmap slice, Nav2-ready.
- [traversability_estimation](../../catalog/repos/leggedrobotics__traversability_estimation.md) - CPU traversability on top of grid_map.

Sources: `README.md` (`main` and `ros2`), `LICENSE`, `elevation_mapping_cupy/package.xml` (both branches), `elevation_mapping_cupy/launch` listings, `config/core/core_param.yaml` (`ros2`), recursive tree of `ros2` (weights file), releases v1.0 v2.0.0 v2.1.0 v2.2.0 and their target branches, issues #72 #122 #124 #137 #139 #141 (github.com/leggedrobotics/elevation_mapping_cupy).
