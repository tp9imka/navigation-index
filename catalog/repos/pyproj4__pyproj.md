# pyproj

`repo:pyproj4/pyproj` - <https://github.com/pyproj4/pyproj>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,236 | Python | MIT | 2026-11-02 | False | production | high |

Python interface to PROJ for CRS definitions, coordinate transformations and geodesic computations.

**Why it matters:** Default Python tool for lat/lon <-> UTM/ECEF/local conversions in nav prototypes.

**Hackathon notes:** pip install pyproj ships PROJ inside the wheel; reuse a Transformer object for speed.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [pyproj4__pyproj](../../docs/integration-cards/pyproj4__pyproj.md) (integration-cards)

**Concepts:** [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md)

**Tags:** `crs`, `transformer`, `geod`

**Domains:** multi

## Related

- depends_on: [PROJ](../../catalog/repos/osgeo__proj.md)
- alternative_to: [pymap3d](../../catalog/repos/geospace-code__pymap3d.md)

## Referenced by

- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [pymap3d](../../catalog/repos/geospace-code__pymap3d.md) (alternative_to)
- [PROJ](../../catalog/repos/osgeo__proj.md) (integrates_with)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
