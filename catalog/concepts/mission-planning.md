# Mission planning and routing

`concept:mission-planning`

Route networks, waypoint missions, coverage, terrain-aware and threat-aware routing.

**Parent:** [Path and motion planning](../../catalog/concepts/path-planning.md)

## Samples (1)

- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) - A small MCP server (stdio JSON-RPC 2.0, pymavlink) that lets Claude Code or any MCP client read and fly an ArduCopter: get_state, get_nav_health (EKF flags, variances, GNSS fix/sats/HDOP => nominal/degraded/lost), arm_ta

## Guides (1)

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) - After this chapter you can convert between the coordinate systems your tools disagree on, fetch free imagery and elevation data for a region, display it, and plan a path or a multi-vehicle mission over it.

## Repositories (25)

- [QGIS](../../catalog/repos/qgis__qgis.md) - fit: high - Desktop open-source GIS for viewing, editing, analyzing and printing geospatial data, extensible via Python plugins.
- [QGroundControl](../../catalog/repos/mavlink__qgroundcontrol.md) - fit: high - Qt/QML cross-platform GCS (desktop, Android, iOS) for PX4 and ArduPilot: setup, mission planning, video and telemetry.
- [BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md) - fit: high - C++ behavior tree library with XML trees, async actions, logging and the Groot editor; the execution engine inside Nav2 and many mission frameworks.
- [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md) - fit: high - Modular coverage path planning library: headland generation, swath generation, route ordering (boustrophedon, snake, spiral) and Dubins/Reeds-Shepp path smoothing, with Python bindings.
- [TARE Planner (CMU Explorer)](../../catalog/repos/caochao39__tare_planner.md) - fit: high - Hierarchical exploration planner from CMU's Team Explorer, which earned the most-sectors-explored award at the SubT final.
- [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md) - fit: high - Command-line, module-based ground station and MAVLink proxy with map, console and many plugins.
- [TypeFly](../../catalog/repos/typefly__typefly.md) - fit: high - LLM-based robot control framework: an OpenAI model turns a natural-language request plus a YOLO scene description into a short Python plan built from the robot's registered skills, which is then executed.
- [MAVLinkMCP](../../catalog/repos/ion-g-ion__mavlinkmcp.md) - fit: high - MCP server bridging an LLM to a drone over MAVLink, exposing arming, takeoff, waypoint and telemetry tools via MAVSDK.
- [CBBA (Python)](../../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md) - fit: high - Python implementation of the Consensus-Based Bundle Algorithm for decentralized multi-agent task allocation with plotting examples.
- [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md) - fit: high - Python TERCOM pipeline from the June 2026 'Полёт вслепую' hackathon, continued into July: correlates radar-altimeter profiles with a DEM using a coarse-to-fine 360-degree search, a hybrid MAD+NCC metric, minima-ratio dis
- [INAV](../../catalog/repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [Mission Planner](../../catalog/repos/ardupilot__missionplanner.md) - fit: medium - Windows-centric C#/.NET GCS for ArduPilot with deep parameter, log-analysis and mission tooling.
- [FUEL - Fast UAV Exploration](../../catalog/repos/hkust-aerial-robotics__fuel.md) - fit: medium - Frontier-information-structure based autonomous exploration for quadrotors, combining global tour planning over frontiers with local viewpoint refinement.
- [GBPlanner (CERBERUS)](../../catalog/repos/ntnu-arl__gbplanner_ros.md) - fit: medium - Graph-based exploration planner from NTNU ARL; the main branch is now OmniPlanner (GBPlanner 3.0) for aerial, ground and underwater robots, and GBPlanner 2.0, the planning core of Team CERBERUS, winner of the DARPA SubT 
- [RACER - multi-UAV exploration](../../catalog/repos/robotics-star-lab__racer.md) - fit: medium - Rapid collaborative exploration with multiple UAVs: decomposes unknown space and allocates exploration regions between drones with pairwise communication.
- [polygon_coverage_planning](../../catalog/repos/ethz-asl__polygon_coverage_planning.md) - fit: medium - ETH ASL coverage planner for polygons with holes that treats boustrophedon sweep selection as a generalized TSP, aimed at UAV survey.
- [PlanSys2](../../catalog/repos/plansys2__ros2_planning_system.md) - fit: medium - PDDL-based symbolic planning system for ROS 2: domain/problem management, plan generation with off-the-shelf planners and execution via behavior trees.
- [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md) - fit: medium - ROS 2 framework for autonomous single and multi-aerial-robot systems with behaviours, state estimation plugins and platform adapters (Gazebo and a multirotor simulator in this repo; PX4, Crazyflie and DJI adapters in sep
- [opennav_coverage](../../catalog/repos/open-navigation__opennav_coverage.md) - fit: medium - Nav2-compatible complete-coverage task server and navigator built on Fields2Cover, with behavior-tree utilities for field/area coverage and row following.
- [GNSS-Radar](../../catalog/repos/taroz__gnss-radar.md) - fit: medium - Web application showing current GNSS satellite positions (sky plot) for a location and time across constellations.
- [Open-RMF rmf_task](../../catalog/repos/open-rmf__rmf_task.md) - fit: medium - Task allocation library from Open-RMF that assigns tasks to fleets of robots, accounting for battery, travel time and task constraints.
- [Swarm in Blocks](../../catalog/repos/grupo-semear-usp__swarm_in_blocks.md) - fit: medium - Block-programming and web control platform for drone swarms on COEX Clover (ROS, Gazebo); CopterHack 2022 winner by team Atena.
- [mavlink-mcp (ArduPilot)](../../catalog/repos/deepakpopli__mavlink-mcp.md) - fit: medium - MCP server for flying ArduPilot vehicles from AI agents over MAVLink, covering missions, camera vision and SITL workflows.
- [Paparazzi UAV](../../catalog/repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [Clover Rescue Project](../../catalog/repos/devmbs__crtclient.md) - fit: low - Main web server and client (Node.js, Socket.IO) of the Clover Rescue Team's CopterHack 2022 project, 3rd place; the drone-side server is DevMBS/CRTClover.

## Documents, talks, courses, datasets (7)

- [Aerostack2: A Software Framework for Developing Multi-robot Aerial Systems](../../catalog/resources/aerostack2-paper.md) - paper - Describes the Aerostack2 ROS 2 architecture for aerial robotics: platform abstraction, behaviors, mission specification and multi-robot support.
- [Fields2Cover: An open-source coverage path planning library for unmanned agricultural vehicles](../../catalog/resources/fields2cover-paper.md) - paper - Paper behind the Fields2Cover library: modular coverage pipeline (headlands, swaths, route ordering, path smoothing) and benchmark of its components.
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) - doc - The microservice used to upload, download and clear waypoint missions, geofences and rally points between a GCS and an autopilot, with its handshake and retry rules.
- [Navigating Using GPS Localization (Nav2 tutorial)](../../catalog/resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [NeBula: Quest for Robotic Autonomy in Challenging Environments; TEAM CoSTAR at the DARPA Subterranean Challenge](../../catalog/resources/nebula-costar-subt-paper.md) - paper - Describes the NeBula belief-space autonomy stack: multi-modal positioning, mapping, traversability, risk-aware mission planning and multi-robot reasoning; CoSTAR won the Urban circuit.
- [PlanSys2: A Planning System Framework for ROS2](../../catalog/resources/plansys2-paper.md) - paper - Presents PlanSys2, a PDDL planning and execution framework for ROS 2 that compiles plans into behavior trees and supports multi-robot execution.
- [TypeFly: Flying Drones with Large Language Model](../../catalog/resources/typefly-2023.md) - paper - Proposes a compact drone programming language for LLM output, cutting token count and latency while keeping plans checkable.

