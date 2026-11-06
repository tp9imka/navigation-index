# DRIFT - integration card
<!-- about: repo:umich-curly/drift -->
C++17 invariant EKF library for proprioceptive dead reckoning (IMU + wheel encoders, leg kinematics, or DVL velocity) on wheeled, legged, full-size and marine robots, with ROS 1 example nodes. A GNSS-free odometry source that keeps running in field time when vision and GNSS are gone.

| | |
|---|---|
| Install | Library: `git clone https://github.com/UMich-CURLY/drift.git && cd drift && mkdir build && cd build && cmake .. && make -j4`, optional `sudo make install` then `find_package(drift REQUIRED)` (README). Deps: C++17 compiler, Eigen3 >= 3.1.0, yaml-cpp. ROS 1 nodes: add `PATH/TO/drift/ROS/drift` to `ROS_PACKAGE_PATH`, then `./build_ros.sh` from the repo root (generates `custom_sensor_msgs` headers with `gencpp` using hard-coded `/opt/ros/noetic` paths, then CMake-builds `ROS/drift`). Not a catkin/colcon package and not in apt. |
| Runs on | README: tested on Ubuntu 20.04 and 22.04; ROS 1 Noetic for the nodes. CPU only for the filter (README runtime chart includes a Jetson AGX Xavier CPU). Optional learned contact estimator is a separate repo (`UMich-CURLY/deep-contact-estimator`, GPU/TensorRT). ROS 2 exists only on an unmerged branch `dev_inekf_ROS2` (10 commits ahead, 129 behind `main` at time of reading). |
| Inputs | `sensor_msgs/Imu` (e.g. Husky `/gx5_1/imu/data`); wheel velocity from `sensor_msgs/JointState` (differential drive, with `wheel_radius` and `track_width` in `ROS/drift/config/<robot>/ros_comm.yaml`), or `geometry_msgs/TwistStamped` / `TwistWithCovarianceStamped` / `nav_msgs/Odometry` velocity; legged kinematics + `custom_sensor_msgs/ContactArray` (mini cheetah). Filter YAMLs in `config/<robot>/` (`inekf_estimator.yaml`, `imu_propagation.yaml`, `velocity_correction.yaml`): IMU-to-body rotation `[w,x,y,z]`, bias priors, noise stds, static bias init (`init_bias_size`, default 250 samples). |
| Outputs | `geometry_msgs/PoseWithCovarianceStamped` on e.g. `/husky/vanila_inekf/pose` (publish rate up to 1000 Hz in the Husky config) and `nav_msgs/Path` on `/husky/vanila_inekf/path`, frame `/odom`. In-library: `RobotStateQueue` of pose, velocity, biases. |
| Key API / entry points | `estimator::InekfEstimator(error_type, inekf_estimator.yaml)` with `.add_imu_propagation(q, mutex, yaml)`, `.add_velocity_correction(...)`, legged kinematics correction, `.InitBias()`, `.InitState()`, `.RunOnce()`, `.get_robot_state_queue_ptr()`. ROS glue `ros_wrapper::ROSSubscriber` (`AddIMUSubscriber`, `AddDifferentialDriveVelocitySubscriber`, `AddVelocitySubscriber`, `AddVelocityWithCovarianceSubscriber`, `AddMiniCheetahKinematicsSubscriber`) and `ros_wrapper::ROSPublisher`. Example nodes: `rosrun drift husky`, `fetch`, `neya` (full-size vehicle), `mini_cheetah`, `girona500` (marine, DVL). |
| Time to first result | Estimate: 1-2 h on Ubuntu 20.04 + Noetic with a matching bag (Husky/Fetch bags shared on Dropbox in closed issue #14); longer for your own robot (new example file + YAMLs). |
| License | BSD-3-Clause (`LICENSE`, Copyright 2023 UMich-CURLY). Datasets shared via Dropbox in issue #14 have no stated licence. |

## Minimal usage
Not run. From README:

```sh
git clone https://github.com/UMich-CURLY/drift.git && cd drift
mkdir build && cd build && cmake .. && make -j4 && sudo make install && cd ..
echo 'export ROS_PACKAGE_PATH=${ROS_PACKAGE_PATH}:'"$PWD"'/ROS/drift' >> ~/.bashrc && source ~/.bashrc
chmod +x build_ros.sh && ./build_ros.sh
roscore & rosbag play husky.bag &        # bag must carry /gx5_1/imu/data and /joint_states
rosrun drift husky
rostopic echo /husky/vanila_inekf/pose
```

## Wiring it into a nav stack
- Pose/velocity out => [robot_localization](./cra-ros-pkg__robot_localization.md) as a relative odometry source next to GNSS or VIO, or => MAVROS `odometry/out` for an ArduPilot/PX4 rover (via a ROS 1 bridge, since the nodes are ROS 1).
- Marine: the `girona500` example fuses IMU and DVL velocity; same pattern for any velocity sensor (radar odometry, optical flow) through `AddVelocitySubscriber`.
- Characterise IMU noise first with [allan_variance_ros](./ori-drs__allan_variance_ros.md) and put the stds into `imu_propagation.yaml`; the shipped values are robot-specific.
- Compare with [AI-IMU](./mbrossar__ai-imu-dr.md) (IMU-only car dead reckoning) and [KF-GINS](./i2nav-whu__kf-gins.md) (GNSS/INS) for outage studies.

## Gotchas
- Config paths are derived from `__FILE__` at compile time (`project_dir + "/config/..."` in each example), so moving the source tree after building breaks config loading.
- Static bias initialisation assumes the robot is still and level for the first `init_bias_size` IMU samples; starting in motion corrupts biases.
- `rotation_imu2body` must match your mounting (Husky config uses a non-identity quaternion); wrong mounting looks like drift.
- Position and yaw are unobservable from proprioception: output drifts without bound, by design.
- ROS 1 only on `main`; `build_ros.sh` hard-codes Noetic paths. GPS and ROS 2 work live on unmerged `dev_*` branches.
- Delay of the estimator queue reported in open issue #16. Small issue tracker (3 issues); last `main` commit 2024-02.

## Alternatives
- [invariant-ekf](../../catalog/repos/rosshartley__invariant-ekf.md) - the underlying contact-aided InEKF core for legged robots, smaller and without ROS wrappers.
- [robot_localization](./cra-ros-pkg__robot_localization.md) - generic EKF/UKF in ROS 2 with wheel + IMU; less accurate attitude handling, much easier to deploy.
- [OpenVINS](./rpng__open_vins.md) or [MINS](./rpng__mins.md) - when a camera or more sensors are available.

Sources: `README.md`, `LICENSE`, `build_ros.sh`, `ROS/drift/examples/husky.cpp`, `ROS/drift/config/husky/ros_comm.yaml`, `config/husky/imu_propagation.yaml`, `ROS/drift/include/communication/ros_subscriber.h`, `ROS/drift/src/communication/ros_publisher.cpp`, repo tree, branch list and compare `main...dev_inekf_ROS2`, issues #14 #16 (github.com/UMich-CURLY/drift).
