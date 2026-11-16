# mavlink-router

`repo:mavlink-router/mavlink-router` - <https://github.com/mavlink-router/mavlink-router>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 625 | C++ | Apache-2.0 | 2026-10-23 | False | production | high |

Lightweight C++ daemon that routes MAVLink between serial, UDP and TCP endpoints with filtering and logging.

**Why it matters:** Typical companion-computer plumbing to share one flight-controller link between GCS, autonomy and loggers.

**Build notes:** Build with meson; one config file. Run it before attaching multiple clients.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [mavlink-router__mavlink-router](../../docs/integration-cards/mavlink-router__mavlink-router.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `router`, `companion`, `udp`, `serial`

**Domains:** multi

## Related

- alternative_to: [mavp2p](../../catalog/repos/bluenviron__mavp2p.md)
- alternative_to: [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MAVProxy](../../catalog/repos/ardupilot__mavproxy.md) (alternative_to)
- [mavp2p](../../catalog/repos/bluenviron__mavp2p.md) (alternative_to)
- [Rpanion-server](../../catalog/repos/stephendade__rpanion-server.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-16._
