# Sample: VIO to MAVLink bridge with ENU/FLU to NED/FRD conversion

`sample:vio-to-mavlink-bridge` - code and walkthrough in [samples/vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge/)

Sends an external pose source (VIO topic or CSV log) to PX4 EKF2 or ArduPilot EKF3 as VISION_POSITION_ESTIMATE or ODOMETRY for GPS-denied position hold. The frame conversion (ENU/FLU to NED/FRD, world to body velocity, MAVLink covariance layout) is a stdlib module with unit tests, and the pymavlink sender plus small set_params / watch_ekf helpers sit on top.

**Verification:** Ran on 2026-11-06: frames.py tests (8 OK) and --dry-run on python3.14.7; the pymavlink ODOMETRY path ran against ArduCopter 4.6.3 SITL (EKF3 'is using external nav data', flags 0x033f) and PX4 v1.17.0 SIH (estimator_status_flags cs_ev_pos/cs_ev_hgt/cs_ev_yaw/cs_ev_vel True), both in Docker from samples/sitl-docker with pymavlink 2.4.50. Only a stationary pose was streamed; no flight on vision was tested. --msg vpe not run.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `mavlink`, `pymavlink`, `external-vision`, `odometry`, `frames`, `enu-ned`, `ekf2`, `ekf3`, `gps-denied`

## Related

- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [MAVLink](../../catalog/repos/mavlink__mavlink.md)
- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- explains: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- explains: [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md)
- explains: [MAVROS](../../catalog/repos/mavlink__mavros.md)
- explains: [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
