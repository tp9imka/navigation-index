# acados

`repo:acados/acados` - <https://github.com/acados/acados>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,519 | C | NOASSERTION | 2026-10-29 | False | production | high |

Fast embedded solvers for nonlinear optimal control and nonlinear MPC. Models are written in CasADi from Python or MATLAB, and acados generates C code with real-time iteration SQP and HPIPM QP solvers.

**Why it matters:** The de-facto open NMPC engine behind most quadrotor and fixed-wing MPC research code; the generated C code is a credible path from a laptop demo to a flight computer.

**Hackathon notes:** License BSD-2-Clause (LICENSE file read; GitHub shows NOASSERTION). Last push 2026-10-29, active. Python interface needs acados built from source plus the tera_renderer binary; plan 30-60 min the first time. Start from the bundled Python examples (pendulum, then a quadrotor model) before writing your own dynamics.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `nmpc`, `optimal-control`, `code-generation`, `embedded`, `casadi`, `bsd-2-clause`

**Domains:** air, ground, multi

## Related

- depends_on: [CasADi](../../catalog/repos/casadi__casadi.md)
- alternative_to: [do-mpc](../../catalog/repos/do-mpc__do-mpc.md)
- alternative_to: [TinyMPC](../../catalog/repos/tinympc__tinympc.md)
- integrates_with: [ML-CasADi](../../catalog/repos/tum-aas__ml-casadi.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [CasADi](../../catalog/repos/casadi__casadi.md) (integrates_with)
- [do-mpc](../../catalog/repos/do-mpc__do-mpc.md) (alternative_to)
- [IPC (Integrated Planning and Control)](../../catalog/repos/hku-mars__ipc.md) (alternative_to)
- [TinyMPC](../../catalog/repos/tinympc__tinympc.md) (alternative_to)
- [mrca-mav](../../catalog/repos/tud-amr__mrca-mav.md) (alternative_to)
- [ML-CasADi](../../catalog/repos/tum-aas__ml-casadi.md) (integrates_with)
- [Data-Driven MPC for Quadrotors](../../catalog/repos/uzh-rpg__data_driven_mpc.md) (depends_on)
- [rpg_mpc (PAMPC)](../../catalog/repos/uzh-rpg__rpg_mpc.md) (alternative_to)
- [acados: a modular open-source framework for fast embedded optimal control](../../catalog/resources/verschueren-acados-2019.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
