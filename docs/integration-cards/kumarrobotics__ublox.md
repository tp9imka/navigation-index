# ublox (KumarRobotics) - integration card
<!-- about: repo:kumarrobotics/ublox -->
One-line: the standard ROS driver for u-blox GNSS receivers (M8, F9P/F9R, M8T...) - `NavSatFix` plus raw UBX topics (NAV-PVT, NAV-SAT, RXM-RAWX, MON-HW) and an RTCM input for RTK.

| | |
|---|---|
| Install | ROS 2 binaries: `sudo apt install ros-${ROS_DISTRO}-ublox` (rosdistro: humble 2.3.0, jazzy 2.3.0, kilted 2.3.0, rolling 3.0.0). ROS 1 noetic: `ros-noetic-ublox` (1.5.0). Source: branch `ros2` for ROS 2 (3.0.0 tagged in commits 2025-09-26), branch `master` for ROS 1 (last commit 2022-12; `dashing-devel`/`foxy-devel`/`galactic-devel` are old ROS 2 branches). `colcon build` / `catkin_make` after `rosdep install`. |
| Runs on | Linux, ROS 1 noetic or ROS 2 (humble/jazzy/kilted/rolling). C++, any arch, no GPU. Serial (USB CDC-ACM or UART); TCP/UDP exists but README calls it untested. |
| Inputs | Serial device (`device`, default `/dev/ttyACM0`, `uart1.baudrate`); YAML parameter file with receiver config (GNSS constellations, rate, dynamic model, TMODE3 base/rover, `publish.*` flags). RTCM corrections on absolute `/rtcm` (`rtcm_msgs/msg/Message`, ROS 2). |
| Outputs | `~/fix` (`sensor_msgs/NavSatFix`), `~/fix_velocity` (`geometry_msgs/TwistWithCovarianceStamped`, ENU, angular part unused); per-message topics from `ublox_msgs` when enabled: `navpvt`, `navsat`, `navstatus`, `navclock`, `navrelposned`, `navheading`, `rxmraw` (RAWX), `rxmsfrb`, `monhw`, `esfins`/`esfmeas` (ADR/UDR), `timtm2` (TIM); optional `sensor_msgs/Imu` heading for F9P moving base. Diagnostics on `/diagnostics`. |
| Key API / entry points | ROS 2: executable `ublox_gps_node` (also a registered component in `ublox_gps`); launch `ublox_gps/launch/ublox_gps_node-launch.py` (loads `config/c94_m8p_rover.yaml`) and `ublox_gps_node-composed-launch.py`; `ublox_logger` executable for raw stream logging. ROS 1: `roslaunch ublox_gps ublox_device.launch node_name:=... param_file_name:=...`. Message package `ublox_msgs`; time sync helper `ublox_msg_filters` (ROS 1 README). Sample configs: `c94_m8p_base/rover`, `c94_m8t_base/rover`, `neo_m8u_rover`, `nmea`, `zed_f9p`. |
| Time to first result | Estimate: 30 min to `NavSatFix` on `/ublox_gps_node/fix` from a binary install with a USB receiver outdoors, assuming one of the sample YAMLs is close to your device; longer if the config handshake NACKs (see Gotchas). |
| License | BSD-3-Clause (LICENSE file, "ublox contributors"). |

## Minimal usage

Not run. ROS 2, ZED-F9P over USB, with corrections from [ntrip_client](./lord-microstrain__ntrip_client.md):

```bash
sudo apt install ros-jazzy-ublox ros-jazzy-ntrip-client
cp $(ros2 pkg prefix ublox_gps)/share/ublox_gps/config/zed_f9p.yaml my_f9p.yaml
# edit my_f9p.yaml: remove the tmode3/sv_in block (it is a base-station survey-in config), set device, publish.aid.all: false
ros2 run ublox_gps ublox_gps_node --ros-args --params-file my_f9p.yaml
ros2 launch ntrip_client ntrip_client_launch.py host:=... mountpoint:=... username:=... password:=... rtcm_message_package:=rtcm_msgs
ros2 topic echo /ublox_gps_node/fix
```

## Wiring it into a nav stack

- RTK: [ntrip_client](./lord-microstrain__ntrip_client.md) publishes `rtcm_msgs/Message` on `/rtcm`; the ROS 2 node subscribes to absolute `/rtcm` (`node.cpp`), so they connect without remapping.
- Fusion: `fix` => [robot_localization](./cra-ros-pkg__robot_localization.md) `navsat_transform_node` (with IMU heading) => `odometry/gps` into the EKF; or a GPS factor in [GTSAM](./borglab__gtsam.md) / [fuse](./locusrobotics__fuse.md). `NavSatFix.position_covariance` comes from the receiver's accuracy estimates.
- Raw GNSS research and integrity: enable `publish.rxm.raw` (RAWX) and `publish.nav.sat` to get pseudoranges, carrier phase, C/N0 per SV; record a bag and post-process with [RTKLIB](./rtklibexplorer__rtklib.md) or [gnss_lib_py](./stanford-navlab__gnss_lib_py.md). C/N0 drops and `monhw` jamming indicator are cheap jamming-detection inputs ([gnss-interference](../../catalog/concepts/gnss-interference.md)).
- Timing: TIM devices publish `timtm2` for external event time-tagging (camera triggers).
- Outside ROS, [pyubx2](./semuconsulting__pyubx2.md) reads the same UBX messages and exposes MON-RF jamming/spoofing flags the ROS driver does not publish.

Catalog page: [catalog/repos/kumarrobotics__ublox.md](../../catalog/repos/kumarrobotics__ublox.md). Concepts: [gnss](../../catalog/concepts/gnss.md), [ros](../../catalog/concepts/ros.md).

## Gotchas

- ROS 1 vs ROS 2 is by branch: GitHub default `master` is ROS 1 and stale since 2022; ROS 2 work is on `ros2`. Parameter syntax differs (`publish/nav/pvt` in ROS 1 docs vs `publish.nav.pvt` dotted in ROS 2 YAML).
- `config/zed_f9p.yaml` on `ros2` is headed "Configuration Settings for C94-M8P device" and sets `tmode3: 1` (survey-in base station). Using it on a rover F9P is a common first failure.
- `U-blox: received NACK: 0x06 / 0x01` on F9-series (#230, #267): the node asks for AID messages F9 no longer supports; `publish.aid.all: false` reportedly clears it. Multi-GNSS config on F9P also NACKs (#197).
- The driver configures the receiver on startup using legacy UBX-CFG messages; RTCM output rates are not applied on firmware >= 23.01 which needs CFG-VALSET (#258). Configure F9 base stations with u-center or [pyubx2](./semuconsulting__pyubx2.md) and set `config_on_startup: false` if the node fights you.
- Startup can rewrite the receiver's port baud rate and dies if it cannot (#223, #254). Note the device's baud before first run.
- `/rtcm` is absolute, so it ignores group namespaces in multi-robot launches (#192).
- 100% CPU reported on Raspberry Pi 3B+ (ROS 1, #199).

## Alternatives

- [pyubx2](./semuconsulting__pyubx2.md) - Python, no ROS; full UBX coverage incl. CFG-VALSET and MON-RF; prefer for configuration and quick logging.
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - receiver-agnostic daemon; prefer if the receiver is not u-blox or several processes need the feed.
- [sparkfun/SparkFun_u-blox_GNSS_v3](../../catalog/repos/sparkfun__sparkfun_u-blox_gnss_v3.md) - Arduino/MCU library; prefer on an ESP32/STM32 sensor node.

Sources: `gh api repos/KumarRobotics/ublox` (BSD-3-Clause, branches), README.md on `master` and `ros2`, LICENSE, ros2 branch ublox_gps/launch/ublox_gps_node-launch.py, ublox_gps/config/zed_f9p.yaml, ublox_gps/src/node.cpp (rtcm subscription, parameters), ublox_gps/CMakeLists.txt (executables, component), commits on `ros2` (3.0.0, 2025-09-26) and `master` (2022-12-07), ros/rosdistro distribution.yaml (humble/jazzy/kilted/rolling/noetic), issues #230, #267, #197, #258, #223, #254, #192, #199.
