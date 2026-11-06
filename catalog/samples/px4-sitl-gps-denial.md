# Sample: PX4 SITL GPS denial: inject, measure drift, recover

`sample:px4-sitl-gps-denial` - code and walkthrough in [samples/px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/)

Flies a square mission in PX4 SITL (SIH quadrotor, headless; Gazebo also works per PX4 docs), denies GPS mid-mission, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home. GPS denial tries MAVSDK failure injection and falls back to SIM_GPS_USED=0 because PX4 v1.17 SIH does not acknowledge GPS failure injection. A stdlib analyzer reports per-phase horizontal drift and time to a 5 m error.

**Verification:** Ran on 2026-11-06 against PX4 v1.17.0 SIH (sihsim_quadx) in Docker from samples/sitl-docker (linux/arm64) with mavsdk-grpc 4.0.5 (its bundled mavsdk_server runs on linux aarch64; the macOS arm64 wheel binary also starts): 15 s GPS denial gave 8.37 m max horizontal error and 12.7 s to 5 m (drift.py on the real log, output in README). MAV_CMD_INJECT_FAILURE for GPS timed out (no ACK) on this target. drift.py tests (4) pass. gz_x500 and ulog_drift.py not run.

**Concepts:** [Assured / resilient PNT](../concepts/assured-pnt.md), [Autopilots and flight control](../concepts/autopilot.md), [Simulation and HIL/SITL](../concepts/simulation.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `px4`, `ekf2`, `sitl`, `gazebo`, `mavsdk`, `failure-injection`, `gps-denied`, `drift`, `ulog`

## Related

- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- uses: [MAVSDK-Python](../repos/mavlink__mavsdk-python.md)
- uses: [MAVSDK](../repos/mavlink__mavsdk.md)
- uses: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)
- explains: [PX4 Flight Review](../repos/px4__flight_review.md)

_Indexed by lane(s): samples_
