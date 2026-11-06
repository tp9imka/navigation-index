# QGroundControl - integration card
<!-- about: repo:mavlink/qgroundcontrol -->
One-line: cross-platform MAVLink ground station for PX4 and ArduPilot; in a hackathon it is the demo screen (map, EKF/GPS status, parameters, MAVLink Inspector) rather than something you modify.

| | |
|---|---|
| Install | Prebuilt binaries from the latest release (v5.1.5, 2026-10-01 at time of writing): `QGroundControl-x86_64.AppImage` (Linux), `QGroundControl.dmg`, `QGroundControl-installer-AMD64.exe`, `QGroundControl.apk`. Linux: `chmod +x QGroundControl-x86_64.AppImage && ./QGroundControl-x86_64.AppImage`. Building from source needs Qt and takes hours to set up (see the Developer Guide). |
| Runs on | Windows, macOS, Linux x86-64, Android, iOS (README). |
| Inputs | MAVLink over UDP (auto-listens on 14550), TCP, serial/USB; QGC `.plan` mission files; video via GStreamer (UDP RTP / RTSP). |
| Outputs | Commands, missions, geofences, rally points, parameters to the vehicle; `.tlog` telemetry logs; downloaded ULog / DataFlash logs. |
| Key API / entry points | Fly View (map, instruments), Plan View (waypoint, survey, structure scan), Vehicle Setup, Parameters, Analyze Tools: MAVLink Inspector, MAVLink Console (PX4 `pxh` shell, so `failure gps off` and `listener` work from the GUI), log download. Developer entry: `AGENTS.md` and `.github/CONTRIBUTING.md` in the repo. |
| Time to first result | Estimate: 5 min with a running SITL on the same machine (download, run, it auto-connects). |
| License | Dual Apache-2.0 / GPL-3.0 (`.github/COPYING.md`); the Apache option requires a commercial Qt license. GitHub metadata shows Apache-2.0. |

## Minimal usage
Not run.

```bash
# Linux
wget https://github.com/mavlink/QGroundControl/releases/latest/download/QGroundControl-x86_64.AppImage
chmod +x QGroundControl-x86_64.AppImage
./QGroundControl-x86_64.AppImage        # start PX4 SIH/gz or ArduPilot SITL; QGC connects on UDP 14550
```
Remote SITL: Application Settings => Comm Links => add UDP/TCP link to the SITL host.

## Wiring it into a nav stack
- Shows what the estimator thinks: GPS fix/satellite count, EKF status flags, and position. Good for showing judges a GNSS-loss event injected via [PX4](./px4__px4-autopilot.md) `failure gps off` or [ArduPilot](./ardupilot__ardupilot.md) `SIM_GPS1_ENABLE 0`.
- When QGC shares a vehicle with ROS/[MAVROS](./mavlink__mavros.md) or scripts, run [mavlink-router](./mavlink-router__mavlink-router.md) and give QGC its own endpoint.
- `.plan` files from QGC can be loaded by [MAVSDK-Python](./mavlink__mavsdk-python.md) (`examples/mission_import.py`) and are produced by [MAVLinkMCP](./ion-g-ion__mavlinkmcp.md) (`download_mission_as_plan`).
- Situational awareness beyond the own vehicle (other tracks, MIL-STD-2525 symbols) belongs in a TAK client fed by [PyTAK](./snstac__pytak.md); QGC has no CoT support.
- Catalog: [QGroundControl page](../../catalog/repos/mavlink__qgroundcontrol.md).

## Gotchas
- Ubuntu: the AppImage needs FUSE and the user in the `dialout` group for serial; ModemManager can grab telemetry radios (QGC docs; not re-verified here).
- Open issues: #13803 segfault in Linux Docker, #13802 video window missing on AArch64 RPi daily build, #15048 freeze with a flood of STATUSTEXT messages (an agent or script spamming status text can lock the UI).
- Custom builds pull in Qt licensing questions; prefer stock binaries for a hackathon.

## Alternatives
- [MAVProxy](./ardupilot__mavproxy.md): terminal GCS, scriptable modules, already in ArduPilot SITL.
- [Mission Planner](../../catalog/repos/ardupilot__missionplanner.md): ArduPilot-focused, Windows-first.
- [APM Planner](../../catalog/repos/ardupilot__apm_planner.md).

Sources: `README.md`, `.github/COPYING.md`, releases API (v5.1.5), issue search (#13803, #13802, #15048).
