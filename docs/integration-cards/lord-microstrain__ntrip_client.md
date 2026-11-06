# ntrip_client (MicroStrain) - integration card
<!-- about: repo:lord-microstrain/ntrip_client -->
One-line: drop-in ROS 1 / ROS 2 node that pulls RTCM3 corrections from an NTRIP caster (or a serial NTRIP device) and publishes them on `/rtcm` for an RTK receiver driver, sending the rover's position back for VRS/network mountpoints.

| | |
|---|---|
| Install | ROS 2 binaries (rosdistro, release 1.4.1): `sudo apt install ros-${ROS_DISTRO}-ntrip-client` on humble, jazzy, kilted, rolling. ROS 1 noetic: `ros-noetic-ntrip-client` (1.4.1). From source: clone the `ros2` branch (ROS 2) or the `ros` branch (ROS 1, the GitHub default) into `ws/src`, `rosdep install --from-paths src --ignore-src -r -y`, then `colcon build` / `catkin_make`. |
| Runs on | Linux with ROS 1 noetic or ROS 2 (Foxy-era docs; binaries for humble/jazzy/kilted/rolling). Pure Python (`rclpy`), any arch, no GPU. Needs internet to a caster, or a serial port for the device mode. |
| Inputs | Caster: host, port (2101), mountpoint, optional user/password, optional SSL client cert/key/CA. Topics: `nmea` (`nmea_msgs/Sentence`, a GGA forwarded to the caster) or, since 1.4.0, `fix` (`sensor_msgs/NavSatFix`, converted to GGA internally). |
| Outputs | `rtcm` topic: `rtcm_msgs/Message` or `mavros_msgs/RTCM`, selected by parameter `rtcm_message_package`; header frame from `rtcm_frame_id` (default `odom`). Raw RTCM3 bytes, not decoded. |
| Key API / entry points | ROS 2: `ros2 launch ntrip_client ntrip_client_launch.py host:=... port:=... mountpoint:=... authenticate:=True username:=... password:=...` (executable `ntrip_ros.py`); `ros2 launch ntrip_client ntrip_serial_device_launch.py port:=/dev/ttyACM0 baudrate:=115200` (executable `ntrip_serial_device_ros.py`). ROS 1: `roslaunch ntrip_client ntrip_client.launch`. Parameters also include `ntrip_version`, `reconnect_attempt_max` (10), `reconnect_attempt_wait_seconds` (5), `rtcm_timeout_seconds` (4), `nmea_max_length` / `nmea_min_length`. Python class `NTRIPClient` in `src/ntrip_client/ntrip_client.py` is reusable without ROS. |
| Time to first result | Estimate: 20-30 min to see RTCM on `/rtcm` with a binary install and caster credentials; RTK FIXED on the receiver depends on baseline length, sky view and the receiver driver, not this node. |
| License | MIT (LICENSE file). GitHub metadata reports NOASSERTION because the LICENSE text carries a stray "Copyright (c) 2013-2017 Niels Lohmann" line (copied MIT template); README states MIT, copyright Parker Hannifin / MicroStrain by HBK. |

## Minimal usage

Not run. ROS 2, public caster, rover fed by the [KumarRobotics ublox driver](./kumarrobotics__ublox.md):

```bash
sudo apt install ros-jazzy-ntrip-client ros-jazzy-rtcm-msgs ros-jazzy-nmea-msgs
ros2 launch ntrip_client ntrip_client_launch.py \
  host:=caster.example.org port:=2101 mountpoint:=MOUNT \
  authenticate:=True username:=$NTRIP_USER password:=$NTRIP_PASS \
  rtcm_message_package:=rtcm_msgs
ros2 topic hz /rtcm
```

For VRS/network mountpoints the caster needs a GGA: publish `nmea_msgs/Sentence` on `/nmea`, or remap `/fix` to your driver's `NavSatFix` topic.

## Wiring it into a nav stack

- Correction path: caster => `ntrip_client` => `/rtcm` (`rtcm_msgs/Message`) => receiver driver. The [ublox ROS 2 driver](./kumarrobotics__ublox.md) subscribes to absolute `/rtcm` with `rtcm_msgs/Message`, so the default launch (namespace `/`, `rtcm_message_package:=rtcm_msgs`) connects with no remap. MicroStrain's own inertial driver consumes the same topic.
- PX4/ArduPilot: set `rtcm_message_package:=mavros_msgs`; [MAVROS](./mavlink__mavros.md) `gps_rtk` plugin forwards `mavros_msgs/RTCM` as `GPS_RTCM_DATA` to the autopilot, which injects into its GPS. Check the topic name the plugin subscribes to and remap.
- Position back-channel: remap `fix` to the receiver's `NavSatFix` (since 1.4.0) instead of building GGA yourself.
- After RTK: the receiver's `NavSatFix` (with cm covariance) goes into [robot_localization](./cra-ros-pkg__robot_localization.md) `navsat_transform_node`, or into a [GTSAM](./borglab__gtsam.md) GPS factor.
- Offline / no-ROS: [pygnssutils](./semuconsulting__pygnssutils.md) `gnssntripclient`, or RTKLIB `str2str` ([rtklib card](./rtklibexplorer__rtklib.md)), do the same caster pull.

Catalog page: [catalog/repos/lord-microstrain__ntrip_client.md](../../catalog/repos/lord-microstrain__ntrip_client.md). Concepts: [gnss-rtk-ppp](../../catalog/concepts/gnss-rtk-ppp.md), [gnss](../../catalog/concepts/gnss.md), [ros](../../catalog/concepts/ros.md).

## Gotchas

- RTCM message type default differs by entry point: the node source (`ntrip_ros_base.py`) defaults `rtcm_message_package` to `mavros_msgs`, the ROS 2 launch file defaults it to `rtcm_msgs`, and `package.xml` only depends on `rtcm_msgs`. `ros2 run` without the launch file and without mavros_msgs installed fails at startup. Always set it explicitly.
- The ROS 2 launch file ships a hard-coded example caster (`host` 20.185.11.35, mountpoint `VRS_RTCM3`, user/pass placeholders) and `authenticate` True; override all of them.
- Open #70: rtk2go.com reportedly blocks this client for poor rate control on reconnects; a fork with rate control is linked from the issue (PaulBouchier/ntrip_client, PR #71). Open #72 asks whether the repo is still maintained (no maintainer reply as of the issue); last release 1.4.1 (2025-04-15).
- Node exits after `reconnect_attempt_max` failed reconnects (#44) and has been reported to die on mangled NMEA from the receiver (#58, open) and on non-UTF-8 bytes (#41, open). Run it under a supervisor / `respawn=True`.
- Checksum errors with some RTCM 3.3 casters (#40, open) and u-blox PointPerfect (#49, closed).
- Credentials go in launch arguments; keep them in env vars, not committed launch files.

## Alternatives

- [pygnssutils](./semuconsulting__pygnssutils.md) `gnssntripclient` - Python CLI/class, no ROS, also does SPARTN; prefer outside ROS or for quick caster checks.
- [RTKLIB](./rtklibexplorer__rtklib.md) `str2str` - stream relay from caster to serial/TCP; prefer for feeding a receiver directly with no ROS at all.
- [go-gnss/ntrip](../../catalog/repos/go-gnss__ntrip.md) - Go client/caster library, if you need to run your own caster too.

Sources: `gh api repos/LORD-MicroStrain/ntrip_client` (default branch `ros`, branches `ros`/`ros2`), README.md on `ros` and `ros2`, LICENSE, CHANGELOG.rst (1.4.1 2025-04-15, 1.4.0 fix topic), package.xml (ros2), launch/ntrip_client_launch.py (ros2), scripts/ntrip_ros.py and scripts/ntrip_ros_base.py (ros2), ros/rosdistro distribution.yaml for humble/jazzy/kilted/rolling/noetic, issues #70, #72, #44, #58, #41, #40, #49.
