# Sample: Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay

`sample:golden-demo-px4` - code and walkthrough in [samples/golden-demo-px4](../../samples/golden-demo-px4/)

The samples/golden-demo v2 scenario on PX4 v1.17.0 SIH in Docker. A pymavlink companion (a subclass of the golden-demo companion; monitor, spoof model and replayed real visual geoloc imported unchanged) feeds the only GPS as MAVLink HIL_GPS (MAV_USEHILGPS=1, SIH sensor_gps_sim off; v1.17 has no GPS_INPUT handler), drags it east at 1 m/s from t=25 s, streams its GNSS-free VIO + visual-geoloc reference as ODOMETRY at 10 Hz (EKF2 needs EV samples < 200 ms apart), and on the first alarm sets EKF2_GPS_CTRL=0 then EKF2_EV_CTRL=5 so EKF2 resets onto external vision. Aux global position was not used because v1.17 has no MAVLink path into it (DDS only). Monitor vs no-monitor flights, a 20-flight sweep, navdash/1 output for templates/demo-dashboard, and a side-by-side with the ArduPilot reference.

**Verification:** Ran 2026-11-06 on Apple Silicon (linux/arm64 Docker 29.5.2, nav-sitl-px4:v1.17.0 built from samples/sitl-docker, companion in nav-sitl-client:latest with Python 3.12 + pymavlink 2.4.50). Reference pair (coherent 1 m/s, seed 7): velocity-test alarm 3.0 s after onset, EKF2_GPS_CTRL=0 + EKF2_EV_CTRL=5 echoed within 0.03 s, max cross-track deviation 7.8 m with the monitor vs 75.0 m without, EKF2 error 8.2 m vs 105.7 m, EKF2 GPS_GLITCH never set and eph 0.22 m while 106 m off; ArduPilot reference 3.0 s, 6.8 m vs 75.0 m. 20-flight sweep (2 seeds x position/coherent x 1/3 m/s + no-spoof, monitor and shadow, 2012 s wall in 3 lanes): all completed; monitor deviation 7-9 m except position 1 m/s (22 m); without monitor 75 m at 1 m/s and 108-152 m at 3 m/s even though EKF2 flagged GPS_GLITCH; 1 SS false alarm in 2 no-spoof monitor flights. 6 unit tests pass in the venv; 3 pass and 3 skip under plain python3. Not tested: speedup, amd64, PX4 main, aux global position over DDS, host-side MAVLink (did not get replies through a published UDP port).

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `coherent-spoof`, `dashboard`, `demo`, `docker`, `ekf2`, `external-vision`, `gps-drag`, `hil-gps`, `integrity`, `odometry`, `protection-level`, `px4`, `pymavlink`, `sih`, `sitl`, `solution-separation`, `spoofing`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [MAVLink](../../catalog/repos/mavlink__mavlink.md)
- uses: [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)

_Indexed by lane(s): samples_
