# PyBaMM

`repo:pybamm-team/pybamm` - <https://github.com/pybamm-team/PyBaMM>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,741 | Python | BSD-3-Clause | 2026-11-22 | False | production | medium |

Python battery modelling library: equivalent-circuit to electrochemical (SPM, DFN) lithium-ion models with parameter sets and fast solvers.

**Why it matters:** Lets an energy-aware planner use a battery model with voltage sag and capacity effects instead of a fixed watt-hour budget.

**Build notes:** License BSD-3-Clause (gh api). Last push 2026-11-06. pip install pybamm. Electrochemical models are overkill for routing; an equivalent-circuit model fitted to a pack datasheet is enough. Use it offline to make a remaining-range lookup.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `battery`, `energy`, `li-ion`, `python`, `bsd-3-clause`

**Domains:** multi

## Related

- integrates_with: [AeroSandbox](../../catalog/repos/peterdsharpe__aerosandbox.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [AeroSandbox](../../catalog/repos/peterdsharpe__aerosandbox.md) (integrates_with)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-23._
