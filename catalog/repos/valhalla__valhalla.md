# Valhalla

`repo:valhalla/valhalla` - <https://github.com/valhalla/valhalla>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,419 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

Tiled OSM routing engine with dynamic costing per request (auto, truck, pedestrian, bicycle), isochrones and map matching.

**Why it matters:** Request-time costing makes it easy to avoid areas or prefer terrain types, and its map-matching snaps noisy tracks to roads.

**Hackathon notes:** Docker images available; build tiles for a region once and run offline. Elevation tiles enable grade-aware costing.

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `routing`, `isochrones`, `map-matching`, `osm`

**Domains:** ground, dismounted

## Related

- alternative_to: [OSRM](../repos/project-osrm__osrm-backend.md)
- alternative_to: [GraphHopper](../repos/graphhopper__graphhopper.md)

## Referenced by

- [GraphHopper](../repos/graphhopper__graphhopper.md) (alternative_to)
- [OSRM](../repos/project-osrm__osrm-backend.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
