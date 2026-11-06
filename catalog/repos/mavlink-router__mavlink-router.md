# mavlink-router

`repo:mavlink-router/mavlink-router` - <https://github.com/mavlink-router/mavlink-router>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 624 | C++ | Apache-2.0 | 2026-10-23 | False | production | high |

Lightweight C++ daemon that routes MAVLink between serial, UDP and TCP endpoints with filtering and logging.

**Why it matters:** Typical companion-computer plumbing to share one flight-controller link between GCS, autonomy and loggers.

**Hackathon notes:** Build with meson; one config file. Run it before attaching multiple clients.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [mavlink-router__mavlink-router](../../docs/integration-cards/mavlink-router__mavlink-router.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `router`, `companion`, `udp`, `serial`

**Domains:** multi

## Related

- alternative_to: [mavp2p](../repos/bluenviron__mavp2p.md)
- alternative_to: [MAVProxy](../repos/ardupilot__mavproxy.md)

## Referenced by

- [MAVProxy](../repos/ardupilot__mavproxy.md) (alternative_to)
- [mavp2p](../repos/bluenviron__mavp2p.md) (alternative_to)
- [Rpanion-server](../repos/stephendade__rpanion-server.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
