# GSV-Cities

`repo:amaralibey/gsv-cities` - <https://github.com/amaralibey/gsv-cities>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 138 | Python | ? | 2024-07-03 | False | research-prototype | medium |

Official training and evaluation code for the GSV-Cities visual place recognition dataset (about 530k street-level images of 62k+ places across many cities), including the Conv-AP aggregator and evaluation notebooks for standard VPR benchmarks.

**Why it matters:** The standard large training set for modern VPR descriptors; training without offline triplet mining makes fine-tuning on your own imagery fast.

**Hackathon notes:** Dataset is on Kaggle under CC BY-NC-ND 4.0 (research only); the code repo has no licence file. Use it to pretrain or fine-tune a descriptor, then adapt to aerial tiles. Last push 2024.

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `vpr`, `training`, `pytorch`, `street-view`

**Domains:** ground, air

## Related

- integrates_with: [MixVPR](../../catalog/repos/amaralibey__mixvpr.md)
- integrates_with: [OpenVPRLab](../../catalog/repos/amaralibey__openvprlab.md)
- integrates_with: [BoQ](../../catalog/repos/amaralibey__bag-of-queries.md)

## Referenced by

- [OpenVPRLab](../../catalog/repos/amaralibey__openvprlab.md) (depends_on)
- [GSV-Cities: Toward Appropriate Supervised Visual Place Recognition](../../catalog/resources/gsv-cities-2022.md) (has_code)

_Indexed by lane(s): backlog_

_GitHub metadata fetched 2026-11-06._
