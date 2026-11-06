# Autopilots and flight control

`concept:autopilot`

Flight stacks, control loops, estimation inside autopilots, firmware.

**Sub-concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

## Samples (6)

- [ArduPilot EKF3 source-set switch under GPS denial](../../catalog/samples/ardupilot-ekf3-source-switch.md) - Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET, cuts simulated GPS, flies a 15 m leg, then restores it.
- [Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay](../../catalog/samples/golden-demo-px4.md) - The samples/golden-demo v2 scenario on PX4 v1.17.0 SIH in Docker.
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) - One command flies ArduCopter 4.6.3 SITL in Docker on a survey and drags its GPS east.
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../../catalog/samples/sitl-docker.md) - Dockerfiles and a compose file that run ArduCopter 4.6.3 SITL (with a simulated vicon for ExternalNav) and PX4 v1.17.0 SIH quadrotor without Gazebo or a GUI, plus a Python client image with pymavlink and mavsdk-grpc that
- [PX4 SITL GPS denial: inject, measure drift, recover](../../catalog/samples/px4-sitl-gps-denial.md) - Flies a square mission in PX4 SITL (SIH quadrotor, headless; Gazebo also works per PX4 docs), denies GPS mid-mission, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home.
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) - Sends an external pose source (VIO topic or CSV log) to PX4 EKF2 or ArduPilot EKF3 as VISION_POSITION_ESTIMATE or ODOMETRY for GPS-denied position hold.

## Guides (1)

- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) - After this chapter you can run PX4 or ArduPilot in simulation, inject your own position source over MAVLink, configure the estimator to switch away from GNSS, and push your vehicle's position and detections onto a TAK co

## Repositories (41)

- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) - fit: high - Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware.
- [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md) - fit: high - Current-generation Gazebo robotics simulator with pluggable physics, rendering and a large sensor library (IMU, GPS/NavSat, lidar, cameras, magnetometer, altimeter).
- [MAVSDK](../../catalog/repos/mavlink__mavsdk.md) - fit: high - C++ SDK exposing high-level MAVLink plugins (action, mission, offboard, telemetry, camera) with a gRPC server for other languages.
- [COEX Clover](../../catalog/repos/copterexpress__clover.md) - fit: high - ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath).
- [BlueOS](../../catalog/repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md) - fit: high - Asyncio Python client for MAVSDK that wraps a bundled mavsdk_server.
- [cflib (Crazyflie Python library)](../../catalog/repos/bitcraze__crazyflie-lib-python.md) - fit: high - Python API to connect, log, set parameters and send setpoints/high-level commands to Crazyflies over Crazyradio or USB.
- [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md) - fit: high - Gazebo Sim plugins that connect ArduPilot SITL to Gazebo physics, with example Iris copter and Zephyr plane models and worlds.
- [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md) - fit: high - Example ROS 2 nodes and helpers (frame transforms) for interfacing with PX4 over DDS.
- [ROS2 PX4 Offboard Example](../../catalog/repos/ark-electronics__ros2_px4_offboard_example.md) - fit: high - Small example of driving PX4 velocity setpoints from ROS 2 teleop, with SITL launch files.
- [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md) - fit: high - C++ library for writing PX4 flight modes and navigation-data sources in ROS 2 on a companion computer, registered with PX4 as first-class modes.
- [px4_msgs](../../catalog/repos/px4__px4_msgs.md) - fit: high - ROS 2 message definitions mirroring PX4 uORB topics, used with the uXRCE-DDS bridge.
- [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md) - fit: high - ROS 2 integration examples for ArduPilot, including Cartographer-based non-GPS navigation and Nav2 setups.
- [INAV](../../catalog/repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [ESP-Drone](../../catalog/repos/espressif__esp-drone.md) - fit: medium - Espressif's mini quadcopter firmware for ESP32/ESP32-S2/S3, derived from Crazyflie code, controlled over Wi-Fi.
- [dRehmFlight VTOL](../../catalog/repos/nickrehm__drehmflight.md) - fit: medium - Single-file Arduino/Teensy flight controller for small VTOL and multirotor craft, written to be read and modified by students.
- [Pegasus Simulator](../../catalog/repos/pegasussimulator__pegasussimulator.md) - fit: medium - Framework on top of NVIDIA Isaac Sim for simulating multirotors with PX4 in the loop and Python-defined vehicles and sensors.
- [MRS UAV System](../../catalog/repos/ctu-mrs__mrs_uav_system.md) - fit: medium - Czech Technical University's multi-robot UAV platform with control, estimation (including GNSS-denied modes), planning and simulation, field-tested in outdoor swarm deployments.
- [PX4 SITL Gazebo Classic](../../catalog/repos/px4__px4-sitl_gazebo-classic.md) - fit: medium - Plugins, vehicle models and worlds that connect PX4 SITL/HITL to Gazebo Classic, including GPS, IMU, magnetometer, barometer and optical-flow plugins.
- [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md) - fit: medium - ROS 2 framework for autonomous single and multi-aerial-robot systems with behaviours, state estimation plugins and platform adapters (Gazebo and a multirotor simulator in this repo; PX4, Crazyflie and DJI adapters in sep
- [ROSflight firmware](../../catalog/repos/rosflight__rosflight_firmware.md) - fit: medium - Lean research autopilot (BYU) that keeps only attitude estimation and low-level control on the flight board and pushes everything else to a ROS companion.
- [ArduPilot SITL Models](../../catalog/repos/ardupilot__sitl_models.md) - fit: medium - Collection of aircraft and vehicle models and parameter files for ArduPilot SITL, mostly for the RealFlight simulator (planes, quadplanes, tailsitters, helicopters, multicopters) plus a Gazebo package with models and wor
- [Vortex AUV](../../catalog/repos/vortexntnu__vortex-auv.md) - fit: medium - Guidance, navigation and control software from NTNU's student Vortex team for competition AUVs and ROVs, built on ROS 2.
- [PX4 Gazebo models](../../catalog/repos/px4__px4-gazebo-models.md) - fit: medium - Model and world repository for the new Gazebo, used by PX4 SITL targets such as gz_x500.
- [DroneMagNav](../../catalog/repos/ajisrawi__dronemagnav.md) - fit: medium - Hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller over 
- [Betaflight](../../catalog/repos/betaflight__betaflight.md) - fit: low - Racing/freestyle-oriented flight controller firmware focused on attitude control and low-latency filtering.
- [DroneKit-Python](../../catalog/repos/dronekit__dronekit-python.md) - fit: low - Older high-level Python API for MAVLink vehicles, built on pymavlink; maintenance has slowed (last push 2024).
- [Paparazzi UAV](../../catalog/repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [OpenPilot (mirror)](../../catalog/repos/openpilot__openpilot.md) - fit: low - Mirror of the original OpenPilot flight controller project (not comma.ai's openpilot), frozen since 2015.
- [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md) - fit: low - Former home of PX4's estimation and control library including the EKF2 navigation filter; archived after the code moved into PX4-Autopilot.
- [LibrePilot](../../catalog/repos/librepilot__librepilot.md) - fit: low - GitHub mirror of LibrePilot, the community continuation of OpenPilot for CC3D/Revolution boards, with the GCS bundled.
- [GEARdrones](../../catalog/repos/excitablecell__geardrones.md) - fit: low - Lightweight STM32 drone control and multi-agent localization system combining a flight controller, UWB relative localization and a monitor tool.
- [ArduPilot Methodic Configurator](../../catalog/repos/ardupilot__methodicconfigurator.md) - fit: low - Guided step-by-step parameter configuration tool for ArduPilot vehicles; the sequence is complete for ArduCopter, while Plane, Heli and Rover guides are still incomplete.
- [Time-optimal quadrotor planning](../../catalog/repos/uzh-rpg__rpg_time_optimal.md) - fit: low - Code for computing time-optimal quadrotor trajectories through waypoints, from the UZH group that placed second in AlphaPilot and built Swift.
- [DroneCAN libcanard](../../catalog/repos/dronecan__libcanard.md) - fit: low - Minimal C implementation of the DroneCAN protocol used for GNSS, compass, airspeed and other peripherals on CAN.
- [Geoscan Pioneer Max](../../catalog/repos/geoscan__geoscan_pioneer_max.md) - fit: low - Meta-repository from Russian vendor Geoscan for the Pioneer Max educational quadcopter: system images, ROS workspace, web control apps and guides, documented in Russian.
- [CRTClover - Clover Rescue Team backend](../../catalog/repos/devmbs__crtclover.md) - fit: low - Drone-side backend of the Clover Rescue project (CopterHack 2022, third place), which the team describes as returning the Clover to the user or takeoff point with one click when radio contact is lost.
- [ArduPilot Copter - українською](../../catalog/repos/c-o-s-t-y-a__ardupilot_ua.md) - fit: low - Unofficial Ukrainian translation of key sections of the ArduPilot Copter documentation, with a translation-status file and a built site.
- [V-NAV (CopterHack 2022) - visual navigation for Clover](../../catalog/repos/v-nav__clover.md) - fit: low - Archived fork of the Clover framework holding team V-NAV's CopterHack 2022 entry (article in docs/ru/v-nav.md on branch v-nav_article): a multi-camera plus IMU optical navigation module using graph-based SLAM with CNN-ex

## Documents, talks, courses, datasets (33)

- [2025 Abu Dhabi Autonomous Racing League](../../catalog/resources/a2rl-2025-season.md) - doc - Summary of the A2RL x DCL autonomous drone championship, won by TU Delft MAVLab ahead of TII Racing and KAIST, including races against human pilots.
- [AlphaPilot: Autonomous Drone Racing](../../catalog/resources/alphapilot-uzh-paper.md) - paper - UZH's second-place AlphaPilot system: learned gate detection, nonlinear filtering of visual-inertial state and time-optimal trajectory planning for GPS-free racing.
- [ArduPilot DevCon 2026 (Ottawa) programme](../../catalog/resources/ardupilot-devcon-2026-ottawa.md) - talk - Programme for the October 2026 ArduPilot developer conference, including a live non-GPS Copter demo using a camera and preloaded satellite imagery for absolute positioning.
- [ArduPilot Developer Conference Kaga 2024 - Schedule and YouTube Links](../../catalog/resources/ardupilot-devcon-kaga-2024.md) - talk - Three days of recorded ArduPilot developer talks; navigation-relevant sessions include 'High Altitude Non-GPS' (Sanket Sharma), 'CINS (DCM replacement)' (Pieter Van Goor, ANU), indoor flight and position offsets.
- [ArduSub documentation](../../catalog/resources/ardusub-docs.md) - doc - User and developer documentation for ArduSub, covering ROV configuration, sensors, and integration of external positioning such as DVL and USBL via MAVLink.
- [Auterion Skynode S and Auterion Visual Navigation](../../catalog/resources/auterion-skynode-visual-navigation.md) - product - Auterion sells PX4-derived AuterionOS plus Skynode flight/mission computers.
- [Autonomous Navigation for Flying Robots (TUM edX, AUTONAVx)](../../catalog/resources/tum-autonavx.md) - course - MOOC version of the TUM flying-robots lecture with lecture videos and browser-based Python exercises on quadrotor state estimation, Kalman filtering, control and visual navigation.
- [CopterHack 2022](../../catalog/resources/copterhack-2022.md) - competition - Results page for CopterHack 2022, an open-source drone project competition on the Clover platform; the final was on April 23, 2022 and Atena - Grupo SEMEAR (Swarm in Blocks, 21.6 points) won ahead of FTL (Advanced Clover
- [CopterHack 2023](../../catalog/resources/coex-copterhack-2023.md) - competition - Russian-language page of COEX's international open-source flying-robotics contest built on the Clover platform: format (teams develop open-source projects over months with expert feedback), final standings and links to p
- [CVAR-UPM Drone Team - A2RL](../../catalog/resources/cvar-upm-a2rl-team.md) - blog - Team page describing participation in A2RL seasons 1 and 2 using the open Aerostack2 framework, MPCC control and multi-gate visual positioning.
- [EKF Source Selection and Switching](../../catalog/resources/ardupilot-ekf3-sources.md) - doc - Reference for EKF3 source parameters (position, velocity, yaw per axis) and how fusion of multiple velocity sources works.
- [HACKtheMACHINE Unmanned (ONR / NavalX)](../../catalog/resources/onr-hackthemachine-unmanned-2021.md) - competition - US Navy prize challenge on unmanned and autonomous systems with tracks on securing a simulated autopilot, separating benign from malicious data, and model-based mission requirements.
- [ICRA 2025 workshop: 25 years of aerial robotics - challenges and opportunities](../../catalog/resources/icra-2025-25-years-aerial-robotics.md) - talk - ICRA 2025 workshop covering aerial perception, navigation and planning.
- [MAVLab wins the AlphaPilot AI challenge](../../catalog/resources/mavlab-alphapilot-win-2019.md) - blog - TU Delft MAVLab's account of winning the 2019 Lockheed Martin AlphaPilot / AIRR autonomous drone race.
- [MAVLink Common Message Set (common.xml)](../../catalog/resources/mavlink-common-messages.md) - doc - Reference of all messages and commands in the common dialect, including GPS_RAW_INT, GPS_INPUT for injecting external position, ODOMETRY and VISION_POSITION_ESTIMATE for non-GNSS navigation sources.
- [MAVLink Developer Guide](../../catalog/resources/mavlink-developer-guide.md) - doc - Official documentation for the MAVLink micro air vehicle messaging protocol: message definitions, microservices (mission, parameters, camera, FTP), dialects and code generators.
- [Non-GPS Navigation](../../catalog/resources/ardupilot-non-gps-navigation-docs.md) - doc - ArduPilot Copter documentation hub for flying without GPS: optical flow, visual odometry cameras (RealSense T265, OAK-D, ModalAI VOXL), motion capture (OptiTrack, Vicon, Nokov), beacons/UWB (Marvelmind, Pozyx, Nooploop),
- [On Your Own: Pro-level Autonomous Drone Racing in Uninstrumented Arenas](../../catalog/resources/tii-pro-level-drone-racing-2025.md) - paper - Autonomous drone racing using only onboard sensing in arenas without motion capture, with released human pilot flight data.
- [PX4 Autopilot YouTube channel](../../catalog/resources/px4-youtube-channel.md) - video - Official channel with PX4 Developer Summit recordings, dev calls and feature demos.
- [PX4 Developer Summit (talks and recordings)](../../catalog/resources/px4-developer-summit.md) - talk - Annual PX4 developer conference; recordings are posted on the PX4 YouTube channel.
- [PX4 Developer Summit 2025 Recap](../../catalog/resources/dronecode-px4-dev-summit-2025-recap.md) - blog - Dronecode recap of the 2025 summit, pointing to the schedule and recordings.
- [PX4 Developer Summit 2025 recordings](../../catalog/resources/px4-dev-summit-2025-playlist.md) - video - YouTube playlist of 2025 PX4 Developer Summit talks; the program included GNSS and navigation sessions, among them a talk on structure-aided visual localisation for PX4 indoors (SAVLoc).
- [PX4 Simulation (Gazebo, SITL) documentation](../../catalog/resources/px4-simulation-docs.md) - doc - How to run PX4 software-in-the-loop with Gazebo and other simulators, including multi-vehicle setups and connecting ROS 2 and ground stations.
- [Relative navigation of fixed-wing aircraft in GPS-denied environments](../../catalog/resources/ion-webinar-brink.md) - talk - AFRL perspective on relative navigation for fixed-wing aircraft without GPS, keeping estimation consistent by working in a relative frame with periodic global updates.
- [SITL Simulator (Software in the Loop)](../../catalog/resources/ardupilot-sitl-docs.md) - doc - Developer docs for running ArduPilot vehicles in SITL, connecting GCS and external simulators.
- [STANAG 4586 - Standard Interfaces of UAV Control System (UCS) for NATO UAV Interoperability](../../catalog/resources/stanag-4586-overview.md) - doc - Public overview of NATO's UAS interoperability standard, which defines a core UCS, a vehicle-specific module and five levels of interoperability from receiving payload data up to full flight control including launch and 
- [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md) - doc - PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.
- [Visual Navigation for Flying Robots (TUM, 2013)](../../catalog/resources/tum-visual-navigation-flying-robots.md) - lecture-series - Award-winning TUM lecture on making quadrotors navigate with cameras: 3D geometry, sensors, state estimation, visual motion estimation, SLAM, dense reconstruction, planning and exploration.
- [В поисках автономного полета](../../catalog/resources/vcru-zimkov-autonomous-flight-2025.md) - blog - English: 'In search of autonomous flight' (15 Dec 2025).
- [Датчик оптического потока -MTF02](../../catalog/resources/habr-mtf02-optical-flow-sensor-2025.md) - blog - English: 'MTF02 optical flow sensor'.
- [Навигация по Optical Flow · Clover](../../catalog/resources/coex-clover-docs-optical-flow-ru.md) - doc - English: 'Optical Flow navigation - Clover docs'.
- [Навигация по карте маркеров · Clover](../../catalog/resources/coex-clover-docs-aruco-map-ru.md) - doc - English: 'Navigation by marker map - Clover docs'.
- [Система управління та навігації БПЛА](../../catalog/resources/kpi-spaskyi-uav-control-nav-under-ew-2025.md) - paper - English: 'UAV control and navigation system'.

