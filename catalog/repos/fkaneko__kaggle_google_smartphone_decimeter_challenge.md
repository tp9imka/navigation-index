# GSDC 10th place solution

`repo:fkaneko/kaggle_google_smartphone_decimeter_challenge` - <https://github.com/Fkaneko/kaggle_Google_Smartphone_Decimeter_Challenge>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 30 | Python | Apache-2.0 | 2022-05-06 | False | archived | low |

10th-place solution for the Kaggle Google Smartphone Decimeter Challenge.

**Why it matters:** Readable Kaggle-style pipeline for smartphone GNSS post-processing.

**Hackathon notes:** Apache-2.0 code; GSDC data is under Kaggle competition rules (not checked). Denoises host-baseline positions (STFT + CNN, LightGBM on IMU) and snaps to training ground truth with KNN, so it relies on repeated routes. Private score about 2.61 m.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md)

**Tags:** `kaggle`, `gsdc`, `smartphone`

**Domains:** ground

## Related

- alternative_to: [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
