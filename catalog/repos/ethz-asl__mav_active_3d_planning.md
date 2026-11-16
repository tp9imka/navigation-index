# mav_active_3d_planning

`repo:ethz-asl/mav_active_3d_planning` - <https://github.com/ethz-asl/mav_active_3d_planning>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 715 | C++ | BSD-3-Clause | 2025-08-14 | False | research-prototype | low |

Modular framework for online informative path planning on MAVs: pluggable trajectory generators, evaluators (information gain), and back-ends, built on Voxblox maps.

**Why it matters:** The evaluator abstraction is exactly where a 'localisability' or 'TRN information' gain would plug in, instead of the usual exploration gain.

**Build notes:** License BSD-3-Clause (gh api). Last push 2025-08-14. ROS 1 catkin stack. Borrow the planner / evaluator split as architecture; do not attempt to build it in the first day.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `informative-path-planning`, `active-perception`, `voxblox`, `bsd-3-clause`

**Domains:** air

## Related

- integrates_with: [RotorS](../../catalog/repos/ethz-asl__rotors_simulator.md)
- alternative_to: [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md)
- alternative_to: [FUEL - Fast UAV Exploration](../../catalog/repos/hkust-aerial-robotics__fuel.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md) (alternative_to)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-16._
