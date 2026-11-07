# Valhalla

`repo:valhalla/valhalla` - <https://github.com/valhalla/valhalla>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,419 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

Tiled OSM routing engine with dynamic costing per request (auto, truck, pedestrian, bicycle), isochrones and map matching.

**Why it matters:** Request-time costing makes it easy to avoid areas or prefer terrain types, and its map-matching snaps noisy tracks to roads.

**Hackathon notes:** Docker images available; build tiles for a region once and run offline. Elevation tiles enable grade-aware costing.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [valhalla__valhalla](../../docs/integration-cards/valhalla__valhalla.md) (integration-cards)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `routing`, `isochrones`, `map-matching`, `osm`

**Domains:** ground, dismounted

## Related

- alternative_to: [OSRM](../../catalog/repos/project-osrm__osrm-backend.md)
- alternative_to: [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md) (alternative_to)
- [OSRM](../../catalog/repos/project-osrm__osrm-backend.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
