# pyproj

`repo:pyproj4/pyproj` - <https://github.com/pyproj4/pyproj>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,236 | Python | MIT | 2026-11-02 | False | production | high |

Python interface to PROJ for CRS definitions, coordinate transformations and geodesic computations.

**Why it matters:** Default Python tool for lat/lon <-> UTM/ECEF/local conversions in nav prototypes.

**Hackathon notes:** pip install pyproj ships PROJ inside the wheel; reuse a Transformer object for speed.

**Concepts:** [Geodesy and coordinate frames](../concepts/geodesy.md)

**Tags:** `crs`, `transformer`, `geod`

**Domains:** multi

## Related

- depends_on: [PROJ](../repos/osgeo__proj.md)
- alternative_to: [pymap3d](../repos/geospace-code__pymap3d.md)

## Referenced by

- [pymap3d](../repos/geospace-code__pymap3d.md) (alternative_to)
- [PROJ](../repos/osgeo__proj.md) (integrates_with)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
