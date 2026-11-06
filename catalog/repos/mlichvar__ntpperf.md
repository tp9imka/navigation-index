# ntpperf

`repo:mlichvar/ntpperf` - <https://github.com/mlichvar/ntpperf>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 79 | C | GPL-2.0 | 2026-11-02 | False | production | low |

Load generator for NTP servers and PTP masters by chrony's author: simulates many clients with raw Ethernet frames via libpcap and reports responses, losses and, with a known direct link, how transmit timestamp accuracy degrades with rate.

**Why it matters:** Tests whether a time server stays accurate under request floods - a denial-of-service angle on timing infrastructure.

**Hackathon notes:** Needs a dedicated link and routing so responses come back to the test host. Lab tool, not demo material.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ntp`, `ptp`, `benchmark`, `load-test`, `libpcap`

**Domains:** multi

## Related

- same_org: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- same_org: [clknetsim](../../catalog/repos/mlichvar__clknetsim.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
