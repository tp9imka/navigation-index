# ML-CasADi

`repo:tum-aas/ml-casadi` - <https://github.com/TUM-AAS/ml-casadi>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 254 | Python | MIT | 2023-11-01 | False | research-prototype | medium |

Bridges PyTorch models into CasADi and acados so a neural network can be part of the MPC prediction model, using local approximations for real-time use.

**Why it matters:** Lets a team plug a learned aerodynamics or propulsion residual into an MPC without rewriting the network in CasADi.

**Build notes:** License MIT (gh api). Last push 2023-11-01. pip-installable per its README (not run here). Only worth it if the team has a residual model to learn from logs; otherwise a physics model is the honest baseline.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `neural-mpc`, `pytorch`, `casadi`, `acados`, `python`, `mit`

**Domains:** air, multi

## Related

- integrates_with: [acados](../../catalog/repos/acados__acados.md)
- depends_on: [CasADi](../../catalog/repos/casadi__casadi.md)
- alternative_to: [Data-Driven MPC for Quadrotors](../../catalog/repos/uzh-rpg__data_driven_mpc.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [acados](../../catalog/repos/acados__acados.md) (integrates_with)
- [Data-Driven MPC for Quadrotors](../../catalog/repos/uzh-rpg__data_driven_mpc.md) (alternative_to)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-23._
