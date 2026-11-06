# KISS-ICP - integration card
<!-- about: repo:prbonn/kiss-icp -->
LiDAR-only odometry (point-to-point ICP, adaptive threshold, voxel-hash local map) that runs from `pip install` on a rosbag, MCAP or KITTI folder with almost no parameters and no IMU.

| | |
|---|---|
| Install | `pip install kiss-icp` (optional viewer and extras: `pip install "kiss-icp[all]"`, which pulls Open3D). ROS 2: `cd ~/ros2_ws/src && git clone https://github.com/PRBonn/kiss-icp && cd .. && colcon build --packages-select kiss_icp`. Latest release v1.3.0 (2026-04-26). |
| Runs on | CPU only (C++ core with pybind, TBB threads). PyPI wheels are built by cibuildwheel on `ubuntu-24.04`, `ubuntu-24.04-arm`, `windows-2022`, `macos-15` (`.github/workflows/pypi.yml`), so Linux aarch64 (Jetson) and Apple Silicon get wheels, subject to your Python version. `requires-python >= 3.8`. ROS 2 supported; ROS 1 deprecated, last ROS 1 release v0.3.0 (README). |
| Inputs | Python: `KissICP.register_frame(frame, timestamps)` with an Nx3 numpy point array and per-point timestamps (used for deskew). CLI dataloaders in `python/kiss_icp/datasets/`: generic folders (.bin/.pcd/.ply etc.), rosbag (ROS 1/2 via `rosbags`), mcap, kitti, kitti_raw, mulran, nclt, ncd, ouster pcap, nuscenes, boreas, helipr, apollo, tum. ROS 2 node subscribes `pointcloud_topic` (remapped from launch arg `topic`), `sensor_msgs/PointCloud2`, SensorDataQoS. |
| Outputs | CLI writes `<sequence>_poses.npy`, `<sequence>_poses_kitti.txt` and `<sequence>_poses_tum.txt` into a results dir (`pipeline.py`). ROS 2 publishes `kiss/odometry` (nav_msgs/Odometry), TF `odom_lidar` => `base_frame` (default frame `odom_lidar`, `publish_odom_tf`, `invert_odom_tf` params), and debug clouds `kiss/frame`, `kiss/keypoints`, `kiss/local_map` when `publish_debug_clouds` is on. |
| Key API / entry points | CLIs `kiss_icp_pipeline <data> [--dataloader X] [--config f.yaml] [--visualize] [--topic T] [--sequence S] [--n-scans N] [--jump J]` and `kiss_icp_dump_config` (`pyproject.toml` scripts, `tools/cmd.py`). Python `kiss_icp.kiss_icp.KissICP(config)` with `.register_frame()`, `.last_pose` (4x4), `.local_map`; `kiss_icp.pipeline.OdometryPipeline`. ROS 2: `ros2 launch kiss_icp odometry.launch.py topic:=<topic> [bagfile:=...] [visualize:=false] [config_file:=...] [base_frame:=...]`. |
| Time to first result | Estimate: 15-30 min with pip and a KITTI sequence or an existing bag; 1 h for a ROS 2 colcon build. |
| License | GitHub metadata: MIT. `ros/` also carries its own LICENSE file. No weights. |

## Minimal usage
From README and `python/README.md`. This listing was not run as written; the Python API ran on KITTI 04 in the hub (see Verified in this hub).

```sh
pip install "kiss-icp[all]"
kiss_icp_dump_config                     # writes kiss_icp.yaml (write_config default name)
kiss_icp_pipeline --visualize ~/data/kitti/sequences/00 --dataloader kitti
kiss_icp_pipeline ~/bags/run1.mcap --topic /ouster/points
```

Python, per scan:

```python
from kiss_icp.kiss_icp import KissICP
from kiss_icp.config import load_config
cfg = load_config(None)          # or a yaml path; voxel_size defaults to max_range / 100
cfg.data.max_range = 100.0
odom = KissICP(cfg)
odom.register_frame(points_nx3, timestamps_n)
pose_4x4 = odom.last_pose
```

Note: set `max_range` before `load_config` (via the yaml) if you want the derived `voxel_size` to follow it; here it stays at the default-derived value.

## Wiring it into a nav stack
- `kiss/odometry` => [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md) (as odom input next to IMU / wheel / GNSS) or => [MAVROS](../../catalog/repos/mavlink__mavros.md) `odometry/out`. Set `base_frame` so TF lands on `base_link` rather than the LiDAR frame (closed issue #489: "odometry and local map showing on the wrong side of the robot in Rviz"; check `base_frame` and `invert_odom_tf` first).
- Loop closure: [KISS-SLAM](../../catalog/repos/prbonn__kiss-slam.md) or [MapClosures](../../catalog/repos/prbonn__mapclosures.md) on top.
- Need an IMU in the loop: [RKO-LIO](../../catalog/repos/prbonn__rko_lio.md) from the same lab, or FAST-LIO2 below.
- Evaluate with [evo](../../catalog/repos/michaelgrupp__evo.md) using the `_tum.txt` output.

## Gotchas
- Deskew needs per-point timestamps; if the cloud has none, disable `data.deskew` or expect smearing in fast motion. Several closed issues on deskew behaviour (#447, #458) and odd scan patterns (#483 Unitree L2).
- ARM throughput: issue #508 reports 3-5 FPS on an embedded ARM board with an Ouster MulRan sequence, `voxel_size` 1.0 and `max_num_iterations` 200; maintainer says 10 FPS "should be more than doable with some tuning". No GPU path.
- Pure LiDAR: degrades in geometrically degenerate scenes (long corridors, open fields, tunnels) where IMU-coupled LIO holds better.
- ROS 1 users must pin v0.3.0.
- The node publishes odometry only; no map save, no relocalization.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- **KITTI 04, default config** (100 m range, 1 m voxel, deskew on), 271 scans / 393.6 m: ATE RMSE 0.23 m (SE3 aligned), final origin-anchored error 0.48 m = 0.12 %, KITTI t_rel 0.41 %. 04 is short and straight: treat as a best case. kiss-icp 1.3.0 - [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md).
- **Throughput on Apple M2 Max (native, CPU)**: 271 scans of 125,717 points in 12.3 s and 19.7 s (22 and 14 fps, host shared), peak RSS 159-167 MB - [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md).
- KITTI GT is in the rectified cam0 frame and KISS-ICP runs in the velodyne frame; conjugate with `T_cam0_velo` before scoring (agrees with OXTS within 2 cm) - [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md).

## Alternatives
- [FAST-LIO2](./hku-mars__fast_lio.md) - when a synced IMU is available and motion is aggressive; GPL-2.0.
- [KISS-SLAM](../../catalog/repos/prbonn__kiss-slam.md) - same family with loop closure and map output.
- [small_gicp](../../catalog/repos/koide3__small_gicp.md) or [GLIM](../../catalog/repos/koide3__glim.md) - if you want your own registration loop or a GPU-accelerated full mapping system.

Sources: `README.md`, `python/README.md`, `python/pyproject.toml`, `python/kiss_icp/config/parser.py`, `python/kiss_icp/kiss_icp.py`, `python/kiss_icp/pipeline.py`, `python/kiss_icp/tools/cmd.py`, `ros/README.md`, `ros/src/OdometryServer.cpp`, `ros/src/OdometryServer.hpp`, `ros/launch/odometry.launch.py`, `ros/package.xml`, `.github/workflows/pypi.yml`, release v1.3.0, issues #447 #458 #483 #489 #508 (github.com/PRBonn/kiss-icp).
