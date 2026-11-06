# linuxptp-daemon (OpenShift)

`repo:openshift/linuxptp-daemon` - <https://github.com/openshift/linuxptp-daemon>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 30 | Go | Apache-2.0 | 2026-11-06 | False | production | medium |

Kubernetes DaemonSet that manages ptp4l, phc2sys, ts2phc and timemaster per node, parses their logs into clock-state events, and for u-blox GNSS grandmasters treats a UBX-NAV-STATUS spoofing flag as GNSS loss.

**Why it matters:** Production code that already wires GNSS spoofing detection into PTP grandmaster state - a concrete reference for clock-state handling and holdover.

**Hackathon notes:** Read pkg/parser and the ts2phc monitoring code for log parsing and state machines; reuse the regexes to parse your own ptp4l logs. Running it needs OpenShift and E810-class NICs.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `ptp`, `linuxptp`, `kubernetes`, `telco`, `ts2phc`, `u-blox`, `spoofing-flag`

**Domains:** multi

## Related

- depends_on: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
