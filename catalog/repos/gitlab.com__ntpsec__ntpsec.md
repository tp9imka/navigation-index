# NTPsec

`repo:gitlab.com/ntpsec/ntpsec` - <https://gitlab.com/NTPsec/ntpsec>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | medium |

A security-focused refactor of the reference NTP implementation with much of the legacy code removed, NTS support and the classic refclock drivers. GitHub mirror: ntpsec/ntpsec.

**Why it matters:** Keeps the reference-implementation refclock drivers (useful for odd timing receivers) while dropping much of the attack surface of classic ntpd.

**Hackathon notes:** Use when a specific refclock driver is needed that chrony lacks; otherwise chrony is easier. ntpviz plots offsets and frequency from its logs.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ntp`, `nts`, `refclock`, `stratum-1`

**Domains:** multi

## Related

- fork_of: [NTP reference implementation (ntpd)](../../catalog/repos/ntp-project__ntp.md)
- alternative_to: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) (alternative_to)
- [NTP reference implementation (ntpd)](../../catalog/repos/ntp-project__ntp.md) (alternative_to)
- [Comparison of NTP implementations (chrony)](../../catalog/resources/chrony-comparison.md) (explains)

_Indexed by lane(s): timing_
