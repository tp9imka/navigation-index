# clknetsim

`repo:mlichvar/clknetsim` - <https://github.com/mlichvar/clknetsim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 37 | C | GPL-2.0 | 2026-10-20 | False | production | medium |

Clock and network simulator from the chrony author: runs real NTP/PTP daemons against simulated clocks and network delays to test synchronization behaviour. Mirror of gitlab.com/chrony/clknetsim.

**Why it matters:** Lets a team test a time daemon's reaction to delay changes, steps or a lying server without hardware.

**Hackathon notes:** Linux only (LD_PRELOAD); the chrony test suite shows usage patterns.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `simulation`, `ntp`, `ptp`, `testing`

**Domains:** multi

## Related

- integrates_with: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- integrates_with: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) (evaluated_on)
- [ntpperf](../../catalog/repos/mlichvar__ntpperf.md) (same_org)
- [LibPTP](../../catalog/repos/ptp-sim__libptp.md) (alternative_to)
- [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
