# Micro XRCE-DDS Agent - integration card
<!-- about: repo:eprosima/micro-xrce-dds-agent -->
One-line: the broker process that turns the autopilot's on-board XRCE-DDS client into normal ROS 2 topics; run it next to PX4 (`/fmu/in|out/*`) or ArduPilot (`/ap/*`) and your VIO/SLAM node can talk to the EKF without MAVLink.

| | |
|---|---|
| Install | Pick the tag that matches your ROS 2 distro, not `master` (see gotchas). PX4 docs: `git clone -b v2.4.3 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git && cd Micro-XRCE-DDS-Agent && mkdir build && cd build && cmake .. && make && sudo make install && sudo ldconfig /usr/local/lib/` (v2.4.3 for Jazzy/Kilted, v2.4.2 for Humble, v3.0.2 for Lyrical/Rolling). Or clone the same tag into a colcon workspace `src/` (repo ships `colcon.pkg`). Snap (`micro-xrce-dds-agent`) and Docker (`eprosima/micro-xrce-dds-agent`, entrypoint `MicroXRCEAgent`) exist per README. ArduPilot instead builds `micro-ROS/micro-ROS-Agent` (branch `humble`) from `Tools/ros2/ros2.repos`, which wraps this agent. |
| Runs on | Linux (UDP/TCP/serial/pseudoterminal/CAN FD), Windows (UDP/TCP only, serial is `#ifndef _WIN32` in `ArgumentParser.hpp`; open issue #321). Default superbuild pulls Fast DDS 3.3 + Fast CDR (`CMakeLists.txt`). CPU only, fine on a Pi or Jetson. Latest release v3.0.2 (2026-09-03). |
| Inputs | XRCE-DDS client traffic from the flight controller over `udp4`/`udp6`/`tcp4`/`tcp6`/`serial`/`multiserial`/`pseudoterminal`/`canfd`. Optional XML refs file (`-r`). |
| Outputs | DDS participants/topics on the ROS 2 domain: PX4 `/fmu/out/*` and `/fmu/in/*` (`px4_msgs`), ArduPilot `/ap/*` (standard ROS msgs + `ardupilot_msgs`). |
| Key API / entry points | CLI `MicroXRCEAgent <transport> [options]` (`include/uxr/agent/utils/ArgumentParser.hpp`): common `-m/--middleware` (default `dds`), `-r/--refs <file>`, `-v/--verbose <0-6>` (default 4), `-d/--discovery [port]` (default 7400), `-P/--p2p`; UDP/TCP `-p/--port <n>`; serial `-D/--dev <tty>`, `-b/--baudrate` (default 115200), `-fc/--flow-control`; multiserial `-D/--devs`; canfd `-D` + `-I/--id`. Library: `eprosima::uxr::AgentInstance::getInstance().create(argc, argv)` then `run()` (`microxrce_agent.cpp`); custom transports in `examples/custom_agent/`. |
| Time to first result | Estimate: 15-30 min from clone to seeing `/fmu/out/*` or `/ap/*` in `ros2 topic list` with SITL. Assumes ROS 2 already installed and the autopilot SITL already builds. |
| License | Apache-2.0. |

## Minimal usage
Command lines from PX4 `docs/en/middleware/uxrce_dds.md` and ArduPilot `libraries/AP_DDS/README.md`. Not run.

```bash
# PX4 SITL: client is on UDP 8888 by default
MicroXRCEAgent udp4 -p 8888
make px4_sitl gz_x500                       # in PX4-Autopilot
ros2 topic list | grep /fmu/

# PX4 hardware, e.g. RPi UART to TELEM2 (PX4 docs example)
sudo MicroXRCEAgent serial --dev /dev/AMA0 -b 921600
# FC side: UXRCE_DDS_CFG = TELEM2 (or Ethernet), port _BAUD param, UXRCE_DDS_DOM_ID

# ArduPilot SITL: client is on UDP 2019 (DDS_UDP_PORT default), agent is the micro-ROS wrapper
ros2 run micro_ros_agent micro_ros_agent udp4 -p 2019
sim_vehicle.py -v ArduCopter -DG --console --enable-DDS     # README uses ArduPlane
ros2 topic echo /ap/navsat

# ArduPilot over serial (README, Pixhawk 6X second USB CDC port)
ros2 run micro_ros_agent micro_ros_agent serial -b 115200 -D /dev/serial/by-id/usb-ArduPilot_Pixhawk6X_<id>-if02
# FC side: DDS_ENABLE=1, SERIALn_PROTOCOL=45, SERIALn_BAUD=115
```

## Wiring it into a nav stack
- PX4 path: VIO/SLAM pose => `/fmu/in/vehicle_visual_odometry` (`px4_msgs/VehicleOdometry`, NED/FRD) => EKF2 with `EKF2_EV_CTRL`. Frame helpers in [px4_ros_com](./px4__px4_ros_com.md); validated publishers in [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md). Message definitions: [px4_msgs](../../catalog/repos/px4__px4_msgs.md). Autopilot: [PX4](./px4__px4-autopilot.md).
- ArduPilot path: publish the `odom` => `base_link` transform on `/ap/tf` (`tf2_msgs/TFMessage`); `AP_DDS_External_Odom.cpp` converts it FLU => NED and calls `AP_VisualOdom::handle_pose_estimate`. Then set EKF3 sources to ExternalNAV and `VISO_TYPE`. See [ardupilot_ros](./ardupilot__ardupilot_ros.md) and [ArduPilot](./ardupilot__ardupilot.md).
- ArduPilot outputs useful for fusion/eval: `/ap/pose/filtered`, `/ap/twist/filtered`, `/ap/geopose/filtered`, `/ap/navsat`, `/ap/imu/experimental/data` (AP_DDS README topic list). Record with `ros2 bag` and score with [evo](./michaelgrupp__evo.md).
- Need GCS telemetry at the same time: keep MAVLink on another port via [mavlink-router](./mavlink-router__mavlink-router.md); the DDS link does not carry MAVLink.
- Catalog: [Micro XRCE-DDS Agent page](../../catalog/repos/eprosima__micro-xrce-dds-agent.md).

## Gotchas
- Version pairing: `master` is v3.0.2 (Fast DDS 3). PX4 v1.18 builds its client for XRCE v2 by default; v3 needs `UXRCE_DDS_CLIENT_USE_DDS_V3` and a custom build. PX4 table: Humble => agent 2.4.2, Jazzy/Kilted => 2.4.3, Lyrical/Rolling => 3.0.2. Cloning the default branch for Humble/Jazzy is the classic "agent connects, no topics" trap.
- Ports differ: PX4 SITL 8888, ArduPilot SITL 2019. One agent instance per link (PX4 docs).
- QoS: PX4 `/fmu/out/*` is best-effort; ArduPilot `/ap/tf_static` needs transient-local to echo (README shows the `--qos-durability transient_local` flags).
- ArduPilot external odom via DDS sends `posErr = angErr = 0` and uses the ROS header stamp directly (TODO for jitter correction in `AP_DDS_External_Odom.cpp`); EKF trust comes from `VISO_*` noise params, not from your covariance. Frame IDs must be exactly `odom` and `base_link`.
- Serial reconnect: open #408 (agent restarts but PX4 1.16 client never reconnects), #357 (Jetson Nano reconnect), #388 (serial stops when an Ethernet interface goes down), #340 (baud rate not set on macOS). Restart the FC side if the link drops.
- Security: no auth on the UDP agent; the PX4 docs recommend keeping it localhost (`UXRCE_DDS_PTCFG`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`) when on a direct link.

## Alternatives
- [MAVROS](./mavlink__mavros.md): MAVLink-based ROS 2 bridge for both autopilots; prefer when you also need parameters/missions or older firmware without DDS.
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md): not a transport but the recommended C++ layer on top of this agent for PX4 nav inputs.
- [mavlink-router](./mavlink-router__mavlink-router.md): if you stay on MAVLink (e.g. [vision_to_mavros](./thien94__vision_to_mavros.md)) and only need to fan out the link.

Sources: `README.md`, `Dockerfile`, `CMakeLists.txt`, `microxrce_agent.cpp`, `include/uxr/agent/utils/ArgumentParser.hpp`, repo tree, releases API; PX4-Autopilot `docs/en/middleware/uxrce_dds.md`; ArduPilot `libraries/AP_DDS/README.md`, `AP_DDS_External_Odom.cpp`, `AP_DDS_Client.cpp` (param defaults), `Tools/ros2/ros2.repos`; issue search (`px4`, `serial`: #408, #388, #357, #340, #321).
