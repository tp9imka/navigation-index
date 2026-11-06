# Project DAVE

`repo:field-robotics-lab/dave` - <https://github.com/Field-Robotics-Lab/dave>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 299 | C++ | Apache-2.0 | 2024-08-19 | False | active-research | medium |

Gazebo-based underwater simulation environment from the Naval Postgraduate School and partners, extending UUV Simulator with DVL, sonar, bathymetry and manipulation models.

**Why it matters:** Navy-funded underwater sim with realistic DVL and sonar sensors for testing AUV nav without water.

**Hackathon notes:** ROS 1 Noetic + Gazebo 11 via Docker; setup is heavy, budget half a day. No push here since 2024-08; the ROS 2 port continues in the IOES-Lab/dave fork.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Underwater navigation](../../catalog/concepts/underwater-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `gazebo`, `uuv`, `dvl`, `multibeam`, `nps`, `underwater`, `sonar`

**Domains:** underwater

## Related

- extends: [UUV Simulator](../../catalog/repos/uuvsimulator__uuv_simulator.md)
- integrates_with: [NPS underwater multibeam sonar plugin](../../catalog/repos/field-robotics-lab__nps_uw_multibeam_sonar.md)
- alternative_to: [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [NPS underwater multibeam sonar plugin](../../catalog/repos/field-robotics-lab__nps_uw_multibeam_sonar.md) (integrates_with)
- [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md) (alternative_to)
- [UUV Simulator](../../catalog/repos/uuvsimulator__uuv_simulator.md) (alternative_to)

_Indexed by lane(s): domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
