# AeroSandbox

`repo:peterdsharpe/aerosandbox` - <https://github.com/peterdsharpe/AeroSandbox>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,388 | Jupyter Notebook | MIT | 2026-10-30 | False | active-research | high |

Python aircraft design and trajectory optimisation toolkit on CasADi: aerodynamics, propeller and electric propulsion models, power sources, wind models, and an optimisation front-end.

**Why it matters:** Gives a team physically grounded drag, propeller and battery-power numbers to put an energy cost into a route planner, without writing aerodynamics from scratch.

**Build notes:** License MIT (gh api). Last push 2026-10-30. pip install aerosandbox. Library folder confirmed to include propulsion_electric, propulsion_propeller and winds modules. Use it offline to build an energy-per-metre table vs airspeed and wind, then use the table in the planner cost; do not put the full optimiser in the flight loop.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `aircraft-design`, `propulsion`, `energy`, `trajectory-optimisation`, `casadi`, `python`, `mit`

**Domains:** air

## Related

- depends_on: [CasADi](../../catalog/repos/casadi__casadi.md)
- alternative_to: [CCBlade.jl](../../catalog/repos/byuflowlab__ccblade.jl.md)
- integrates_with: [PyBaMM](../../catalog/repos/pybamm-team__pybamm.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [CCBlade.jl](../../catalog/repos/byuflowlab__ccblade.jl.md) (alternative_to)
- [CasADi](../../catalog/repos/casadi__casadi.md) (integrates_with)
- [PyBaMM](../../catalog/repos/pybamm-team__pybamm.md) (integrates_with)
- [UIUC Propeller Data Site](../../catalog/resources/uiuc-propeller-database.md) (dataset_for)
- [Energy Minimization for Wireless Communication with Rotary-Wing UAV](../../catalog/resources/zeng-rotary-wing-energy-model-2018.md) (uses)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
