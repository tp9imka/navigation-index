# SatPulse

`repo:jclark/satpulse` - <https://github.com/jclark/satpulse>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 70 | Go | MIT | 2026-11-02 | False | production | high |

Software for using a GNSS receiver on a computer for precise time: stratum-1 NTP with chrony, ntpd-rs or NTPsec, a PTP grandmaster on Raspberry Pi CM4/CM5 or Intel NICs via linuxptp, RTK base/rover, and a web GUI to configure and monitor receivers.

**Why it matters:** The shortest path from a GNSS timing receiver to a working NTP/PTP time server with monitoring, on cheap hardware.

**Hackathon notes:** Install on a Pi CM4/CM5 with a u-blox timing receiver; follow satpulse.net. The GUI makes receiver state visible during a jamming or spoofing demo.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [jclark__satpulse](../../docs/integration-cards/jclark__satpulse.md) (integration-cards)

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `gnss`, `pps`, `ntp`, `ptp`, `grandmaster`, `raspberry-pi`

**Domains:** multi

## Related

- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- integrates_with: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- alternative_to: [Time Pi](../../catalog/repos/geerlingguy__time-pi.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Time Pi](../../catalog/repos/geerlingguy__time-pi.md) (alternative_to)
- [GNSSTimeServer](../../catalog/repos/montecri__gnsstimeserver.md) (alternative_to)
- [linuxptp](../../catalog/repos/nwtime__linuxptp.md) (integrates_with)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
