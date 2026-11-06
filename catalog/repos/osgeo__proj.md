# PROJ

`repo:osgeo/proj` - <https://github.com/osgeo/proj>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,033 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.

**Why it matters:** Correct datum and projection handling (WGS84, ITRF, local grids, UTM) is foundational for any nav system that mixes map sources.

**Hackathon notes:** Bundle the proj-data grids offline if your demo has no internet.

**Concepts:** [Geodesy and coordinate frames](../concepts/geodesy.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `crs`, `datum`, `utm`, `itrf`

**Domains:** multi

## Related

- integrates_with: [pyproj](../repos/pyproj4__pyproj.md)
- integrates_with: [GDAL](../repos/osgeo__gdal.md)

## Referenced by

- [GDAL](../repos/osgeo__gdal.md) (depends_on)
- [pyproj](../repos/pyproj4__pyproj.md) (depends_on)
- [QGIS](../repos/qgis__qgis.md) (depends_on)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
