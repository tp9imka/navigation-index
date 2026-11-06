# EGO-Swarm

`repo:zju-fast-lab/ego-planner-swarm` - <https://github.com/ZJU-FAST-Lab/ego-planner-swarm>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,247 | C++ | GPL-3.0 | 2025-03-08 | False | research-prototype | high |

Decentralized multi-quadrotor extension of EGO-Planner with inter-agent collision avoidance and trajectory sharing over a network.

**Why it matters:** Open reference for drone swarms that coordinate paths without a central server, relevant to contested comms scenarios.

**Hackathon notes:** Simulation launches many drones on one machine; trajectory broadcast assumes reliable comms - an interesting knob to degrade in a hackathon.

**Concepts:** [Swarms and multi-agent navigation](../concepts/multi-agent.md), [Path and motion planning](../concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md)

**Tags:** `swarm`, `trajectory`, `quadrotor`, `decentralized`

**Domains:** air, multi

## Related

- integrates_with: [Aerostack2](../repos/aerostack2__aerostack2.md)
- extends: [EGO-Planner](../repos/zju-fast-lab__ego-planner.md)

## Referenced by

- [MADER](../repos/mit-acl__mader.md) (alternative_to)
- [EGO-Planner](../repos/zju-fast-lab__ego-planner.md) (extends)

_Indexed by lane(s): domains-swarm, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
