# SAFEVPR: Patch-Based Verification with Empirical FDR Control for Cross-Condition Sequence Visual Place Recognition

`res:sier-2026-safevpr-empirical-fdr-vpr` - paper - <https://arxiv.org/abs/2605.28048>

**By:** Ha Sier, Jiaqiang Zhang, Zhuo Zou, Xianjia Yu, Tomi Westerlund - **Year:** 2026 - **Level:** advanced - **Access:** open

Training-free accept/abstain decision for place-recognition matches: a frozen DINOv2 patch-agreement score with Mondrian (score-binned) Learn-Then-Test calibration of accept thresholds. Targets a false-discovery rate on conditions not seen in calibration. Ground-vehicle datasets only.

## Key takeaways

- README claim: target FDR held on 23/23 held-out cross-condition setups at alpha 0.10
- README claim: 29.6x fewer wrong loop closures, median trajectory error 95.5 m => 9.7 m
- README says the control is empirical, not a formal guarantee under arbitrary shift
- arXiv comment: accepted to RA-L; MIT code with a no-GPU demo

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `conformal-prediction`, `vpr`, `false-discovery-rate`, `dinov2`, `innovation-scan`

## Related

- has_code: [SafeVPR](../../catalog/repos/tiers__safevpr.md)

## Referenced by

- [Wider innovation scan: ten algorithmic directions for a 48h navigation POC](../../docs/research/innovation-prior-art/04-wider-innovation-scan.md) (mentions)

_Indexed by lane(s): innovation-pa-wider_
