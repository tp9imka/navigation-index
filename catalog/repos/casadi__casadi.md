# CasADi

`repo:casadi/casadi` - <https://github.com/casadi/casadi>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2,332 | C++ | LGPL-3.0 | 2026-11-07 | False | production | high |

Symbolic framework for numerical optimisation with automatic differentiation, interfaces to IPOPT and other solvers, and C code generation. Used from Python, C++, MATLAB and Julia.

**Why it matters:** The modelling layer for nearly every open trajectory-optimisation and MPC prototype; pip-installable, so a team can write an optimal-control problem in an hour.

**Build notes:** License LGPL-3.0 (gh api): usable in a commercial product if linked dynamically and modifications to CasADi itself are shared; check with legal before static linking. Last push 2026-11-07. Python wheels exist, so offline-capable once cached. Good for an offline trajectory optimiser (min-time or min-energy route over a DEM) where solve time is not critical.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `optimisation`, `automatic-differentiation`, `ipopt`, `python`, `lgpl-3.0`

**Domains:** multi

## Related

- integrates_with: [acados](../../catalog/repos/acados__acados.md)
- integrates_with: [do-mpc](../../catalog/repos/do-mpc__do-mpc.md)
- integrates_with: [AeroSandbox](../../catalog/repos/peterdsharpe__aerosandbox.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [acados](../../catalog/repos/acados__acados.md) (depends_on)
- [do-mpc](../../catalog/repos/do-mpc__do-mpc.md) (depends_on)
- [PANTHER](../../catalog/repos/mit-acl__panther.md) (depends_on)
- [AeroSandbox](../../catalog/repos/peterdsharpe__aerosandbox.md) (depends_on)
- [ML-CasADi](../../catalog/repos/tum-aas__ml-casadi.md) (depends_on)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
