# Sample: Golden demo: GPS drag on an ArduCopter SITL AUTO mission, chi-square detection and EKF3 switch to vision, replayed on the dashboard

`sample:golden-demo` - code and walkthrough in [samples/golden-demo](../../samples/golden-demo/)

One command flies ArduCopter 4.6.3 SITL in Docker on a survey, drags its GPS east at 1 m/s with SIM_GPS_GLITCH_X/Y, and runs a pymavlink companion that streams simulated visual-geolocalization fixes as VISION_POSITION_ESTIMATE, tests GNSS against a VIO dead-reckoning + visual-geoloc reference with navapp's windowed chi-square monitor, and on alarm commands MAV_CMD_SET_EKF_SOURCE_SET 2 (ExternalNav). A contrast run without the response shows the copter following the spoof while its EKF raises no GPS_GLITCHING flag. Both runs are logged and converted to navdash/1 for templates/demo-dashboard, with a headless screenshot.

**Verification:** Ran 2026-11-06 on Apple Silicon (linux/arm64 Docker, Copter-4.6.3 SITL image from samples/sitl-docker, pymavlink 2.4.50, Python 3.12), one run per mode, seed 7: monitor alarm 9.4 s after onset at 9.3 m spoof offset, max cross-track deviation 7.6 m with the monitor vs 75.0 m without, max EKF error 7.7 m vs 88.3 m; EKF GPS_GLITCHING never set in either run. 6 converter unit tests pass; dashboard rendered headless in Chrome via the DevTools protocol. Alt-PNT and VIO inputs are truth plus noise; no Monte Carlo; amd64 and ArduPilot 4.7+ not tested.

**Concepts:** [Assured / resilient PNT](../concepts/assured-pnt.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Simulation and HIL/SITL](../concepts/simulation.md), [Autopilots and flight control](../concepts/autopilot.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md)

**Tags:** `demo`, `spoofing`, `gps-drag`, `sitl`, `ardupilot`, `ekf3`, `source-switch`, `externalnav`, `vision-position-estimate`, `chi-square`, `integrity`, `pymavlink`, `dashboard`, `navdash`, `docker`

## Related

- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../repos/ardupilot__pymavlink.md)
- uses: [MapLibre GL JS](../repos/maplibre__maplibre-gl-js.md)

_Indexed by lane(s): samples_
