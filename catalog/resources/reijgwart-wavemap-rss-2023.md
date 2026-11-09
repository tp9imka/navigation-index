# Efficient volumetric mapping of multi-scale environments using wavelet-based compression

`res:reijgwart-wavemap-rss-2023` - paper - <https://www.roboticsproceedings.org/rss19/p065.pdf>

**By:** Victor Reijgwart, Cesar Cadena, Roland Siegwart, Lionel Ott - **Year:** 2023 - **Level:** advanced - **Access:** open

Peer-reviewed (RSS 2023). Stores occupancy as Haar wavelet coefficients in an octree, giving multi-resolution queries and good handling of thin structures at long range with low memory.

## Key takeaways

- Multi-resolution map without separate pyramids
- Designed and tested for CPU-only systems
- Thin obstacles survive better than in coarse fixed grids

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `occupancy-map`, `wavelet`, `peer-reviewed`

## Related

- has_code: [wavemap](../../catalog/repos/ethz-asl__wavemap.md)

_Indexed by lane(s): close-area-planning_
