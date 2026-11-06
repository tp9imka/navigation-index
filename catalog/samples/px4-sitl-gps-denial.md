# Sample: PX4 SITL GPS denial: inject, measure drift, recover

`sample:px4-sitl-gps-denial` - code and walkthrough in [samples/px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/)

Flies a square mission in PX4 SITL (Gazebo gz_x500), turns the GPS off mid-mission with MAVSDK failure injection, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home. A stdlib analyzer reports per-phase horizontal drift and time to a 5 m error, and reads 'not measured' when no truth is available.

**Verification:** drift.py and test_drift.py ran with python3.14.7 stdlib on 2026-11-06 (4 tests OK, synthetic drift output shown in README). gps_denial_mission.py and ulog_drift.py are unverified sketches: syntax-checked only, require mavsdk-grpc with PX4 SITL (Gazebo) and pyulog respectively.

**Concepts:** [Assured / resilient PNT](../concepts/assured-pnt.md), [Autopilots and flight control](../concepts/autopilot.md), [Simulation and HIL/SITL](../concepts/simulation.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `px4`, `ekf2`, `sitl`, `gazebo`, `mavsdk`, `failure-injection`, `gps-denied`, `drift`, `ulog`

## Related

- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- uses: [MAVSDK-Python](../repos/mavlink__mavsdk-python.md)
- uses: [MAVSDK](../repos/mavlink__mavsdk.md)
- uses: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)
- explains: [PX4 Flight Review](../repos/px4__flight_review.md)

_Indexed by lane(s): samples_
