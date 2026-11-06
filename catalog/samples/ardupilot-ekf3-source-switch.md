# Sample: ArduPilot EKF3 source-set switch under GPS denial

`sample:ardupilot-ekf3-source-switch` - code and walkthrough in [samples/ardupilot-ekf3-source-switch](../../samples/ardupilot-ekf3-source-switch/)

Flies ArduCopter SITL on GPS, switches EKF3 to an external-nav source set (SITL vicon) with MAV_CMD_SET_EKF_SOURCE_SET or an RC aux switch, cuts simulated GPS, keeps flying, then restores it. EKF_STATUS_REPORT is logged throughout, decoded by a stdlib module with unit tests.

**Verification:** ekf_flags.py and test_ekf_flags.py ran with python3.14.7 stdlib on 2026-11-06 (6 tests OK), output shown in README. source_switch.py is an unverified sketch: syntax-checked only, requires pymavlink and ArduPilot SITL (sim_vehicle.py with the vicon simulator); parameter names were checked against ArduPilot master and the ArduPilot-4.6 branch source on 2026-11-06.

**Concepts:** [Autopilots and flight control](../concepts/autopilot.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Simulation and HIL/SITL](../concepts/simulation.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `ardupilot`, `ekf3`, `source-sets`, `sitl`, `pymavlink`, `gps-denied`, `external-nav`, `vicon`

## Related

- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../repos/ardupilot__pymavlink.md)
- uses: [MAVProxy](../repos/ardupilot__mavproxy.md)
- explains: [MAVLink](../repos/mavlink__mavlink.md)

_Indexed by lane(s): samples_
