# Kilometer-Scale GNSS-Denied UAV Navigation via Heightmap Gradients: A Winning System from the SPRIN-D Challenge

`res:sprind-heightmap-gradients-2025` - paper - <https://arxiv.org/abs/2510.01348>

**By:** Werner, Capek, Musil, Franek, Baca, Saska (CTU MRS / Fly4Future) - **Year:** 2025 - **Level:** advanced - **Access:** open

Describes the winning SPRIN-D Fully Autonomous Flight system: LiDAR local heightmaps matched against prior elevation data by gradient templates, fused with odometry in a clustered particle filter, flying about 9 km below 25 m AGL without GNSS.

## Key takeaways

- Terrain gradients beat raw height matching at low altitude
- Clustered particle filter handles multimodal position
- Runs on CPU in real time
- No public code found

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [LiDAR odometry and SLAM](../concepts/lidar-slam.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `sprind`, `ctu`, `particle-filter`, `icra2026`

## Related

- uses: [MRS UAV System](../repos/ctu-mrs__mrs_uav_system.md)
- part_of: [SPRIND Fully Autonomous Flight challenge](../resources/sprind-fully-autonomous-flight.md)

## Referenced by

- [SPRIND Fully Autonomous Flight challenge](../resources/sprind-fully-autonomous-flight.md) (explains)

_Indexed by lane(s): round3-expansion_
