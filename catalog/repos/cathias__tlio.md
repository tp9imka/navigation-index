# TLIO

`repo:cathias/tlio` - <https://github.com/CathIAS/TLIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 414 | Python | NOASSERTION | 2023-08-08 | False | research-prototype | medium |

Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.

**Why it matters:** Strong blueprint for combining a learned motion prior with a classical filter.

**Hackathon notes:** Training data is head-mounted; expect domain gap on other platforms. The released dataset is CC BY-NC (non-commercial); the code is BSD-licensed.

## Deep dives

- [tlio-paper](../../docs/paper-digests/tlio-paper.md) (paper-digests)

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial`, `ekf`, `pytorch`

**Domains:** dismounted

## Related

- alternative_to: [RoNIN](../../catalog/repos/sachini__ronin.md)
- extends: [EqNIO](../../catalog/repos/royinajayanth__eqnio.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [RIDI](../../catalog/repos/higerra__ridi_imu.md) (alternative_to)
- [EqNIO](../../catalog/repos/royinajayanth__eqnio.md) (extends)
- [RoNIN](../../catalog/repos/sachini__ronin.md) (alternative_to)
- [TLIO: Tight Learned Inertial Odometry](../../catalog/resources/tlio-paper.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
