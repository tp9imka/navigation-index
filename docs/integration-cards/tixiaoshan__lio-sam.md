# LIO-SAM - integration card
<!-- about: repo:tixiaoshan/lio-sam -->
Tightly coupled LiDAR-inertial odometry and mapping on GTSAM factor graphs, with an optional GPS factor and ICP loop closure; the classic reference stack for "LiDAR + 9-axis IMU + optional GNSS" when you already run ROS.

| | |
|---|---|
| Install | No releases or tags. ROS 1 (`master`): `sudo apt install ros-<distro>-navigation ros-<distro>-robot-localization ros-<distro>-robot-state-publisher`, GTSAM 4.0 via `sudo add-apt-repository ppa:borglab/gtsam-release-4.0 && sudo apt install libgtsam-dev libgtsam-unstable-dev`, then `cd ~/catkin_ws/src && git clone https://github.com/TixiaoShan/LIO-SAM.git && cd .. && catkin_make`. ROS 2 (branch `ros2`): `sudo apt install ros-<distro>-perception-pcl ros-<distro>-pcl-msgs ros-<distro>-vision-opencv ros-<distro>-xacro`, GTSAM 4.1 PPA `ppa:borglab/gtsam-release-4.1`, clone with `-b ros2`, `colcon build`. Docker: `docker build -t liosam-kinetic-xenial .` (master) or `liosam-humble-jammy` (ros2 branch Dockerfile). |
| Runs on | Linux, CPU only. `master` README: tested on ROS Kinetic and Melodic, Noetic via issue #206 hints. `ros2` README: tested on Foxy and Galactic (Ubuntu 20.04) and Humble (22.04). No Jazzy (open issue #549). |
| Inputs | `pointCloudTopic` (default `points_raw`, sensor_msgs/PointCloud2) with per-point relative `time` (0..0.1 s at 10 Hz) and `ring` fields; mechanical spinning LiDAR expected (`sensor: velodyne / ouster / livox`, `N_SCAN`, `Horizon_SCAN`). `imuTopic` (default `imu_raw`, sensor_msgs/Imu) from a **9-axis** IMU with orientation, README recommends >= 200 Hz. Optional `gpsTopic` (nav_msgs/Odometry from robot_localization `navsat_transform`, e.g. `odometry/gps`). Extrinsics `extrinsicTrans`, `extrinsicRot`, `extrinsicRPY` in `config/params.yaml`. |
| Outputs | `lio_sam/mapping/odometry` and `lio_sam/mapping/odometry_incremental` (nav_msgs/Odometry, keyframe rate), `odometry/imu` (IMU-rate fused odometry, `odomTopic`), `lio_sam/imu/path`, `lio_sam/mapping/path`, `lio_sam/mapping/map_global`, `map_local`, `cloud_registered`, `trajectory` (PointCloud2), loop-closure markers; TF `map` => `odom` => `base_link`. Map saving: service `/lio_sam/save_map` (resolution, destination) writes PCD, or `savePCD: true` on shutdown. |
| Key API / entry points | `roslaunch lio_sam run.launch` (ROS 1) / `ros2 launch lio_sam run.launch.py` (ROS 2). Four nodes from `src/`: `imageProjection.cpp` (deskew, range image), `featureExtraction.cpp` (edge/surf features), `imuPreintegration.cpp` (IMU preintegration graph and `TransformFusion`), `mapOptmization.cpp` (keyframe graph, GPS and loop factors; note the filename spelling). ROS 1 includes `launch/include/module_navsat.launch` (robot_localization EKF + navsat_transform for the GPS factor). |
| Time to first result | Estimate: 1-2 h on Ubuntu with matching ROS and the GTSAM PPA, using the README's walking/park bags; a day or more for your own sensor (extrinsics, time/ring fields). |
| License | LICENSE file: BSD-3-Clause (Tixiao Shan, 2020). Depends on GTSAM (BSD). Sample datasets are Google Drive links with no stated licence. |

## Minimal usage
Not run. From README (`master`, ROS 1):

```sh
roslaunch lio_sam run.launch
rosbag play walking_dataset.bag -r 3
rosservice call /lio_sam/save_map 0.2 "/Downloads/LOAM/"
```

ROS 2 branch:

```sh
ros2 launch lio_sam run.launch.py
ros2 bag play your-bag
ros2 service call /lio_sam/save_map lio_sam/srv/SaveMap "{resolution: 0.2, destination: /Downloads/service_LOAM}"
```

To turn on GNSS: set `gpsTopic: "odometry/gps"` in `params.yaml`. The shipped default is `odometry/gpsz`, a topic nothing publishes, so the GPS factor is off by default.

## Wiring it into a nav stack
- GNSS input: [robot_localization](./cra-ros-pkg__robot_localization.md) `navsat_transform_node` turns NavSatFix into the nav_msgs/Odometry that `gpsTopic` expects (`module_navsat.launch` does this in ROS 1). `gpsCovThreshold` (m^2) rejects bad fixes, so a degraded or spoofed receiver with honest covariance gets gated out; one with optimistic covariance does not.
- Output to an autopilot: `lio_sam/mapping/odometry` or `odometry/imu` => [MAVROS](./mavlink__mavros.md) `odometry/out` or [vision_to_mavros](./thien94__vision_to_mavros.md); ArduPilot EKF3 external nav path in [ardupilot_ros](./ardupilot__ardupilot_ros.md).
- Map reuse: the saved PCD is the map input for [FAST_LIO_LOCALIZATION](./hviktortsoi__fast_lio_localization.md) (its README names LIO-SAM as a map builder).
- Better loop closure: [SC-LIO-SAM](../../catalog/repos/gisbi-kim__sc-lio-sam.md) (Scan Context).
- Evaluate with [evo](./michaelgrupp__evo.md); export the path topic to TUM yourself, there is no built-in trajectory file.

## Gotchas
- 9-axis IMU required (orientation used for init and heading). The Ouster internal IMU is 6-axis and does not work; README points to [liorf](https://github.com/YJZLuckyBoy/liorf) or LIO_SAM_6AXIS for 6-axis IMUs.
- Two separate IMU extrinsics (`extrinsicRot` for accel/gyro, `extrinsicRPY` for attitude). Wrong signs give "jumping up and down" at start (README Issues section).
- Point clouds without per-point `time` disable deskew with a warning that the system "will drift significantly" (open issue #490). Livox and other solid-state LiDARs need the author's custom `livox_ros_driver`.
- GTSAM version mismatches crash `mapOptmization` / `imuPreintegration` (README; open issue #475 "GTSAM was built against a different version of Eigen", #455 exit code -6). Use the PPA version named in the branch README.
- `savePCDDirectory` code deletes and recreates the target folder (comment in `params.yaml`).
- Loop closure is a LeGO-LOAM-style ICP proof of concept, off by default (`loopClosureEnableFlag`); README recommends playback at `-r 1` with loops or GPS on.
- Open bugs worth knowing: #581 (scan2map uses the pose even when LM does not converge), #583 (`downsampleRate: 0` divides by zero), README TODO #104 (imuPreintegration bug). Last commit 2025-02.

## Alternatives
- [FAST-LIO2](./hku-mars__fast_lio.md) - faster, handles solid-state LiDARs and 6-axis IMUs, no GPS factor or loop closure built in; GPL-2.0.
- [RKO-LIO](./prbonn__rko_lio.md) - pip-installable LIO with minimal sensor-specific tuning and ROS 2 apt packages; no GNSS factor.
- [GLIM](../../catalog/repos/koide3__glim.md) or [KISS-SLAM](./prbonn__kiss-slam.md) - when you want a maintained full mapping system with loop closure.

Sources: `README.md` (master and ros2 branches), `LICENSE`, `config/params.yaml`, `launch/` and `launch/include/` listings, `src/mapOptmization.cpp`, `src/imuPreintegration.cpp`, branches list, commit log, issues #475 #490 #455 #549 #581 #583 (github.com/TixiaoShan/LIO-SAM).
