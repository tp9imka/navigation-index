# Underwater navigation

`concept:underwater-nav`

DVL, USBL/LBL acoustics, AUV navigation, underwater SLAM.

## Repositories (21)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [BlueOS](../repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [Stonefish](../repos/patrykcieslak__stonefish.md) - fit: high - C++ simulation library for marine robotics with hydrodynamics, underwater rendering and sensors including DVL, USBL, multibeam and forward-looking sonar; has a ROS wrapper.
- [sonar-SLAM](../repos/jake3991__sonar-slam.md) - fit: medium - Underwater SLAM for robots with multibeam imaging sonar, from Stevens Institute research on BlueROV-class vehicles, combining sonar feature extraction and pose-graph optimization.
- [Project DAVE](../repos/field-robotics-lab__dave.md) - fit: medium - Gazebo-based underwater simulation environment from the Naval Postgraduate School and partners, extending UUV Simulator with DVL, sonar, bathymetry and manipulation models.
- [Vortex AUV](../repos/vortexntnu__vortex-auv.md) - fit: medium - Guidance, navigation and control software from NTNU's student Vortex team for competition AUVs and ROVs, built on ROS 2.
- [SubPipe](../repos/remaro-network__subpipe-dataset.md) - fit: medium - Underwater dataset recorded by a lightweight AUV inspecting a submarine pipeline, with camera, side-scan sonar and navigation data for segmentation and visual-inertial localization.
- [Ping Python](../repos/bluerobotics__ping-python.md) - fit: medium - Python library and examples for Blue Robotics Ping echosounder and Ping360 scanning sonar using the Ping protocol.
- [HoloOcean ROS bridge](../repos/byu-holoocean__holoocean-ros.md) - fit: medium - ROS bridge for HoloOcean, BYU's Unreal Engine based underwater simulator with DVL, IMU, depth, sonar and acoustic modem sensors.
- [ping360_sonar ROS package](../repos/centralenantesrobotics__ping360_sonar.md) - fit: medium - ROS package that drives the Ping360 scanning sonar and publishes scans as images and laser-scan style messages.
- [DISO](../repos/senseroboticslab__diso.md) - fit: medium - Direct imaging sonar odometry: estimates vehicle motion directly from forward-looking imaging sonar frames without feature extraction.
- [HoloOcean (documentation)](../repos/byu-holoocean__holoocean-docs.md) - fit: medium - Documentation repository for HoloOcean, BYU's Unreal-based underwater simulator with sonar, DVL, IMU, depth and camera sensors and multi-agent support.
- [USBL Simulator](../repos/maximilian-nitsch__usbl-simulator.md) - fit: medium - C++ library and ROS 2 node that simulates ultra-short baseline acoustic positioning measurements, with a Gazebo plugin.
- [Water Linked DVL Python](../repos/waterlinked__dvl-python.md) - fit: medium - Example Python code for talking to Water Linked DVLs over their serial and TCP/JSON protocols, parsing velocity and dead-reckoning reports.
- [AuvEstimator](../repos/alliwong__auvestimator.md) - fit: medium - Work-in-progress EKF that fuses DVL, IMU and barometer data for AUV state estimation, with a ROS wrapper.
- [UUV Simulator](../repos/uuvsimulator__uuv_simulator.md) - fit: low - Gazebo/ROS packages for underwater vehicle simulation with hydrodynamics, thrusters and sensors; archived.
- [Ping Viewer](../repos/bluerobotics__ping-viewer.md) - fit: low - Desktop application to view and record data from Blue Robotics Ping echosounder and Ping360 sonar.
- [NPS underwater multibeam sonar plugin](../repos/field-robotics-lab__nps_uw_multibeam_sonar.md) - fit: low - GPU (CUDA) multibeam sonar simulation plugin for Gazebo producing physically motivated sonar imagery.
- [Water Linked DVL A50 ROS driver](../repos/waterlinked__dvl-a50-ros-driver.md) - fit: low - ROS 1 driver publishing Water Linked DVL A50 velocity and beam data as ROS messages; now archived.
- [BRUCE](../repos/jinkunw__bruce.md) - fit: low - BlueROV underwater SLAM and exploration code from Stevens Institute, combining sonar-based SLAM with active exploration planning.
- [SMARC navigation](../repos/halajun__smarc_navigation.md) - fit: low - Localization and SLAM components for the SMARC AUVs (KTH), including EKF localization with IMU, DVL and multibeam sonar against a feature map.

## Documents, talks, courses, datasets (6)

- [ArduSub documentation](../resources/ardusub-docs.md) - doc - User and developer documentation for ArduSub, covering ROV configuration, sensors, and integration of external positioning such as DVL and USBL via MAVLink.
- [European Defense Tech Hackathon: Як стартапи в Мюнхені вирішують проблеми оборони України](../resources/militarnyi-edth-munich-2025.md) - blog - English: 'European Defense Tech Hackathon: how startups in Munich tackle Ukraine's defense problems'.
- [From Sea to Space: Advancing Perception in Harsh Domains (ICRA 2026 workshop)](../resources/icra-2026-sea-to-space-perception-workshop.md) - talk - ICRA 2026 (Vienna) workshop on perception for underwater, space and terrestrial field robots, including localization and mapping in degraded sensing, GPS-denied global localization, novel sensors (sonar, radar, thermal, 
- [HoloOcean Documentation](../resources/byu-holoocean-docs.md) - doc - Install guide, sensor reference (sonar, DVL, IMU, depth) and examples for the HoloOcean underwater simulator.
- [SubPipe: A Submarine Pipeline Inspection Dataset for Segmentation and Visual-inertial Localization](../resources/subpipe-paper-2024.md) - paper - Describes an AUV dataset from a pipeline inspection mission with camera, side-scan sonar and navigation data, with VIO and segmentation baselines.
- [Water Linked documentation (DVL and Underwater GPS)](../resources/waterlinked-docs.md) - doc - Vendor documentation for Water Linked DVLs and Underwater GPS (USBL-style) systems, including the JSON-over-TCP and serial protocols.

