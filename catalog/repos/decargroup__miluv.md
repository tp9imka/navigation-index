# MILUV devkit

`repo:decargroup/miluv` - <https://github.com/decargroup/miluv>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 32 | Python | MIT | 2026-07-27 | False | active-research | medium |

Python devkit for MILUV, a multi-UAV indoor localization dataset with UWB ranging (including inter-robot), vision and IMU data.

**Why it matters:** UWB plus vision data with multiple vehicles, for relative and indoor localization.

**Build notes:** Download the dataset via devkit scripts; examples include UWB EKF.

## Deep dives

- [miluv](../../docs/dataset-cards/miluv.md) (dataset-cards)

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `uwb`, `multi-uav`, `dataset`, `indoor`

**Domains:** air

## Related

- alternative_to: [UTIL UWB TDoA dataset tools](../../catalog/repos/williamwenda__uwb_tdoa_dataset.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Wider innovation scan: ten algorithmic directions for a 48h navigation POC](../../docs/research/innovation-prior-art/04-wider-innovation-scan.md) (mentions)
- [UWB drone dataset (TIERS)](../../catalog/repos/tiers__uwb-drone-dataset.md) (alternative_to)
- [MILUV: A Multi-UAV Indoor Localization dataset with UWB and Vision](../../catalog/resources/miluv-dataset-2025.md) (has_code)
- [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md) (explains)
- [Cooperative localization on real UWB: MILUV drones through the swarm-coop filters](../../catalog/samples/swarm-coop-real-uwb.md) (uses)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-09._
