# ROVIO

`repo:ethz-asl/rovio` - <https://github.com/ethz-asl/rovio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,272 | C++ | NOASSERTION | 2026-09-03 | False | research-prototype | medium |

Robust visual-inertial odometry using an iterated EKF directly on image-patch photometric errors.

**Why it matters:** Long a go-to VIO on PX4/MAV research platforms because it is cheap to run.

**Hackathon notes:** ROS 1 / catkin. Lightweight; tuning of patch and feature counts matters.

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `iekf`, `patch-based`, `ros1`

**Domains:** air

## Related

- extends: [ROVTIO](../repos/ntnu-arl__rovtio.md)

## Referenced by

- [ethzasl_msf (Multi Sensor Fusion)](../repos/ethz-asl__ethzasl_msf.md) (same_org)
- [ROVTIO](../repos/ntnu-arl__rovtio.md) (extends)
- [SVO Pro](../repos/uzh-rpg__rpg_svo_pro_open.md) (alternative_to)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
