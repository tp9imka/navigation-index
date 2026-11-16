# Genesis World

`repo:genesis-embodied-ai/genesis-world` - <https://github.com/Genesis-Embodied-AI/genesis-world>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 30,235 | Python | Apache-2.0 | 2026-11-15 | False | active-research | medium |

Python multi-physics simulation platform with camera, depth and lidar sensors and a compiler that targets CUDA, Apple Metal and ARM64. Ships drone hover and route-following examples.

**Why it matters:** One of the few GPU-class simulators with a Metal backend, so it can use the Mac GPU for depth and lidar rendering.

**Build notes:** Apache-2.0, very active. pip install genesis-world. Drone examples in examples/drone/. API changes fast; pin the version on Day 0 and test before relying on it.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `genesis`, `metal`, `lidar`, `depth-camera`, `rl`, `apache-2.0`

**Domains:** air

## Related

- alternative_to: [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md)

_Indexed by lane(s): close-area-sims_

_GitHub metadata fetched 2026-11-16._
