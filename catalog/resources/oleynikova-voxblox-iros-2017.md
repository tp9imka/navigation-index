# Voxblox: Incremental 3D Euclidean Signed Distance Fields for On-Board MAV Planning

`res:oleynikova-voxblox-iros-2017` - paper - <https://arxiv.org/abs/1611.03631>

**By:** Helen Oleynikova, Zachary Taylor, Marius Fehr, Juan Nieto, Roland Siegwart - **Year:** 2017 - **Level:** intermediate - **Access:** open

Preprint on arXiv; published at IROS 2017. Builds an ESDF incrementally from a TSDF so a CPU-only MAV can keep distance and gradient to obstacles up to date for trajectory optimisation.

## Key takeaways

- ESDF from TSDF is cheaper than from raw occupancy
- Gradient-based planners need distance plus gradient, not just occupied or free
- Runs on CPU at MAV scale

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `esdf`, `tsdf`, `mav`, `preprint`

## Related

- has_code: [voxblox](../../catalog/repos/ethz-asl__voxblox.md)

## Referenced by

- [nvblox: GPU-Accelerated Incremental Signed Distance Field Mapping](../../catalog/resources/millane-nvblox-2023.md) (same_author)

_Indexed by lane(s): close-area-planning_
