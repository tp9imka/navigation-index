# Sample: Anti-spoof autopilot configurations tested in SITL: 13 PX4 EKF2 / ArduPilot EKF3 configs (EV velocity + EKF2_GPS_MODE 1, aux global position, EK3 source sets, fuse-all-velocities, EK3_GLITCH_RAD 0, dual GPS affinity / blending, a Lua GPS-vs-ExternalNav source-switch applet, companion monitor) x coherent drag 0.3/1/3 m/s + clean, 3 seeds, 156 flights, ranked recipe table

`sample:autopilot-resilient-configs` - code and walkthrough in [samples/autopilot-resilient-configs](../../samples/autopilot-resilient-configs/)

Builds on samples/autopilot-spoof-response (both EKFs believe a coherent GNSS drag) and looks for configurations that keep each autopilot flying. Reuses the golden-demo / golden-demo-px4 companions and spoof_fly.py unchanged, adds committed parameter files per config, a second unspoofed GPS_INPUT receiver, and an ArduPilot Lua applet (scripts/gnss_extnav_switch.lua) that dead-reckons with ExternalNav velocity recovered from EKF3 innovations and switches to source set 2 on a GPS position or velocity disagreement. 156 flights on PX4 v1.17.0 SIH and ArduCopter 4.6.3 SITL in Docker; metrics per flight: max EKF error and cross-track deviation, time GNSS stopped being used (source switch or EKF2 cs_gnss_pos sampled from the PX4 shell), false alarms on clean flights, failsafes. Best onboard recipes: ArduPilot Lua switch (6/6 safe at 1 and 3 m/s, switch 2.3-3.5 s), PX4 EKF2_EV_CTRL 4 + EKF2_GPS_MODE 1 + gates 3 (6/6 safe at 1 and 3 m/s, GNSS out 8-15 s); nothing onboard caught 0.3 m/s, the external companion monitor did.

**Verification:** Ran 2026-11-06 on Apple Silicon (linux/arm64 Docker): 156 flights (13 configs x coherent drag 0.3/1/3 m/s + clean x seeds 1-3), PX4 v1.17.0 SIH (nav-sitl-px4:v1.17.0, companion in nav-sitl-client:latest) and ArduCopter 4.6.3 SITL (nav-sitl-ardupilot:copter-4.6.3, companion on the host, Python 3.12 + pymavlink 2.4.50), every parameter override echoed by PARAM_VALUE. ArduPilot lua-switch: 1 and 3 m/s 6/6 safe, source switch 2.3-3.5 s after onset, max EKF error 9.1-11.7 m, 0/3 clean false switches (dead-reckoning distance peaked 11.5 m of the 25 m threshold); 0.3 m/s 0/3 (one switch at 91 s). PX4 EKF2_EV_CTRL 4 + EKF2_GPS_MODE 1 + GPS gates 3: 1 and 3 m/s 6/6 safe, GNSS position fusion off 8.3-15.1 s after onset, max EKF error 4.7-12.5 m; 0.3 m/s 0/3. Same without the gates: 4/9. Dual GPS affinity held only 3 m/s (lane switch 0.1 s after onset); blending believed exactly half the spoof. EK3_SRC_OPTIONS 1, EK3_GLITCH_RAD 0, PX4 EV velocity in mode 0 and the defaults believed 92-105 %. PX4 aux global position (SIH sensor_agp_sim) + mode 1 lost GNSS before the attack in all 12 flights (cs_gnss_hgt_fault, not diagnosed). PX4 companion monitor 9/9 incl. 0.3 m/s (44-51 s). Wall 5809 s for 151 flights in 3+3 lanes plus 314 s smoke and 316 s for one re-flown takeoff timeout. Unit tests: 16, plain python3 15 pass / 1 skip (pymavlink); venv 16 pass. SITL only, simulated VIO with fixed bias, only coherent drags east, one spoofed receiver of two.

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `ekf2`, `ekf3`, `spoofing`, `coherent-spoof`, `lua`, `source-set`, `external-vision`, `aux-global-position`, `dual-gps`, `gps-blending`, `ek3-affinity`, `px4`, `ardupilot`, `sitl`, `sih`, `docker`, `pymavlink`, `parameters`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [MAVLink](../../catalog/repos/mavlink__mavlink.md)

## Referenced by

- [Autopilot GNSS fault handling: PX4 EKF2 and ArduPilot EKF3 under spoofing](../../docs/autopilot-gnss-fault-handling.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
