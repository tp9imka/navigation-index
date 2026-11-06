# Kilometer-Scale GNSS-Denied UAV Navigation via Heightmap Gradients: A Winning System from the SPRIN-D Challenge

`res:sprind-heightmap-gradients-2025` - paper - <https://arxiv.org/abs/2510.01348>

**By:** Michal Werner, David Capek, Tomas Musil, Ondrej Franek, Tomas Baca, Martin Saska - **Year:** 2025 - **Level:** advanced - **Access:** open

Describes the winning SPRIN-D Fully Autonomous Flight system: LiDAR local heightmaps matched against prior elevation data by gradient templates, fused with odometry in a clustered particle filter, flying about 9 km below 25 m AGL without GNSS.

## Key takeaways

- Heightmap gradients avoid needing reliable absolute (barometric) height
- Clustered particle filter handles multimodal position
- Runs on CPU in real time
- No public code found

## Deep dives

- [ctu-sprind-terrain-nav](../../docs/paper-digests/ctu-sprind-terrain-nav.md) (paper-digests)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [LiDAR odometry and SLAM](../../catalog/concepts/lidar-slam.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `sprind`, `ctu`, `particle-filter`, `icra2026`

## Related

- uses: [MRS UAV System](../../catalog/repos/ctu-mrs__mrs_uav_system.md)
- part_of: [SPRIND Fully Autonomous Flight challenge](../../catalog/resources/sprind-fully-autonomous-flight.md)

## Referenced by

- [SPRIND Fully Autonomous Flight challenge](../../catalog/resources/sprind-fully-autonomous-flight.md) (explains)
- [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md) (explains)

_Indexed by lane(s): round3-expansion_
