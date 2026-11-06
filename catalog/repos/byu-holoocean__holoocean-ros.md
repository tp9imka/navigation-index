# HoloOcean ROS bridge

`repo:byu-holoocean/holoocean-ros` - <https://github.com/byu-holoocean/holoocean-ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 56 | Python | MIT | 2026-10-09 | False | active-research | medium |

ROS bridge for HoloOcean, BYU's Unreal Engine based underwater simulator with DVL, IMU, depth, sonar and acoustic modem sensors.

**Why it matters:** Photo-realistic underwater sim with multi-agent acoustic comms, useful for cooperative AUV nav.

**Hackathon notes:** HoloOcean itself is not installed from PyPI (that package is an old 0.5.x): the source repo is only visible to a GitHub account linked to Epic Games, then pip install the client and run holoocean.install('Ocean') for the world package. The bridge is ROS 2 (Humble/Jazzy), Docker recommended. Needs a decent GPU.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Underwater navigation](../../catalog/concepts/underwater-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `holoocean`, `unreal`, `sonar`, `dvl`

**Domains:** underwater

## Related

- alternative_to: [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md) (alternative_to)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
