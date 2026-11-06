# jMAVSim

`repo:px4/jmavsim` - <https://github.com/PX4/jMAVSim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 107 | Java | BSD-3-Clause | 2026-01-29 | False | production | medium |

Lightweight Java multirotor simulator that speaks MAVLink to PX4, without a 3D-world physics engine.

**Why it matters:** Was the fastest way to get a PX4 SITL quad flying for MAVLink, GCS or mission-logic work when sensors and worlds do not matter; PX4 has since replaced it with SIH.

**Hackathon notes:** Removed from PX4-Autopilot main in September 2026; 'make px4_sitl jmavsim' only exists up to PX4 v1.17. On current PX4 use 'make px4_sitl_sih sihsim_quadx' with Hawkeye. Needs a JDK. No cameras or lidar, so not for perception work. This repo is PX4's fork of DrTon/jMAVSim.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `px4`, `mavlink`, `java`, `sitl`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- alternative_to: [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md)

## Referenced by

- [PX4 Simulation (Gazebo, SITL) documentation](../../catalog/resources/px4-simulation-docs.md) (explains)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
