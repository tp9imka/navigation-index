# Predicting to Improve: Integrity Measures for Assessing Visual Localization Performance

`res:carson-2022-predicting-to-improve-vpr-integrity` - paper - <https://eprints.qut.edu.au/234489/>

**By:** Helen Carson, Jason J. Ford, Michael Milford - **Year:** 2022 - **Level:** intermediate - **Access:** paywalled

IEEE Robotics and Automation Letters 7(4):9627-9634 (doi 10.1109/LRA.2022.3191205). Supervised, technique-agnostic per-frame predictor of whether a VPR estimate is correct, built from signals of the VPR technique itself; used to discard bad estimates. Reports 74 % average precision over 12 dataset/technique combinations. Abstract only read.

## Key takeaways

- Predicts VPR success per frame after retrieval has run
- Not used to decide whether to spend the expensive matching step
- MIT code with a Nordland example

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `vpr`, `integrity`, `failure-prediction`, `introspection`

## Related

- has_code: [predict2improve](../../catalog/repos/qvpr__predict2improve.md)

## Referenced by

- [predict2improve](../../catalog/repos/qvpr__predict2improve.md) (integrates_with)
- [Unsupervised Quality Prediction for Improved Single-Frame and Weighted Sequential Visual Place Recognition](../../catalog/resources/carson-2023-unsupervised-quality-prediction-vpr.md) (same_author)

_Indexed by lane(s): innovation-pa-scheduling_
