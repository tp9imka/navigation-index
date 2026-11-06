# GraphHopper

`repo:graphhopper/graphhopper` - <https://github.com/graphhopper/graphhopper>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6,755 | Java | Apache-2.0 | 2026-11-05 | False | production | medium |

Java OSM routing engine usable as library or server, with custom models for per-request costing and map matching.

**Why it matters:** Embeddable routing on the JVM, relevant for dismounted navigation apps; on-device Android routing is no longer officially supported (last Android demo is v1.0).

**Hackathon notes:** Single jar + OSM pbf; custom model JSON lets you penalize road classes or areas.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `routing`, `osm`, `android`, `custom-model`

**Domains:** ground, dismounted

## Related

- alternative_to: [Valhalla](../../catalog/repos/valhalla__valhalla.md)

## Referenced by

- [OSRM](../../catalog/repos/project-osrm__osrm-backend.md) (alternative_to)
- [Valhalla](../../catalog/repos/valhalla__valhalla.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
