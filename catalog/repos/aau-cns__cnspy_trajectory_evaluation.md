# cnspy trajectory evaluation

`repo:aau-cns/cnspy_trajectory_evaluation` - <https://github.com/aau-cns/cnspy_trajectory_evaluation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 8 | Python | GPL-3.0 | 2024-09-10 | False | active-research | medium |

Python package that aligns an estimated trajectory with ground truth from CSV files, associates timestamps and reports position/attitude error metrics, including NEES from pose covariance.

**Why it matters:** Consistency checks (NEES) matter as much as RMSE when judging a GNSS-denied filter; this tool computes both from plain CSV.

**Hackathon notes:** pip install cnspy-trajectory-evaluation; estimated CSV must carry pose covariance. Use evo for quick plots, this when you need filter consistency.

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `ate`, `rpe`, `nees`, `evaluation`, `python`

**Domains:** multi

## Related

- alternative_to: [evo](../repos/michaelgrupp__evo.md)
- alternative_to: [rpg_trajectory_evaluation](../repos/uzh-rpg__rpg_trajectory_evaluation.md)

## Referenced by

- [MaRS (Modular and Robust Sensor-Fusion)](../repos/aau-cns__mars_lib.md) (same_org)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
