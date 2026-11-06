# elevation_mapping_cupy

`repo:leggedrobotics/elevation_mapping_cupy` - <https://github.com/leggedrobotics/elevation_mapping_cupy>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,160 | Python | MIT | 2026-10-03 | False | active-research | high |

GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.

**Why it matters:** Terrain-aware planning for off-road robots needs a live elevation and traversability map; this is the modern GPU version.

**Hackathon notes:** Needs CUDA; Docker image available. Feed a depth camera or lidar and get a traversability layer.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [leggedrobotics__elevation_mapping_cupy](../../docs/integration-cards/leggedrobotics__elevation_mapping_cupy.md) (integration-cards)

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `elevation-map`, `traversability`, `cupy`, `gpu`

**Domains:** ground

## Related

- depends_on: [grid_map](../../catalog/repos/anybotics__grid_map.md)
- integrates_with: [Wild Visual Navigation](../../catalog/repos/leggedrobotics__wild_visual_navigation.md)
- depends_on: [grid_map](../../catalog/repos/leggedrobotics__grid_map.md)

## Referenced by

- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [grid_map](../../catalog/repos/anybotics__grid_map.md) (integrates_with)
- [elevation_mapping](../../catalog/repos/leggedrobotics__elevation_mapping.md) (alternative_to)
- [grid_map](../../catalog/repos/leggedrobotics__grid_map.md) (integrates_with)
- [Wild Visual Navigation](../../catalog/repos/leggedrobotics__wild_visual_navigation.md) (integrates_with)

_Indexed by lane(s): domains-swarm, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
