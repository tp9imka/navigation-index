# Online Graph Pruning for Pathfinding On Grid Maps

`res:harabor-grastien-jps-aaai-2011` - paper - <https://doi.org/10.1609/aaai.v25i1.7994>

**By:** Daniel Harabor, Alban Grastien - **Year:** 2011 - **Level:** intro - **Access:** open

Peer-reviewed (AAAI 2011). Introduces Jump Point Search: on uniform-cost grids, symmetric paths are pruned so A* expands only jump points, keeping optimality with far fewer expansions.

## Key takeaways

- Same optimal path as A* on uniform grids
- Large speedups on open maps, smaller in cluttered ones
- Needs uniform cost; clearance-weighted grids break the assumption

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `jps`, `a-star`, `grid-search`, `peer-reviewed`

## Related

- has_code: [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md)

## Referenced by

- [Planning Dynamically Feasible Trajectories for Quadrotors Using Safe Flight Corridors in 3-D Complex Environments](../../catalog/resources/liu-sfc-quadrotor-ral-2017.md) (cites)

_Indexed by lane(s): close-area-planning_
