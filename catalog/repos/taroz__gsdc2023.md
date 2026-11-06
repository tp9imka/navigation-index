# GSDC 2023 solution (taroz)

`repo:taroz/gsdc2023` - <https://github.com/taroz/gsdc2023>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 116 | MATLAB | MIT | 2025-01-15 | False | active-research | medium |

Code reproducing Taro Suzuki's Google Smartphone Decimeter Challenge 2023 entry (1st on the public leaderboard, 2nd on the private one), using factor graph optimization of smartphone GNSS and IMU in MATLAB.

**Why it matters:** Shows what state-of-the-art smartphone positioning looks like on a public benchmark.

**Hackathon notes:** MATLAB required. Read it for the pipeline design even if you reimplement in Python.

## Deep dives

- [gsdc](../../docs/dataset-cards/gsdc.md) (dataset-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [GNSS/INS integration](../../catalog/concepts/gnss-ins.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md)

**Tags:** `gsdc`, `smartphone`, `matlab`, `factor-graph`, `kaggle`

**Domains:** ground, dismounted

## Related

- same_org: [gtsam_gnss](../../catalog/repos/taroz__gtsam_gnss.md)
- evaluated_on: [GPS Measurement Tools (incl. GnssLogger)](../../catalog/repos/google__gps-measurement-tools.md)
- integrates_with: [GPS Measurement Tools (incl. GnssLogger)](../../catalog/repos/google__gps-measurement-tools.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [ML GNSS/IMU integration (GSDC 2022)](../../catalog/repos/akpozi__machine_learning_gnss_imu_integration.md) (alternative_to)
- [Smartphone Decimeter Challenge MATLAB package](../../catalog/repos/arnauochoa__smartphone-decimeter-challenge.md) (alternative_to)
- [GSDC 10th place solution](../../catalog/repos/fkaneko__kaggle_google_smartphone_decimeter_challenge.md) (alternative_to)
- [GPS Measurement Tools (incl. GnssLogger)](../../catalog/repos/google__gps-measurement-tools.md) (integrates_with)
- [MatRTKLIB](../../catalog/repos/taroz__matrtklib.md) (same_org)
- [Google Smartphone Decimeter Challenge 2023-2024](../../catalog/resources/google-gsdc-2023.md) (has_code)
- [ION Smartphone Decimeter Challenge (with Google)](../../catalog/resources/ion-smartphone-decimeter-challenge.md) (has_code)

_Indexed by lane(s): gnss, sim-data_

_GitHub metadata fetched 2026-11-06._
