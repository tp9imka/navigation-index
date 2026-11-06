# Stonefish

`repo:patrykcieslak/stonefish` - <https://github.com/patrykcieslak/stonefish>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 332 | C++ | GPL-3.0 | 2026-11-05 | False | production | high |

C++ simulation library for marine robotics with hydrodynamics, underwater rendering and sensors including DVL, USBL, multibeam and forward-looking sonar; has a ROS wrapper.

**Why it matters:** One of the few open sims with credible underwater nav sensors for AUV dead reckoning and sonar-based localization work.

**Hackathon notes:** Build with CMake; use stonefish_ros for ROS integration. Good for a DVL+USBL EKF demo.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [patrykcieslak__stonefish](../../docs/integration-cards/patrykcieslak__stonefish.md) (integration-cards)
- [underwater-datasets](../../docs/dataset-cards/underwater-datasets.md) (dataset-cards)

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md)

**Tags:** `simulator`, `dvl`, `usbl`, `sonar`, `opengl`, `auv`, `marine`

**Domains:** underwater, maritime

## Related

- alternative_to: [Project DAVE](../../catalog/repos/field-robotics-lab__dave.md)
- alternative_to: [HoloOcean ROS bridge](../../catalog/repos/byu-holoocean__holoocean-ros.md)
- alternative_to: [HoloOcean (documentation)](../../catalog/repos/byu-holoocean__holoocean-docs.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [HoloOcean (documentation)](../../catalog/repos/byu-holoocean__holoocean-docs.md) (alternative_to)
- [HoloOcean ROS bridge](../../catalog/repos/byu-holoocean__holoocean-ros.md) (alternative_to)
- [Project DAVE](../../catalog/repos/field-robotics-lab__dave.md) (alternative_to)
- [USBL Simulator](../../catalog/repos/maximilian-nitsch__usbl-simulator.md) (alternative_to)
- [Vortex AUV](../../catalog/repos/vortexntnu__vortex-auv.md) (integrates_with)

_Indexed by lane(s): domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
