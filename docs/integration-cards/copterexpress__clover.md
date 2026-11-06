# Clover (COEX) - integration card
<!-- about: repo:copterexpress/clover -->
One-line: ROS Noetic package and Raspberry Pi image that turns a PX4 drone into a Python-scriptable one (`navigate(x, y, z, frame_id='aruco_map')`). Includes ArUco-marker navigation for GNSS-free indoor flight and a Gazebo + PX4 SITL simulator VM.

| | |
|---|---|
| Install | Preferred: flash the Raspberry Pi image from GitHub Releases (latest stable `v0.25`, 2024-08-08; `v0.26-alpha.1` 2024-09-19). The README lists Raspbian Buster, ROS Noetic, mavros and OpenCV. Manual: ROS Noetic catkin workspace, `git clone https://github.com/CopterExpress/clover.git clover` into `src`, `rosdep install -y --from-paths src --ignore-src`, `catkin_make -j1`, then `curl https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh \| sudo bash` (clover/README.md). Simulation: the `clover_simulation` package (needs `px4` and `sitl_gazebo` in the workspace) or the prebuilt VM from `CopterExpress/clover_vm` (release v1.4, 2023-04-12). |
| Runs on | Raspberry Pi 4 companion + PX4 flight controller (USB `/dev/px4fmu` by default, via udev rule `99-px4fmu.rules`, or set `fcu_url` in `mavros.launch`). Desktop: Ubuntu 20.04 + ROS Noetic for the simulator. ROS 1 only, with no plans for ROS 2 (maintainer in #497). |
| Inputs | ROS services from your script; PX4 state through mavros; Pi camera (`main_camera.launch`); ArUco marker map file for `aruco_pose` (`aruco.launch`, `map/`); optional optical flow / rangefinder per the docs. |
| Outputs | Setpoints to PX4 via mavros; TF frames (`map`, `body`, `aruco_map`, per-marker frames); `aruco_pose` marker detections and a map-relative vision pose fed to PX4 (docs, not read in source); telemetry through `get_telemetry`. |
| Key API / entry points | Launch: `roslaunch clover clover.launch` (also `mavros.launch`, `aruco.launch`, `main_camera.launch`, `led.launch`, `simulator.launch`). Services (`clover/srv/`): `navigate` (`x y z yaw speed frame_id auto_arm`), `navigate_global` (`NavigateGlobal.srv`), `set_position`, `set_velocity`, `set_attitude`, `set_rates`, `set_altitude`, `set_yaw`, `set_yaw_rate`, `get_telemetry` (`frame_id` in; `connected armed mode x y z lat lon alt vx vy vz roll pitch yaw ... voltage cell_voltage` out), `land` (`std_srvs/Trigger`). Service names confirmed in `clover/src/simple_offboard.cpp` `advertiseService` calls. `set_led_effect` comes from the LED node. |
| Time to first result | Estimate: 1-2 h to a scripted takeoff/navigate/land in the Clover VM (download + boot + run the docs example). A day to fly ArUco-map navigation on real hardware, assuming a calibrated camera and a printed marker field. |
| License | Code: **MIT** (LICENSE, Copter Express Technologies 2018). **Documentation** (`docs/`) is **CC BY-NC-SA 4.0** (README). Do not copy doc text or images into a commercial or sponsor-owned deliverable. |

## Minimal usage

Not run. The standard pattern from the Clover docs (`simple_offboard`), using the service names from `clover/srv/`.

```python
import rospy
from clover import srv
from std_srvs.srv import Trigger

rospy.init_node('flight')
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
land = rospy.ServiceProxy('land', Trigger)

navigate(x=0, y=0, z=1.5, frame_id='body', auto_arm=True)       # take off to 1.5 m
rospy.sleep(5)
navigate(x=1, y=1, z=1.5, frame_id='aruco_map')                   # fly to a point in the marker map
rospy.sleep(5)
print(get_telemetry(frame_id='aruco_map'))
land()
```

## Wiring it into a nav stack

- GNSS-denied demo out of the box: an `aruco_pose` marker map gives PX4 a vision position (the same idea as [vision_to_mavros](./thien94__vision_to_mavros.md)). Swap in your own VIO or visual geolocalization by publishing to the mavros vision pose topic instead.
- PX4 side: [PX4 card](./px4__px4-autopilot.md). Bridge: [MAVROS card](./mavlink__mavros.md). Clover's services are a thin layer over mavros setpoints plus TF, so anything that understands mavros works next to them.
- For a ROS 2 stack use [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) or [px4_ros_com](./px4__px4_ros_com.md) instead. Clover stays on Noetic.
- Sim: `simulator.launch` starts Gazebo Classic + PX4 SITL + the Clover model. For GNSS-denial experiments in sim see [samples/px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/).

Catalog page: [catalog/repos/copterexpress__clover.md](../../catalog/repos/copterexpress__clover.md). Concepts: [autopilot](../../catalog/concepts/autopilot.md), [ros](../../catalog/concepts/ros.md), [visual-slam](../../catalog/concepts/visual-slam.md).

## Gotchas

- ROS Noetic reached end of life in May 2025 and the image is Raspbian Buster. Expect apt and rosdep breakage on fresh manual installs. Prefer the release image or the VM.
- OpenCV 4.7+ ArUco API change: #495 (`cv2.aruco` has no `DetectorParameters_create`, closed) and #506 (aruco_pose with OpenCV 4.10, closed). Pin the OpenCV that ships in the image.
- `No connection to FCU` (#485, closed) usually means a wrong `fcu_url` or a missing udev rule.
- Sim: #496 (PX4 startup script returns 256, closed). Gazebo may drop the real-time factor below `PX4_SIM_SPEED_FACTOR` (clover_simulation README). Adjust it, or camera-based positioning degrades.
- `catkin_make` permission errors (#484) come from building as a different user than the one who owns the workspace.
- Docs are CC BY-NC-SA (see Licence).

## Alternatives

- [MAVROS](./mavlink__mavros.md) directly - same capability without the Clover convenience layer, and available on ROS 2.
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) - ROS 2 C++ modes and setpoints for PX4. Prefer it for new ROS 2 work.
- [MAVSDK](../../catalog/repos/mavlink__mavsdk.md) - ROS-free Python/C++ offboard control.

Sources: `gh api repos/copterexpress/clover` (MIT, pushed 2026-04-14), LICENSE, README.md (image features, License), clover/README.md (manual install, running), `clover/srv/*.srv` listing plus Navigate.srv and GetTelemetry.srv, `clover/launch/` listing, clover_simulation/README.md, releases (v0.25, v0.26-alpha.1), `gh api repos/CopterExpress/clover_vm` + releases, issues #497, #495, #506, #485, #496, #484.
