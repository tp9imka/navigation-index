# Statime

`repo:pendulum-project/statime` - <https://github.com/pendulum-project/statime>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 322 | Rust | NOASSERTION | 2026-11-03 | False | active-research | medium |

A PTP (IEEE 1588-2019) implementation in Rust: a platform-agnostic library with a Linux daemon and an STM32 example for embedded targets.

**Why it matters:** A second PTP stack to compare against linuxptp, and a route to PTP on embedded targets.

**Hackathon notes:** Try the Linux daemon against a linuxptp grandmaster; library use needs more effort.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `ptp`, `ieee-1588`, `rust`, `embedded`

**Domains:** multi

## Related

- alternative_to: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- same_org: [ntpd-rs](../../catalog/repos/pendulum-project__ntpd-rs.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [linuxptp](../../catalog/repos/nwtime__linuxptp.md) (alternative_to)
- [ntpd-rs](../../catalog/repos/pendulum-project__ntpd-rs.md) (same_org)
- [IEEE 1588-2019: IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems](../../catalog/resources/ieee-1588-2019.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
