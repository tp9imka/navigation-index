# Sample: Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor

`sample:swarm-coop-localization` - code and walkthrough in [samples/swarm-coop-localization](../../samples/swarm-coop-localization/)

A stdlib-only simulation of six vehicles with biased odometry where only two keep GNSS. Inter-agent UWB two-way ranging has dropouts, Markov NLOS episodes and gross outliers; optional camera bearings; a lossy, range-limited mesh with a TDMA slot budget. It compares independent dead reckoning, a centralized 24-state EKF at a fusion centre (multi-hop uplink), a naive decentralized filter that ignores cross-correlation, and decentralized covariance intersection, each with plain or robust (gate + Huber + NLOS-aware) ranging. It reports per-agent error over time, NEES and bytes per second, then spoofs one anchor's GNSS with a slow walk-off and shows how far the error propagates with no check, a per-fix gate, peer range votes and solution separation (centralized sub-filters and a distributed per-anchor filter bank).

**Verification:** ran with python3.14.7 stdlib on 2026-11-06: nominal and spoof scenarios, each range-only and with bearings (seed 1), and 10-seed Monte Carlo for all four; outputs saved in out/ and pasted in README. 20 unittest tests pass; mutations (SS gate disabled, robust weighting disabled) make the detection and robust-ranging tests fail. Synthetic data only: NLOS, comms and odometry models are stated assumptions, no UWB dataset or hardware was used, and none of the related repos was run.

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `cooperative-localization`, `uwb`, `two-way-ranging`, `nlos`, `huber`, `innovation-gate`, `covariance-intersection`, `decentralized-estimation`, `ekf`, `swarm`, `spoofing`, `solution-separation`, `integrity`, `communication-cost`, `stdlib`

## Related

- explains: [Swarm relative localization (ETH PBL)](../../catalog/repos/eth-pbl__swarm-relative-localization.md)
- explains: [Onboard Ranging-based Relative Localization and Stability for Lightweight Aerial Swarms](../../catalog/resources/li-onboard-relative-localization-swarms.md)
- explains: [uwb-localization (MAV swarm)](../../catalog/repos/lijx10__uwb-localization.md)
- explains: [Omni-swarm](../../catalog/repos/hkust-aerial-robotics__omni-swarm.md)
- explains: [CoLRIO](../../catalog/repos/pengyu-team__co-lrio.md)
- explains: [UWB Software Library (USL)](../../catalog/repos/vladniculescu__uwb-software-library.md)
- explains: [MILUV devkit](../../catalog/repos/decargroup__miluv.md)
- explains: [UTIL: An Ultra-wideband Time-difference-of-arrival Indoor Localization Dataset](../../catalog/resources/util-uwb-dataset.md)
- explains: [Cooperative Localization for GNSS-Denied Subterranean Navigation: A UAV-UGV Team Approach](../../catalog/resources/ion-webinar-gross.md)
- explains: [Martin Saska - Onboard relative localization for agile aerial swarming in the wild (RSS 2024 Aerial Swarms workshop slides)](../../catalog/resources/saska-rss-2024-aerial-swarms.md)
- explains: [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Cooperative localization on real UWB: MILUV drones through the swarm-coop filters](../../catalog/samples/swarm-coop-real-uwb.md) (uses)

_Indexed by lane(s): samples_
