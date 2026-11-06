# Project DAVE

`repo:field-robotics-lab/dave` - <https://github.com/Field-Robotics-Lab/dave>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 299 | C++ | Apache-2.0 | 2024-08-19 | False | active-research | medium |

Gazebo-based underwater simulation environment from the Naval Postgraduate School and partners, extending UUV Simulator with DVL, sonar, bathymetry and manipulation models.

**Why it matters:** Navy-funded underwater sim with realistic DVL and sonar sensors for testing AUV nav without water.

**Hackathon notes:** ROS 1 Noetic + Gazebo 11 via Docker; setup is heavy, budget half a day. A ROS 2 port has been in progress.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Underwater navigation](../concepts/underwater-nav.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `gazebo`, `uuv`, `dvl`, `multibeam`, `nps`, `underwater`, `sonar`

**Domains:** underwater

## Related

- extends: [UUV Simulator](../repos/uuvsimulator__uuv_simulator.md)
- integrates_with: [NPS underwater multibeam sonar plugin](../repos/field-robotics-lab__nps_uw_multibeam_sonar.md)
- alternative_to: [Stonefish](../repos/patrykcieslak__stonefish.md)

## Referenced by

- [NPS underwater multibeam sonar plugin](../repos/field-robotics-lab__nps_uw_multibeam_sonar.md) (integrates_with)
- [Stonefish](../repos/patrykcieslak__stonefish.md) (alternative_to)
- [UUV Simulator](../repos/uuvsimulator__uuv_simulator.md) (alternative_to)

_Indexed by lane(s): domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
