# NVIDIA Isaac Sim

`repo:isaac-sim/isaacsim` - <https://github.com/isaac-sim/IsaacSim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,437 | Python | NOASSERTION | 2026-11-05 | False | production | medium |

NVIDIA's Omniverse-based robot simulator, now open source, with RTX sensor simulation (cameras, lidar, IMU) and ROS 2 bridges.

**Why it matters:** Base layer for Pegasus, OmniDrones and Isaac Lab; strong for synthetic data generation for perception models.

**Hackathon notes:** RTX GPU and a lot of disk required. Use the prebuilt container or pip install rather than building from source in a hackathon.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `omniverse`, `nvidia`, `rtx`, `synthetic-data`

**Domains:** air, ground, multi

## Related

- integrates_with: [Isaac Lab](../../catalog/repos/isaac-sim__isaaclab.md)
- integrates_with: [Pegasus Simulator](../../catalog/repos/pegasussimulator__pegasussimulator.md)
- integrates_with: [OmniDrones](../../catalog/repos/btx0424__omnidrones.md)

## Referenced by

- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [OmniDrones](../../catalog/repos/btx0424__omnidrones.md) (depends_on)
- [Isaac Lab](../../catalog/repos/isaac-sim__isaaclab.md) (depends_on)
- [Pegasus Simulator](../../catalog/repos/pegasussimulator__pegasussimulator.md) (depends_on)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
