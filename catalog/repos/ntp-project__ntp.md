# NTP reference implementation (ntpd)

`repo:ntp-project/ntp` - <https://github.com/ntp-project/ntp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 197 | C | NOASSERTION | 2026-08-27 | False | production | low |

The Network Time Foundation's reference implementation of NTPv4 (ntpd, ntpq, ntpdate and refclock drivers).

**Why it matters:** The baseline that NTP attack papers were written against; useful to reproduce published time-shifting attacks in a lab.

**Hackathon notes:** Mostly a reference for behaviour comparisons; prefer chrony or ntpd-rs for new builds.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `ntp`, `ntpd`, `reference-implementation`

**Domains:** multi

## Related

- alternative_to: [NTPsec](../repos/gitlab.com__ntpsec__ntpsec.md)

## Referenced by

- [NTPsec](../repos/gitlab.com__ntpsec__ntpsec.md) (fork_of)
- [Attacking the Network Time Protocol](../resources/malhotra-2016-attacking-ntp.md) (evaluates)
- [RFC 5905: Network Time Protocol Version 4: Protocol and Algorithms Specification](../resources/rfc5905-ntpv4.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
