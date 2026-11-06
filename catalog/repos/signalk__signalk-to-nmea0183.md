# signalk-to-nmea0183

`repo:signalk/signalk-to-nmea0183` - <https://github.com/SignalK/signalk-to-nmea0183>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 18 | TypeScript | Apache-2.0 | 2026-10-31 | False | production | medium |

Signal K server plugin that converts Signal K data back into NMEA 0183 sentences for legacy displays and autopilots.

**Why it matters:** Lets a custom position or heading source reach any off-the-shelf NMEA consumer such as OpenCPN or a chartplotter.

**Hackathon notes:** Enable in the Signal K admin UI, choose sentences, output over TCP.

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md)

**Tags:** `signalk`, `nmea0183`, `plugin`

**Domains:** maritime

## Related

- extends: [Signal K Server](../../catalog/repos/signalk__signalk-server.md)

## Referenced by

- [Signal K Server](../../catalog/repos/signalk__signalk-server.md) (integrates_with)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
