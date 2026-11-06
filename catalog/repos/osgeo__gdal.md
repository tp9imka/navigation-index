# GDAL

`repo:osgeo/gdal` - <https://github.com/osgeo/gdal>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,133 | C++ | NOASSERTION | 2026-11-03 | False | production | high |

Translator library and CLI tools for raster and vector geospatial formats (GeoTIFF, COG, GeoPackage, Shapefile, KML and hundreds more) with reprojection, warping and DEM utilities.

**Why it matters:** Every map, DEM and imagery pipeline goes through GDAL; gdalwarp, gdaldem and gdal_translate cover most reference-map preparation.

**Hackathon notes:** Use conda or the OSGeo Docker image to avoid version mismatches between GDAL and Python bindings.

**Concepts:** [GIS, maps and geospatial data](../concepts/gis-mapping.md), [Geodesy and coordinate frames](../concepts/geodesy.md)

**Tags:** `raster`, `vector`, `geotiff`, `cog`, `gdaldem`

**Domains:** multi

## Related

- depends_on: [PROJ](../repos/osgeo__proj.md)
- integrates_with: [Rasterio](../repos/rasterio__rasterio.md)
- integrates_with: [QGIS](../repos/qgis__qgis.md)

## Referenced by

- [elevation](../repos/bopen__elevation.md) (depends_on)
- [Cesium Terrain Builder](../repos/geo-data__cesium-terrain-builder.md) (depends_on)
- [grid_map](../repos/leggedrobotics__grid_map.md) (integrates_with)
- [OpenDroneMap (ODM)](../repos/opendronemap__odm.md) (depends_on)
- [PROJ](../repos/osgeo__proj.md) (integrates_with)
- [QGIS](../repos/qgis__qgis.md) (depends_on)
- [Rasterio](../repos/rasterio__rasterio.md) (depends_on)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
