# ROS / ROS 2 robotics middleware

`concept:ros`

ROS ecosystem packages for navigation and localization.

## Repositories (78)

- [Nav2 (ROS 2 Navigation)](../repos/ros-navigation__navigation2.md) - fit: high - The standard ROS 2 navigation stack: behavior-tree driven navigator, global planners (NavFn, Smac hybrid-A*/lattice, Theta*), local controllers (DWB, MPPI, Regulated Pure Pursuit), costmaps, recovery behaviors and waypoi
- [BehaviorTree.CPP](../repos/behaviortree__behaviortree.cpp.md) - fit: high - C++ behavior tree library with XML trees, async actions, logging and the Groot editor; the execution engine inside Nav2 and many mission frameworks.
- [RTAB-Map](../repos/introlab__rtabmap.md) - fit: high - Graph-based SLAM library and app supporting RGB-D, stereo and LiDAR, with memory management for large-scale loop closure and map reuse.
- [robot_localization](../repos/cra-ros-pkg__robot_localization.md) - fit: high - ROS package with EKF and UKF state estimation nodes that fuse any number of odometry, IMU, pose and GNSS inputs, plus a navsat_transform node for GPS-to-map conversion.
- [ROSA (ROS Agent)](../repos/nasa-jpl__rosa.md) - fit: high - NASA JPL's LangChain-based AI agent that lets operators query and command ROS 1 and ROS 2 systems in natural language through a set of ROS introspection and control tools.
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) - fit: high - Current-generation Gazebo robotics simulator with pluggable physics, rendering and a large sensor library (IMU, GPS/NavSat, lidar, cameras, magnetometer, altimeter).
- [rtabmap_ros](../repos/introlab__rtabmap_ros.md) - fit: high - ROS and ROS 2 integration for RTAB-Map, exposing SLAM, localization and odometry nodes.
- [ROS MCP Server](../repos/robotmcp__ros-mcp-server.md) - fit: high - Model Context Protocol server that exposes ROS topics, services and parameters (via rosbridge) to LLM clients such as Claude or GPT, for ROS 1 and ROS 2.
- [Isaac ROS Visual SLAM](../repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) - fit: high - ROS 2 package wrapping NVIDIA's GPU-accelerated cuVSLAM for stereo visual(-inertial) odometry and SLAM on Jetson and x86 GPUs.
- [MAVROS](../repos/mavlink__mavros.md) - fit: high - ROS/ROS 2 node bridging MAVLink to ROS topics and services, with GCS proxy; widely used to push vision/SLAM poses into PX4 or ArduPilot.
- [imu_tools](../repos/ccnyroboticslab__imu_tools.md) - fit: high - ROS tools for IMUs: Madgwick and complementary orientation filters and an RViz IMU visualisation plugin.
- [imu_x_fusion](../repos/cggos__imu_x_fusion.md) - fit: high - Loosely coupled IMU + GNSS / 6-DoF odometry fusion with multiple estimators side by side (ESKF, IEKF, UKF variants, MAP).
- [livox_ros_driver2](../repos/livox-sdk__livox_ros_driver2.md) - fit: high - ROS 1/ROS 2 driver for Livox LiDARs such as Mid-360 and HAP.
- [Isaac ROS nvblox](../repos/nvidia-isaac-ros__isaac_ros_nvblox.md) - fit: high - GPU-accelerated 3D reconstruction (TSDF/ESDF) that provides Nav2 local costmaps from depth cameras.
- [Virtual RobotX (VRX)](../repos/osrf__vrx.md) - fit: high - Gazebo-based simulation environment for the RobotX maritime autonomy competition, with a WAM-V USV model, waves, wind, sensors and scored tasks such as station keeping, wayfinding and perception.
- [allan_variance_ros](../repos/ori-drs__allan_variance_ros.md) - fit: high - ROS tool (Oxford DRS) that computes Allan deviation plots from an IMU bag and outputs noise parameters in a Kalibr-compatible format.
- [COEX Clover](../repos/copterexpress__clover.md) - fit: high - ROS-based software stack and Raspberry Pi image for the Clover educational quadcopter (PX4 underneath).
- [ros_gz bridge](../repos/gazebosim__ros_gz.md) - fit: high - Bridge packages that relay topics, services and clock between Gazebo Sim transport and ROS 1/ROS 2.
- [ublox ROS driver](../repos/kumarrobotics__ublox.md) - fit: high - ROS driver for u-blox receivers that publishes fixes, raw measurements and receiver status as ROS messages.
- [ORB_SLAM3_ROS2](../repos/zang09__orb_slam3_ros2.md) - fit: high - ROS 2 wrapper package that exposes ORB-SLAM3 as nodes for monocular, stereo and RGB-D input.
- [Nav2 tutorials](../repos/ros-navigation__navigation2_tutorials.md) - fit: high - Tutorial packages referenced by docs.nav2.org: example planner, controller and behavior-tree plugins, SLAM and GPS waypoint following setups.
- [Beluga](../repos/ekumen-os__beluga.md) - fit: high - Modern C++17 library of Monte Carlo Localization algorithms with a ROS 2 node that is a drop-in replacement for the Nav2 AMCL package.
- [vision_to_mavros](../repos/thien94__vision_to_mavros.md) - fit: high - ROS and Python scripts that convert external localisation (fiducials, T265 VIO, SLAM, depth) into MAVROS/MAVLink pose messages, tested on ArduPilot.
- [px4_ros_com](../repos/px4__px4_ros_com.md) - fit: high - Example ROS 2 nodes and helpers (frame transforms) for interfacing with PX4 over DDS.
- [ROS2 PX4 Offboard Example](../repos/ark-electronics__ros2_px4_offboard_example.md) - fit: high - Small example of driving PX4 velocity setpoints from ROS 2 teleop, with SITL launch files.
- [DRIFT](../repos/umich-curly__drift.md) - fit: high - Symmetry-preserving (invariant) state estimation library from University of Michigan for legged, wheeled and other robots, with real-time ROS support.
- [PX4 ROS 2 Interface Library](../repos/auterion__px4-ros2-interface-lib.md) - fit: high - C++ library for writing PX4 flight modes and navigation-data sources in ROS 2 on a companion computer, registered with PX4 as first-class modes.
- [px4_msgs](../repos/px4__px4_msgs.md) - fit: high - ROS 2 message definitions mirroring PX4 uORB topics, used with the uXRCE-DDS bridge.
- [ROS NTRIP client](../repos/lord-microstrain__ntrip_client.md) - fit: high - ROS/ROS 2 node that connects to an NTRIP caster and publishes RTCM corrections, forwarding NMEA position back to the caster.
- [tercom_nav (TERCOM + ESKF)](../repos/mzahana__tercom_nav.md) - fit: high - ROS 2 (Humble) package for GPS-denied fixed-wing UAV navigation: a TERCOM node correlates baro + rangefinder terrain profiles against a GeoTIFF DEM and feeds fixes into a 15-state error-state Kalman filter driven by IMU,
- [ROSCon UK 2025 State Estimation workshop](../repos/locusrobotics__roscon-uk-2025-se-workshop.md) - fit: high - Materials for an eight-task ROS 2 state estimation workshop at ROSCon UK 2025, with a Docker image, recorded bags and step-by-step exercises using robot_localization and fuse.
- [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md) - fit: high - ROS 2 integration examples for ArduPilot, including Cartographer-based non-GPS navigation and Nav2 setups.
- [grid_map](../repos/leggedrobotics__grid_map.md) - fit: high - Universal multi-layer 2.5D grid map library for mobile robots with ROS/ROS 2 integration, filters, iterators and conversion to images, point clouds and costmaps.
- [Autoware](../repos/autowarefoundation__autoware.md) - fit: medium - Meta-repository for Autoware, the open-source ROS 2 autonomous driving stack covering localization (NDT, EKF), perception, planning and control.
- [Kalibr](../repos/ethz-asl__kalibr.md) - fit: medium - ETH ASL calibration toolbox for multi-camera and camera-IMU systems (extrinsics and time offset), plus IMU intrinsics and rolling-shutter calibration.
- [Webots](../repos/cyberbotics__webots.md) - fit: medium - General-purpose open-source robot simulator with many robot models and sensors including GPS, compass, IMU, lidar and radar.
- [NVIDIA Isaac Sim](../repos/isaac-sim__isaacsim.md) - fit: medium - NVIDIA's Omniverse-based robot simulator, now open source, with RTX sensor simulation (cameras, lidar, IMU) and ROS 2 bridges.
- [Fast-Planner](../repos/hkust-aerial-robotics__fast-planner.md) - fit: medium - HKUST quadrotor planning framework: kinodynamic A* front-end plus B-spline optimization, with topological and perception-aware variants for fast flight in unknown environments.
- [EGO-Planner](../repos/zju-fast-lab__ego-planner.md) - fit: medium - ESDF-free gradient-based local planner for quadrotors from ZJU FAST Lab: optimizes B-spline trajectories using collision terms computed only where the trajectory hits obstacles.
- [imu_utils](../repos/gaowenliang__imu_utils.md) - fit: medium - ROS package for analysing IMU performance with Allan variance to estimate noise and bias instability.
- [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md) - fit: medium - Modular EKF framework from ETH ASL for fusing IMU propagation with pose, position and other sensor updates, with delayed-measurement handling.
- [ros_deep_learning](../repos/dusty-nv__ros_deep_learning.md) - fit: medium - ROS/ROS 2 nodes wrapping jetson-inference for detection, classification and segmentation with TensorRT.
- [fuse](../repos/locusrobotics__fuse.md) - fit: medium - ROS framework for sensor fusion as factor-graph optimization: plugin sensor models, motion models and publishers on top of Ceres, supporting both smoothing and fixed-lag estimation.
- [Spatio-Temporal Voxel Layer](../repos/stevemacenski__spatio_temporal_voxel_layer.md) - fit: medium - Nav2 costmap layer using OpenVDB voxel grids with time decay to represent 3D obstacles from depth and LiDAR sensors.
- [KR Autonomous Flight](../repos/kumarrobotics__kr_autonomous_flight.md) - fit: medium - UPenn Kumar Robotics end-to-end autonomy stack for GPS-denied quadrotors: state estimation, mapping, planning and control in one system.
- [iKalibr](../repos/unsigned-long__ikalibr.md) - fit: medium - Continuous-time, targetless multi-sensor calibration framework (IMU, cameras, LiDAR, radar, RGB-D, event cameras) estimating extrinsics and time offsets (IEEE T-RO 2025).
- [MRS UAV System](../repos/ctu-mrs__mrs_uav_system.md) - fit: medium - Czech Technical University's multi-robot UAV platform with control, estimation (including GNSS-denied modes), planning and simulation, field-tested in outdoor swarm deployments.
- [PlanSys2](../repos/plansys2__ros2_planning_system.md) - fit: medium - PDDL-based symbolic planning system for ROS 2: domain/problem management, plan generation with off-the-shelf planners and execution via behavior trees.
- [Aerostack2](../repos/aerostack2__aerostack2.md) - fit: medium - ROS 2 framework for autonomous multi-aerial-robot systems: platform abstraction (PX4, DJI, Crazyflie, Gazebo), behaviors, mission scripting in Python and BT, and multi-drone coordination.
- [DepthAI ROS](../repos/luxonis__depthai-ros.md) - fit: medium - ROS 1/2 driver for Luxonis OAK cameras publishing depth, detections and IMU.
- [rpg_dvs_ros](../repos/uzh-rpg__rpg_dvs_ros.md) - fit: medium - ROS drivers and tools for DVS/DAVIS event cameras, including calibration and rendering.
- [opennav_coverage](../repos/open-navigation__opennav_coverage.md) - fit: medium - Nav2-compatible complete-coverage task server and navigator built on Fields2Cover, with behavior-tree utilities for field/area coverage and row following.
- [Project DAVE](../repos/field-robotics-lab__dave.md) - fit: medium - Gazebo-based underwater simulation environment from the Naval Postgraduate School and partners, extending UUV Simulator with DVL, sonar, bathymetry and manipulation models.
- [Crazyswarm2](../repos/imrclab__crazyswarm2.md) - fit: medium - ROS 2 framework for flying many Crazyflie nano-quadrotors with motion capture or onboard localization, including simulation backends.
- [Micro XRCE-DDS Agent](../repos/eprosima__micro-xrce-dds-agent.md) - fit: medium - Agent that bridges DDS-XRCE clients on microcontrollers into a full DDS / ROS 2 graph; PX4 and ArduPilot use it for native ROS 2.
- [ESKF ROS (EliaTarasov)](../repos/eliatarasov__eskf.md) - fit: medium - ROS error-state Kalman filter derived from PX4/ecl that fuses IMU with GPS, magnetometer, vision pose and optical flow.
- [ROSflight firmware](../repos/rosflight__rosflight_firmware.md) - fit: medium - Lean research autopilot (BYU) that keeps only attitude estimation and low-level control on the flight board and pushes everything else to a ROS companion.
- [Isaac ROS DNN Inference](../repos/nvidia-isaac-ros__isaac_ros_dnn_inference.md) - fit: medium - ROS 2 packages for TensorRT and Triton inference on Jetson and x86, with encoder/decoder nodes for common model types.
- [Vortex AUV](../repos/vortexntnu__vortex-auv.md) - fit: medium - Guidance, navigation and control software from NTNU's student Vortex team for competition AUVs and ROVs, built on ROS 2.
- [ROS2swarm](../repos/ros2swarm__ros2swarm.md) - fit: medium - ROS 2 package providing a library of swarm behaviours (aggregation, dispersion, flocking) and an easy-to-extend framework, tested on TurtleBot-class robots.
- [ROSflight ROS packages](../repos/rosflight__rosflight_ros_pkgs.md) - fit: medium - ROS 2 interface, simulator and utilities for the ROSflight autopilot.
- [WiseVision ROS 2 MCP](../repos/wise-vision__ros2_mcp.md) - fit: medium - MCP server that lets AI agents discover and operate ROS 2 robots: topic echo/publish, services, actions and introspection, implemented natively in ROS 2 rather than through rosbridge.
- [cuckoo_time_translator](../repos/ethz-asl__cuckoo_time_translator.md) - fit: medium - ROS algorithms that translate a sensor's own hardware timestamps into host system time from one-way timing, estimating skew and offset.
- [ardupilot_gz](../repos/ardupilot__ardupilot_gz.md) - fit: medium - ROS 2 + Gazebo packages for ArduPilot SITL integration and testing.
- [HoloOcean ROS bridge](../repos/byu-holoocean__holoocean-ros.md) - fit: medium - ROS bridge for HoloOcean, BYU's Unreal Engine based underwater simulator with DVL, IMU, depth, sonar and acoustic modem sensors.
- [ping360_sonar ROS package](../repos/centralenantesrobotics__ping360_sonar.md) - fit: medium - ROS package that drives the Ping360 scanning sonar and publishes scans as images and laser-scan style messages.
- [Swarm-SLAM](../repos/lajoiepy__cslam.md) - fit: medium - ROS 2 decentralized collaborative SLAM supporting LiDAR, stereo and RGB-D, with sparse inter-robot communication.
- [Open-RMF rmf_task](../repos/open-rmf__rmf_task.md) - fit: medium - Task allocation library from Open-RMF that assigns tasks to fleets of robots, accounting for battery, travel time and task constraints.
- [ROS MCP Server demos](../repos/robotmcp__demos-ros-mcp-server.md) - fit: medium - Standalone demos for driving robots with natural language through the ROS MCP server: a Tugbot in a Gazebo warehouse, a Unitree Go2 with the CHAMP controller, a PX4 drone via MAVROS (Gazebo and real hardware) and TurtleB
- [ORB_SLAM3_system_local](../repos/sasha-lobov__orb_slam3_system_local.md) - fit: medium - Pet project for local UAV navigation without GNSS: AirSim video streamed over ZeroMQ into monocular ORB-SLAM3, a ROS node converts NED/ENU frames, IMU data corrects monocular scale, and a PID controller tracks a trajecto
- [MoveIt 2](../repos/moveit__moveit2.md) - fit: low - Motion planning framework for ROS 2 manipulators: kinematics, collision checking, planners (OMPL, Pilz, STOMP) and real-time servoing.
- [ROS-LLM](../repos/auromix__ros-llm.md) - fit: low - Framework for natural-language interaction with ROS robots, letting an LLM call robot functions and chain behaviors.
- [PX4 Avoidance](../repos/px4__px4-avoidance.md) - fit: low - Archived ROS nodes for local planning, global planning and safe landing using depth sensors with PX4.
- [GraphGNSSLib](../repos/weisongwen__graphgnsslib.md) - fit: low - Open-source GNSS positioning and RTK package using factor graph optimization, built on RTKLIB data handling and ROS.
- [gnss_comm](../repos/hkust-aerial-robotics__gnss_comm.md) - fit: low - C++/ROS definitions and utilities for raw GNSS measurement processing (ephemeris, satellite positions, pseudorange models) used by GVINS.
- [Water Linked DVL A50 ROS driver](../repos/waterlinked__dvl-a50-ros-driver.md) - fit: low - ROS 1 driver publishing Water Linked DVL A50 velocity and beam data as ROS messages; now archived.
- [Geoscan Pioneer Max](../repos/geoscan__geoscan_pioneer_max.md) - fit: low - Meta-repository from Russian vendor Geoscan for the Pioneer Max educational quadcopter: system images, ROS workspace, web control apps and guides, documented in Russian.
- [LCAS ROS 2 MCP](../repos/lcas__ros2_mcp.md) - fit: low - ROS 2 MCP server from the Lincoln Centre for Autonomous Systems: tools to list and echo topics, inspect message/service/action interfaces, fetch camera images for VLM analysis and send simple drive commands, plus canned 

## Documents, talks, courses, datasets (22)

- [Aerostack2: A Software Framework for Developing Multi-robot Aerial Systems](../resources/aerostack2-paper.md) - paper - Describes the Aerostack2 ROS 2 architecture for aerial robotics: platform abstraction, behaviors, mission specification and multi-robot support.
- [Autoware documentation](../resources/autoware-docs.md) - doc - Official Autoware documentation with architecture, installation, tutorials and design notes for localization, perception and planning components.
- [Crazyswarm2 documentation](../resources/crazyswarm2-docs.md) - doc - Docs for Crazyswarm2 with installation, simulation backends, swarm configuration and tutorials.
- [Enabling Novel Mission Operations and Interactions with ROSA: The Robot Operating System Agent](../resources/jpl-rosa-paper-2024.md) - paper - Describes ROSA, an LLM agent that lets operators inspect and command ROS systems in natural language through a curated tool set, and discusses safety and operational considerations.
- [From the Desks of ROS Maintainers: A Survey of Modern & Capable Mobile Robotics Algorithms in the Robot Operating System 2](../resources/macenski-ros2-algorithms-survey.md) - paper - Survey by ROS maintainers of the mobile robotics algorithms available in ROS 2: localization, SLAM, planning, control and perception packages, with their maturity and use.
- [Gazebo documentation and tutorials](../resources/gazebo-docs-tutorials.md) - doc - Official Gazebo (gz) docs and tutorials: building worlds, sensors (IMU, GPS/NavSat, cameras, LiDAR), ROS 2 bridging and plugins.
- [GSoC 2022: Update ROS integration for Non-GPS navigation and off-board path planning](../resources/ardupilot-gsoc2022-ros-non-gps.md) - blog - Wrap-up of a GSoC project updating ArduPilot's ROS integration for lidar/SLAM-based non-GPS navigation and off-board planning.
- [Isaac ROS Visual SLAM documentation](../resources/isaac-ros-visual-slam-docs.md) - doc - Docs and quickstarts for NVIDIA's GPU-accelerated stereo visual-inertial odometry and SLAM package for ROS 2 on Jetson, including tutorials with Isaac Sim and RealSense cameras.
- [MIT 16.485 Visual Navigation for Autonomous Vehicles (VNAV)](../resources/mit-vnav-16485.md) - course - MIT graduate course on the math and software of visual navigation: 3D geometry, Lie groups, quadrotor modelling and control, trajectory optimization, feature tracking, two-view geometry, nonlinear optimization, VIO and S
- [Nav2 Documentation](../resources/nav2-docs.md) - doc - Official Nav2 documentation: concepts, configuration guides for every planner/controller/costmap plugin, tuning guide and tutorials including GPS-based navigation.
- [Nav2 first-time robot setup: Odometry and robot_localization](../resources/nav2-robot-localization-setup-guide.md) - doc - Setup guide for fusing wheel odometry and IMU with robot_localization's EKF to produce the odom frame Nav2 expects.
- [Nav2 ROSCon Talks (index)](../resources/nav2-roscon-talks.md) - talk - Curated index of ROSCon talks by the Nav2 team and community from 2018 onward, covering features such as Smac planners and the MPPI controller plus tuning and deployment advice.
- [Nav2 ROSCon Talks index](../resources/nav2-roscon-talks-index.md) - video - Index of ROSCon talks by Nav2 developers and the community (Vimeo links), including SLAM Toolbox and large-scale indoor mapping talks.
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [PlanSys2: A Planning System Framework for ROS2](../resources/plansys2-paper.md) - paper - Presents PlanSys2, a PDDL planning and execution framework for ROS 2 that compiles plans into behavior trees and supports multi-robot execution.
- [robot_localization package documentation](../resources/robot-localization-docs.md) - doc - Documentation for the widely used ROS EKF/UKF state estimation package, including state-estimation node configuration, sensor integration, and navsat_transform for GPS.
- [ROS and VIO tracking camera for non-GPS navigation](../resources/ardupilot-ros-vio-tracking-camera.md) - doc - Developer tutorial wiring a VIO camera through ROS and MAVROS into ArduPilot for indoor flight.
- [ROSCon 2023 videos and slides](../resources/roscon-2023-videos.md) - video - Announcement and index of ROSCon 2023 recordings and slides, including navigation talks such as bidirectional navigation with Nav2 and localization on 3D mesh surfaces.
- [ROSCon 2024 (Odense) programme and recordings](../resources/roscon-2024.md) - talk - ROSCon 2024 site with the programme and links to recorded talks, including localization talks such as Ekumen's Beluga particle-filter localization library.
- [ROSCon UK 2025 - State Estimation for Mobile Robotics Workshop](../resources/nav2-roscon-uk-2025-state-estimation-workshop.md) - masterclass - Hands-on workshop material comparing two ROS 2 state-estimation approaches: Kalman filtering with robot_localization (EKF/UKF, covariance tuning, frames, rate handling) and factor-graph fixed-lag smoothing with fuse.
- [The Marathon 2: A Navigation System](../resources/macenski-marathon2-nav2.md) - paper - Paper introducing Nav2: behavior-tree based navigation architecture for ROS 2, its design choices and a long-duration campus deployment test.
- [Using Vision or Motion Capture Systems for Position Estimation](../resources/px4-external-position-estimation.md) - doc - How to feed external vision or mocap poses into PX4 EKF2 via MAVLink or ROS, including frame conventions and EKF2_EV_* parameters.

