# small_gicp - integration card
<!-- about: repo:koide3/small_gicp -->
Header-only C++17 point cloud registration (ICP, point-to-plane ICP, GICP, VGICP) with parallel downsampling, KdTree and covariance estimation, plus pip-installable Python bindings; the building block when you need scan-to-map alignment inside your own localizer.

| | |
|---|---|
| Install | Python: `pip install small_gicp` (PyPI name `small-gicp`, 1.0.1 uploaded 2026-06-13, `requires-python >= 3.7`). C++: header-only, or build the helper library: `sudo apt-get install libeigen3-dev libomp-dev && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j && sudo make install`. Examples: `cmake .. -DBUILD_EXAMPLES=ON`. Also has a `package.xml` (format 3, `build_type` cmake) so it builds inside a colcon workspace. Latest GitHub release is v1.0.0 (2024-08-09); PyPI is ahead at 1.0.1. |
| Runs on | CPU only; README states GPU implementations are not included. OpenMP or TBB backends. PyPI 1.0.1 wheels for CPython 3.10-3.14 on manylinux x86_64, manylinux aarch64 (Jetson-class Linux), macOS 14 arm64, win_amd64. C++17 required; PCL interface needs PCL >= 1.11. |
| Inputs | Python: Nx3 or Nx4 float64 numpy arrays, or `small_gicp.PointCloud`. C++: `std::vector<Eigen::Vector(3|4)(f|d)>`, `small_gicp::PointCloud`, or `pcl::PointCloud<PointT>` via the PCL interface; any custom cloud via traits. Initial guess as a 4x4 / `Eigen::Isometry3d` `T_target_source`. Units are whatever your points are in (metres in practice; `downsampling_resolution` and `max_correspondence_distance` use the same unit). |
| Outputs | `RegistrationResult`: `T_target_source` (4x4), `converged`, `iterations`, `num_inliers`, `H` (6x6 final Hessian), `b`, `e` (final error). The Hessian is usable as an information matrix for a factor graph or a degeneracy check. |
| Key API / entry points | Python: `small_gicp.align(target, source, [target_tree], init_T_target_source=..., registration_type='GICP'|'ICP'|'PLANE_ICP'|'VGICP', voxel_resolution, downsampling_resolution, max_correspondence_distance, num_threads)`, `small_gicp.preprocess_points(points, downsampling_resolution, num_neighbors, num_threads)` => `(cloud, tree)`, `PointCloud`, `KdTree`, `voxelgrid_sampling`, `estimate_covariances`. C++: `small_gicp::align()` and `preprocess_points()` in `registration_helper.hpp`; `Registration<GICPFactor, ParallelReductionOMP>` template; `RegistrationPCL<PointT, PointT>` drop-in for `pcl::Registration` (`setRegistrationType("VGICP")`). |
| Time to first result | Estimate: 10 min with `pip install small_gicp` and two PLY files (e.g. the repo's `data/target.ply` / `data/source.ply`); 30 min for the C++ examples. |
| License | LICENSE file: MIT (Kenji Koide). Bundles nanoflann (BSD) and Sophus (MIT) headers. No weights. |

## Minimal usage
Not run. Adapted from README Python examples B and D.

```python
import numpy as np, open3d as o3d, small_gicp
tgt = np.asarray(o3d.io.read_point_cloud("data/target.ply").points)
src = np.asarray(o3d.io.read_point_cloud("data/source.ply").points)
target, target_tree = small_gicp.preprocess_points(tgt, downsampling_resolution=0.25)
source, source_tree = small_gicp.preprocess_points(src, downsampling_resolution=0.25)
result = small_gicp.align(target, source, target_tree)
print(result.converged, result.num_inliers)
print(result.T_target_source)
```

C++ examples: `./build/01_basic_registration`, `./build/02_basic_registration_pcl`, `./build/03_registration_template` after `cmake .. -DBUILD_EXAMPLES=ON && make -j`.

## Wiring it into a nav stack
- Map-based relocalization: crop a prior map (from [LIO-SAM](./tixiaoshan__lio-sam.md), [KISS-SLAM](./prbonn__kiss-slam.md) or [GLIM](../../catalog/repos/koide3__glim.md)) around the odometry pose and align the live scan with GICP or VGICP; the same pattern [FAST_LIO_LOCALIZATION](./hviktortsoi__fast_lio_localization.md) implements with Open3D ICP. Publish the result as a map => odom correction or a pose to [robot_localization](./cra-ros-pkg__robot_localization.md).
- Factor graphs: feed `T_target_source` and `H` into a [GTSAM](./borglab__gtsam.md) between-factor.
- Cookbook odometry pipelines (`src/benchmark/odometry_benchmark_*.cpp`, `src/example/kitti_odometry.py`) give scan-to-scan and scan-to-model (iVox / Gaussian voxel map) odometry to start from.

## Gotchas
- No ROS node and no topics: it is a library. You write the subscriber and TF glue.
- Python default `num_threads=1`; set it explicitly or it runs single-threaded.
- Issue #89 (open): user reports worse results than fast_gicp on the same data with a "PCD is too small" warning, so check point counts after downsampling. Issue #134 (open): KdTree ICP reported slower than Open3D in one case.
- Issue #33 (open): the default PCL shipped with ROS Noetic does not work with the PCL interface CMake usage; matches the README "PCL >= 1.11" note.
- Issue #64 (closed): segfault on macOS 14.5 / Apple M2 was reported for an earlier build; current wheels target macOS 14 arm64.
- Issue #105 (open) questions the Jacobian shape in `plane_icp_factor.hpp`; prefer GICP/VGICP if point-to-plane misbehaves.

## Alternatives
- [fast_gicp](../../catalog/repos/koide3__fast_gicp.md) - predecessor with CUDA (VGICP-CUDA) kernels, if a GPU path matters more than maintenance.
- [KISS-ICP](./prbonn__kiss-icp.md) - a complete LiDAR odometry pipeline rather than a registration library.
- Open3D / PCL registration - already in many stacks; README benchmarks claim small_gicp is faster (author numbers, not reproduced here).

Sources: `README.md`, `LICENSE`, `pyproject.toml`, `package.xml`, release v1.0.0, PyPI JSON for `small-gicp` 1.0.1 (file list), issues #33 #64 #89 #105 #134 (github.com/koide3/small_gicp).
