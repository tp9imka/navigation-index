# fuse - integration card
<!-- about: repo:locusrobotics/fuse -->
One-line: ROS 2 sensor-fusion framework where every sensor and motion model is a plugin that adds Ceres factors to a fixed-lag smoother or batch optimizer; use it when the robot_localization EKF cannot express what you need (delayed or out-of-order measurements, robust losses, custom constraints such as a map-match or range factor).

| | |
|---|---|
| Install | Binary on Jazzy, Kilted, Lyrical and Rolling (rosdistro `distribution.yaml`: jazzy release 1.1.6-1 from branch `jazzy`, kilted 1.2.7-1, lyrical and rolling 1.3.4-1, all three sourced from `rolling`): `sudo apt install ros-$ROS_DISTRO-fuse` (standard ROS package naming; `fuse` is the metapackage). Source: clone the matching branch into a colcon workspace, `rosdep install --from-paths src --ignore-src -y`, `colcon build`. Deps: Ceres (`libceres-dev`), Eigen, glog, Boost (`fuse_core/package.xml`). |
| Runs on | ROS 2 branches: `jazzy` (1.1.6), `kilted` (1.2.7), `lyrical`/`rolling` (1.3.4), `iron` (1.0.1, last commit 2024-10). No Humble branch and no Humble rosdistro entry (open issue #339). Default branch `devel` is ROS 1 (catkin, 0.15.0); `noetic-devel` is older ROS 1. CPU only, Linux. |
| Inputs | Built-in sensor models in `fuse_models` (all 2D): `Odometry2D` (`nav_msgs/Odometry`), `Imu2D` (`sensor_msgs/Imu`, yaw/yaw-rate/accel), `Pose2D` (`geometry_msgs/PoseWithCovarianceStamped`), `Twist2D`, `Acceleration2D`, plus `Unicycle2DIgnition` / `GraphIgnition` (initial state) and `Transaction` (raw fuse transactions). Configured per sensor in YAML with `topic`, frame and dimension lists. |
| Outputs | `fuse_models::Odometry2DPublisher` => `nav_msgs/Odometry` + TF (`map`/`odom`/`base_link` frames configurable); `fuse_publishers::Pose2DPublisher`, `Path2DPublisher`, `SerializedPublisher` (whole graph, for `fuse_viz` in RViz). |
| Key API / entry points | Executables `fuse_optimizers fixed_lag_smoother_node` and `batch_optimizer_node`. Plugin base classes `fuse_core::SensorModel`, `fuse_core::MotionModel`, `fuse_core::Publisher`, `fuse_core::Constraint`, `fuse_core::Variable`. Motion model `fuse_models::Unicycle2D`. Constraint library `fuse_constraints` has 2D and 3D absolute/relative pose, position and orientation constraints (`AbsolutePose3DStampedConstraint`, `RelativePose3DStampedConstraint`, `MarginalConstraint` ...); `fuse_variables` has 2D and 3D position/orientation/velocity/acceleration and landmark variables. Robust losses in `fuse_loss`. Tutorials: `fuse_tutorials fuse_simple_tutorial.launch.py`, `range_sensor_tutorial.launch.py` (custom sensor + constraint example in `src/range_sensor_model.cpp`, `range_constraint.cpp`). |
| Time to first result | Estimate: 30-60 min to run `fuse_simple_tutorial.launch.py` on the bundled TurtleBot3 bag and see `odom_filtered` in RViz (apt install on Jazzy). A custom sensor model is a day of C++ plugin work. Assumes ROS 2 Jazzy or Kilted. |
| License | GitHub: NOASSERTION. `LICENSE` and `package.xml`: BSD (3-clause text, Locus Robotics 2018). |

## Minimal usage
From `fuse_tutorials/launch/fuse_simple_tutorial.launch.py` and `config/fuse_simple_tutorial.yaml` on `jazzy`. Not run.

```bash
sudo apt install ros-jazzy-fuse
ros2 launch fuse_tutorials fuse_simple_tutorial.launch.py
# plays fuse_tutorials/data/turtlebot3.bag (--clock -l), starts fixed_lag_smoother_node as "state_estimator"
ros2 topic echo /odom_filtered
```

Config shape (abridged from the tutorial YAML):

```yaml
state_estimator:
  ros__parameters:
    optimization_frequency: 20.0
    lag_duration: 0.5
    motion_models: { unicycle_motion_model: { type: fuse_models::Unicycle2D } }
    sensor_models:
      initial_localization_sensor: { type: fuse_models::Unicycle2DIgnition, motion_models: [unicycle_motion_model], ignition: true }
      odometry_sensor: { type: fuse_models::Odometry2D, motion_models: [unicycle_motion_model] }
      imu_sensor: { type: fuse_models::Imu2D, motion_models: [unicycle_motion_model] }
    odometry_sensor: { topic: odom, twist_target_frame: base_footprint, linear_velocity_dimensions: [x, y], angular_velocity_dimensions: [yaw] }
    imu_sensor: { topic: imu, twist_target_frame: base_footprint, angular_velocity_dimensions: [yaw] }
    publishers: { filtered_publisher: { type: fuse_models::Odometry2DPublisher } }
    filtered_publisher: { topic: odom_filtered, base_link_frame_id: base_footprint, odom_frame_id: odom, map_frame_id: map, world_frame_id: odom, publish_tf: true }
```

## Wiring it into a nav stack
- Same topic contract as [robot_localization](./cra-ros-pkg__robot_localization.md): wheel odometry + IMU in, `nav_msgs/Odometry` + TF out, so [Nav2](./ros-navigation__navigation2.md) consumes either.
- GNSS-denied ground robot: feed lidar odometry ([KISS-ICP](./prbonn__kiss-icp.md)) or VIO ([OpenVINS](./rpng__open_vins.md)) as `Pose2D`/`Odometry2D` alongside wheel odometry; add GNSS as a `Pose2D` in a local ENU frame (convert with [pymap3d](./geospace-code__pymap3d.md)) and drop it during outages. There is no NavSatFix sensor model.
- Absolute fixes from vision geo-localization or terrain matching map naturally to an `AbsolutePose2DStampedConstraint` with your own covariance, which is the main reason to choose fuse over an EKF: late fixes are inserted at their own timestamp inside the lag window.
- Heavier factor-graph needs (IMU preintegration, 3D, iSAM2): [GTSAM](./borglab__gtsam.md). Ceres itself: [ceres-solver](../../catalog/repos/ceres-solver__ceres-solver.md).
- Workshop material with Docker: [roscon-uk-2025-se-workshop](../../catalog/repos/locusrobotics__roscon-uk-2025-se-workshop.md).
- Catalog: [fuse page](../../catalog/repos/locusrobotics__fuse.md).

## Gotchas
- 2D only out of the box: every `fuse_models` sensor/motion model is 2D on `jazzy`, `kilted` and `rolling`. 3D variables and constraints exist, but 3D sensor processing is an open request (#318, #226). Not a drop-in for an aerial 6-DoF estimator without writing your own models.
- No Humble: #339 (missing humble-devel) and #359 (closed) - teams on Humble must build `iron` or `jazzy` from source and fix API drift themselves, or move to Jazzy.
- Default GitHub branch is ROS 1 `devel`; cloning without `-b jazzy` (or `rolling`) gives you catkin packages.
- Ignition: the tutorial config declares an ignition sensor (`Unicycle2DIgnition` with `ignition: true`, `publish_on_startup: true`) to give the graph its prior; keep one in your config (behaviour without it not checked for this card).
- `lag_duration` and `optimization_frequency` trade latency vs CPU; measurements older than the lag window are dropped.
- Ceres builds from source are slow on small boards; prefer the apt binary.

## Alternatives
- [robot_localization](./cra-ros-pkg__robot_localization.md): config-only EKF/UKF with GNSS (`navsat_transform_node`) built in; faster to stand up, prefer it unless you need delayed fixes or custom factors.
- [GTSAM](./borglab__gtsam.md): library, not a ROS framework; prefer for 3D, IMU preintegration and iSAM2.
- [MINS](./rpng__mins.md): tightly coupled multi-sensor filter for 3D vehicles with camera/lidar/GNSS/wheel.

Sources: `README.md`, `LICENSE` and `fuse_core/package.xml` (jazzy), `fuse_models/fuse_plugins.xml` (jazzy, kilted, rolling, devel), `fuse_publishers/fuse_plugins.xml`, `fuse_constraints/fuse_plugins.xml`, `fuse_optimizers/CMakeLists.txt`, `fuse_tutorials/launch/fuse_simple_tutorial.launch.py`, `fuse_tutorials/config/fuse_simple_tutorial.yaml`, repo trees (devel, jazzy), branch list, `fuse/package.xml` per branch; ros/rosdistro `humble|jazzy|kilted|rolling/distribution.yaml`; issue search (`3d`, `humble`: #226, #318, #339, #359).
