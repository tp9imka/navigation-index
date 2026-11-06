# ros_gz - integration card
<!-- about: repo:gazebosim/ros_gz -->
The ROS 2 <=> Gazebo (gz-sim) glue: `parameter_bridge` maps Gazebo sensor topics (IMU, NavSat, magnetometer, altimeter, air pressure, cameras, LiDAR, odometry, clock) onto ROS 2 messages, plus launch files to start Gazebo and spawn models. This is what lets a ROS nav stack run against a simulated GNSS that you can degrade or cut.

| | |
|---|---|
| Install | Binary: `sudo apt install ros-$ROS_DISTRO-ros-gz` (README shows `ros-rolling-ros-gz`). Supported pairs from the README table, binaries on packages.ros.org: Humble + Fortress, Jazzy + Harmonic, Kilted + Ionic, Lyrical + Jetty, Rolling + Jetty. Humble + Harmonic (or Garden) binaries come from packages.osrfoundation.org. Other pairs are source-only: `git clone https://github.com/gazebosim/ros_gz.git -b <branch>` into `~/ws/src`, `rosdep install -r --from-paths src -i -y --rosdistro <distro>`, `colcon build`. Branches: `humble`, `jazzy`, `kilted`, `ros2` (Rolling); ROS 1 is on `noetic`. |
| Runs on | Ubuntu with ROS 2 (source build documented for Linux and macOS). CPU for the bridge; GPU needed by Gazebo for camera / GPU-LiDAR sensors, not by the bridge. |
| Inputs | Gazebo Transport topics (`gz.msgs.*`) and ROS 2 topics; bridge spec on the command line or a YAML array (`topic_name` or `ros_topic_name`/`gz_topic_name`, `ros_type_name`, `gz_type_name`, `direction`, `lazy`, queue sizes, QoS). |
| Outputs | Nav-relevant mappings (bridge README table): `sensor_msgs/msg/Imu` <=> `gz.msgs.IMU`, `sensor_msgs/msg/NavSatFix` <=> `gz.msgs.NavSat`, `gps_msgs/msg/GPSFix` <=> `gz.msgs.NavSat`, `sensor_msgs/msg/MagneticField` <=> `gz.msgs.Magnetometer`, `ros_gz_interfaces/msg/Altimeter` <=> `gz.msgs.Altimeter`, `sensor_msgs/msg/FluidPressure` <=> `gz.msgs.FluidPressure`, `nav_msgs/msg/Odometry` <=> `gz.msgs.Odometry` / `OdometryWithCovariance`, `tf2_msgs/msg/TFMessage` <=> `gz.msgs.Pose_V`, `rosgraph_msgs/msg/Clock` <=> `gz.msgs.Clock`. Services `ControlWorld`, `SpawnEntity`, `DeleteEntity`, `SetEntityPose`. Images through `ros_gz_image` (image_transport). |
| Key API / entry points | `ros2 run ros_gz_bridge parameter_bridge <topic>@<ROS type><dir><gz type>` where dir is `@` bidirectional, `[` Gazebo => ROS, `]` ROS => Gazebo (usage text in `parameter_bridge.cpp`); `ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=bridge.yaml`; launch files `ros_gz_sim/launch/gz_sim.launch.py` (args `gz_args`, `gz_version`), `gz_server.launch.py`, `gz_spawn_model.launch.py`, `ros_gz_sim.launch.py`, `ros_gz_bridge/launch/ros_gz_bridge.launch.py`; XML launch tags `<gz_server>` and `<ros_gz_bridge>`. Demos in `ros_gz_sim_demos/launch/`: `navsat.launch.xml`, `navsat_gpsfix.launch.xml`, `imu.launch.xml`, `magnetometer.launch.xml`, `air_pressure.launch.xml`, `dvl.launch.py`, `gpu_lidar_bridge.launch.xml`, `rgbd_camera_bridge.launch.xml`, `tf_bridge.launch.xml`. |
| Time to first result | Estimate: 10-20 min with apt binaries on a matching ROS/Gazebo pair (run the navsat demo, echo `/navsat`). Source build: 30-90 min, longer on low-RAM machines. |
| License | `LICENSE`: Apache-2.0. |

## Minimal usage
Not run. Adapted from `ros_gz_sim_demos/launch/navsat.launch.xml`, `config/navsat.yaml` and the bridge README.

```sh
sudo apt install ros-jazzy-ros-gz
ros2 launch ros_gz_sim_demos navsat.launch.xml        # world spherical_coordinates.sdf + NavSat bridge
ros2 topic echo /navsat                               # sensor_msgs/NavSatFix
```

Ad-hoc bridges for a GNSS + IMU + clock nav test:

```sh
ros2 run ros_gz_bridge parameter_bridge \
  /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock \
  /navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat \
  /imu@sensor_msgs/msg/Imu[gz.msgs.IMU
```

YAML form (from `navsat.yaml`):

```yaml
- topic_name: "/navsat"
  ros_type_name: "sensor_msgs/msg/NavSatFix"
  gz_type_name: "gz.msgs.NavSat"
  lazy: true
  direction: GZ_TO_ROS
```

## Wiring it into a nav stack
- `/navsat` + `/imu` => [robot_localization](./cra-ros-pkg__robot_localization.md) (`navsat_transform_node` + EKF) => [Nav2](./ros-navigation__navigation2.md). GNSS-denied test: stop bridging `/navsat` (or remap it through a node that drops / offsets fixes) mid-run.
- Simulator side: [Gazebo Sim card](./gazebosim__gz-sim.md) for sensors and SDF; PX4 and ArduPilot SITL ride on the same Gazebo ([ardupilot_gz](../../catalog/repos/ardupilot__ardupilot_gz.md), [PX4](./px4__px4-autopilot.md)).
- LiDAR / camera => [KISS-ICP](./prbonn__kiss-icp.md), [RTAB-Map](./introlab__rtabmap.md), [OpenVINS](./rpng__open_vins.md).
- Always bridge `/clock` and set `use_sim_time:=true` on consumers.

## Gotchas
- Version pairing is the main trap: the apt package for your ROS distro is built against one Gazebo release (table above); mixing (e.g. Humble + Harmonic) needs the OSRF packages or a source build, and `ros_ign_*` packages are only shims.
- NavSat realism is thin: open issue #542 "No way to get covariances out of GPS data", open #695 "Ability to set the Fix.Status of a NavSat Message". Plan to post-process `/navsat` yourself if you need covariance or fix-status changes.
- `/clock`: if another publisher exists, Gazebo only publishes `/world/<name>/clock` (bridge README note).
- QoS: open issue #583 asks for documented best practice; sensor topics may need QoS overrides for `SensorDataQoS` consumers.
- Source builds are template-heavy and can OOM: README suggests `colcon build --parallel-workers=1 --executor sequential` and `MAKEFLAGS="-j 1"`. Closed #924: `ros_gz_sim` failed to build for Humble arm64.

## Alternatives
- [MAVROS](./mavlink__mavros.md) / [px4_ros_com](./px4__px4_ros_com.md) - when the GNSS/IMU you want in ROS comes through the autopilot (SITL or real) rather than straight from Gazebo.
- [Stonefish](./patrykcieslak__stonefish.md) - marine sim with its own ROS 2 interface instead of Gazebo.
- [AirSim](../../catalog/repos/microsoft__airsim.md) - Unreal-based, own ROS wrapper.

Sources: `README.md`, `LICENSE`, `ros_gz_bridge/README.md`, `ros_gz_bridge/src/parameter_bridge.cpp`, `ros_gz_bridge/launch/` listing, `ros_gz_sim/launch/` listing, `ros_gz_sim/launch/gz_sim.launch.py.in`, `ros_gz_sim_demos/launch/` listing, `ros_gz_sim_demos/launch/navsat.launch.xml`, `ros_gz_sim_demos/config/navsat.yaml`, issues #542 #583 #695 #924 (github.com/gazebosim/ros_gz).
