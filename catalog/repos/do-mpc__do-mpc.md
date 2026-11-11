# do-mpc

`repo:do-mpc/do-mpc` - <https://github.com/do-mpc/do-mpc>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,481 | Python | LGPL-3.0 | 2026-09-22 | False | active-research | high |

Python toolbox for model predictive control and moving horizon estimation on top of CasADi, with templates for model, controller, estimator and simulator.

**Why it matters:** The fastest route from 'we have dynamics equations' to a working MPC loop in pure Python, which suits a 48h build better than a compiled stack.

**Build notes:** License LGPL-3.0 (gh api). Last push 2026-09-22. pip install; examples run on CPU in seconds. Not real-time on a flight computer as-is: present it as the design and evaluation tool, and acados or TinyMPC as the onboard path. The MHE half is a natural tie-in to the hub's estimation samples.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `mpc`, `mhe`, `python`, `casadi`, `lgpl-3.0`

**Domains:** multi

## Related

- depends_on: [CasADi](../../catalog/repos/casadi__casadi.md)
- alternative_to: [acados](../../catalog/repos/acados__acados.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [acados](../../catalog/repos/acados__acados.md) (alternative_to)
- [CasADi](../../catalog/repos/casadi__casadi.md) (integrates_with)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
