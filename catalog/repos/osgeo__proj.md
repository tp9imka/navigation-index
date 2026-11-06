# PROJ

`repo:osgeo/proj` - <https://github.com/osgeo/proj>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,033 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.

**Why it matters:** Correct datum and projection handling (WGS84, ITRF, local grids, UTM) is foundational for any nav system that mixes map sources.

**Hackathon notes:** Bundle the proj-data grids offline if your demo has no internet.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [osgeo__proj](../../docs/integration-cards/osgeo__proj.md) (integration-cards)

**Concepts:** [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `crs`, `datum`, `utm`, `itrf`

**Domains:** multi

## Related

- integrates_with: [pyproj](../../catalog/repos/pyproj4__pyproj.md)
- integrates_with: [GDAL](../../catalog/repos/osgeo__gdal.md)

## Referenced by

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [GDAL](../../catalog/repos/osgeo__gdal.md) (depends_on)
- [pyproj](../../catalog/repos/pyproj4__pyproj.md) (depends_on)
- [QGIS](../../catalog/repos/qgis__qgis.md) (depends_on)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
