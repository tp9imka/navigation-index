# OpenCPN

`repo:opencpn/opencpn` - <https://github.com/OpenCPN/OpenCPN>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,517 | C | GPL-2.0 | 2026-11-05 | False | production | high |

Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes. Large plugin ecosystem.

**Why it matters:** The de facto open maritime nav display; a ready-made situational awareness front end for any surface-vessel or GNSS-denied maritime demo.

**Hackathon notes:** Install the packaged build, feed it NMEA over UDP/TCP from your own nav filter or a simulator and you have a chart display in minutes. Writing a plugin needs the plugin SDK and a full C++ build.

**Concepts:** [Maritime navigation](../concepts/maritime-nav.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `chartplotter`, `s57`, `ais`, `nmea0183`, `plugins`

**Domains:** maritime

## Related

- integrates_with: [OpenCPN radar_pi](../repos/opencpn-radar-pi__radar_pi.md)
- integrates_with: [Signal K Server](../repos/signalk__signalk-server.md)
- integrates_with: [AIS-catcher](../repos/jvde-github__ais-catcher.md)

## Referenced by

- [AIS-catcher](../repos/jvde-github__ais-catcher.md) (integrates_with)
- [OpenCPN radar_pi](../repos/opencpn-radar-pi__radar_pi.md) (extends)
- [Signal K Server](../repos/signalk__signalk-server.md) (integrates_with)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
