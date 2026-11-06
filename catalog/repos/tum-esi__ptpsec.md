# PTPsec

`repo:tum-esi/ptpsec` - <https://github.com/tum-esi/ptpsec>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | C | MIT | 2025-04-16 | False | research-prototype | medium |

Research implementation, based on linuxptp 3.1.1, that detects and mitigates PTP time-delay attacks by checking path asymmetry around cyclic redundant paths; includes a DPDK man-in-the-middle delay attacker for testing.

**Why it matters:** Shows how to defend the network time path, the part a GNSS-vs-PTP cross-check silently trusts.

**Hackathon notes:** Needs two NICs with hardware timestamping per node and DPDK for the attacker; plan a day of setup. The detection idea can be reproduced in software on logged offsets.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `ptp`, `security`, `delay-attack`, `asymmetry`, `linuxptp`, `dpdk`

**Domains:** multi

## Related

- extends: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [linuxptp](../../catalog/repos/nwtime__linuxptp.md) (extends)
- [PTPsec: Securing the Precision Time Protocol Against Time Delay Attacks Using Cyclic Path Asymmetry Analysis](../../catalog/resources/finkenzeller-2024-ptpsec.md) (has_code)
- [Securing the Precision Time Protocol with SDN-enabled Cyclic Path Asymmetry Analysis](../../catalog/resources/finkenzeller-2025-ptpsec-sdn.md) (has_code)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md) (explains)
- [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
