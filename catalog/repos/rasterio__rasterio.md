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

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md)

**Tags:** `geotiff`, `dem`, `raster`

**Domains:** multi

## Related

- depends_on: [GDAL](../../catalog/repos/osgeo__gdal.md)
- integrates_with: [elevation](../../catalog/repos/bopen__elevation.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [elevation](../../catalog/repos/bopen__elevation.md) (integrates_with)
- [GDAL](../../catalog/repos/osgeo__gdal.md) (integrates_with)
- [pystac-client](../../catalog/repos/stac-utils__pystac-client.md) (integrates_with)
- [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md) (uses)
- [Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models](../../catalog/resources/geobasis-nrw-dom1-dgm1.md) (has_code)
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) (has_code)
- [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md) (uses)
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md) (uses)
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) (uses)
- [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md) (uses)
- [Terrain-relative navigation with a particle filter](../../catalog/samples/terrain-relative-nav-pf.md) (uses)
- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) (uses)
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
