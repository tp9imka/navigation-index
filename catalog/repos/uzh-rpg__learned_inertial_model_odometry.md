# Learned Inertial Odometry for Drone Racing

`repo:uzh-rpg/learned_inertial_model_odometry` - <https://github.com/uzh-rpg/learned_inertial_model_odometry>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 280 | Python | GPL-3.0 | 2023-09-19 | False | research-prototype | low |

UZH RPG code fusing a learned inertial displacement model with an EKF for drone racing state estimation.

**Why it matters:** Shows learned IO on aggressive UAV flight.

**Hackathon notes:** Research code; trained and tested on the MIT Blackbird dataset (converter script, one sample sequence and the trained network are in the repo). Reuses TLIO filter code.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `learned-inertial`, `drone-racing`, `ekf`

**Domains:** air

## Related

- alternative_to: [AirIO](../../catalog/repos/air-io__air-io.md)

## Referenced by

- [AirIO](../../catalog/repos/air-io__air-io.md) (alternative_to)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
