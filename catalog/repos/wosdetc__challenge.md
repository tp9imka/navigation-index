# Drone-vs-Bird Detection Challenge

`repo:wosdetc/challenge` - <https://github.com/wosdetc/challenge>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 72 | Python | ? | 2022-12-16 | False | archived | high |

Repository of the long-running Drone-vs-Bird challenge: annotations and instructions for a video dataset of small drones with birds as distractors.

**Why it matters:** Telling a distant drone from a bird is the core false-alarm problem in camera-based C-UAS; this is the reference benchmark.

**Hackathon notes:** Videos only on request (wosdetc@googlegroups.com) after signing a data usage agreement, research use only - allow lead time. Then train a small-object YOLO; the hard part is tiny targets, so tile the frames. Repo not updated since 2022-12 (2023 edition is the last listed).

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Tracking and data association](../concepts/target-tracking.md)

**Tags:** `drone-vs-bird`, `video`, `detection`, `c-uas`

**Domains:** air

## Related

- alternative_to: [Anti-UAV](../repos/zhaoj9014__anti-uav.md)
- alternative_to: [Drone detection dataset (IR, visible, audio)](../repos/dronedetectionthesis__drone-detection-dataset.md)

## Referenced by

- [Drone detection dataset (IR, visible, audio)](../repos/dronedetectionthesis__drone-detection-dataset.md) (alternative_to)
- [NRC UAV vs bird radar tracks](../repos/nrc-cnrc__cuas-sensing-dataset.md) (alternative_to)
- [Improving Small Drone Detection Through Multi-Scale Processing and Data Augmentation](../resources/drone-vs-bird-2025-multiscale.md) (evaluates)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
