# TinyMPC

`repo:tinympc/tinympc` - <https://github.com/TinyMPC/TinyMPC>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,120 | C++ | MIT | 2026-09-02 | False | active-research | medium |

ADMM-based convex MPC solver small enough for microcontrollers, with Python bindings and code generation; demonstrated on a Crazyflie.

**Why it matters:** Shows MPC running on autopilot-class hardware rather than a companion computer, which answers the 'how does this run on the aircraft' question.

**Hackathon notes:** License MIT (gh api). Last push 2026-09-02. Linear (linearised) MPC only, so it suits hover / tracking around a trim, not large manoeuvres. A separate TinyMPC/tinympc-px4 repo exists (3 stars, MIT, not reviewed here).

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `mpc`, `admm`, `microcontroller`, `embedded`, `mit`

**Domains:** air

## Related

- alternative_to: [acados](../../catalog/repos/acados__acados.md)
- evaluated_on: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [acados](../../catalog/repos/acados__acados.md) (alternative_to)
- [OSQP](../../catalog/repos/osqp__osqp.md) (alternative_to)
- [TinyMPC: Model-Predictive Control on Resource-Constrained Microcontrollers](../../catalog/resources/alavilli-tinympc-2023.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
