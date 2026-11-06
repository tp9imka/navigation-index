# UWB Software Library (USL)

`repo:vladniculescu/uwb-software-library` - <https://github.com/vladniculescu/uwb-software-library>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3 | C | ? | 2024-06-29 | False | research-prototype | medium |

FreeRTOS UWB library for DW1000 on Crazyflie providing double-sided two-way ranging and UWB data messaging between drones.

**Why it matters:** Peer-to-peer ranging building block for anchor-free relative localization.

**Hackathon notes:** Flash as Crazyflie app; ranging between two nodes in a few lines. Fork of iGNSS/uwb-software-library, tested against a pinned crazyflie-firmware commit. No LICENSE file, so all rights reserved by default.

**Concepts:** [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `uwb`, `dw1000`, `twr`, `crazyflie`

**Domains:** air, multi

## Related

- integrates_with: [Swarm relative localization (ETH PBL)](../../catalog/repos/eth-pbl__swarm-relative-localization.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Swarm relative localization (ETH PBL)](../../catalog/repos/eth-pbl__swarm-relative-localization.md) (depends_on)
- [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
