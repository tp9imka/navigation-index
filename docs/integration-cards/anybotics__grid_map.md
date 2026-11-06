# Grid Map - integration card
<!-- about: repo:anybotics/grid_map -->
Multi-layer 2.5D grid map library (Eigen storage, circular buffer, iterators, filters, RViz plugin, converters to OccupancyGrid / PointCloud2 / OpenCV / costmap_2d / OctoMap); the common map container for elevation, traversability and cost layers in ROS.

| | |
|---|---|
| Install | ROS 2 binaries: rosdistro releases grid_map 2.0.1 for Humble and 2.2.2 for Jazzy, so `sudo apt install ros-$ROS_DISTRO-grid-map` (the ROS 2 branch READMEs strike this line through, but the packages are in rosdistro; issue #526 tracks binaries for newer distros, #544 Lyrical). Source: clone the branch matching your distro (`humble`, `jazzy`, `rolling`; `master` is ROS 1) into a workspace, `rosdep install --from-paths src --ignore-src -y`, `colcon build`. The rolling README also has a `tools/ros2_dependencies.repos` vcs step (issue #512 reports a 404 on that wget). |
| Runs on | CPU, Linux. `grid_map_core` depends only on Eigen (no ROS). ROS 1 Noetic on `master`; ROS 2 Humble/Iron/Jazzy/Rolling branches listed as maintained in the README. |
| Inputs | Your own data via C++ API, or conversions: `GridMapRosConverter::fromMessage`, `fromOccupancyGrid`, `fromImage` (grid_map_cv), PCL clouds/meshes (grid_map_pcl), `costmap_2d` (grid_map_costmap_2d), OctoMap (grid_map_octomap). Frame is a string `map.setFrameId("map")`; positions in metres. |
| Outputs | `grid_map_msgs/msg/GridMap` messages, `toOccupancyGrid`, `toPointCloud` (one-way: PointCloud2 => grid map is not supported, README note and issue #158), OpenCV images, signed distance field (`grid_map_sdf`), filter-chain results (normals, inpainting, slope, roughness via `grid_map_filters`). |
| Key API / entry points | `grid_map::GridMap map({"elevation"})`, `setGeometry(Length, resolution[, Position])`, `add(layer, value)`, `at(layer, index)`, `atPosition(layer, Position)`, `getPosition(index, pos)`, `getIndex(pos, idx)`, `isInside(pos)`, `move(pos)` (shift without copy), `getSubmap(...)`; iterators `GridMapIterator`, `SubmapIterator`, `CircleIterator`, `PolygonIterator`, `LineIterator`; `grid_map::GridMapRosConverter::toMessage(map)` (returns `std::unique_ptr` on ROS 2). Demos: `ros2 launch grid_map_demos simple_demo_launch.py`, `tutorial_demo_launch.py`, `filters_demo_launch.py`, `image_to_gridmap_demo_launch.py`, `iterators_demo_launch.py`. |
| Time to first result | Estimate: 15 min with apt binaries and `simple_demo_launch.py` in RViz; 30-60 min from source. |
| License | `LICENSE`: BSD-3-Clause. No weights or data. |

## Minimal usage
Not run. Adapted from `grid_map_demos/src/simple_demo_node.cpp` (rolling).

```cpp
#include <grid_map_ros/grid_map_ros.hpp>
auto pub = node->create_publisher<grid_map_msgs::msg::GridMap>("grid_map", rclcpp::QoS(1).transient_local());
grid_map::GridMap map({"elevation"});
map.setFrameId("map");
map.setGeometry(grid_map::Length(1.2, 2.0), 0.03);     // metres, metres/cell
for (grid_map::GridMapIterator it(map); !it.isPastEnd(); ++it) {
  grid_map::Position p; map.getPosition(*it, p);
  map.at("elevation", *it) = 0.1 * p.x();
}
map.setTimestamp(node->now().nanoseconds());
pub->publish(grid_map::GridMapRosConverter::toMessage(map));
```

```sh
ros2 launch grid_map_demos simple_demo_launch.py
```

## Wiring it into a nav stack
- Producer upstream: [elevation_mapping_cupy](./leggedrobotics__elevation_mapping_cupy.md) and the original [elevation_mapping](../../catalog/repos/leggedrobotics__elevation_mapping.md) publish `grid_map_msgs/GridMap`.
- Consumer downstream: convert a traversability layer to `nav_msgs/OccupancyGrid` with `toOccupancyGrid` for [Navigation2](./ros-navigation__navigation2.md); there is no Nav2 costmap plugin in this repo (open issue #534 "Plugin for nav2?").
- Use as the state validity source for [OMPL](./ompl__ompl.md) (`atPosition` lookup in the callback).
- DEM ingest: load a GeoTIFF tile through OpenCV/[GDAL](./osgeo__gdal.md) into an image and use `grid_map_cv` `GridMapCvConverter::addLayerFromImage` for terrain-referenced work.

## Gotchas
- ROS 2 package hygiene issues are open: #537-#539 (undeclared deps on `filters`, `grid_map_core`, `grid_map_cv`), #518 (apt 2.0.1 include/lib paths not set by CMake), #521 (compile problems).
- Eigen 5 compatibility is open (#528); pin Eigen 3.4 if your distro moves.
- `octomap_to_gridmap_demo_launch.py` is noted as not working in the ROS 2 README (pending octomap_server port).
- PointCloud2 => GridMap is one-way only (#158); rasterize clouds yourself or via `grid_map_pcl`.
- `master` (ROS 1) carries a squashed sync from ANYbotics' internal repo (commit message references git.anybotics.com); ROS 2 branches get separate releases.
- RViz plugin performance limits on large grids (#167).

## Alternatives
- [elevation_mapping_cupy](./leggedrobotics__elevation_mapping_cupy.md) - if you want the full GPU mapping pipeline rather than the container.
- Nav2 costmap_2d ([Navigation2](./ros-navigation__navigation2.md)) - for flat 2D occupancy only.
- [isaac_ros_nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - GPU 3D TSDF/ESDF instead of 2.5D layers.

Sources: `README.md` (`master`, `rolling`, `humble`, `jazzy`), `LICENSE`, `grid_map_core/include/grid_map_core/GridMap.hpp` (rolling), `grid_map_demos/src/simple_demo_node.cpp`, `grid_map_demos/launch` listing, branch list and latest commits, open issues #158 #167 #512 #518 #521 #526 #528 #534 #537 #538 #539 #544 (github.com/ANYbotics/grid_map); rosdistro `humble/` and `jazzy/distribution.yaml`.
