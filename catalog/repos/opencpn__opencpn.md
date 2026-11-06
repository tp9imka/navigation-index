# OpenCPN

`repo:opencpn/opencpn` - <https://github.com/OpenCPN/OpenCPN>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,517 | C | GPL-2.0 | 2026-11-05 | False | production | high |

Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes. Large plugin ecosystem.

**Why it matters:** The de facto open maritime nav display; a ready-made situational awareness front end for any surface-vessel or GNSS-denied maritime demo.

**Hackathon notes:** Install the packaged build, feed it NMEA over UDP/TCP from your own nav filter or a simulator and you have a chart display in minutes. Writing a plugin needs the plugin SDK and a full C++ build.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [opencpn__opencpn](../../docs/integration-cards/opencpn__opencpn.md) (integration-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `chartplotter`, `s57`, `ais`, `nmea0183`, `plugins`

**Domains:** maritime

## Related

- integrates_with: [OpenCPN radar_pi](../../catalog/repos/opencpn-radar-pi__radar_pi.md)
- integrates_with: [Signal K Server](../../catalog/repos/signalk__signalk-server.md)
- integrates_with: [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md) (integrates_with)
- [OpenCPN radar_pi](../../catalog/repos/opencpn-radar-pi__radar_pi.md) (extends)
- [Signal K Server](../../catalog/repos/signalk__signalk-server.md) (integrates_with)
- [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md) (explains)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
