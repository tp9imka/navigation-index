# jMAVSim

`repo:px4/jmavsim` - <https://github.com/PX4/jMAVSim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 107 | Java | BSD-3-Clause | 2026-01-29 | False | production | medium |

Lightweight Java multirotor simulator that speaks MAVLink to PX4, without a 3D-world physics engine.

**Why it matters:** Fastest way to get a PX4 SITL quad flying for MAVLink, GCS or mission-logic work when sensors and worlds do not matter.

**Hackathon notes:** Runs with 'make px4_sitl jmavsim'. Needs a JDK. No cameras or lidar, so not for perception work.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `px4`, `mavlink`, `java`, `sitl`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- alternative_to: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)

## Referenced by

- [PX4 Simulation (Gazebo, SITL) documentation](../resources/px4-simulation-docs.md) (explains)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
