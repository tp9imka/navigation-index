# grid_map

`repo:leggedrobotics/grid_map` - <https://github.com/leggedrobotics/grid_map>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 27 | C++ | BSD-3-Clause | 2026-09-07 | False | production | high |

Universal multi-layer 2.5D grid map library for mobile robots with ROS/ROS 2 integration, filters, iterators and conversion to images, point clouds and costmaps.

**Why it matters:** Common data structure for elevation, slope and cost layers - the glue between DEMs and planners.

**Hackathon notes:** Available as ROS 2 binaries; load a GeoTIFF DEM (via GDAL) into a grid_map layer for terrain-aware costs.

**Concepts:** [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Path and motion planning](../concepts/path-planning.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `grid-map`, `elevation`, `costmap`

**Domains:** ground

## Related

- integrates_with: [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md)
- integrates_with: [GDAL](../repos/osgeo__gdal.md)

## Referenced by

- [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md) (depends_on)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
