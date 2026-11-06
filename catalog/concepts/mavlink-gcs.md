# MAVLink, ground control and C2 links

`concept:mavlink-gcs`

MAVLink protocol, SDKs, ground control stations, telemetry radios.

**Parent:** [Autopilots and flight control](../concepts/autopilot.md)

## Samples (6)

- [ArduPilot EKF3 source-set switch under GPS denial](../samples/ardupilot-ekf3-source-switch.md) - Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET, cuts simulated GPS, flies a 15 m leg, then restores it.
- [Golden demo: GPS drag on an ArduCopter SITL AUTO mission, chi-square detection and EKF3 switch to vision, replayed on the dashboard](../samples/golden-demo.md) - One command flies ArduCopter 4.6.3 SITL in Docker on a survey, drags its GPS east at 1 m/s with SIM_GPS_GLITCH_X/Y, and runs a pymavlink companion that streams simulated visual-geolocalization fixes as VISION_POSITION_ES
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../samples/sitl-docker.md) - Dockerfiles and a compose file that run ArduCopter 4.6.3 SITL (with a simulated vicon for ExternalNav) and PX4 v1.17.0 SIH quadrotor without Gazebo or a GUI, plus a Python client image with pymavlink and mavsdk-grpc that
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../samples/llm-mission-agent.md) - A small MCP server (stdio JSON-RPC 2.0, pymavlink) that lets Claude Code or any MCP client read and fly an ArduCopter: get_state, get_nav_health (EKF flags, variances, GNSS fix/sats/HDOP => nominal/degraded/lost), arm_ta
- [MAVLink telemetry to TAK Cursor-on-Target](../samples/mavlink-to-tak-cot.md) - Bridges autopilot GLOBAL_POSITION_INT messages into Cursor-on-Target events so a UAV shows up as a friendly track on ATAK, WinTAK or iTAK.
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) - Sends an external pose source (VIO topic or CSV log) to PX4 EKF2 or ArduPilot EKF3 as VISION_POSITION_ESTIMATE or ODOMETRY for GPS-denied position hold.

## Repositories (34)

- [QGroundControl](../repos/mavlink__qgroundcontrol.md) - fit: high - Qt/QML cross-platform GCS (desktop, Android, iOS) for PX4 and ArduPilot: setup, mission planning, video and telemetry.
- [MAVLink](../repos/mavlink__mavlink.md) - fit: high - Message definitions (XML dialects) and the pymavlink-based generator for the MAVLink micro air vehicle protocol, used by PX4, ArduPilot and most GCS tools.
- [MAVROS](../repos/mavlink__mavros.md) - fit: high - ROS/ROS 2 node bridging MAVLink to ROS topics and services, with GCS proxy; widely used to push vision/SLAM poses into PX4 or ArduPilot.
- [MAVSDK](../repos/mavlink__mavsdk.md) - fit: high - C++ SDK exposing high-level MAVLink plugins (action, mission, offboard, telemetry, camera) with a gRPC server for other languages.
- [pymavlink](../repos/ardupilot__pymavlink.md) - fit: high - Python MAVLink implementation plus tools for connections, log parsing (DataFlash/tlog) and code generation.
- [COEX Clover](../repos/copterexpress__clover.md) - fit: high - ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath).
- [mavlink-router](../repos/mavlink-router__mavlink-router.md) - fit: high - Lightweight C++ daemon that routes MAVLink between serial, UDP and TCP endpoints with filtering and logging.
- [MAVProxy](../repos/ardupilot__mavproxy.md) - fit: high - Command-line, module-based ground station and MAVLink proxy with map, console and many plugins.
- [BlueOS](../repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [MAVSDK-Python](../repos/mavlink__mavsdk-python.md) - fit: high - Asyncio Python client for MAVSDK that wraps a bundled mavsdk_server.
- [cflib (Crazyflie Python library)](../repos/bitcraze__crazyflie-lib-python.md) - fit: high - Python API to connect, log, set parameters and send setpoints/high-level commands to Crazyflies over Crazyradio or USB.
- [vision_to_mavros](../repos/thien94__vision_to_mavros.md) - fit: high - ROS and Python scripts that convert external localisation (fiducials, T265 VIO, SLAM, depth) into MAVROS/MAVLink pose messages, tested on ArduPilot.
- [mavp2p](../repos/bluenviron__mavp2p.md) - fit: high - Single-binary Go MAVLink router/proxy supporting serial, UDP and TCP with deduplication.
- [Rpanion-server](../repos/stephendade__rpanion-server.md) - fit: high - Web-based companion-computer manager for MAVLink vehicles: telemetry routing, video streaming, logging and network config on Raspberry Pi/Jetson.
- [MAVLinkMCP](../repos/ion-g-ion__mavlinkmcp.md) - fit: high - MCP server bridging an LLM to a drone over MAVLink, exposing arming, takeoff, waypoint and telemetry tools via MAVSDK.
- [OpenHD](../repos/openhd__openhd.md) - fit: medium - Open-source long-range digital HD video and telemetry link over Wi-Fi adapters in monitor mode (wifibroadcast-style), for air and ground units.
- [Mission Planner](../repos/ardupilot__missionplanner.md) - fit: medium - Windows-centric C#/.NET GCS for ArduPilot with deep parameter, log-analysis and mission tooling.
- [WFB-ng](../repos/svpcom__wfb-ng.md) - fit: medium - Long-range packet radio link over raw Wi-Fi injection with FEC, carrying video, MAVLink and IP tunnels.
- [mLRS](../repos/olliw42__mlrs.md) - fit: medium - LoRa-based bidirectional link carrying RC and full MAVLink serial data on 2.4 GHz, 868/915 MHz and 433 MHz.
- [rust-mavlink](../repos/mavlink__rust-mavlink.md) - fit: medium - Rust implementation of MAVLink with generated dialects and serial/UDP/TCP connections.
- [PX4 Flight Review](../repos/px4__flight_review.md) - fit: medium - Web app for uploading and plotting PX4 ULog flight logs, including estimator innovations and test ratios.
- [UAV Log Viewer](../repos/ardupilot__uavlogviewer.md) - fit: medium - Browser-based viewer for ArduPilot DataFlash and MAVLink logs (also reads PX4 ULog), with 3D replay and plotting.
- [gomavlib](../repos/bluenviron__gomavlib.md) - fit: medium - Go MAVLink v1/v2 library with dialect generation and multiple transports.
- [MAVLink Camera Manager](../repos/mavlink__mavlink-camera-manager.md) - fit: medium - Rust service that exposes cameras as MAVLink camera components and streams video (RTSP/UDP) to GCS.
- [MAVLink Developer Guide](../repos/mavlink__mavlink-devguide.md) - fit: medium - Source of the mavlink.io documentation: protocol, microservices (mission, parameters, camera, Open Drone ID) and message reference.
- [jMAVSim](../repos/px4__jmavsim.md) - fit: medium - Lightweight Java multirotor simulator that speaks MAVLink to PX4, without a 3D-world physics engine.
- [node-mavlink](../repos/ardupilot__node-mavlink.md) - fit: medium - TypeScript/Node.js MAVLink bindings and tools.
- [DroneMagNav](../repos/ajisrawi__dronemagnav.md) - fit: medium - Open hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller 
- [mavlink-mcp (ArduPilot)](../repos/deepakpopli__mavlink-mcp.md) - fit: medium - MCP server for flying ArduPilot vehicles from AI agents over MAVLink, covering missions, camera vision and SITL workflows.
- [ardupilot-mcp (safety-gated)](../repos/rmeadomavic__ardupilot-mcp.md) - fit: medium - SITL-first MCP server for talking to ArduPilot vehicles over MAVLink, with explicit safety gating of commands.
- [DroneKit-Python](../repos/dronekit__dronekit-python.md) - fit: low - Older high-level Python API for MAVLink vehicles, built on pymavlink; maintenance has slowed (last push 2024).
- [APM Planner 2](../repos/ardupilot__apm_planner.md) - fit: low - Qt-based cross-platform ArduPilot GCS, now largely in maintenance mode.
- [SiK radio firmware](../repos/ardupilot__sik.md) - fit: low - Firmware and tools for Si1000-based telemetry radios (3DR/RFD900 class) carrying MAVLink.
- [ArduPilot Copter - українською](../repos/c-o-s-t-y-a__ardupilot_ua.md) - fit: low - Unofficial Ukrainian translation of key sections of the ArduPilot Copter documentation, with a translation-status file and a built site.

## Documents, talks, courses, datasets (10)

- [MAVLink 2 and Message Signing](../resources/mavlink-2-signing.md) - doc - Describes MAVLink 2 packet signing: a shared-secret SHA-256 based signature and timestamp appended to frames to authenticate the link and resist replay.
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) - doc - Reference of all messages and commands in the common dialect, including GPS_RAW_INT, GPS_INPUT for injecting external position, ODOMETRY and VISION_POSITION_ESTIMATE for non-GNSS navigation sources.
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) - doc - Official documentation for the MAVLink micro air vehicle messaging protocol: message definitions, microservices (mission, parameters, camera, FTP), dialects and code generators.
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) - doc - The microservice used to upload, download and clear waypoint missions, geofences and rally points between a GCS and an autopilot, with its handshake and retry rules.
- [Non-GPS Position Estimation (MAVLink messages)](../resources/ardupilot-dev-mavlink-nongps-position.md) - doc - Developer page listing the MAVLink messages ArduPilot accepts for external position/velocity estimates and their expected frames.
- [Open Drone ID (MAVLink microservice)](../resources/mavlink-opendroneid-microservice.md) - doc - Defines the MAVLink messages and flow for Remote ID between flight controller, GCS and transponder.
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) - doc - How to run PX4 software-in-the-loop with Gazebo and other simulators, including multi-vehicle setups and connecting ROS 2 and ground stations.
- [ROS and VIO tracking camera for non-GPS navigation](../resources/ardupilot-ros-vio-tracking-camera.md) - doc - Developer tutorial wiring a VIO camera through ROS and MAVROS into ArduPilot for indoor flight.
- [STANAG 4586 - Standard Interfaces of UAV Control System (UCS) for NATO UAV Interoperability](../resources/stanag-4586-overview.md) - doc - Public overview of NATO's UAS interoperability standard, which defines a core UCS, a vehicle-specific module and five levels of interoperability from receiving payload data up to full flight control including launch and 
- [Навигация по карте маркеров · Clover](../resources/coex-clover-docs-aruco-map-ru.md) - doc - English: 'Navigation by marker map - Clover docs'.

