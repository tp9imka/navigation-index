# Sample: ArduPilot EKF3 source-set switch under GPS denial

`sample:ardupilot-ekf3-source-switch` - code and walkthrough in [samples/ardupilot-ekf3-source-switch](../../samples/ardupilot-ekf3-source-switch/)

Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET, cuts simulated GPS, flies a 15 m leg, then restores it. A --no-switch contrast run shows the EKF losing position and the EKF failsafe landing the copter. EKF_STATUS_REPORT, GPS fix and local position are logged throughout; the flag decoder is stdlib with unit tests.

**Verification:** Ran on 2026-11-06 against ArduCopter Copter-4.6.3 SITL in Docker (samples/sitl-docker, linux/arm64) with pymavlink 2.4.50 on python3.12: source switch accepted, EKF kept POS_HORIZ_ABS with GPS fix_type 1 for 30 s and flew the 15 m leg; --no-switch lost position after ~6 s and triggered 'EKF Failsafe: changed to LAND Mode'. Output in README. ekf_flags.py tests (6) pass on python3.14.7. --switch-via rc not run.

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Simulation and HIL/SITL](../concepts/simulation.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `ardupilot`, `ekf3`, `source-sets`, `sitl`, `pymavlink`, `gps-denied`, `external-nav`, `vicon`

## Related

- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../repos/ardupilot__pymavlink.md)
- uses: [MAVProxy](../repos/ardupilot__mavproxy.md)
- explains: [MAVLink](../repos/mavlink__mavlink.md)

_Indexed by lane(s): samples_
