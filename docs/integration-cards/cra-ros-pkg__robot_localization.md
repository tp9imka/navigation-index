# robot_localization - integration card
<!-- about: repo:cra-ros-pkg/robot_localization -->
One-line: config-only ROS 2 EKF/UKF that fuses wheel odometry, IMU and GNSS into `odom` and `map` frames, so a ground robot gets a GNSS-anchored pose in an afternoon.

| | |
|---|---|
| Install | ROS 2 binary: `sudo apt install ros-$ROS_DISTRO-robot-localization` (standard ROS package naming; distro branches exist for humble, iron, jazzy, kilted, lyrical, rolling). Source: clone the `<distro>-devel` branch into a colcon workspace, `colcon build`. Version on `jazzy-devel` package.xml: 3.8.4. |
| Runs on | Ubuntu with ROS 2 (humble/jazzy/rolling...) or ROS 1 (noetic-devel and older branches). CPU only. |
| Inputs | `nav_msgs/Odometry`, `sensor_msgs/Imu`, `geometry_msgs/PoseWithCovarianceStamped`, `geometry_msgs/TwistWithCovarianceStamped` into `ekf_node`/`ukf_node` (configured as `odom0`, `imu0`, `pose0`, `twist0`...). `navsat_transform_node` takes `sensor_msgs/NavSatFix` (`gps/fix`), `sensor_msgs/Imu` (`imu`, needs absolute yaw) and `nav_msgs/Odometry` (`odometry/filtered`). Frames per REP-103/105 (ENU, `map`/`odom`/`base_link`). |
| Outputs | `odometry/filtered` (`nav_msgs/Odometry`), TF `odom->base_link` or `map->odom`; from navsat: `odometry/gps` (GNSS as Odometry in the world frame), optional `gps/filtered` (NavSatFix), optional `utm` TF. |
| Key API / entry points | Executables `ekf_node`, `ukf_node`, `navsat_transform_node`. Launch files `launch/ekf.launch.py`, `ukf.launch.py`, `navsat_transform.launch.py`, `dual_ekf_navsat_example.launch.py`; params `params/ekf.yaml`, `navsat_transform.yaml`, `dual_ekf_navsat_example.yaml`. Services (`srv/`): `SetPose`, `SetDatum`, `ToLL`, `FromLL`, `ToggleFilterProcessing`, `GetState`, `SetUTMZone`. Per-sensor `<sensor>_config` is a 15-bool mask (x y z, roll pitch yaw, vx vy vz, vroll vpitch vyaw, ax ay az). |
| Time to first result | Estimate: 1-2 h to get `ekf_node` publishing on a bag with odom + IMU; plus 2-4 h to get the dual-EKF + navsat setup consistent. Assumes a working ROS 2 install and sensors already publishing with covariances. |
| License | GitHub: NOASSERTION. `package.xml` on `jazzy-devel`: Apache License 2.0. |

## Minimal usage
From `launch/dual_ekf_navsat_example.launch.py` and `params/` on `jazzy-devel`. Not run.

```bash
sudo apt install ros-jazzy-robot-localization
ros2 launch robot_localization dual_ekf_navsat_example.launch.py
# expects: imu/data (sensor_msgs/Imu), gps/fix (NavSatFix), plus the odom topics named in the yaml
# provides: odometry/local (odom-frame EKF), odometry/global (map-frame EKF), odometry/gps
```

Topology in that launch file: `ekf_filter_node_odom` (remapped to `odometry/local`), `ekf_filter_node_map` (remapped to `odometry/global`), `navsat_transform` (consumes `odometry/global`, produces `odometry/gps` that the map EKF takes as an input).

Key `navsat_transform.yaml` fields: `magnetic_declination_radians`, `yaw_offset`, `zero_altitude`, `use_odometry_yaw`, `wait_for_datum`, `datum: [lat, lon, heading]`, `broadcast_utm_transform`.

## Wiring it into a nav stack
- Downstream: [Nav2](./ros-navigation__navigation2.md) consumes the `map->odom->base_link` TF chain this setup publishes. Nav2's GPS navigation tutorial uses this package (from memory of the Nav2 docs, not re-read for this card).
- GNSS source: a u-blox via a ROS driver, or a node that decodes with [pyubx2](./semuconsulting__pyubx2.md) / [pygnssutils](./semuconsulting__pygnssutils.md) and publishes `NavSatFix` with honest covariance.
- IMU: run raw IMU through [imu_tools](../../catalog/repos/ccnyroboticslab__imu_tools.md) (Madgwick/complementary) or [xioTechnologies Fusion](./xiotechnologies__fusion.md) to get orientation before feeding `imu0`.
- GNSS-denied: drop or gate `odometry/gps` (rejection thresholds `*_pose_rejection_threshold`) and the map EKF falls back to odometry dead reckoning; compare with the gated EKF in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage).
- Simulation: [Gazebo gz-sim](./gazebosim__gz-sim.md) NavSat + IMU sensors bridged to ROS 2 topics.
- Catalog: [robot_localization page](../../catalog/repos/cra-ros-pkg__robot_localization.md).

## Gotchas
- Double-counting: feeding both pose and velocity from the same odometry source, or the same IMU yaw into both EKFs inconsistently, makes the filter overconfident. Use `*_differential` / `*_relative` deliberately.
- `navsat_transform_node` needs an IMU whose yaw is earth-referenced (ENU, zero facing east) or a `datum`; magnetometer declination and `yaw_offset` errors show up as a rotated GNSS track.
- Open issues on navsat: UTM range error with huge eastings (#951), high CPU on Jazzy (#890), no wait for valid time (#399), uses `odom` for `/tf_static` (#453), no reset on time jump (#882). Expect to restart the node after sim time jumps.
- `two_d_mode: true` for ground robots, otherwise unobserved z/roll/pitch drift.
- Sensors with zero or missing covariance break fusion; set realistic covariances in the drivers.
- README is a pointer to http://wiki.ros.org/robot_localization (ROS 1 wiki); ROS 2 parameter names mostly match but read the yaml in your distro branch.

## Alternatives
- [fuse](../../catalog/repos/locusrobotics__fuse.md): factor-graph ROS 2 fusion when you need smoothing or custom sensor models.
- [ethzasl_msf](../../catalog/repos/ethz-asl__ethzasl_msf.md): ROS 1 MAV-oriented EKF with sensor self-calibration (older).
- [MINS](./rpng__mins.md): tightly coupled multi-sensor filter with camera/LiDAR when odometry + GNSS is not enough.

Sources: `README.md`, `package.xml`, `launch/dual_ekf_navsat_example.launch.py`, `params/ekf.yaml`, `params/navsat_transform.yaml`, `srv/` listing (all `jazzy-devel`), branch list, issue search (`navsat`).
