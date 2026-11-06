# EqNIO

`repo:royinajayanth/eqnio` - <https://github.com/RoyinaJayanth/EqNIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 42 | Python | ? | 2026-02-15 | False | active-research | low |

Subequivariant neural inertial odometry (ICLR 2025) that canonicalises IMU data so networks generalise across orientations; applied on top of TLIO and RoNIN.

**Why it matters:** State of the art learned inertial odometry with released code.

**Hackathon notes:** Repo vendors modified TLIO (TLIO-master/) and RoNIN code, so no separate setup; get the TLIO dataset (CC BY-NC) or RoNIN data (non-commercial licence) first. No licence file in the repo, so the code is all rights reserved.

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial`, `equivariance`

**Domains:** dismounted

## Related

- extends: [TLIO](../../catalog/repos/cathias__tlio.md)
- evaluated_on: [RoNIN](../../catalog/repos/sachini__ronin.md)

## Referenced by

- [TLIO](../../catalog/repos/cathias__tlio.md) (extends)
- [RoNIN](../../catalog/repos/sachini__ronin.md) (evaluated_on)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
