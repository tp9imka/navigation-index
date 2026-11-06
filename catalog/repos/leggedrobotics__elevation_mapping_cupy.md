# elevation_mapping_cupy

`repo:leggedrobotics/elevation_mapping_cupy` - <https://github.com/leggedrobotics/elevation_mapping_cupy>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,160 | Python | MIT | 2026-10-03 | False | active-research | high |

GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.

**Why it matters:** Terrain-aware planning for off-road robots needs a live elevation and traversability map; this is the modern GPU version.

**Hackathon notes:** Needs CUDA; Docker image available. Feed a depth camera or lidar and get a traversability layer.

**Concepts:** [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [Terrain-relative navigation](../concepts/terrain-nav.md), [Onboard / edge AI perception](../concepts/edge-ai.md), [Path and motion planning](../concepts/path-planning.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `elevation-map`, `traversability`, `cupy`, `gpu`

**Domains:** ground

## Related

- depends_on: [grid_map](../repos/anybotics__grid_map.md)
- integrates_with: [Wild Visual Navigation](../repos/leggedrobotics__wild_visual_navigation.md)
- depends_on: [grid_map](../repos/leggedrobotics__grid_map.md)

## Referenced by

- [grid_map](../repos/anybotics__grid_map.md) (integrates_with)
- [elevation_mapping](../repos/leggedrobotics__elevation_mapping.md) (alternative_to)
- [grid_map](../repos/leggedrobotics__grid_map.md) (integrates_with)
- [Wild Visual Navigation](../repos/leggedrobotics__wild_visual_navigation.md) (integrates_with)

_Indexed by lane(s): domains-swarm, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
