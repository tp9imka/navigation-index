# UFOMap: An Efficient Probabilistic 3D Mapping Framework That Embraces the Unknown

`res:duberg-ufomap-ral-2020` - paper - <https://arxiv.org/abs/2003.04749>

**By:** Daniel Duberg, Patric Jensfelt - **Year:** 2020 - **Level:** intermediate - **Access:** open

Peer-reviewed (IEEE RA-L 2020, doi 10.1109/LRA.2020.3013861); arXiv copy linked. Extends octree mapping with an explicit unknown state and indicators per node so planners can ask whether a region is entirely known-free in one query.

## Key takeaways

- Explicit unknown enables safe 'known-free only' collision checks
- Faster than OctoMap in the reported benchmarks
- Built for planning and exploration queries

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `occupancy-map`, `unknown-space`, `peer-reviewed`

## Related

- has_code: [UFOMap](../../catalog/repos/unknownfreeoccupied__ufomap.md)

_Indexed by lane(s): close-area-planning_
