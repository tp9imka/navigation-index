# rpg_mpc (PAMPC)

`repo:uzh-rpg/rpg_mpc` - <https://github.com/uzh-rpg/rpg_mpc>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 525 | C | GPL-3.0 | 2022-04-04 | False | archived | medium |

Quadrotor MPC built on ACADO code generation, including the Perception-Aware MPC (PAMPC) variant that adds a cost to keep a point of interest visible in the camera while tracking a trajectory.

**Why it matters:** The canonical example of putting a perception term into the controller cost, which is what keeps a visual-nav vehicle localisable when GNSS is gone.

**Build notes:** License GPL-3.0 (gh api). Last push 2022-04-04. ROS 1 and ACADO (not acados). Re-implement the PAMPC cost term in acados or do-mpc rather than reviving this build; cite the paper for the method.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `mpc`, `perception-aware`, `acado`, `multirotor`, `gpl-3.0`

**Domains:** air

## Related

- integrates_with: [rpg_quadrotor_control](../../catalog/repos/uzh-rpg__rpg_quadrotor_control.md)
- alternative_to: [acados](../../catalog/repos/acados__acados.md)
- same_org: [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md) (same_org)
- [rpg_quadrotor_control](../../catalog/repos/uzh-rpg__rpg_quadrotor_control.md) (integrates_with)
- [PAMPC: Perception-Aware Model Predictive Control for Quadrotors](../../catalog/resources/falanga-pampc-2018.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
