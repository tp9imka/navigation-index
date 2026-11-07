# Sample: How PX4 EKF2 and ArduPilot EKF3 handle a spoofed GNSS: source walk-through plus a 45-flight SITL sweep (drag rate 0.1-5 m/s, step offsets, default vs tightened gates, PX4 EKF2_GPS_MODE)

`sample:autopilot-spoof-response` - code and walkthrough in [samples/autopilot-spoof-response](../../samples/autopilot-spoof-response/)

Explains from source (PX4 v1.17.0, ArduPilot Copter-4.6.3) why both EKFs end up on a spoofed position even after flagging a GNSS glitch: innovation gates reject the GNSS, then a fixed timeout (EKF2 reset_timeout_max 7 s, EKF3 posRetryTimeUseVel_ms 10 s) resets position onto the GNSS when no other position source is fused; a coherent drag inside the gate is simply fused. Measures it with the golden-demo companions in shadow mode on PX4 SIH and ArduCopter SITL in Docker: coherent drag 0.1/0.5/1/2/3/5 m/s, position-only drag 3 m/s, 20 m and 100 m steps, PX4 default / gates 3 / EKF2_GPS_MODE 1 and ArduPilot default / gates 300. Reports flag times, reset jumps (cross-checked with EKF2 ODOMETRY.reset_counter), share of the spoof believed, path deviation and failsafes; docs/autopilot-gnss-fault-handling.md turns it into parameter and monitor guidance.

**Verification:** Ran 2026-11-06 on Apple Silicon (linux/arm64 Docker): 45 flights, seed 7, one per cell, PX4 v1.17.0 SIH (nav-sitl-px4:v1.17.0, companion in nav-sitl-client:latest) and ArduCopter 4.6.3 SITL (nav-sitl-ardupilot:copter-4.6.3, companion on the host with Python 3.12 + pymavlink), all parameter overrides echoed by PARAM_VALUE. Steps 20/100 m: PX4 rejected (GPS_GLITCH 0.2-7.2 s) then reset onto the full offset at 7.3 s; ArduPilot flagged 1.1-20.1 s and reset at 10.1 s; gates 3 / 300 identical. Position drag 3 m/s: PX4 5 resets of 24-28 m every ~10 s, ArduPilot 3 of 29-41 m every ~19 s, both ended 150 m off (spoof cap). Coherent 0.1-5 m/s: every config believed 96-110 % of the offset; no flag at <= 1 m/s with default gates. Tighter gates added LAND failsafes (PX4 coherent 2 m/s, ArduPilot coherent 3 m/s) without reducing capture. PX4 EKF2_GPS_MODE 1 refused steps and position drags (EKF error <= 5 m) and blind-landed after 12-14 s. Wall 1812 s for 43 flights in 3+2 lanes plus 287 s for 2. Source line citations at PX4 v1.17.0 (d6f12ad) and Copter-4.6.3 (92b0cd7) in docs/autopilot-gnss-fault-handling.md. Unit tests: 11 run, plain python3 9 pass / 2 skip (pymavlink, matplotlib); venv 11 pass. Not tested: EK3_GLITCH_RAD, EKF3 affinity with 2 receivers, EKF2_GPS_MODE 1 with a second aiding source, real receivers with spoof flags, hardware.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `ekf2`, `ekf3`, `gps-glitch`, `innovation-gate`, `reset`, `spoofing`, `coherent-spoof`, `px4`, `ardupilot`, `sitl`, `sih`, `docker`, `pymavlink`, `failsafe`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [MAVLink](../../catalog/repos/mavlink__mavlink.md)

## Referenced by

- [Autopilot GNSS fault handling: PX4 EKF2 and ArduPilot EKF3 under spoofing](../../docs/autopilot-gnss-fault-handling.md) (mentions)
- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
