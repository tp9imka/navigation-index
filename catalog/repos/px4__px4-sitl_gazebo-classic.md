# PX4 SITL Gazebo Classic

`repo:px4/px4-sitl_gazebo-classic` - <https://github.com/PX4/PX4-SITL_gazebo-classic>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 467 | C++ | ? | 2026-10-27 | False | production | medium |

Plugins, vehicle models and worlds that connect PX4 SITL/HITL to Gazebo Classic, including GPS, IMU, magnetometer, barometer and optical-flow plugins.

**Why it matters:** Large existing corpus of tutorials and research setups still target it; the GPS plugin is a common starting point for spoofing and jamming experiments in sim.

**Hackathon notes:** Works with Ubuntu 20.04/22.04 and Gazebo 11. Gazebo Classic has reached end of life, so prefer gz-sim for new builds unless you need a specific legacy model.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `gazebo-classic`, `sitl`, `hitl`, `px4`

**Domains:** air, ground, maritime

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- alternative_to: [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md)

## Referenced by

- [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md) (alternative_to)

_Indexed by lane(s): autopilots, sim-data_

_GitHub metadata fetched 2026-11-06._
