# gf_orb_slam2 (Good Feature / Good Graph)

`repo:ivalab/gf_orb_slam2` - <https://github.com/ivalab/gf_orb_slam2>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 261 | C++ | NOASSERTION | 2025-05-09 | False | research-prototype | low |

ORB-SLAM2 fork from Georgia Tech IVALab with good-feature selection and the budget-aware Good Graph local bundle adjustment.

**Why it matters:** Reference code for anticipating estimation needs and capping compute per step in visual SLAM. GPL-3.0 (inherited from ORB-SLAM2; GitHub reports NOASSERTION, LICENSE.txt points to License-gpl.txt), so not for a closed product.

**Build notes:** Heavy ORB-SLAM2-era build; not run here. Read for the budget logic only.

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `orb-slam2`, `budget-aware`, `bundle-adjustment`, `c++`, `ros`

**Domains:** ground, air

## Related

- integrates_with: [Good Graph to Optimize: Cost-Effective, Budget-Aware Bundle Adjustment in Visual SLAM](../../catalog/resources/zhao-2020-good-graph-budget-ba.md)
- fork_of: [ORB-SLAM2](../../catalog/repos/raulmur__orb_slam2.md)

## Referenced by

- [Good Graph to Optimize: Cost-Effective, Budget-Aware Bundle Adjustment in Visual SLAM](../../catalog/resources/zhao-2020-good-graph-budget-ba.md) (has_code)

_Indexed by lane(s): innovation-pa-scheduling_

_GitHub metadata fetched 2026-11-09._
