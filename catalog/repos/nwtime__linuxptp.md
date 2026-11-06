# linuxptp

`repo:nwtime/linuxptp` - <https://github.com/nwtime/linuxptp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 43 | C | GPL-2.0 | 2026-08-09 | False | production | high |

The standard Linux implementation of IEEE 1588 PTP: ptp4l (boundary/ordinary/transparent clock), phc2sys (sync system clock to a NIC hardware clock), ts2phc (discipline a PHC from 1PPS + NMEA), pmc for management queries, and timemaster. richardcochran/linuxptp on GitHub carries the same tree.

**Why it matters:** If a hackathon build needs sub-microsecond time across several computers (sensor nodes, TDOA receivers, a radar array), this is the off-the-shelf way to get it on Linux with hardware timestamping.

**Hackathon notes:** apt install linuxptp. Needs NICs with hardware timestamping (check `ethtool -T`); Raspberry Pi CM4/CM5 and Intel i210/i225 work. Use ts2phc with a GNSS 1PPS to build a grandmaster, ptp4l -S for software timestamping in a demo. Log `pmc` offsets to show holdover and attack behaviour.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [nwtime__linuxptp](../../docs/integration-cards/nwtime__linuxptp.md) (integration-cards)

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `ptp`, `ieee-1588`, `ptp4l`, `phc2sys`, `ts2phc`, `hardware-timestamping`, `linux`

**Domains:** multi

## Related

- integrates_with: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- alternative_to: [Statime](../../catalog/repos/pendulum-project__statime.md)
- alternative_to: [PTPd](../../catalog/repos/ptpd__ptpd.md)
- extends: [PTPsec](../../catalog/repos/tum-esi__ptpsec.md)
- integrates_with: [SatPulse](../../catalog/repos/jclark__satpulse.md)
- integrates_with: [Meta Time libraries](../../catalog/repos/meta__time.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Time Pi](../../catalog/repos/geerlingguy__time-pi.md) (depends_on)
- [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) (integrates_with)
- [PPSi](../../catalog/repos/gitlab.com__ohwr__project__ppsi.md) (alternative_to)
- [SatPulse](../../catalog/repos/jclark__satpulse.md) (integrates_with)
- [Meta Time libraries](../../catalog/repos/meta__time.md) (integrates_with)
- [clknetsim](../../catalog/repos/mlichvar__clknetsim.md) (integrates_with)
- [Statime](../../catalog/repos/pendulum-project__statime.md) (alternative_to)
- [PTPd](../../catalog/repos/ptpd__ptpd.md) (alternative_to)
- [GPSDO PTP Master](../../catalog/repos/rjrouquette__gpsdo.md) (integrates_with)
- [PTPsec](../../catalog/repos/tum-esi__ptpsec.md) (extends)
- [IEEE 1588-2019: IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems](../../catalog/resources/ieee-1588-2019.md) (has_code)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
