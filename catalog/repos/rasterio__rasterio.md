# Rasterio

`repo:rasterio/rasterio` - <https://github.com/rasterio/rasterio>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,592 | Python | NOASSERTION | 2026-11-03 | False | production | high |

Pythonic raster I/O on top of GDAL: read/write GeoTIFF and COG, windowed reads, masks and affine georeferencing.

**Why it matters:** Easiest way to sample a DEM or orthophoto at a coordinate for terrain-referenced or visual navigation experiments.

**Hackathon notes:** pip wheels include GDAL; use windowed reads to crop tiles around a vehicle position.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [rasterio__rasterio](../../docs/integration-cards/rasterio__rasterio.md) (integration-cards)

**Concepts:** [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Terrain-relative navigation](../concepts/terrain-nav.md)

**Tags:** `geotiff`, `dem`, `raster`

**Domains:** multi

## Related

- depends_on: [GDAL](../repos/osgeo__gdal.md)
- integrates_with: [elevation](../repos/bopen__elevation.md)

## Referenced by

- [elevation](../repos/bopen__elevation.md) (integrates_with)
- [GDAL](../repos/osgeo__gdal.md) (integrates_with)
- [pystac-client](../repos/stac-utils__pystac-client.md) (integrates_with)
- [Copernicus DEM on AWS Open Data](../resources/copernicus-dem-aws.md) (uses)
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../samples/geoloc-license-clean.md) (uses)
- [Heightmap-gradient particle filter on real Copernicus DEM (SPRIN-D CTU method) vs TERCOM](../samples/terrain-heightmap-pf.md) (uses)
- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) (uses)
- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
