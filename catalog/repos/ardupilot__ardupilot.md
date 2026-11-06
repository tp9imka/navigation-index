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

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Visual(-inertial) odometry](../concepts/vio.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [Maritime navigation](../concepts/maritime-nav.md), [Underwater navigation](../concepts/underwater-nav.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `ekf3`, `arducopter`, `arduplane`, `ardurover`, `ardusub`, `lua-scripting`, `sitl`, `mavlink`

**Domains:** air, ground, maritime, underwater

## Related

- alternative_to: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- integrates_with: [pymavlink](../repos/ardupilot__pymavlink.md)
- integrates_with: [MAVProxy](../repos/ardupilot__mavproxy.md)
- integrates_with: [Mission Planner](../repos/ardupilot__missionplanner.md)
- integrates_with: [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md)
- integrates_with: [ArduRemoteID](../repos/ardupilot__arduremoteid.md)
- integrates_with: [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md)
- integrates_with: [BlueOS](../repos/bluerobotics__blueos.md)
- integrates_with: [MAVROS](../repos/mavlink__mavros.md)

## Referenced by

- [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md) (extends)
- [ardupilot_gazebo](../repos/ardupilot__ardupilot_gazebo.md) (integrates_with)
- [ardupilot_ros](../repos/ardupilot__ardupilot_ros.md) (integrates_with)
- [ArduRemoteID](../repos/ardupilot__arduremoteid.md) (integrates_with)
- [MAVProxy](../repos/ardupilot__mavproxy.md) (integrates_with)
- [ArduPilot Methodic Configurator](../repos/ardupilot__methodicconfigurator.md) (integrates_with)
- [Mission Planner](../repos/ardupilot__missionplanner.md) (integrates_with)
- [ArduPilot SITL Models](../repos/ardupilot__sitl_models.md) (integrates_with)
- [UAV Log Viewer](../repos/ardupilot__uavlogviewer.md) (integrates_with)
- [BlueOS](../repos/bluerobotics__blueos.md) (integrates_with)
- [ArduPilot Copter - українською](../repos/c-o-s-t-y-a__ardupilot_ua.md) (extends)
- [DroneCAN libcanard](../repos/dronecan__libcanard.md) (integrates_with)
- [Micro XRCE-DDS Agent](../repos/eprosima__micro-xrce-dds-agent.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) (integrates_with)
- [vision_landing](../repos/goodrobots__vision_landing.md) (integrates_with)
- [JSBSim](../repos/jsbsim-team__jsbsim.md) (integrates_with)
- [MAVROS](../repos/mavlink__mavros.md) (integrates_with)
- [mLRS](../repos/olliw42__mlrs.md) (integrates_with)
- [Virtual RobotX (VRX)](../repos/osrf__vrx.md) (integrates_with)
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) (alternative_to)
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) (alternative_to)
- [PX4 OpticalFlow](../repos/px4__px4-opticalflow.md) (integrates_with)
- [Rpanion-server](../repos/stephendade__rpanion-server.md) (integrates_with)
- [vision_to_mavros](../repos/thien94__vision_to_mavros.md) (integrates_with)
- [Non-GPS Position Estimation (MAVLink messages)](../resources/ardupilot-dev-mavlink-nongps-position.md) (explains)
- [ArduPilot DevCon 2026 (Ottawa) programme](../resources/ardupilot-devcon-2026-ottawa.md) (explains)
- [ArduPilot Developer Conference Kaga 2024 - schedule and YouTube links](../resources/ardupilot-devcon-kaga-2024.md) (explains)
- [ArduPilot Developer Conference Kaga 2024 - schedule and YouTube links](../resources/ardupilot-devcon-kaga-2024.md) (uses)
- [Extended Kalman Filter (EKF) navigation overview](../resources/ardupilot-ekf-overview.md) (explains)
- [EKF Source Selection and Switching](../resources/ardupilot-ekf3-sources.md) (explains)
- [GPS / Non-GPS Transitions](../resources/ardupilot-gps-non-gps-transitions.md) (explains)
- [GSoC 2022: Update ROS integration for Non-GPS navigation and off-board path planning](../resources/ardupilot-gsoc2022-ros-non-gps.md) (explains)
- [Non-GPS Navigation](../resources/ardupilot-non-gps-navigation-docs.md) (explains)
- [Non-GPS Navigation](../resources/ardupilot-non-gps-navigation-docs.md) (has_code)
- [Optical Flow Sensor setup](../resources/ardupilot-optical-flow-setup.md) (explains)
- [Remote ID (ArduPilot)](../resources/ardupilot-remote-id-docs.md) (explains)
- [ROS and VIO tracking camera for non-GPS navigation](../resources/ardupilot-ros-vio-tracking-camera.md) (explains)
- [ArduPilot SITL Simulator (Software in the Loop)](../resources/ardupilot-sitl-docs.md) (explains)
- [Intel RealSense T265 / VIO tracking camera setup](../resources/ardupilot-vio-tracking-camera.md) (explains)
- [ArduSub documentation](../resources/ardusub-docs.md) (explains)
- [GPS-denied RTH for MAVLink systems using LoRa radio ranging](../resources/hyams-gps-denied-rth-lora-ranging.md) (uses)
- [Система управління та навігації БПЛА](../resources/kpi-spaskyi-uav-control-nav-under-ew-2025.md) (uses)
- [MAVLink 2 and Message Signing](../resources/mavlink-2-signing.md) (uses)
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) (uses)
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) (uses)
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) (uses)
- [Developer Unconference - Paul Riseborough (EKF)](../resources/riseborough-ardupilot-unconference-2017-ekf.md) (explains)
- [ArduPilot EKF3 source-set switch under GPS denial](../samples/ardupilot-ekf3-source-switch.md) (uses)
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../samples/sitl-docker.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
