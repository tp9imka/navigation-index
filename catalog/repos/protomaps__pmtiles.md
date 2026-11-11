# PMTiles

`repo:protomaps/pmtiles` - <https://github.com/protomaps/pmtiles>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 3,105 | TypeScript | NOASSERTION | 2026-09-16 | False | production | high |

Single-file tile archive format and tooling, served by HTTP range requests from static storage, with JS/Go readers and extraction CLI.

**Why it matters:** Ship an entire regional basemap as one file on a USB stick or static server - ideal for disconnected ops.

**Build notes:** pmtiles extract from a planet build to cut your AOI; load with the MapLibre protocol plugin.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [protomaps__pmtiles](../../docs/integration-cards/protomaps__pmtiles.md) (integration-cards)

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `pmtiles`, `offline`, `static-hosting`

**Domains:** multi

## Related

- integrates_with: [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md)
- integrates_with: [Planetiler](../../catalog/repos/onthegomap__planetiler.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Demo dashboard](../../templates/demo-dashboard/README.md) (mentions)
- [Offline kit](../../templates/offline-kit/README.md) (mentions)
- [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md) (integrates_with)
- [Martin](../../catalog/repos/maplibre__martin.md) (integrates_with)
- [Planetiler](../../catalog/repos/onthegomap__planetiler.md) (integrates_with)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-09._
