# predict2improve

`repo:qvpr/predict2improve` - <https://github.com/QVPR/predict2improve>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2 | Jupyter Notebook | MIT | 2022-10-26 | False | research-prototype | medium |

Code for Carson, Ford and Milford's RA-L 2022 paper on predicting per-frame visual localization integrity. A Jupyter notebook runs the predictor on precomputed Nordland features.

**Why it matters:** A ready per-frame VPR success predictor; a fix scheduler can reuse the idea to estimate success probability before paying for fine matching. MIT license.

**Build notes:** README only: run `jupyter lab example.ipynb` with the linked Nordland feature set. Last push 2022-10. Retrain on VPAIR retrieval scores rather than reusing the Nordland model; not run here.

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `vpr`, `integrity`, `failure-prediction`, `jupyter`

**Domains:** multi

## Related

- integrates_with: [Predicting to Improve: Integrity Measures for Assessing Visual Localization Performance](../../catalog/resources/carson-2022-predicting-to-improve-vpr-integrity.md)

## Referenced by

- [Predicting to Improve: Integrity Measures for Assessing Visual Localization Performance](../../catalog/resources/carson-2022-predicting-to-improve-vpr-integrity.md) (has_code)

_Indexed by lane(s): innovation-pa-scheduling_

_GitHub metadata fetched 2026-11-09._
