# TARE Planner - integration card
<!-- about: repo:caochao39/tare_planner -->
Hierarchical exploration planner (dense local horizon + sparse global TSP) from CMU's SubT team that emits a single `/way_point` for a ground robot; you get autonomous coverage of an unknown indoor/tunnel/campus scene inside the CMU simulator.

| | |
|---|---|
| Install | Pick the branch for your ROS: `melodic-noetic` (README on default branch: `git checkout melodic-noetic && catkin_make`), `humble-jazzy` (`git checkout humble-jazzy && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release`), or `lyrical` (most recent commit, 2026-05). First set up the [Autonomous Exploration Development Environment](../../catalog/repos/hongbiaoz__autonomous_exploration_development_environment.md) on the matching branch and download its simulation worlds. No releases or tags. |
| Runs on | Ubuntu 18.04/20.04 (ROS 1) or 22.04/24.04 (Humble/Jazzy) per README. CPU only. Bundles a prebuilt OR-Tools in `src/tare_planner/or-tools`; README says it now works on AMD64 and ARM, but on ARM you must download the matching OR-Tools binary (e.g. `or-tools_arm64_debian-11_cpp_v9.8.3296.tar.gz`) and replace `include` and `lib`. |
| Inputs | From the dev environment stack (`config/<scenario>.yaml`): `/registered_scan` (PointCloud2, scans already in the map frame), `/state_estimation_at_scan` (nav_msgs/Odometry), `/terrain_map` and `/terrain_map_ext` (terrain analysis clouds), optional `/navigation_boundary`, `/sensor_coverage_planner/coverage_boundary`, `/sensor_coverage_planner/nogo_boundary` (geometry_msgs/PolygonStamped), `/start_exploration` (std_msgs/Bool), `/joy`, `/reset_waypoint` (std_msgs/Empty). Types from `sensor_coverage_planner_ground.h`. |
| Outputs | `/way_point` (geometry_msgs/PointStamped) consumed by the dev environment's local planner, plus `exploration_finish` (Bool), `/runtime` (Float32), `runtime_breakdown`, and several nav_msgs/Path debug outputs (global, local TSP, exploration path). |
| Key API / entry points | `ros2 launch tare_planner explore_<garage|campus|indoor|tunnel|forest|matterport>.launch` (or `roslaunch` on ROS 1) next to `ros2 launch vehicle_simulator system_<env>.launch`. Generic `explore.launch` takes `scenario:=<yaml name>`, `rviz`, `use_sim_time`. Node `tare_planner_node`. Parameters in `config/*.yaml` (`kAutoStart`, `kExtendWayPoint`, topic names). |
| Time to first result | Estimate: 1-2 h, most of it building the dev environment and downloading worlds. Real robot: needs the dev environment's terrain analysis + local planner ported to your platform. |
| License | No LICENSE file on any branch (checked `melodic-noetic`, `humble-jazzy`, `lyrical`). `package.xml` says `BSD`; GitHub metadata has no licence; open issue #27 asks for one. Treat as unlicensed for redistribution. Bundled OR-Tools is Google's (Apache-2.0 upstream, not restated in this repo). |

## Minimal usage
Not run. From the `humble-jazzy` README.

```sh
# after building autonomous_exploration_development_environment (humble-jazzy branch) in ~/aede
git clone https://github.com/caochao39/tare_planner.git && cd tare_planner
git checkout humble-jazzy
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
# terminal 1, in the dev-environment workspace
source install/setup.sh && ros2 launch vehicle_simulator system_garage.launch
# terminal 2, in tare_planner
source install/setup.sh && ros2 launch tare_planner explore_garage.launch
```

## Wiring it into a nav stack
- TARE is the top layer only. Below it you need the CMU stack: terrain analysis => `/terrain_map`, local planner + path follower consuming `/way_point`. For a real robot, feed `/registered_scan` and `/state_estimation_at_scan` from a LIO such as [FAST-LIO](./hku-mars__fast_lio.md) or LOAM (issue #29 uses A-LOAM).
- Aerial use is not supported out of the box (issue #25 "how to use in uav" has no answer). The vertical structure is assumed to be a ground vehicle.
- Pair with [FAR Planner](../../catalog/repos/michaelfyang__far_planner.md) from the same group for goal-directed route planning in the same stack.

## Gotchas
- No licence file (issue #27); fine for a hackathon demo, a blocker for shipping.
- Issue #29: on a real robot it reports "Exploration completed, returning home" immediately with the warning "Cannot get candidate viewpoints, skipping this round". Usually means scans or terrain map are not arriving in the expected frame/topics; check `/registered_scan` is in the map frame.
- Issue #26: `KeyposeGraph::AddKeyposeNode: Nearest keypose ind out of range: -1`.
- Issue #28: prebuilt OR-Tools fails on Melodic due to GLIBC version.
- Branch must match both ROS distro and the dev-environment branch.

## Alternatives
- [GBPlanner](../../catalog/repos/ntnu-arl__gbplanner_ros.md) - graph-based exploration used on legged and aerial robots in SubT.
- [FUEL](../../catalog/repos/hkust-aerial-robotics__fuel.md) - fast frontier-based exploration for quadrotors.
- [EGO-Swarm](./zju-fast-lab__ego-planner-swarm.md) - if you need multi-drone local planning to given goals rather than coverage.

Sources: `README.md` (`melodic-noetic`, `humble-jazzy`), `src/tare_planner/package.xml` on three branches, `src/tare_planner/launch/explore.launch` and directory listing, `src/tare_planner/config/garage.yaml`, `include/sensor_coverage_planner/sensor_coverage_planner_ground.h`, branch commit dates, issues #25 #26 #27 #28 #29 (github.com/caochao39/tare_planner).
