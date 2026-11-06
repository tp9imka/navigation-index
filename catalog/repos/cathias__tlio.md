# TLIO

`repo:cathias/tlio` - <https://github.com/CathIAS/TLIO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 414 | Python | NOASSERTION | 2023-08-08 | False | research-prototype | medium |

Tight Learned Inertial Odometry: a network regresses displacement and uncertainty from IMU windows, fused in a stochastic-cloning EKF.

**Why it matters:** Strong blueprint for combining a learned motion prior with a classical filter.

**Hackathon notes:** Training data is head-mounted; expect domain gap on other platforms.

**Concepts:** [Indoor and pedestrian navigation](../concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Onboard / edge AI perception](../concepts/edge-ai.md)

**Tags:** `learned-inertial`, `ekf`, `pytorch`

**Domains:** dismounted

## Related

- alternative_to: [RoNIN](../repos/sachini__ronin.md)
- extends: [EqNIO](../repos/royinajayanth__eqnio.md)

## Referenced by

- [RIDI](../repos/higerra__ridi_imu.md) (alternative_to)
- [EqNIO](../repos/royinajayanth__eqnio.md) (extends)
- [RoNIN](../repos/sachini__ronin.md) (alternative_to)
- [TLIO: Tight Learned Inertial Odometry](../resources/tlio-paper.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
