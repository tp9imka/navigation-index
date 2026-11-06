# Planetiler

`repo:onthegomap/planetiler` - <https://github.com/onthegomap/planetiler>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,243 | Java | Apache-2.0 | 2026-11-05 | False | production | medium |

Fast vector tile generator that builds OpenMapTiles-compatible tilesets from OSM extracts on a single machine.

**Why it matters:** Build your own up-to-date offline basemap for an AOI in minutes.

**Hackathon notes:** planetiler --download --area=<region> --output=<name>.pmtiles builds mbtiles or pmtiles; the jar needs Java 25+, the Homebrew, single-file and Docker launchers need no Java. The first run downloads about 1 GB of ocean and Natural Earth data.

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `vector-tiles`, `osm`, `openmaptiles`

**Domains:** multi

## Related

- integrates_with: [PMTiles](../../catalog/repos/protomaps__pmtiles.md)
- integrates_with: [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md)

## Referenced by

- [PMTiles](../../catalog/repos/protomaps__pmtiles.md) (integrates_with)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
