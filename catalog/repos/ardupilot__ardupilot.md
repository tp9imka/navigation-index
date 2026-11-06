# ArduPilot

`repo:ardupilot/ardupilot` - <https://github.com/ArduPilot/ardupilot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 16,324 | C++ | GPL-3.0 | 2026-11-06 | False | production | high |

GPL autopilot covering Copter, Plane (incl. QuadPlane VTOL), Rover, boats and ArduSub, plus AP_Periph CAN peripherals. EKF3 supports switchable source sets, so GNSS, optical flow, beacons, wheel odometry and external vision can be swapped in flight.

**Why it matters:** Very broad vehicle coverage and mature non-GPS navigation docs; EKF3 source switching (EK3_SRCn_*) is directly useful for GNSS-loss and spoofing-resilience experiments.

**Hackathon notes:** `sim_vehicle.py -v ArduCopter --console --map` gives SITL in minutes. Lua scripting lets you add behaviour on the flight controller without a fork. Use SIM_GPS1_ENABLE=0 / EK3_SRC1_* to simulate GNSS denial.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [ardupilot__ardupilot](../../docs/integration-cards/ardupilot__ardupilot.md) (integration-cards)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ekf3`, `arducopter`, `arduplane`, `ardurover`, `ardusub`, `lua-scripting`, `sitl`, `mavlink`

**Domains:** air, ground, maritime, underwater

## Related

- alternative_to: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- integrates_with: [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md)
- integrates_with: [Mission Planner](../../catalog/repos/ardupilot__missionplanner.md)
- integrates_with: [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md)
- integrates_with: [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md)
- integrates_with: [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md)
- integrates_with: [BlueOS](../../catalog/repos/bluerobotics__blueos.md)
- integrates_with: [MAVROS](../../catalog/repos/mavlink__mavros.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md) (extends)
- [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md) (integrates_with)
- [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md) (integrates_with)
- [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md) (integrates_with)
- [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md) (integrates_with)
- [ArduPilot Methodic Configurator](../../catalog/repos/ardupilot__methodicconfigurator.md) (integrates_with)
- [Mission Planner](../../catalog/repos/ardupilot__missionplanner.md) (integrates_with)
- [ArduPilot SITL Models](../../catalog/repos/ardupilot__sitl_models.md) (integrates_with)
- [UAV Log Viewer](../../catalog/repos/ardupilot__uavlogviewer.md) (integrates_with)
- [BlueOS](../../catalog/repos/bluerobotics__blueos.md) (integrates_with)
- [ArduPilot Copter - українською](../../catalog/repos/c-o-s-t-y-a__ardupilot_ua.md) (extends)
- [DroneCAN libcanard](../../catalog/repos/dronecan__libcanard.md) (integrates_with)
- [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md) (integrates_with)
- [vision_landing](../../catalog/repos/goodrobots__vision_landing.md) (integrates_with)
- [JSBSim](../../catalog/repos/jsbsim-team__jsbsim.md) (integrates_with)
- [MAVROS](../../catalog/repos/mavlink__mavros.md) (integrates_with)
- [mLRS](../../catalog/repos/olliw42__mlrs.md) (integrates_with)
- [Virtual RobotX (VRX)](../../catalog/repos/osrf__vrx.md) (integrates_with)
- [Paparazzi UAV](../../catalog/repos/paparazzi__paparazzi.md) (alternative_to)
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) (alternative_to)
- [PX4 OpticalFlow](../../catalog/repos/px4__px4-opticalflow.md) (integrates_with)
- [Rpanion-server](../../catalog/repos/stephendade__rpanion-server.md) (integrates_with)
- [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md) (integrates_with)
- [Non-GPS Position Estimation](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md) (explains)
- [ArduPilot DevCon 2026 (Ottawa) programme](../../catalog/resources/ardupilot-devcon-2026-ottawa.md) (explains)
- [ArduPilot Developer Conference Kaga 2024 - Schedule and YouTube Links](../../catalog/resources/ardupilot-devcon-kaga-2024.md) (explains)
- [ArduPilot Developer Conference Kaga 2024 - Schedule and YouTube Links](../../catalog/resources/ardupilot-devcon-kaga-2024.md) (uses)
- [Extended Kalman Filter (EKF)](../../catalog/resources/ardupilot-ekf-overview.md) (explains)
- [EKF Source Selection and Switching](../../catalog/resources/ardupilot-ekf3-sources.md) (explains)
- [GPS / Non-GPS Transitions](../../catalog/resources/ardupilot-gps-non-gps-transitions.md) (explains)
- [GSoC 2022 wrapping up: Update ROS integration for Non-GPS navigation and off-board path-planning](../../catalog/resources/ardupilot-gsoc2022-ros-non-gps.md) (explains)
- [Non-GPS Navigation](../../catalog/resources/ardupilot-non-gps-navigation-docs.md) (explains)
- [Non-GPS Navigation](../../catalog/resources/ardupilot-non-gps-navigation-docs.md) (has_code)
- [Optical Flow Sensor Testing and Setup](../../catalog/resources/ardupilot-optical-flow-setup.md) (explains)
- [Remote ID (aka Drone ID)](../../catalog/resources/ardupilot-remote-id-docs.md) (explains)
- [ROS and VIO tracking camera for non-GPS Navigation](../../catalog/resources/ardupilot-ros-vio-tracking-camera.md) (explains)
- [SITL Simulator (Software in the Loop)](../../catalog/resources/ardupilot-sitl-docs.md) (explains)
- [Intel RealSense T265](../../catalog/resources/ardupilot-vio-tracking-camera.md) (explains)
- [ArduSub documentation](../../catalog/resources/ardusub-docs.md) (explains)
- [Датчик оптического потока -MTF02](../../catalog/resources/habr-mtf02-optical-flow-sensor-2025.md) (uses)
- [Sam Hyams's GPS-denied RTH for MAVLink systems using LoRa radio ranging](../../catalog/resources/hyams-gps-denied-rth-lora-ranging.md) (uses)
- [Система управління та навігації БПЛА](../../catalog/resources/kpi-spaskyi-uav-control-nav-under-ew-2025.md) (uses)
- [MAVLink 2 and Message Signing](../../catalog/resources/mavlink-2-signing.md) (uses)
- [MAVLink Common Message Set (common.xml)](../../catalog/resources/mavlink-common-messages.md) (uses)
- [MAVLink Developer Guide](../../catalog/resources/mavlink-developer-guide.md) (uses)
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) (uses)
- [Developer Unconference - Paul Riseborough (EKF)](../../catalog/resources/riseborough-ardupilot-unconference-2017-ekf.md) (explains)
- [ArduPilot EKF3 source-set switch under GPS denial](../../catalog/samples/ardupilot-ekf3-source-switch.md) (uses)
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) (uses)
- [LLM mission agent: a safety-gated MAVLink MCP server flying ArduPilot SITL](../../catalog/samples/llm-mission-agent.md) (uses)
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../../catalog/samples/sitl-docker.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
