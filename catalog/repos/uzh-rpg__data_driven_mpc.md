# Data-Driven MPC for Quadrotors

`repo:uzh-rpg/data_driven_mpc` - <https://github.com/uzh-rpg/data_driven_mpc>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 365 | Python | GPL-3.0 | 2021-04-20 | False | archived | medium |

Python code for the Data-Driven MPC paper: a nominal quadrotor model in acados corrected by Gaussian-process regression of the residual dynamics (drag, unmodelled effects), with Gazebo and simplified-sim pipelines.

**Why it matters:** A template for 'physics model + learned correction' in the loop, which is the propulsion / applied-physics angle the brief's expertise list hints at.

**Build notes:** License GPL-3.0, README says a commercial license is available from the lab (gh api + README). Last push 2021-04-20. Tested on Ubuntu 18.04 / Python 3.6 / ROS Melodic, with a python3.8 branch for Noetic. Expect dependency pain; lift the GP-residual idea, not the code.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `mpc`, `gaussian-process`, `acados`, `aerodynamics`, `python`, `gpl-3.0`

**Domains:** air

## Related

- depends_on: [acados](../../catalog/repos/acados__acados.md)
- alternative_to: [ML-CasADi](../../catalog/repos/tum-aas__ml-casadi.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [ML-CasADi](../../catalog/repos/tum-aas__ml-casadi.md) (alternative_to)
- [Data-Driven MPC for Quadrotors](../../catalog/resources/torrente-data-driven-mpc-2021.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
