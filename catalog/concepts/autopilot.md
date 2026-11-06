# Autopilots and flight control

`concept:autopilot`

Flight stacks, control loops, estimation inside autopilots, firmware.

**Sub-concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

## Samples (3)

- [ArduPilot EKF3 source-set switch under GPS denial](../samples/ardupilot-ekf3-source-switch.md) - Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET or an RC aux switch, cuts simulated GPS, keeps flying, then restores it.
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) - Flies a square mission in PX4 SITL (Gazebo gz_x500), turns the GPS off mid-mission with MAVSDK failure injection, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home.
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) - Sends an external pose source (VIO topic or CSV log) to PX4 EKF2 or ArduPilot EKF3 as VISION_POSITION_ESTIMATE or ODOMETRY for GPS-denied position hold.

## Repositories (36)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) - fit: high - Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware.
- [Crazyflie firmware](../repos/bitcraze__crazyflie-firmware.md) - fit: high - Firmware for the Crazyflie nano quad, Bolt and the Roadrunner positioning tag, with EKF and complementary estimators supporting UWB Loco positioning, Lighthouse, Flow deck and mocap.
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) - fit: high - Current-generation Gazebo robotics simulator with pluggable physics, rendering and a large sensor library (IMU, GPS/NavSat, lidar, cameras, magnetometer, altimeter).
- [MAVSDK](../repos/mavlink__mavsdk.md) - fit: high - C++ SDK exposing high-level MAVLink plugins (action, mission, offboard, telemetry, camera) with a gRPC server for other languages.
- [BlueOS](../repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [MAVSDK-Python](../repos/mavlink__mavsdk-python.md) - fit: high - Asyncio Python client for MAVSDK that wraps a bundled mavsdk_server.
- [cflib (Crazyflie Python library)](../repos/bitcraze__crazyflie-lib-python.md) - fit: high - Python API to connect, log, set parameters and send setpoints/high-level commands to Crazyflies over Crazyradio or USB.
- [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md) - fit: high - Gazebo Sim plugins and models that connect ArduPilot SITL to Gazebo physics for copters, rovers and boats.
- [px4_ros_com](../repos/px4__px4_ros_com.md) - fit: high - Example ROS 2 nodes and helpers (frame transforms) for interfacing with PX4 over DDS.
- [ROS2 PX4 Offboard Example](../repos/ark-electronics__ros2_px4_offboard_example.md) - fit: high - Small example of driving PX4 velocity setpoints from ROS 2 teleop, with SITL launch files.
- [PX4 ROS 2 Interface Library](../repos/auterion__px4-ros2-interface-lib.md) - fit: high - C++ library for writing PX4 flight modes and navigation-data sources in ROS 2 on a companion computer, registered with PX4 as first-class modes.
- [px4_msgs](../repos/px4__px4_msgs.md) - fit: high - ROS 2 message definitions mirroring PX4 uORB topics, used with the uXRCE-DDS bridge.
- [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md) - fit: high - ROS 2 integration examples for ArduPilot, including Cartographer-based non-GPS navigation and Nav2 setups.
- [INAV](../repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [ESP-Drone](../repos/espressif__esp-drone.md) - fit: medium - Espressif's mini quadcopter firmware for ESP32/ESP32-S2/S3, derived from Crazyflie code, controlled over Wi-Fi.
- [dRehmFlight VTOL](../repos/nickrehm__drehmflight.md) - fit: medium - Single-file Arduino/Teensy flight controller for small VTOL and multirotor craft, written to be read and modified by students.
- [Pegasus Simulator](../repos/pegasussimulator__pegasussimulator.md) - fit: medium - Framework on top of NVIDIA Isaac Sim for simulating multirotors with PX4 in the loop and Python-defined vehicles and sensors.
- [MRS UAV System](../repos/ctu-mrs__mrs_uav_system.md) - fit: medium - Czech Technical University's multi-robot UAV platform with control, estimation (including GNSS-denied modes), planning and simulation, field-tested in outdoor swarm deployments.
- [PX4 SITL Gazebo Classic](../repos/px4__px4-sitl_gazebo-classic.md) - fit: medium - Plugins, vehicle models and worlds that connect PX4 SITL/HITL to Gazebo Classic, including GPS, IMU, magnetometer, barometer and optical-flow plugins.
- [Aerostack2](../repos/aerostack2__aerostack2.md) - fit: medium - ROS 2 framework for autonomous multi-aerial-robot systems: platform abstraction (PX4, DJI, Crazyflie, Gazebo), behaviors, mission scripting in Python and BT, and multi-drone coordination.
- [ROSflight firmware](../repos/rosflight__rosflight_firmware.md) - fit: medium - Lean research autopilot (BYU) that keeps only attitude estimation and low-level control on the flight board and pushes everything else to a ROS companion.
- [ArduPilot SITL Models](../repos/ardupilot__sitl_models.md) - fit: medium - Collection of aircraft and vehicle models and parameter files for ArduPilot SITL across several simulator backends.
- [Vortex AUV](../repos/vortexntnu__vortex-auv.md) - fit: medium - Guidance, navigation and control software from NTNU's student Vortex team for competition AUVs and ROVs, built on ROS 2.
- [PX4 Gazebo models](../repos/px4__px4-gazebo-models.md) - fit: medium - Model and world repository for the new Gazebo, used by PX4 SITL targets such as gz_x500.
- [DroneMagNav](../repos/ajisrawi__dronemagnav.md) - fit: medium - Open hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller 
- [Betaflight](../repos/betaflight__betaflight.md) - fit: low - Racing/freestyle-oriented flight controller firmware focused on attitude control and low-latency filtering; GPS rescue mode is its main navigation feature.
- [DroneKit-Python](../repos/dronekit__dronekit-python.md) - fit: low - Older high-level Python API for MAVLink vehicles, built on pymavlink; maintenance has slowed (last push 2024).
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [OpenPilot (mirror)](../repos/openpilot__openpilot.md) - fit: low - Mirror of the original OpenPilot flight controller project (not comma.ai's openpilot), frozen since 2015.
- [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md) - fit: low - Former home of PX4's estimation and control library including the EKF2 navigation filter; archived after the code moved into PX4-Autopilot.
- [LibrePilot](../repos/librepilot__librepilot.md) - fit: low - GitHub mirror of LibrePilot, the community continuation of OpenPilot for CC3D/Revolution boards, with the GCS bundled.
- [GEARdrones](../repos/excitablecell__geardrones.md) - fit: low - Lightweight STM32 drone control and multi-agent localization system combining a flight controller, UWB relative localization and a monitor tool.
- [ArduPilot Methodic Configurator](../repos/ardupilot__methodicconfigurator.md) - fit: low - Guided step-by-step parameter configuration tool for ArduPilot vehicles.
- [Time-optimal quadrotor planning](../repos/uzh-rpg__rpg_time_optimal.md) - fit: low - Code for computing time-optimal quadrotor trajectories through waypoints, from the UZH group that placed second in AlphaPilot and built Swift.
- [DroneCAN libcanard](../repos/dronecan__libcanard.md) - fit: low - Minimal C implementation of the DroneCAN protocol used for GNSS, compass, airspeed and other peripherals on CAN.

## Documents, talks, courses, datasets (21)

- [2025 Abu Dhabi Autonomous Racing League (A2RL) - drone championship](../resources/a2rl-2025-season.md) - doc - Summary of the A2RL x DCL autonomous drone championship, won by TU Delft MAVLab ahead of TII Racing and KAIST, including races against human pilots.
- [AlphaPilot: Autonomous Drone Racing](../resources/alphapilot-uzh-paper.md) - paper - UZH's second-place AlphaPilot system: learned gate detection, nonlinear filtering of visual-inertial state and time-optimal trajectory planning for GPS-free racing.
- [ArduPilot Developer Conference Kaga 2024 - schedule and YouTube links](../resources/ardupilot-devcon-kaga-2024.md) - talk - Three days of recorded ArduPilot developer talks; navigation-relevant sessions include 'High Altitude Non-GPS' (Sanket Sharma), 'CINS (DCM replacement)' (Pieter Van Goor, ANU), indoor flight and position offsets.
- [ArduPilot SITL Simulator (Software in the Loop)](../resources/ardupilot-sitl-docs.md) - doc - Developer docs for running ArduPilot vehicles in SITL, connecting GCS and external simulators.
- [ArduSub documentation](../resources/ardusub-docs.md) - doc - User and developer documentation for ArduSub, covering ROV configuration, sensors, and integration of external positioning such as DVL and USBL via MAVLink.
- [Autonomous Navigation for Flying Robots (TUM edX, AUTONAVx)](../resources/tum-autonavx.md) - course - MOOC version of the TUM flying-robots lecture with lecture videos and browser-based Python exercises on quadrotor state estimation, Kalman filtering, control and visual navigation.
- [EKF Source Selection and Switching](../resources/ardupilot-ekf3-sources.md) - doc - Reference for EKF3 source parameters (position, velocity, yaw per axis) and how fusion of multiple velocity sources works.
- [HACKtheMACHINE Unmanned (ONR / NavalX)](../resources/onr-hackthemachine-unmanned-2021.md) - competition - US Navy prize challenge on unmanned and autonomous systems with tracks on securing a simulated autopilot, separating benign from malicious data, and model-based mission requirements.
- [MAVLab wins the AlphaPilot challenge](../resources/mavlab-alphapilot-win-2019.md) - blog - TU Delft MAVLab's account of winning the 2019 Lockheed Martin AlphaPilot / AIRR autonomous drone race.
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) - doc - Reference of all messages and commands in the common dialect, including GPS_RAW_INT, GPS_INPUT for injecting external position, ODOMETRY and VISION_POSITION_ESTIMATE for non-GNSS navigation sources.
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) - doc - Official documentation for the MAVLink micro air vehicle messaging protocol: message definitions, microservices (mission, parameters, camera, FTP), dialects and code generators.
- [Non-GPS Navigation](../resources/ardupilot-non-gps-navigation-docs.md) - doc - Landing page in the ArduPilot wiki listing every supported way to navigate without GNSS: optical flow, beacons, wheel encoders, visual odometry/VIO cameras, motion capture and MAVLink external position.
- [PX4 Autopilot YouTube channel](../resources/px4-youtube-channel.md) - video - Official channel with PX4 Developer Summit recordings, dev calls and feature demos.
- [PX4 Developer Summit (talks and recordings)](../resources/px4-developer-summit.md) - talk - Annual PX4 developer conference; recordings are posted on the PX4 YouTube channel.
- [PX4 Developer Summit 2025 Recap](../resources/dronecode-px4-dev-summit-2025-recap.md) - blog - Dronecode recap of the 2025 summit, pointing to the schedule and recordings.
- [PX4 Developer Summit 2025 recordings](../resources/px4-dev-summit-2025-playlist.md) - video - YouTube playlist of 2025 PX4 Developer Summit talks; the program included GNSS and navigation sessions, among them a talk on structure-aided visual localisation for PX4 indoors (SAVLoc).
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) - doc - How to run PX4 software-in-the-loop with Gazebo and other simulators, including multi-vehicle setups and connecting ROS 2 and ground stations.
- [Relative navigation of fixed-wing aircraft in GPS-denied environments](../resources/ion-webinar-brink.md) - talk - AFRL perspective on relative navigation for fixed-wing aircraft without GPS, keeping estimation consistent by working in a relative frame with periodic global updates.
- [STANAG 4586 - Standard Interfaces of UAV Control System (UCS) for NATO UAV Interoperability](../resources/stanag-4586-overview.md) - doc - Public overview of NATO's UAS interoperability standard, which defines a core UCS, a vehicle-specific module and five levels of interoperability from receiving payload data up to full flight control including launch and 
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) - doc - PX4 guide to its EKF2 estimator: which sensors it fuses (IMU, GNSS, baro, mag, optical flow, external vision, range), how to configure and tune them, and how to read innovation logs.
- [Visual Navigation for Flying Robots (TUM, 2013)](../resources/tum-visual-navigation-flying-robots.md) - lecture-series - Award-winning TUM lecture on making quadrotors navigate with cameras: 3D geometry, sensors, state estimation, visual motion estimation, SLAM, dense reconstruction, planning and exploration.

