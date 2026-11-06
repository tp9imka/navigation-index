# Open Time Server spec

`repo:time-appliances-project/open-time-server` - <https://github.com/Time-Appliances-Project/Open-Time-Server>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 16 |  | MIT | 2025-02-17 | False | production | low |

OCP specification for an open time server: COTS server, a NIC with hardware timestamps and PPS in/out, and the Time Card as the GNSS/oscillator source.

**Why it matters:** A concise architecture document for a GNSS-backed time server with holdover; useful as a slide template for a resilient-timing pitch.

**Hackathon notes:** Read-only spec. Use the block diagram and responsibilities split when designing your own time node.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `spec`, `ocp`, `time-server`, `ptp`, `ntp`

**Domains:** multi

## Related

- same_org: [OCP Time Card](../../catalog/repos/time-appliances-project__time-card.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [OCP Time Card](../../catalog/repos/time-appliances-project__time-card.md) (same_org)
- [Open-sourcing a more precise time appliance](../../catalog/resources/meta-time-appliance-2021.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
