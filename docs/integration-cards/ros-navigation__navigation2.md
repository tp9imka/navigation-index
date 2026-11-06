# Nav2 (ROS 2 Navigation) - integration card
<!-- about: repo:ros-navigation/navigation2 -->
One-line: a complete ROS 2 ground-robot navigation stack (localization, costmaps, planners, controllers, behavior trees, GPS waypoint following) you can drive from a short Python script, so you spend the hackathon on localization under degraded PNT rather than on path following.

| | |
|---|---|
| Install | Binary: `sudo apt install ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-bringup` (per docs.nav2.org Getting Started). Source: colcon build of the distro branch (`humble`, `jazzy`, ...), or the prebuilt containers at `ghcr.io/ros-navigation/navigation2`. README build table lists humble, jazzy and lyrical Debian builds. |
| Runs on | Ubuntu with ROS 2 (Humble on 22.04, Jazzy on 24.04 per the build table; main targets the newest distro). amd64 binaries confirmed in the build table; arm64 not checked here. No GPU required. Simulation demos use Gazebo ([gz-sim](./gazebosim__gz-sim.md)) or the built-in `nav2_loopback_sim` (no physics). |
| Inputs | TF tree `map => odom => base_link` (REP-105), `nav_msgs/Odometry`, `sensor_msgs/LaserScan` / `PointCloud2` for costmaps, `nav_msgs/OccupancyGrid` map from `nav2_map_server` (YAML + PGM), goals as `geometry_msgs/PoseStamped` or `geographic_msgs/GeoPose` (GPS waypoints). Parameters in one YAML file. |
| Outputs | `cmd_vel` (`geometry_msgs/Twist` or `TwistStamped` depending on distro), planned paths (`nav_msgs/Path`), costmaps, action results/feedback on `navigate_to_pose`, `follow_waypoints`, `follow_gps_waypoints`, etc. |
| Key API / entry points | Launch: `nav2_bringup` `tb3_simulation_launch.py`, `tb4_simulation_launch.py`, `tb3_loopback_simulation_launch.py`, `bringup_launch.py`, `localization_launch.py`, `navigation_launch.py`, `slam_launch.py`. Python: `nav2_simple_commander.robot_navigator.BasicNavigator` with `setInitialPose(PoseStamped)`, `waitUntilNav2Active()`, `goToPose(PoseStamped)`, `followWaypoints(...)`, `followGpsWaypoints(list[GeoPose])`, `isTaskComplete()`, `getFeedback()`, `getResult()`, `getPath(start, goal)`. Plugins: `nav2_amcl`, `nav2_smac_planner`, `nav2_mppi_controller`, `nav2_regulated_pure_pursuit_controller`, `nav2_collision_monitor`, `nav2_route`. |
| Time to first result | Estimate: about 1 hour from a working ROS 2 install to the TurtleBot simulation navigating to a clicked goal, assuming apt binaries and Gazebo already work on the machine. Plugging in your own robot and tuning the params YAML is days, not hours. |
| License | Mixed, per package: LGPL-2.1-or-later, Apache-2.0, BSD-3-Clause (top-level `LICENSE`; e.g. `nav2_amcl` is LGPL-2.1-or-later). GitHub shows NOASSERTION. |

## Minimal usage

Commands from the Nav2 getting-started flow and `nav2_simple_commander/example_nav_to_pose.py`. Not run.

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

```python
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator

rclpy.init()
nav = BasicNavigator()
p = PoseStamped(); p.header.frame_id = 'map'; p.header.stamp = nav.get_clock().now().to_msg()
p.pose.orientation.w = 1.0
nav.setInitialPose(p)
nav.waitUntilNav2Active()

goal = PoseStamped(); goal.header.frame_id = 'map'; goal.header.stamp = nav.get_clock().now().to_msg()
goal.pose.position.x, goal.pose.position.y, goal.pose.orientation.w = 2.0, 0.5, 1.0
nav.goToPose(goal)
while not nav.isTaskComplete():
    fb = nav.getFeedback()
print(nav.getResult())
```

## Wiring it into a nav stack

- Localization is pluggable through TF. Nav2 only needs someone to publish `map => odom`. Replace AMCL with [robot_localization](./cra-ros-pkg__robot_localization.md) (dual EKF + `navsat_transform_node`) for GNSS outdoors, or with a SLAM / VIO / terrain-matching node for GNSS-denied runs. That is the clean seam for a PNT-resilience demo: swap or degrade the `map => odom` source and show the planner keeps working.
- GPS waypoints: `followGpsWaypoints` takes `geographic_msgs/GeoPose` and converts via the robot_localization `fromLL` service; the docs.nav2.org GPS tutorial pairs it with robot_localization.
- Simulation: [gz-sim](./gazebosim__gz-sim.md) + `ros_gz` bridges provide LiDAR, IMU, odometry and NavSat topics. `tb3_loopback_simulation_launch.py` skips physics entirely for fast behavior-tree iteration.
- Maps: occupancy grids from `slam_toolbox`, or rasterize a DEM / building footprints with [GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md) into PGM + YAML for `nav2_map_server`.
- Aerial: Nav2 is a 2D ground stack. For drones, use PX4/ArduPilot mission logic instead (see [PX4 SITL GPS denial sample](../../samples/px4-sitl-gps-denial/)).

## Gotchas

- The `BasicNavigator` API on `main` differs from distro branches: on main, `goToPose` returns a task handle and `isTaskComplete(task=...)` / `getFeedback(task=...)` take it (see `example_nav_to_pose.py` on main). On Humble/Jazzy, `goToPose` returns a bool and the calls take no task argument. Read the example on the branch that matches your install.
- `BasicNavigator.followGpsWaypoints` exists on the `jazzy` branch but not on `humble` (checked `robot_navigator.py` on both); issue #5434 tracked adding the GPS waypoint action server to Humble. On Humble, call the action directly or use Jazzy.
- Most "nothing moves" reports are TF problems: missing or wrong `map => odom` (issue #3179, "invalid tf between map and odom"), wrong frame ids, or sim time mismatches (`use_sim_time`).
- Simulation launches break when Gazebo / TurtleBot model packages update (issue #5634, "tb3_simulation and tb4_simulation no longer working after the last update"; #5892 on GPS world generation). Pin a distro and binary versions for the event.
- Tuning the params YAML (costmap inflation, controller critics, footprint) is the main time sink. Start from `nav2_bringup/params/nav2_params.yaml` and change one plugin at a time.
- LGPL packages (AMCL) matter if you ship a closed derivative.

## Alternatives

- [ompl/ompl](../../catalog/repos/ompl__ompl.md): motion planning library only, no navigation runtime; prefer it for custom vehicles or 3D planning.
- [open-navigation/opennav_coverage](../../catalog/repos/open-navigation__opennav_coverage.md): Nav2 extension for area coverage (search patterns, survey lanes).
- PX4 / ArduPilot mission modes for aerial or when the vehicle already runs an autopilot: see [px4/px4-autopilot](../../catalog/repos/px4__px4-autopilot.md), [ardupilot/ardupilot](../../catalog/repos/ardupilot__ardupilot.md).

Sources: `gh api repos/ros-navigation/navigation2/readme`; top-level `LICENSE`; `nav2_amcl/package.xml`; `nav2_bringup/launch` listing; `nav2_simple_commander/nav2_simple_commander/robot_navigator.py` and `example_nav_to_pose.py` (main); issue searches for "gps" and "tb3_simulation". Catalog: [record](../../catalog/repos/ros-navigation__navigation2.md).
