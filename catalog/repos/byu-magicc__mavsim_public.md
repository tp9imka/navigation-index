# mavsim_public (Small Unmanned Aircraft)

`repo:byu-magicc/mavsim_public` - <https://github.com/byu-magicc/mavsim_public>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1,053 | Python | GPL-3.0 | 2026-06-13 | False | educational | high |

Project files for Beard and McLain's 'Small Unmanned Aircraft: Theory and Practice': a Python fixed-wing simulator built chapter by chapter, with autopilot (PID, LQR, TECS), straight-line and orbit path following, Dubins path manager and RRT planners.

**Why it matters:** The most direct pure-Python fixed-wing GNC chain available: estimation, guidance and path planning in one readable codebase, with wind.

**Build notes:** License GPL-3.0 (gh api): fine for a demo, rewrite before productising. Last push 2026-06-13, maintained. Folders confirmed: mavsim_python/planners (dubins_parameters, path_follower, path_manager, rrt_dubins, rrt_straight_line) and controllers (autopilot_tecs, autopilot_lqr). Some files are student templates with blanks to fill; check each module before relying on it. No ROS, no SITL needed.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `fixed-wing`, `path-following`, `dubins`, `tecs`, `rrt`, `python`, `textbook`, `gpl-3.0`

**Domains:** air

## Related

- alternative_to: [pydubins](../../catalog/repos/andrewwalker__pydubins.md)
- alternative_to: [JSBSim](../../catalog/repos/jsbsim-team__jsbsim.md)
- alternative_to: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [pydubins](../../catalog/repos/andrewwalker__pydubins.md) (alternative_to)
- [Small Unmanned Aircraft: Theory and Practice](../../catalog/resources/beard-mclain-small-unmanned-aircraft.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-16._
