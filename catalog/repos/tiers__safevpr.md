# SafeVPR

`repo:tiers/safevpr` - <https://github.com/TIERS/SafeVPR>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 5 | Python | MIT | 2026-11-05 | False | active-research | high |

Accept/abstain verifier for place-recognition matches: DINOv2 patch-agreement score plus Mondrian conformal threshold calibration with an FDR target.

**Why it matters:** The closest open code to calibrated acceptance of visual fixes; MIT, so it can be adapted for aerial fixes.

**Build notes:** MIT. README: `pip install -e .` then `python demo.py` runs on bundled real scores without a GPU. Swap its score for our inliers + retrieval margin on cached VPAIR candidates. Ground datasets only in the paper.

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `conformal-prediction`, `vpr`, `dinov2`, `python`

**Domains:** multi

## Referenced by

- [SAFEVPR: Patch-Based Verification with Empirical FDR Control for Cross-Condition Sequence Visual Place Recognition](../../catalog/resources/sier-2026-safevpr-empirical-fdr-vpr.md) (has_code)

_Indexed by lane(s): innovation-pa-wider_

_GitHub metadata fetched 2026-11-16._
