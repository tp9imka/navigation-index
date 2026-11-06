# Swarm relative localization (ETH PBL)

`repo:eth-pbl/swarm-relative-localization` - <https://github.com/ETH-PBL/swarm-relative-localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | GPL-3.0 | 2024-03-25 | False | research-prototype | medium |

Infrastructure-less relative localization for decentralized swarm formation of nano-drones using UWB ranging (IROS 2023).

**Why it matters:** Relative positioning without anchors, the realistic case for field swarms.

**Hackathon notes:** The repo holds only a Python demo of the algorithm (demo.py) and a PDF supplement; no Crazyflie or UWB firmware is included.

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `uwb`, `relative-localization`, `crazyflie`, `nano-drone`

**Domains:** air, multi

## Related

- depends_on: [UWB Software Library (USL)](../../catalog/repos/vladniculescu__uwb-software-library.md)
- extends: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [GEARdrones](../../catalog/repos/excitablecell__geardrones.md) (alternative_to)
- [UWB Software Library (USL)](../../catalog/repos/vladniculescu__uwb-software-library.md) (integrates_with)
- [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
