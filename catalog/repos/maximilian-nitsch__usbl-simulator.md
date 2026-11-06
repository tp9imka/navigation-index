# USBL Simulator

`repo:maximilian-nitsch/usbl-simulator` - <https://github.com/maximilian-nitsch/USBL-Simulator>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 14 | C++ | BSD-3-Clause | 2025-04-11 | False | research-prototype | medium |

C++ library and ROS 2 (Humble) node that simulates ultra-short baseline acoustic positioning measurements; a Gazebo plugin is only listed as a planned feature.

**Why it matters:** USBL is the main absolute fix for submerged vehicles; simulated USBL lets a team test an aided-INS filter.

**Hackathon notes:** ROS 2 colcon build; generate USBL fixes to fuse with DVL dead reckoning.

**Concepts:** [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `usbl`, `acoustic`, `ros2`, `gazebo`

**Domains:** underwater

## Related

- integrates_with: [AuvEstimator](../../catalog/repos/alliwong__auvestimator.md)
- alternative_to: [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
