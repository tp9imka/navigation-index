# Mission planning and routing

`concept:mission-planning`

Route networks, waypoint missions, coverage, terrain-aware and threat-aware routing.

**Parent:** [Path and motion planning](../concepts/path-planning.md)

## Repositories (24)

- [QGIS](../repos/qgis__qgis.md) - fit: high - Desktop open-source GIS for viewing, editing, analyzing and printing geospatial data, extensible via Python plugins.
- [QGroundControl](../repos/mavlink__qgroundcontrol.md) - fit: high - Qt/QML cross-platform GCS (desktop, Android, iOS) for PX4 and ArduPilot: setup, mission planning, video and telemetry.
- [BehaviorTree.CPP](../repos/behaviortree__behaviortree.cpp.md) - fit: high - C++ behavior tree library with XML trees, async actions, logging and the Groot editor; the execution engine inside Nav2 and many mission frameworks.
- [Fields2Cover](../repos/fields2cover__fields2cover.md) - fit: high - Modular coverage path planning library: headland generation, swath generation, route ordering (boustrophedon, snake, spiral) and Dubins/Reeds-Shepp path smoothing, with Python bindings.
- [TARE Planner (CMU Explorer)](../repos/caochao39__tare_planner.md) - fit: high - Hierarchical exploration planner from CMU's Team Explorer, which earned the most-sectors-explored award at the SubT final.
- [MAVProxy](../repos/ardupilot__mavproxy.md) - fit: high - Command-line, module-based ground station and MAVLink proxy with map, console and many plugins.
- [TypeFly](../repos/typefly__typefly.md) - fit: high - LLM-based robot control framework: an OpenAI model turns a natural-language request plus a YOLO scene description into a short Python plan built from the robot's registered skills, which is then executed.
- [MAVLinkMCP](../repos/ion-g-ion__mavlinkmcp.md) - fit: high - MCP server bridging an LLM to a drone over MAVLink, exposing arming, takeoff, waypoint and telemetry tools via MAVSDK.
- [CBBA (Python)](../repos/inmo-jang__consensus-based-bundle-algorithm.md) - fit: high - Python implementation of the Consensus-Based Bundle Algorithm for decentralized multi-agent task allocation with plotting examples.
- [INAV](../repos/inavflight__inav.md) - fit: medium - Navigation-focused fork of the Cleanflight/Betaflight lineage for small multirotors, fixed-wing and rovers, adding GPS position hold, return-to-home and waypoint missions on cheap F4/F7/H7 boards.
- [Mission Planner](../repos/ardupilot__missionplanner.md) - fit: medium - Windows-centric C#/.NET GCS for ArduPilot with deep parameter, log-analysis and mission tooling.
- [FUEL - Fast UAV Exploration](../repos/hkust-aerial-robotics__fuel.md) - fit: medium - Frontier-information-structure based autonomous exploration for quadrotors, combining global tour planning over frontiers with local viewpoint refinement.
- [GBPlanner (CERBERUS)](../repos/ntnu-arl__gbplanner_ros.md) - fit: medium - NTNU ARL graph-based exploration planner for subterranean environments, used in the DARPA SubT challenge on legged and aerial robots.
- [RACER - multi-UAV exploration](../repos/robotics-star-lab__racer.md) - fit: medium - Rapid collaborative exploration with multiple UAVs: decomposes unknown space and allocates exploration regions between drones with pairwise communication.
- [polygon_coverage_planning](../repos/ethz-asl__polygon_coverage_planning.md) - fit: medium - ETH ASL coverage planner for polygons with holes that treats boustrophedon sweep selection as a generalized TSP, aimed at UAV survey.
- [PlanSys2](../repos/plansys2__ros2_planning_system.md) - fit: medium - PDDL-based symbolic planning system for ROS 2: domain/problem management, plan generation with off-the-shelf planners and execution via behavior trees.
- [Aerostack2](../repos/aerostack2__aerostack2.md) - fit: medium - ROS 2 framework for autonomous multi-aerial-robot systems: platform abstraction (PX4, DJI, Crazyflie, Gazebo), behaviors, mission scripting in Python and BT, and multi-drone coordination.
- [opennav_coverage](../repos/open-navigation__opennav_coverage.md) - fit: medium - Nav2-compatible complete-coverage task server and navigator built on Fields2Cover, with behavior-tree utilities for field/area coverage and row following.
- [GNSS-Radar](../repos/taroz__gnss-radar.md) - fit: medium - Web application showing current GNSS satellite positions (sky plot) for a location and time across constellations.
- [Open-RMF rmf_task](../repos/open-rmf__rmf_task.md) - fit: medium - Task allocation library from Open-RMF that assigns tasks to fleets of robots, accounting for battery, travel time and task constraints.
- [Swarm in Blocks](../repos/grupo-semear-usp__swarm_in_blocks.md) - fit: medium - Block-programming interface for drone swarms on COEX Clover, CopterHack 2022 winner by team Atena.
- [mavlink-mcp (ArduPilot)](../repos/deepakpopli__mavlink-mcp.md) - fit: medium - MCP server for flying ArduPilot vehicles from AI agents over MAVLink, covering missions, camera vision and SITL workflows.
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) - fit: low - Long-running academic autopilot (ENAC, TU Delft and others) for fixed-wing, rotorcraft and hybrids, with its own ground segment, flight-plan language and INS modules.
- [Clover Rescue Project](../repos/devmbs__crtclient.md) - fit: low - Frontend and backend from the Clover Rescue Team's CopterHack 2022 project.

## Documents, talks, courses, datasets (7)

- [Aerostack2: A Software Framework for Developing Multi-robot Aerial Systems](../resources/aerostack2-paper.md) - paper - Describes the Aerostack2 ROS 2 architecture for aerial robotics: platform abstraction, behaviors, mission specification and multi-robot support.
- [Fields2Cover: An open-source coverage path planning library for unmanned agricultural vehicles](../resources/fields2cover-paper.md) - paper - Paper behind the Fields2Cover library: modular coverage pipeline (headlands, swaths, route ordering, path smoothing) and benchmark of its components.
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) - doc - The microservice used to upload, download and clear waypoint missions, geofences and rally points between a GCS and an autopilot, with its handshake and retry rules.
- [Navigating Using GPS Localization (Nav2 tutorial)](../resources/nav2-gps-navigation-tutorial.md) - doc - Nav2 tutorial on outdoor navigation with GPS: fusing GNSS, IMU and odometry with robot_localization's navsat_transform, configuring Nav2 for GPS waypoints, and demonstrating it in Gazebo.
- [NeBula: Quest for Robotic Autonomy in Challenging Environments; TEAM CoSTAR at the DARPA Subterranean Challenge](../resources/nebula-costar-subt-paper.md) - paper - Describes the NeBula belief-space autonomy stack: multi-modal positioning, mapping, traversability, risk-aware mission planning and multi-robot reasoning; CoSTAR won the Urban circuit.
- [PlanSys2: A Planning System Framework for ROS2](../resources/plansys2-paper.md) - paper - Presents PlanSys2, a PDDL planning and execution framework for ROS 2 that compiles plans into behavior trees and supports multi-robot execution.
- [TypeFly: Flying Drones with Large Language Model](../resources/typefly-2023.md) - paper - Proposes a compact drone programming language for LLM output, cutting token count and latency while keeping plans checkable.

