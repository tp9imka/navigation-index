# SymForce

`repo:symforce-org/symforce` - <https://github.com/symforce-org/symforce>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,657 | C++ | Apache-2.0 | 2026-10-30 | False | production | medium |

Symbolic computation and code generation library with a fast sparse nonlinear least-squares optimizer, from Skydio, which says it uses it in production for SLAM, calibration and MPC.

**Why it matters:** Lets a team write a custom measurement model (drag force, rotor thrust, learned velocity) once symbolically and get optimized C++/Python residuals and Jacobians, avoiding hand-derived Jacobian bugs under time pressure.

**Build notes:** Apache-2.0, pip install symforce. Learning curve is real; worth it only if the team writes new factors.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `factor-graph`, `codegen`, `symbolic`, `optimization`

**Domains:** multi

## Related

- alternative_to: [GTSAM](../../catalog/repos/borglab__gtsam.md)
- alternative_to: [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-23._
