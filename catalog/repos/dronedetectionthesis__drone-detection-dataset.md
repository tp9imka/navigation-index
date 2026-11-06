# Drone detection dataset (IR, visible, audio)

`repo:dronedetectionthesis/drone-detection-dataset` - <https://github.com/DroneDetectionThesis/Drone-detection-dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 343 | MATLAB | CC0-1.0 | 2026-04-26 | False | research-prototype | high |

Multi-sensor dataset from a Swedish thesis: 650 infrared and visible videos (airplane, bird, drone, helicopter; 203k labelled frames) plus 90 audio clips (drone, helicopter, background).

**Why it matters:** Lets a team prototype sensor fusion for C-UAS (thermal + RGB + audio) on one consistent set of targets and distractors.

**Hackathon notes:** Data sits in the repo (~360 MB, no LFS), CC0. Labels are MATLAB groundTruth .mat files that scipy cannot read; use pip install mcos-decoder in Python. Good for a fused IR+audio classifier demo in a weekend.

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `infrared`, `audio`, `multi-sensor`, `c-uas`

**Domains:** air

## Related

- alternative_to: [Drone-vs-Bird Detection Challenge](../repos/wosdetc__challenge.md)

## Referenced by

- [MMC-UAV dataset](../repos/chance1911__mmc-uav-dataset.md) (alternative_to)
- [Drone-vs-Bird Detection Challenge](../repos/wosdetc__challenge.md) (alternative_to)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
