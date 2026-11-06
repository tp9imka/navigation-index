# EGO-Swarm - integration card
<!-- about: repo:zju-fast-lab/ego-planner-swarm -->
Decentralized multi-quadrotor local planner (B-spline, ESDF-free) with its own simulator, so you can show several drones replanning through clutter in RViz in under an hour.

| | |
|---|---|
| Install | ROS 1 (`master`, README "Quick Start"): `sudo apt-get install libarmadillo-dev && git clone https://github.com/ZJU-FAST-Lab/ego-planner-swarm.git && cd ego-planner-swarm && catkin_make -j1` (README also gives `catkin_make -DCMAKE_BUILD_TYPE=Release -j1`). ROS 2: branch `ros2_version` (README there): needs PCL/VTK, then `colcon build`; README tells you to switch to CycloneDDS (`sudo apt install ros-humble-rmw-cyclonedds-cpp`, `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`). No releases or tags. |
| Runs on | `master`: Ubuntu 16.04/18.04/20.04 with ROS 1 desktop-full (README). `ros2_version`: ROS 2 Humble (from its README commands). CPU by default; optional CUDA depth rendering in the simulated `local_sensing` package (`set(ENABLE_CUDA true)` and fix the `compute_61` gencode). |
| Inputs | Per drone `i`: odometry `/drone_i_<odometry_topic>` (nav_msgs/Odometry), and either depth image `/drone_i_<depth_topic>` + camera pose `/drone_i_<camera_pose_topic>` or a point cloud `/drone_i_<cloud_topic>` for the local map (`advanced_param.xml` remaps). Goals: `fsm/flight_type` 1 = manual goal from `/move_base_simple/goal` (RViz 2D Nav Goal), 2 = preset waypoints `point0_x..point4_z` started by `/traj_start_trigger` (`ego_replan_fsm.cpp/.h`). |
| Outputs | `/drone_i_planning/bspline` (`traj_utils/Bspline`), shared swarm trajectories on `/broadcast_bspline` (`traj_utils/Bspline`), `traj_server` => `drone_i_planning/pos_cmd` (`quadrotor_msgs/PositionCommand`: position, velocity, acceleration, yaw). |
| Key API / entry points | `roslaunch ego_planner simple_run.launch`, `rviz.launch`, `swarm.launch`, `swarm_large.launch`, `single_run_in_sim.launch`, `run_in_sim.launch` (per-drone include) and `advanced_param.xml` (all tuning, `max_vel`, `max_acc`, `planning_horizon`, `grid_map/resolution` 0.1). Nodes `ego_planner_node`, `traj_server`. `rosmsg_tcp_bridge/launch/bridge.launch` for sharing trajectories between machines. ROS 2: `ros2 launch ego_planner rviz.launch.py`, `single_run_in_sim.launch.py`, `swarm.launch.py`. |
| Time to first result | Estimate: 30-60 min on Ubuntu 20.04 + Noetic (catkin build plus RViz goal clicks). Real drone: days (odometry, depth, controller bridge). |
| License | `LICENSE`: GPL-3.0 (README also says GPLv3 and gives a contact for commercial inquiries). `src/planner/drone_detect` carries its own LICENSE file. No weights. |

## Minimal usage
Not run. From README.

```sh
sudo apt-get install libarmadillo-dev
git clone https://github.com/ZJU-FAST-Lab/ego-planner-swarm.git
cd ego-planner-swarm && catkin_make -DCMAKE_BUILD_TYPE=Release -j1
source devel/setup.bash && roslaunch ego_planner rviz.launch     # terminal 1
source devel/setup.bash && roslaunch ego_planner swarm.launch    # terminal 2, then click 2D Nav Goal
```

## Wiring it into a nav stack
- Odometry in: any VIO/LIO that gives nav_msgs/Odometry in a common world frame per drone, e.g. [OpenVINS](./rpng__open_vins.md), [FAST-LIO](./hku-mars__fast_lio.md), or [Isaac ROS Visual SLAM](./nvidia-isaac-ros__isaac_ros_visual_slam.md). Swarm avoidance assumes all drones share that frame; there is no relative-localization fusion in the planner.
- Commands out: `quadrotor_msgs/PositionCommand` is not a PX4/ArduPilot type. Write a small bridge to [MAVROS](./mavlink__mavros.md) `setpoint_raw/local` (PositionTarget) or to [px4_ros_com](./px4__px4_ros_com.md) `TrajectorySetpoint`. Issue #19 asks about Gazebo + PX4 SITL; there is no shipped PX4 bridge.
- Depth-only mapping: issue #84 discusses LiDAR instead of a depth camera; the grid map accepts `PointCloud2` on `grid_map/cloud`.

## Gotchas
- `catkin_make -j1` is in the README for a reason (generated message dependencies); parallel builds may fail on first run.
- The default sim uses `fake_drone` (commands converted straight to odometry, no dynamics). README: switch to `quadrotor_simulator_so3` in `simulator.xml` for dynamics; the author reports about 15 drones max on an i7-9700KF with dynamics.
- README asks you to set the CPU governor to `performance` because planning cycles are too short for frequency scaling.
- `ros2_version` README reports "significant lag" with FastDDS and switches to CycloneDDS; the cause is not identified.
- Activity: last commits on `master` and `ros2_version` are README updates (2025-03); treat it as a research release.
- GPL-3.0 applies to anything you link into the planner.
- Open issue #76 is a `std::runtime_error` termination at start; check your parameter file if you hit it.

## Alternatives
- [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md) - single-drone version with less moving parts.
- [MADER](../../catalog/repos/mit-acl__mader.md) - decentralized multi-UAV planner that also handles dynamic obstacles.
- [OMPL](./ompl__ompl.md) - global sampling-based planning when you do not need reactive replanning.

Sources: `README.md` (`master` and `ros2_version`), `LICENSE`, `src/planner/plan_manage/launch/advanced_param.xml`, `run_in_sim.launch`, launch directory listing, `src/planner/plan_manage/src/ego_replan_fsm.cpp`, `include/plan_manage/ego_replan_fsm.h`, branch list and latest commits, issues #5 #19 #76 #81 #84 (github.com/ZJU-FAST-Lab/ego-planner-swarm).
