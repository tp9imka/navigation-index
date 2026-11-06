# PX4 Autopilot

`repo:px4/px4-autopilot` - <https://github.com/PX4/PX4-Autopilot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 12,976 | C++ | BSD-3-Clause | 2026-11-05 | False | production | high |

Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware. Its EKF2 estimator fuses IMU, GNSS, baro, magnetometer, optical flow, range finders and external vision.

**Why it matters:** The most common permissive-licensed (BSD) autopilot base for defense and commercial UAS; EKF2 external-vision and flow fusion is the standard route to GPS-denied flight.

**Hackathon notes:** Run `make px4_sitl gz_x500` for SITL with Gazebo in under an hour. Feed VIO/SLAM poses via the ROS 2 uXRCE-DDS bridge or MAVLink ODOMETRY; disable GPS with EKF2_GPS_CTRL to test GPS-denied behaviour.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [px4__px4-autopilot](../../docs/integration-cards/px4__px4-autopilot.md) (integration-cards)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ekf2`, `uorb`, `nuttx`, `vtol`, `sitl`

**Domains:** air, ground, maritime

## Related

- alternative_to: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- integrates_with: [MAVSDK](../../catalog/repos/mavlink__mavsdk.md)
- integrates_with: [QGroundControl](../../catalog/repos/mavlink__qgroundcontrol.md)
- integrates_with: [px4_msgs](../../catalog/repos/px4__px4_msgs.md)
- integrates_with: [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md)
- extends: [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md)
- integrates_with: [PX4 Flight Review](../../catalog/repos/px4__flight_review.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md) (integrates_with)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (alternative_to)
- [ROS2 PX4 Offboard Example](../../catalog/repos/ark-electronics__ros2_px4_offboard_example.md) (integrates_with)
- [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md) (integrates_with)
- [drone_navigation - ROS 2 + PX4 + RTAB-Map diploma](../../catalog/repos/bolotnaya-glesenb__drone_navigation.md) (depends_on)
- [COEX Clover](../../catalog/repos/copterexpress__clover.md) (integrates_with)
- [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md) (integrates_with)
- [MAVROS](../../catalog/repos/mavlink__mavros.md) (integrates_with)
- [MAVSDK](../../catalog/repos/mavlink__mavsdk.md) (integrates_with)
- [QGroundControl](../../catalog/repos/mavlink__qgroundcontrol.md) (integrates_with)
- [AirSim](../../catalog/repos/microsoft__airsim.md) (integrates_with)
- [Paparazzi UAV](../../catalog/repos/paparazzi__paparazzi.md) (alternative_to)
- [Pegasus Simulator](../../catalog/repos/pegasussimulator__pegasussimulator.md) (integrates_with)
- [PX4 Flight Review](../../catalog/repos/px4__flight_review.md) (integrates_with)
- [jMAVSim](../../catalog/repos/px4__jmavsim.md) (integrates_with)
- [PX4 Avoidance](../../catalog/repos/px4__px4-avoidance.md) (integrates_with)
- [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md) (integrates_with)
- [PX4 ECL (Estimation & Control Library)](../../catalog/repos/px4__px4-ecl.md) (same_org)
- [PX4 Gazebo models](../../catalog/repos/px4__px4-gazebo-models.md) (integrates_with)
- [PX4 OpticalFlow](../../catalog/repos/px4__px4-opticalflow.md) (integrates_with)
- [PX4 SITL Gazebo Classic](../../catalog/repos/px4__px4-sitl_gazebo-classic.md) (integrates_with)
- [px4_msgs](../../catalog/repos/px4__px4_msgs.md) (depends_on)
- [ROSflight firmware](../../catalog/repos/rosflight__rosflight_firmware.md) (alternative_to)
- [Auterion Skynode S and Auterion Visual Navigation](../../catalog/resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [PX4 Developer Summit 2025 Recap](../../catalog/resources/dronecode-px4-dev-summit-2025-recap.md) (explains)
- [Датчик оптического потока -MTF02](../../catalog/resources/habr-mtf02-optical-flow-sensor-2025.md) (uses)
- [MAVLink 2 and Message Signing](../../catalog/resources/mavlink-2-signing.md) (uses)
- [MAVLink Common Message Set (common.xml)](../../catalog/resources/mavlink-common-messages.md) (uses)
- [MAVLink Developer Guide](../../catalog/resources/mavlink-developer-guide.md) (uses)
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) (uses)
- [PX4 Developer Summit 2025 recordings](../../catalog/resources/px4-dev-summit-2025-playlist.md) (explains)
- [PX4 Developer Summit (talks and recordings)](../../catalog/resources/px4-developer-summit.md) (uses)
- [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md) (explains)
- [Using PX4's Navigation Filter (EKF2)](../../catalog/resources/px4-ekf2-tuning-guide.md) (has_code)
- [Using Vision or Motion Capture Systems for Position Estimation](../../catalog/resources/px4-external-position-estimation.md) (explains)
- [Optical Flow](../../catalog/resources/px4-optical-flow-docs.md) (explains)
- [Remote ID (Open Drone ID)](../../catalog/resources/px4-remote-id-docs.md) (explains)
- [PX4 Simulation (Gazebo, SITL) documentation](../../catalog/resources/px4-simulation-docs.md) (explains)
- [PX4 Simulation (Gazebo, SITL) documentation](../../catalog/resources/px4-simulation-docs.md) (uses)
- [Visual Inertial Odometry (VIO)](../../catalog/resources/px4-visual-inertial-odometry.md) (explains)
- [PX4 Autopilot YouTube channel](../../catalog/resources/px4-youtube-channel.md) (uses)
- [PX4 State Estimation](../../catalog/resources/riseborough-px4-state-estimation-2020.md) (explains)
- [Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay](../../catalog/samples/golden-demo-px4.md) (uses)
- [PX4 SITL GPS denial: inject, measure drift, recover](../../catalog/samples/px4-sitl-gps-denial.md) (uses)
- [Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file](../../catalog/samples/sitl-docker.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../../catalog/samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
