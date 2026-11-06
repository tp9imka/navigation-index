# PX4 Autopilot

`repo:px4/px4-autopilot` - <https://github.com/PX4/PX4-Autopilot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 12,976 | C++ | BSD-3-Clause | 2026-11-05 | False | production | high |

Dronecode flight stack for multirotors, fixed-wing, VTOL, rovers and boats, built on NuttX with a uORB pub/sub middleware. Its EKF2 estimator fuses IMU, GNSS, baro, magnetometer, optical flow, range finders and external vision.

**Why it matters:** The most common permissive-licensed (BSD) autopilot base for defense and commercial UAS; EKF2 external-vision and flow fusion is the standard route to GPS-denied flight.

**Hackathon notes:** Run `make px4_sitl gz_x500` for SITL with Gazebo in under an hour. Feed VIO/SLAM poses via the ROS 2 uXRCE-DDS bridge or MAVLink ODOMETRY; disable GPS with EKF2_GPS_CTRL to test GPS-denied behaviour.

## Deep dives

- [px4__px4-autopilot](../../docs/integration-cards/px4__px4-autopilot.md) (integration-cards)

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Visual(-inertial) odometry](../concepts/vio.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `ekf2`, `uorb`, `nuttx`, `vtol`, `sitl`

**Domains:** air, ground, maritime

## Related

- alternative_to: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [MAVSDK](../repos/mavlink__mavsdk.md)
- integrates_with: [QGroundControl](../repos/mavlink__qgroundcontrol.md)
- integrates_with: [px4_msgs](../repos/px4__px4_msgs.md)
- integrates_with: [Micro XRCE-DDS Agent](../repos/eprosima__micro-xrce-dds-agent.md)
- extends: [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md)
- integrates_with: [PX4 Flight Review](../repos/px4__flight_review.md)

## Referenced by

- [Aerostack2](../repos/aerostack2__aerostack2.md) (integrates_with)
- [ArduPilot](../repos/ardupilot__ardupilot.md) (alternative_to)
- [ROS2 PX4 Offboard Example](../repos/ark-electronics__ros2_px4_offboard_example.md) (integrates_with)
- [PX4 ROS 2 Interface Library](../repos/auterion__px4-ros2-interface-lib.md) (integrates_with)
- [COEX Clover](../repos/copterexpress__clover.md) (integrates_with)
- [Micro XRCE-DDS Agent](../repos/eprosima__micro-xrce-dds-agent.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) (integrates_with)
- [MAVROS](../repos/mavlink__mavros.md) (integrates_with)
- [MAVSDK](../repos/mavlink__mavsdk.md) (integrates_with)
- [QGroundControl](../repos/mavlink__qgroundcontrol.md) (integrates_with)
- [AirSim](../repos/microsoft__airsim.md) (integrates_with)
- [Paparazzi UAV](../repos/paparazzi__paparazzi.md) (alternative_to)
- [Pegasus Simulator](../repos/pegasussimulator__pegasussimulator.md) (integrates_with)
- [PX4 Flight Review](../repos/px4__flight_review.md) (integrates_with)
- [jMAVSim](../repos/px4__jmavsim.md) (integrates_with)
- [PX4 Avoidance](../repos/px4__px4-avoidance.md) (integrates_with)
- [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md) (integrates_with)
- [PX4 ECL (Estimation & Control Library)](../repos/px4__px4-ecl.md) (same_org)
- [PX4 Gazebo models](../repos/px4__px4-gazebo-models.md) (integrates_with)
- [PX4 OpticalFlow](../repos/px4__px4-opticalflow.md) (integrates_with)
- [PX4 SITL Gazebo Classic](../repos/px4__px4-sitl_gazebo-classic.md) (integrates_with)
- [px4_msgs](../repos/px4__px4_msgs.md) (depends_on)
- [ROSflight firmware](../repos/rosflight__rosflight_firmware.md) (alternative_to)
- [Auterion Skynode S and Auterion Visual Navigation](../resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [PX4 Developer Summit 2025 Recap](../resources/dronecode-px4-dev-summit-2025-recap.md) (explains)
- [MAVLink 2 and Message Signing](../resources/mavlink-2-signing.md) (uses)
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) (uses)
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) (uses)
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) (uses)
- [PX4 Developer Summit 2025 recordings](../resources/px4-dev-summit-2025-playlist.md) (explains)
- [PX4 Developer Summit (talks and recordings)](../resources/px4-developer-summit.md) (uses)
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) (explains)
- [Using the ECL EKF (EKF2)](../resources/px4-ekf2-tuning-guide.md) (has_code)
- [Using Vision or Motion Capture Systems for Position Estimation](../resources/px4-external-position-estimation.md) (explains)
- [Optical Flow (PX4)](../resources/px4-optical-flow-docs.md) (explains)
- [Remote ID (Open Drone ID) in PX4](../resources/px4-remote-id-docs.md) (explains)
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) (explains)
- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) (uses)
- [Visual Inertial Odometry (VIO) in PX4](../resources/px4-visual-inertial-odometry.md) (explains)
- [PX4 Autopilot YouTube channel](../resources/px4-youtube-channel.md) (uses)
- [PX4 state estimation update (PX4 Developer Summit Virtual 2020)](../resources/riseborough-px4-state-estimation-2020.md) (explains)
- [PX4 SITL GPS denial: inject, measure drift, recover](../samples/px4-sitl-gps-denial.md) (uses)
- [VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion](../samples/vio-to-mavlink-bridge.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
