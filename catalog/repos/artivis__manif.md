# manif

`repo:artivis/manif` - <https://github.com/artivis/manif>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,828 | C++ | MIT | 2026-08-05 | False | production | high |

Header-only C++11 library for Lie theory (SO2, SE2, SO3, SE3, SE_2(3) and more) with Jacobians, built around Sola's micro Lie theory paper; Python bindings available.

**Why it matters:** Correct on-manifold Jacobians for custom ESKF or factor-graph code.

**Hackathon notes:** Header-only C++; Python bindings (manifpy) via conda install -c conda-forge manifpy or pip install from a clone - there is no PyPI package. Use alongside the micro Lie theory paper.

**Concepts:** [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `lie-group`, `jacobians`, `header-only`

**Domains:** multi

## Related

- alternative_to: [Sophus](../repos/strasdat__sophus.md)
- alternative_to: [navlie](../repos/decargroup__navlie.md)

## Referenced by

- [navlie](../repos/decargroup__navlie.md) (alternative_to)
- [Sophus](../repos/strasdat__sophus.md) (alternative_to)
- [liegroups (Python)](../repos/utiasstars__liegroups.md) (alternative_to)
- [A micro Lie theory for state estimation in robotics](../resources/sola-micro-lie-theory.md) (has_code)
- [Quaternion kinematics for the error-state Kalman filter](../resources/sola-quaternion-kinematics-eskf.md) (same_author)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
