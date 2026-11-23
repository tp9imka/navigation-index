# Signal K Server

`repo:signalk/signalk-server` - <https://github.com/SignalK/signalk-server>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 450 | TypeScript | Apache-2.0 | 2026-11-22 | False | production | high |

Node.js server implementing the Signal K open marine data standard: it ingests NMEA 0183, NMEA 2000 and other boat buses and republishes everything as a JSON data model over REST and WebSocket, with a plugin ecosystem.

**Why it matters:** A modern data bus for a vessel; ideal glue between sensors, your own nav filter and displays.

**Build notes:** Run via Docker or npm, enable the sample data playback, subscribe over WebSocket. Write a plugin to inject an alternative position source.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [signalk__signalk-server](../../docs/integration-cards/signalk__signalk-server.md) (integration-cards)
- [maritime-datasets](../../docs/dataset-cards/maritime-datasets.md) (dataset-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `signalk`, `nmea2000`, `nmea0183`, `websocket`, `iot`

**Domains:** maritime

## Related

- depends_on: [Signal K Specification](../../catalog/repos/signalk__specification.md)
- integrates_with: [signalk-to-nmea0183](../../catalog/repos/signalk__signalk-to-nmea0183.md)
- integrates_with: [OpenCPN](../../catalog/repos/opencpn__opencpn.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [CANboat](../../catalog/repos/canboat__canboat.md) (integrates_with)
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) (integrates_with)
- [signalk-to-nmea0183](../../catalog/repos/signalk__signalk-to-nmea0183.md) (extends)
- [Signal K Specification](../../catalog/repos/signalk__specification.md) (same_org)
- [Signal K Specification](../../catalog/resources/signalk-spec.md) (explains)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-23._
