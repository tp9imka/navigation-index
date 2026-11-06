# KISS-SLAM - integration card
<!-- about: repo:prbonn/kiss-slam -->
Offline LiDAR-only SLAM on top of KISS-ICP: local submaps, MapClosures loop detection and a g2o pose graph, with optional global map, 3D occupancy and a Nav2-style 2D `map.png` + `map.yaml`; turns a bag or KITTI folder into a loop-closed trajectory and map with one command.

| | |
|---|---|
| Install | `pip install kiss-slam` (PyPI name `kiss-slam`, latest 0.0.2, same as GitHub release v0.0.2 of 2025-05-15). Dev/source: `sudo apt install git python3-pip libeigen3-dev libsuitesparse-dev`, `git clone https://github.com/PRBonn/kiss-slam.git && cd kiss-slam && make editable`. Paper reproduction: `git checkout IROS25`. |
| Runs on | CPU only. PyPI 0.0.2 wheels: CPython 3.8-3.13 on manylinux x86_64 and macOS 11 arm64 only; no Linux aarch64 (Jetson) or Windows wheels, so those build from sdist (g2o, SuiteSparse, Eigen fetched by CMake). Dependencies: `kiss-icp>=1.2.3`, `map_closures>=2.0.2`, `open3d>=0.19.0`, `pydantic>=2`, `pydantic-settings`. No ROS node. |
| Inputs | Any KISS-ICP dataloader (`--dataloader`): generic point cloud folders, ROS 1/2 bags (`--topic`), MCAP, KITTI, MulRan, NCLT, Ouster pcap (`--meta` for the JSON), etc. Point clouds as Nx3 with per-point timestamps for deskew. Config `kiss_slam.yaml` (pydantic): `odometry.preprocessing.max_range`, `local_mapper.voxel_size` (0.5), `local_mapper.splitting_distance` (100.0 m), `loop_closer.overlap_threshold` (0.4), `occupancy_mapper.resolution` (0.5), `z_min`/`z_max`, `pose_graph_optimizer.max_iterations` (10), `out_dir` (`slam_output`). |
| Outputs | Results dir under `out_dir`: optimized poses via the inherited KISS-ICP `OdometryPipeline` writers (`_poses.npy`, `_poses_kitti.txt`, `_poses_tum.txt`), `trajectory.g2o`, `local_maps/local_map_graph.g2o` and `local_maps/plys/<id>.ply` per local map, `trajectory.png` (trajectory with closures drawn in red), config and log. With `--refuse-scans`: `occupancy_grid/occupancy_pcd.ply` and `occupancy_grid/map2d/map.png` + `map.yaml` (image, resolution, origin, occupied/free thresholds, `negate: 0`). |
| Key API / entry points | CLIs `kiss_slam_pipeline <data> [--dataloader X] [--config f.yaml] [--topic T] [--sequence S] [-n N] [-j J] [-v] [-rs/--refuse-scans] [-m meta.json]` (`kiss_slam.tools.cli:run`) and `kiss_slam_dump_config` (`kiss_slam.config.config:write_config`, writes `kiss_slam.yaml`). Python: `kiss_slam.pipeline.SlamPipeline(dataset, config_file, visualize, n_scans, jump, refuse_scans).run()`, `kiss_slam.slam.KissSLAM(config).process_scan(scan, timestamps)`, `.fine_grained_optimization()`; `kiss_slam.occupancy_mapper.OccupancyGridMapper`. |
| Time to first result | Estimate: 20-40 min on x86_64 Linux or Apple Silicon with pip and a KITTI sequence or an existing bag; longer on aarch64 (source build). |
| License | LICENSE file: MIT. Fetched third-party deps under `kiss_slam/kiss_slam_pybind/3rdparty/` (g2o, SuiteSparse, Eigen, Bonxai) each carry their own LICENSE file; SuiteSparse in particular is not uniformly permissive, so check before shipping a binary. No weights. |

## Minimal usage
Not run. From README.

```sh
pip install kiss-slam
kiss_slam_dump_config                          # writes kiss_slam.yaml
kiss_slam_pipeline --help
kiss_slam_pipeline ~/data/kitti/sequences/00 --dataloader kitti --config kiss_slam.yaml
kiss_slam_pipeline ~/bags/run1 --topic /ouster/points --refuse-scans   # + occupancy maps (see gotchas)
```

README tip for indoor runs: set `odometry.preprocessing.max_range: 50.0` (voxel size follows to 0.5) and shrink `local_mapper.splitting_distance`.

## Wiring it into a nav stack
- `occupancy_grid/map2d/map.png` + `map.yaml` is in the shape [Nav2](./ros-navigation__navigation2.md) `map_server` loads, giving a 2D prior map from a single LiDAR drive.
- The per-local-map `.ply` files (`local_maps/plys/`) or the occupancy point cloud are a prior map for scan-to-map relocalization with [small_gicp](./koide3__small_gicp.md) or [FAST_LIO_LOCALIZATION](./hviktortsoi__fast_lio_localization.md).
- Odometry front end is [KISS-ICP](./prbonn__kiss-icp.md); for IMU-aided odometry use [RKO-LIO](./prbonn__rko_lio.md) (same lab).
- Loop detection comes from [MapClosures](../../catalog/repos/prbonn__mapclosures.md). Evaluate trajectories with [evo](./michaelgrupp__evo.md).

## Gotchas
- Batch/offline only: the pose graph is optimized at the end (`fine_grained_optimization` after the last scan). Maintainer in closed issue #49: no relocalization support and no streaming API at that time; "definitely runs faster than" 10 Hz on Avia data (no number).
- `--refuse-scans` in PyPI 0.0.2 calls `map_closures.align_map_to_local_ground`, which issue #59 reports does not exist in any released `map_closures`. `main` now uses `closer.detector.get_ground_alignment_from_id(0)`. If you need occupancy maps, install from source.
- Dependency friction: closed issue #57 (ouster-sdk vs typer `click` pin clash, fixed in KISS-ICP main at the time), #56 (rosbags not found, it is optional), #48 (Open3D now a hard dependency).
- LiDAR only. Long degenerate corridors and open fields hurt KISS-ICP odometry, and no IMU or GNSS factor exists to hold it.
- Open issue #61: identity information matrices on loop closures can degrade local accuracy on KITTI.
- Last release 2025-05; last `main` commit 2025-12.

## Alternatives
- [GLIM](../../catalog/repos/koide3__glim.md) - full online LiDAR(-IMU) mapping with GPU options.
- [LIO-SAM](./tixiaoshan__lio-sam.md) - online ROS SLAM with IMU and GPS factors.
- [RTAB-Map ROS](./introlab__rtabmap_ros.md) - online mapping plus localization mode with a reusable database.

Sources: `README.md`, `LICENSE`, `pyproject.toml`, `kiss_slam/tools/cli.py`, `kiss_slam/pipeline.py` (main and tag v0.0.2), `kiss_slam/config/config.py`, `kiss_slam/occupancy_mapper.py`, repo tree, tags, release v0.0.2, PyPI JSON for `kiss-slam`, issues #48 #49 #56 #57 #59 #61 (github.com/PRBonn/kiss-slam).
