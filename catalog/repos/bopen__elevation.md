# elevation

`repo:bopen/elevation` - <https://github.com/bopen/elevation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 356 | Python | Apache-2.0 | 2026-10-29 | False | production | high |

CLI/Python tool to download, cache and clip global DEMs (SRTM, Copernicus DEM and others) for a bounding box.

**Why it matters:** One-command DEM for an AOI, the first input for terrain-referenced navigation and terrain-aware planning.

**Hackathon notes:** Needs GDAL on PATH; eio clip --bounds ... produces a GeoTIFF.

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `dem`, `srtm`, `copernicus-dem`

**Domains:** multi

## Related

- integrates_with: [Rasterio](../repos/rasterio__rasterio.md)
- depends_on: [GDAL](../repos/osgeo__gdal.md)

## Referenced by

- [Rasterio](../repos/rasterio__rasterio.md) (integrates_with)
- [Copernicus DEM on AWS Open Data](../resources/copernicus-dem-aws.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
