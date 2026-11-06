# Signal K Server

`repo:signalk/signalk-server` - <https://github.com/SignalK/signalk-server>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 448 | TypeScript | Apache-2.0 | 2026-11-05 | False | production | high |

Node.js server implementing the Signal K open marine data standard: it ingests NMEA 0183, NMEA 2000 and other boat buses and republishes everything as a JSON data model over REST and WebSocket, with a plugin ecosystem.

**Why it matters:** A modern data bus for a vessel; ideal glue between sensors, your own nav filter and displays.

**Hackathon notes:** Run via Docker or npm, enable the sample data playback, subscribe over WebSocket. Write a plugin to inject an alternative position source.

**Concepts:** [Maritime navigation](../concepts/maritime-nav.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `signalk`, `nmea2000`, `nmea0183`, `websocket`, `iot`

**Domains:** maritime

## Related

- depends_on: [Signal K Specification](../repos/signalk__specification.md)
- integrates_with: [signalk-to-nmea0183](../repos/signalk__signalk-to-nmea0183.md)
- integrates_with: [OpenCPN](../repos/opencpn__opencpn.md)

## Referenced by

- [OpenCPN](../repos/opencpn__opencpn.md) (integrates_with)
- [signalk-to-nmea0183](../repos/signalk__signalk-to-nmea0183.md) (extends)
- [Signal K Specification](../repos/signalk__specification.md) (same_org)
- [Signal K Specification](../resources/signalk-spec.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
