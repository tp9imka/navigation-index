# MapLibre GL JS

`repo:maplibre/maplibre-gl-js` - <https://github.com/maplibre/maplibre-gl-js>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 12,032 | TypeScript | NOASSERTION | 2026-11-05 | False | production | high |

Open-source WebGL vector tile map renderer (fork of Mapbox GL JS v1) with styles, 3D terrain and globe view.

**Why it matters:** Fast, license-clean 2D/2.5D web map for C2 dashboards, works fully offline with your own tiles.

**Hackathon notes:** Pair with martin or tileserver-gl and a PMTiles extract for an offline basemap.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [maplibre__maplibre-gl-js](../../docs/integration-cards/maplibre__maplibre-gl-js.md) (integration-cards)

**Concepts:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `vector-tiles`, `webgl`, `maplibre-style`

**Domains:** multi

## Related

- integrates_with: [Martin](../../catalog/repos/maplibre__martin.md)
- integrates_with: [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md)
- integrates_with: [PMTiles](../../catalog/repos/protomaps__pmtiles.md)
- alternative_to: [OpenLayers](../../catalog/repos/openlayers__openlayers.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [CesiumJS](../../catalog/repos/cesiumgs__cesium.md) (alternative_to)
- [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md) (integrates_with)
- [OpenLayers](../../catalog/repos/openlayers__openlayers.md) (alternative_to)
- [PMTiles](../../catalog/repos/protomaps__pmtiles.md) (integrates_with)
- [deck.gl](../../catalog/repos/visgl__deck.gl.md) (integrates_with)
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) (uses)
- [Fixed-wing golden demo: ArduPlane 4.6.3 SITL on a 27.6 km route, coherent GPS drag, golden-demo monitor, EKF3 switch to ExternalNav fed by measured day (VPAIR) and night (thermal) geoloc fix models vs airspeed dead reckoning only](../../catalog/samples/golden-demo-fixedwing.md) (uses)
- [Golden demo on PX4 v1.17 SIH: coherent GPS drag via HIL_GPS, integrity monitor (SS + PL, GNSS-vs-VIO velocity), EKF2 switch from GNSS to external vision, comparison with ArduPilot, dashboard replay](../../catalog/samples/golden-demo-px4.md) (uses)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
