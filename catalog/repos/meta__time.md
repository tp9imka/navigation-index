# Meta Time libraries

`repo:meta/time` - <https://github.com/meta/time>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 680 | Go | Apache-2.0 | 2026-11-02 | False | production | medium |

Meta's Go libraries and tools for NTP and PTP: protocol implementations, PTP hardware clock and timestamping helpers, a PTP server (ptp4u), the simple-PTP client sptp, ptpcheck/ntpcheck diagnostics, a Calnex API client, leap-second utilities and the oscillatord monitoring protocol. Formerly facebook/time.

**Why it matters:** Production code from a large-scale PTP deployment, including tools to inspect PTP clients and to monitor time cards.

**Hackathon notes:** Go build; `ptpcheck` and `ntpcheck` are the quickest wins for diagnosing a lab setup.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ptp`, `ntp`, `go`, `ptp4u`, `phc`, `monitoring`

**Domains:** multi

## Related

- integrates_with: [OCP Time Card](../../catalog/repos/time-appliances-project__time-card.md)
- integrates_with: [oscillatord](../../catalog/repos/orolia2s__oscillatord.md)
- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [linuxptp](../../catalog/repos/nwtime__linuxptp.md) (integrates_with)
- [oscillatord](../../catalog/repos/orolia2s__oscillatord.md) (integrates_with)
- [OCP Time Card](../../catalog/repos/time-appliances-project__time-card.md) (integrates_with)
- [How Precision Time Protocol is being deployed at Meta](../../catalog/resources/meta-ptp-at-meta-2022.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
