# EGO-Swarm

`repo:zju-fast-lab/ego-planner-swarm` - <https://github.com/ZJU-FAST-Lab/ego-planner-swarm>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,247 | C++ | GPL-3.0 | 2025-03-08 | False | research-prototype | high |

Decentralized multi-quadrotor extension of EGO-Planner with inter-agent collision avoidance and trajectory sharing over a network.

**Why it matters:** Open reference for drone swarms that coordinate paths without a central server, relevant to contested comms scenarios.

**Hackathon notes:** Simulation launches many drones on one machine; trajectory broadcast assumes reliable comms - an interesting knob to degrade in a hackathon.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [zju-fast-lab__ego-planner-swarm](../../docs/integration-cards/zju-fast-lab__ego-planner-swarm.md) (integration-cards)

**Concepts:** [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `swarm`, `trajectory`, `quadrotor`, `decentralized`

**Domains:** air, multi

## Related

- integrates_with: [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md)
- extends: [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md)

## Referenced by

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MADER](../../catalog/repos/mit-acl__mader.md) (alternative_to)
- [EGO-Planner](../../catalog/repos/zju-fast-lab__ego-planner.md) (extends)

_Indexed by lane(s): domains-swarm, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
