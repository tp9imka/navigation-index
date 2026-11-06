# Cesium Terrain Builder

`repo:geo-data/cesium-terrain-builder` - <https://github.com/geo-data/cesium-terrain-builder>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 888 | C++ | NOASSERTION | 2023-03-05 | False | archived | medium |

Command-line tools to convert GDAL-readable DEMs into Cesium terrain tiles (heightmap and quantized-mesh with the docker variant).

**Why it matters:** Turns a Copernicus/SRTM DEM into offline 3D terrain for a CesiumJS display without internet.

**Hackathon notes:** Unmaintained since 2023; use the tum-gis docker image to avoid build pain.

**Concepts:** [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Terrain-relative navigation](../concepts/terrain-nav.md)

**Tags:** `quantized-mesh`, `dem`, `offline-terrain`

**Domains:** multi

## Related

- integrates_with: [CesiumJS](../repos/cesiumgs__cesium.md)
- depends_on: [GDAL](../repos/osgeo__gdal.md)

## Referenced by

- [CesiumJS](../repos/cesiumgs__cesium.md) (integrates_with)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
