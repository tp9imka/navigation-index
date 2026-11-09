# FASTER: Fast and Safe Trajectory Planner for Navigation in Unknown Environments

`res:tordesillas-faster-tro-2022` - paper - <https://arxiv.org/abs/2001.04420>

**By:** Jesus Tordesillas, Brett T. Lopez, Michael Everett, Jonathan P. How - **Year:** 2022 - **Level:** advanced - **Access:** open

Peer-reviewed (IEEE T-RO, doi 10.1109/TRO.2021.3100142); arXiv copy linked. Plans two trajectories each cycle: a fast one through known and unknown space, and a safe backup that stops inside known free space. Only the prefix up to the backup branch point is committed.

## Key takeaways

- Safety = always holding a stop trajectory in known free space
- Optimism about unknown space is fine if it is never committed
- Corridors from JPS + convex decomposition keep the problem an MIQP

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `unknown-space`, `backup-trajectory`, `peer-reviewed`

## Related

- has_code: [FASTER](../../catalog/repos/mit-acl__faster.md)

## Referenced by

- [Safety-assured high-speed navigation for MAVs](../../catalog/resources/ren-super-scirobotics-2025.md) (cites)

_Indexed by lane(s): close-area-planning_
