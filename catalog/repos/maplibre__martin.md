# Martin

`repo:maplibre/martin` - <https://github.com/maplibre/martin>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 4,093 | Rust | Apache-2.0 | 2026-11-23 | False | production | high |

Fast Rust tile server for PostGIS, MBTiles and PMTiles sources, with tile generation and mbtiles tooling.

**Why it matters:** Serves live PostGIS layers (tracks, zones) as vector tiles alongside static basemaps.

**Build notes:** Single binary or docker; point at a PostGIS table to stream dynamic features.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [maplibre__martin](../../docs/integration-cards/maplibre__martin.md) (integration-cards)

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `tile-server`, `postgis`, `pmtiles`, `rust`

**Domains:** multi

## Related

- alternative_to: [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md)
- integrates_with: [PMTiles](../../catalog/repos/protomaps__pmtiles.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md) (integrates_with)
- [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md) (alternative_to)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-23._
