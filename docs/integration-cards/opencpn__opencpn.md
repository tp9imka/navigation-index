# OpenCPN - integration card
<!-- about: repo:opencpn/opencpn -->
One-line: open chartplotter for the surface-vessel operator view - S-57 vector and BSB raster charts, own-ship from any NMEA 0183 / NMEA 2000 / Signal K feed, AIS targets, routes - fed by your nav filter over UDP with no code.

| | |
|---|---|
| Install | Ubuntu: `sudo add-apt-repository ppa:opencpn/opencpn && sudo apt install opencpn` (PPA `~opencpn/ubuntu/opencpn`). Any Linux: `flatpak install flathub org.opencpn.OpenCPN` (Flathub 5.14.2). Windows `opencpn_5.14.2-..._setup.exe` and macOS universal `OpenCPN_5.14.2-universal+....pkg` from GitHub release `Release_5.14.2`. Source: `mk-build-deps -i -r ci/control`, then `cmake .. && make -j4` (INSTALL). |
| Runs on | Windows, macOS (universal), Linux x86_64 and ARM (Raspberry Pi), Android. Needs wxWidgets >= 3.0 and OpenGL for good S-57 performance (`-G` disables GL). |
| Inputs | Connections (Options => Connections): serial, UDP, TCP NMEA 0183 (GGA/RMC/VTG/HDT/HDG and AIS `!AIVDM`), NMEA 2000 via gateways, Signal K server. Charts: S-57 ENC (`.000`), BSB/KAP raster, CM93; S-63 encrypted ENC and others via plugins. GPX for routes, tracks, waypoints. Tide/current data bundled (`tcdata`). |
| Outputs | Chart display with own-ship, track, AIS targets and CPA/TCPA alarms; NMEA output on a connection (e.g. route-following sentences to an autopilot); GPX export; plugin hooks. |
| Key API / entry points | GUI `opencpn` with flags (`opencpn.1`): `-p` portable, `-c <dir>` config dir, `-f` fullscreen, `-G` no OpenGL, `-D` rebuild chart DB, `-P` parse all ENC, `-s` safe mode (no plugins), `-r` remote (talk to running instance), `-l <level>` log level. `opencpn-cmd` (alpha, plugin management). Plugin API `include/ocpn_plugin.h` (API 1.22, base `opencpn_plugin_122`): capability flags `WANTS_NMEA_SENTENCES`, `WANTS_AIS_SENTENCES`, `WANTS_PLUGIN_MESSAGING`; callbacks `SetNMEASentence(wxString&)`, `SetPositionFixEx(PlugIn_Position_Fix_Ex&)`, `RenderOverlayMultiCanvas(...)`; calls `PushNMEABuffer(wxString)`, `AddSingleWaypoint(...)`, `AddPlugInRoute(...)`, `AddPlugInTrack(...)`, `GetAISTargetArray()`, `JumpToPosition(lat, lon, scale)`, `GetActiveDrivers()` / `WriteCommDriver(...)`. |
| Time to first result | Estimate: 15 min to see own-ship from a UDP NMEA feed on the bundled world shoreline; 30-60 min with real ENCs for the area. Assumes packaged install and a free ENC source (e.g. NOAA for US waters). Writing a plugin: a day, full C++ toolchain. |
| License | GPL-2.0-or-later for project files (LICENSING); bundled third-party code under GPLv3, LGPLv2/3, BSD, MIT, Apache-2.0, SGI FSL-B and others (file list in `data/copyright`). GitHub metadata: GPL-2.0. |

## Minimal usage
Not run. Options => Connections => Add: Network, UDP, address 0.0.0.0, port 10110, protocol NMEA 0183, Receive. Then stream own-ship from any process:

```python
import socket, time, math
from functools import reduce
def nmea(body): return f"${body}*{reduce(lambda a, c: a ^ ord(c), body, 0):02X}\r\n"
def dm(v, lat):  # decimal degrees => ddmm.mmmm,H
    h = ("N" if v >= 0 else "S") if lat else ("E" if v >= 0 else "W"); v = abs(v)
    d = int(v); return f"{d:02d}{(v - d) * 60:07.4f},{h}" if lat else f"{d:03d}{(v - d) * 60:07.4f},{h}"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lat, lon, hdg, sog = 63.44, 10.40, 45.0, 6.0
while True:
    t = time.strftime("%H%M%S.00", time.gmtime()); d = time.strftime("%d%m%y", time.gmtime())
    for b in (f"GPRMC,{t},A,{dm(lat,1)},{dm(lon,0)},{sog:.1f},{hdg:.1f},{d},,,A",
              f"HEHDT,{hdg:.1f},T"):
        s.sendto(nmea(b).encode(), ("127.0.0.1", 10110))
    lat += sog * 0.514 / 111320 * math.cos(math.radians(hdg)); time.sleep(1)
```

Port 10110 is the conventional NMEA-over-IP port; any free port works as long as both sides match.

## Wiring it into a nav stack
- Estimator => chart: emit RMC (position, SOG, COG) and HDT (true heading) from your fused solution, [robot_localization](./cra-ros-pkg__robot_localization.md) output or a [GTSAM](./borglab__gtsam.md) smoother. Add a second connection with raw GNSS to compare truth vs estimate during a spoofing or outage demo (OpenCPN shows one own-ship position at a time; send the second solution as an AIS target via AIVDM, or draw it from a plugin).
- Contacts: AIS from a receiver via [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md); synthetic or radar-derived tracks can be encoded as AIVDM with [pyais](../../catalog/repos/m0r13n__pyais.md). Radar overlay: [radar_pi](../../catalog/repos/opencpn-radar-pi__radar_pi.md).
- ArduPilot boats: MAVProxy's `nmeaout` module writes GGA/RMC to a serial port only (`mavproxy_nmeaout.py`), so for UDP write a small [pymavlink](./ardupilot__pymavlink.md) bridge like the snippet above. On BlueOS boats, see the [BlueOS card](./bluerobotics__blueos.md).
- [Signal K server](../../catalog/repos/signalk__signalk-server.md) is the usual hub when several sensors and displays share data; OpenCPN connects to it natively.
- Autonomy sim on the same chart: [MOOS-IvP](./moos-ivp__moos-ivp.md) or [colav-simulator](./ntnu-itk-autonomous-ship-lab__colav-simulator.md) positions converted to RMC/AIVDM.
- Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [situational-awareness](../../catalog/concepts/situational-awareness.md), [gis-mapping](../../catalog/concepts/gis-mapping.md). Catalog page: [catalog/repos/opencpn__opencpn.md](../../catalog/repos/opencpn__opencpn.md).

## Gotchas
- Charts are not bundled beyond a world shoreline. NOAA ENCs (US) are free; many national ENCs are S-63 encrypted and need paid permits plus the oeSENC/S-63 plugins. Flatpak and native builds have handled S-63 install permits differently (#4119, open).
- Connection setup is the usual failure: wrong direction (receive vs transmit), firewall on the UDP port, or filters. A filter on a network connection destroying it is open in #5490; #3700 asks for guards against common mistakes.
- NMEA checksums must be correct or sentences are dropped; HDT/HDG is needed for heading, otherwise the icon follows COG.
- Raspberry Pi: startup crash if Settings is opened before the canvas loads (#2493, open); S-63 slow on Pi 4 (#3789, open). Try `-G` (no OpenGL) if rendering misbehaves.
- macOS arm64 5.14.2 crash in Route & Mark Manager (#5516, open); Signal K AIS delta crash on macOS (#5145, open).
- Plugins must be built against the matching plugin API; use the in-app plugin manager catalog rather than random binaries.
- Licensing: GPL-2.0+; a closed-source plugin linking `ocpn_plugin.h` is a grey area, keep plugins GPL-compatible.

## Alternatives
- [QGroundControl](./mavlink__qgroundcontrol.md) - when the vessel is a MAVLink vehicle and the operator mostly needs mission control, not nautical charts.
- [MapLibre GL JS](./maplibre__maplibre-gl-js.md) - custom browser view when you need your own layers (uncertainty, spoofing alerts) more than S-57 rendering.
- TAK clients ([ATAK-CIV](../../catalog/repos/tak-product-center__atak-civ.md), [goatak](./kdudkov__goatak.md)) - when the maritime picture must be shared with a TAK-based team.

Sources: `gh api repos/OpenCPN/OpenCPN` (GPL-2.0, release Release_5.14.2 2026-09-28 and assets), README, LICENSING, INSTALL, opencpn.1, opencpn-cmd.1, include/ocpn_plugin.h (API_VERSION 1.22, flags, functions), Launchpad API for `~opencpn/ubuntu/opencpn`, Flathub appstream for `org.opencpn.OpenCPN`, ArduPilot/MAVProxy `MAVProxy/modules/mavproxy_nmeaout.py`, issues #2493, #3700, #3789, #4119, #5145, #5490, #5516.
