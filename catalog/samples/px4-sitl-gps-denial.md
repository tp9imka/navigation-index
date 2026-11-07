# Sample: PX4 SITL GPS denial: inject, measure drift, recover

`sample:px4-sitl-gps-denial` - code and walkthrough in [samples/px4-sitl-gps-denial](../../samples/px4-sitl-gps-denial/)

Flies a square mission in PX4 SITL (SIH quadrotor, headless; Gazebo also works per PX4 docs), denies GPS mid-mission, logs EKF2 health and estimated vs ground-truth position, then restores GPS and returns home. GPS denial tries MAVSDK failure injection and falls back to SIM_GPS_USED=0 because PX4 v1.17 SIH does not acknowledge GPS failure injection. A stdlib analyzer reports per-phase horizontal drift and time to a 5 m error.

**Verification:** Ran on 2026-11-06 against PX4 v1.17.0 SIH (sihsim_quadx) in Docker from samples/sitl-docker (linux/arm64) with mavsdk-grpc 4.0.5 (its bundled mavsdk_server runs on linux aarch64; the macOS arm64 wheel binary starts but was not flown). Two flights of the same 15 s GPS denial (fresh containers each): run A 8.37 m max horizontal error and 12.7 s to 5 m, run B 17.71 m and 8.5 s (drift.py on the MAVSDK logs, output in README). ulog_drift.py (pyulog 1.3.0) ran on the run B .ulg: 18.30 m max during denial, 7.8 s to 5 m, agreeing with the MAVSDK log at ~125 Hz. MAV_CMD_INJECT_FAILURE for GPS timed out (no ACK) on this target. drift.py tests (4) pass. Not run: gz_x500 (Gazebo).

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `px4`, `ekf2`, `sitl`, `gazebo`, `mavsdk`, `failure-injection`, `gps-denied`, `drift`, `ulog`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)
- uses: [MAVSDK](../../catalog/repos/mavlink__mavsdk.md)
- uses: [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md)
- explains: [PX4 Flight Review](../../catalog/repos/px4__flight_review.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)

_Indexed by lane(s): samples_
