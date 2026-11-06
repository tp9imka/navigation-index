# ntpd-rs

`repo:pendulum-project/ntpd-rs` - <https://github.com/pendulum-project/ntpd-rs>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,156 | Rust | NOASSERTION | 2026-11-05 | False | production | medium |

A memory-safe NTP client and server in Rust with NTS support, from the Pendulum project (Trifecta Tech Foundation).

**Why it matters:** NTS-authenticated time from a small Rust daemon: a reasonable second time source to cross-check GNSS time on an edge box.

**Hackathon notes:** Packages and a container exist; configure NTS sources and read offsets via ntp-ctl. Its source-selection behaviour is a useful comparison with chrony.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ntp`, `nts`, `rust`, `memory-safe`

**Domains:** multi

## Related

- alternative_to: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- same_org: [Statime](../../catalog/repos/pendulum-project__statime.md)
- same_org: [NTS pool](../../catalog/repos/pendulum-project__nts-pool.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [cfnts](../../catalog/repos/cloudflare__cfnts.md) (alternative_to)
- [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) (alternative_to)
- [NTS pool](../../catalog/repos/pendulum-project__nts-pool.md) (same_org)
- [Statime](../../catalog/repos/pendulum-project__statime.md) (same_org)
- [Comparison of NTP implementations (chrony)](../../catalog/resources/chrony-comparison.md) (explains)
- [RFC 8915: Network Time Security for the Network Time Protocol](../../catalog/resources/rfc8915-nts.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
