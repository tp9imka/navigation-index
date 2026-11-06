# RoNIN

`repo:sachini/ronin` - <https://github.com/Sachini/ronin>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 431 | Python | GPL-3.0 | 2023-02-03 | False | research-prototype | medium |

Robust Neural Inertial Navigation: smartphone IMU dataset and baseline networks (ResNet, LSTM, TCN) regressing pedestrian velocity from IMU.

**Why it matters:** Main benchmark and baselines for learned pedestrian inertial navigation.

**Hackathon notes:** PyTorch; dataset is large and only about half of it was published (security concerns). Pretrained models give a quick baseline. The RoNIN data and pretrained models are under a custom licence for non-commercial and scientific research use only (code is GPL-3.0).

## Deep dives

- [ronin](../../docs/dataset-cards/ronin.md) (dataset-cards)

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `learned-inertial`, `smartphone`, `pytorch`

**Domains:** dismounted

## Related

- alternative_to: [TLIO](../../catalog/repos/cathias__tlio.md)
- evaluated_on: [EqNIO](../../catalog/repos/royinajayanth__eqnio.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [TLIO](../../catalog/repos/cathias__tlio.md) (alternative_to)
- [RIDI](../../catalog/repos/higerra__ridi_imu.md) (alternative_to)
- [EqNIO](../../catalog/repos/royinajayanth__eqnio.md) (evaluated_on)
- [RoNIN: Robust Neural Inertial Navigation in the Wild: Benchmark, Evaluations, and New Methods](../../catalog/resources/ronin-paper.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
