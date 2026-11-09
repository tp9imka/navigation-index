# Object Pose Estimation with Statistical Guarantees: Conformal Keypoint Detection and Geometric Uncertainty Propagation

`res:yang-pavone-2023-conformal-keypoint-pose` - paper - <https://arxiv.org/abs/2303.12246>

**By:** Heng Yang, Marco Pavone - **Year:** 2023 - **Level:** advanced - **Access:** open

CVPR 2023. Uses inductive conformal prediction to turn learned keypoint heatmaps into prediction sets with a chosen coverage, then propagates those sets into a pose uncertainty set. The template for giving a learned geometric measurement a coverage-calibrated error region before it reaches a filter.

## Key takeaways

- Peer-reviewed (CVPR 2023); abstract read, full text not read
- Calibration set of a few hundred labelled images is enough per the precursor paper's abstract
- Code repo has no license file: read only

**Concepts:** [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `conformal-prediction`, `uncertainty`, `pose-estimation`, `innovation-scan`

## Related

- has_code: [ConformalKeypoint](../../catalog/repos/nvlabs__conformalkeypoint.md)

## Referenced by

- [Wider innovation scan: ten algorithmic directions for a 48h navigation POC](../../docs/research/innovation-prior-art/04-wider-innovation-scan.md) (mentions)

_Indexed by lane(s): innovation-pa-wider_
