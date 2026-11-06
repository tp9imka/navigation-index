# elevation

`repo:bopen/elevation` - <https://github.com/bopen/elevation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 356 | Python | Apache-2.0 | 2026-10-29 | False | production | high |

CLI/Python tool to download, cache and clip global DEMs (SRTM, Copernicus DEM and others) for a bounding box.

**Why it matters:** One-command DEM for an AOI, the first input for terrain-referenced navigation and terrain-aware planning.

**Hackathon notes:** Needs GDAL on PATH; eio clip --bounds ... produces a GeoTIFF.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [bopen__elevation](../../docs/integration-cards/bopen__elevation.md) (integration-cards)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `dem`, `srtm`, `copernicus-dem`

**Domains:** multi

## Related

- integrates_with: [Rasterio](../../catalog/repos/rasterio__rasterio.md)
- depends_on: [GDAL](../../catalog/repos/osgeo__gdal.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Rasterio](../../catalog/repos/rasterio__rasterio.md) (integrates_with)
- [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
