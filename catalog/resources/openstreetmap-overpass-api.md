# OpenStreetMap data via the Overpass API

`res:openstreetmap-overpass-api` - dataset - <https://wiki.openstreetmap.org/wiki/Overpass_API>

**By:** OpenStreetMap contributors - **Year:** ? - **Level:** intro - **Access:** open

A read-only query API over the OpenStreetMap database that returns features (coastlines, bridges, wind turbines, buoys) inside a bounding box. The USV GNSS-denied sample builds its radar chart and landmark set from Overpass queries; OSM data is under ODbL with attribution.

## Key takeaways

- Quick way to build a real chart or landmark map for any region
- Public endpoints rate-limit; keep fallbacks and cache results
- If the simulated sensor sees the same OSM map the matcher uses, error numbers are optimistic

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md)

**Tags:** `openstreetmap`, `overpass`, `odbl`, `landmarks`, `coastline`

## Related

- dataset_for: [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md)
- has_code: [OSMnx](../../catalog/repos/gboeing__osmnx.md)

_Indexed by lane(s): datasets-used_
