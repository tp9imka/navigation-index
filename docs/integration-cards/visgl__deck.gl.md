# deck.gl - integration card
<!-- about: repo:visgl/deck.gl -->
One-line: GPU layer stack for the common operating picture - thousands of live tracks (ADS-B, AIS, swarm telemetry), trails with time fade, hexbin density and 3D tiles, drawn over a MapLibre basemap or standalone.

| | |
|---|---|
| Install | `npm install deck.gl` (npm `latest` 9.4.1, 2026-10-28; GitHub "latest release" shows v9.3.12, a 9.3 maintenance build published 2026-10-30). Scoped modules: `@deck.gl/core`, `@deck.gl/layers`, `@deck.gl/geo-layers`, `@deck.gl/maplibre` (new in 9.4, PR #10566), `@deck.gl/mapbox`. Script tag: `https://unpkg.com/deck.gl@9.4.1/dist.min.js` (README uses `@latest`; pin it). Python: `pip install pydeck` (PyPI 0.9.3, Apache-2.0, requires Python >=3.8). |
| Runs on | Browser with WebGL2; WebGPU is in progress (tracker #9504, several open WebGPU bugs). Works in React, pure JS, Jupyter (pydeck). |
| Inputs | Arrays of JS objects or binary attribute buffers; accessors such as `getPosition: d => [lon, lat, alt]`. Positions are `[lng, lat, z]` in WGS84 by default (`coordinateSystem` can switch to meter offsets from an origin). GeoJSON, MVT tiles (`MVTLayer`), 3D Tiles (`Tile3DLayer`), terrain (`TerrainLayer`), H3/S2/geohash cells. |
| Outputs | Rendered canvas; picking results (`onClick`/`onHover` give the source object); no data export. |
| Key API / entry points | `new Deck({initialViewState, controller, layers})`; `deck.setProps({layers})` for updates; `new MapLibreOverlay({interleaved, layers})` from `@deck.gl/maplibre` added with `map.addControl(...)`; `ScatterplotLayer`, `PathLayer`, `IconLayer`, `TextLayer`, `GeoJsonLayer` (`@deck.gl/layers`); `TripsLayer` (props `getPath`, `getTimestamps`, `currentTime`, `trailLength`, `fadeTrail`), `MVTLayer`, `TileLayer`, `Tile3DLayer`, `H3HexagonLayer`, `GreatCircleLayer` (`@deck.gl/geo-layers`). Names confirmed in `modules/*/src/index.ts`. |
| Time to first result | Estimate: 20 min to a scatter of live tracks over a MapLibre demo basemap from a static HTML page; 2-4 h to a polished COP with trails, picking tooltips and an offline basemap. Assumes a WebSocket feed already exists. |
| License | MIT (LICENSE, "Copyright Vis.gl contributors"); GitHub metadata MIT. pydeck is Apache-2.0 on PyPI. Basemap and data licences are separate. |

## Minimal usage

Not run. Live tracks as dots plus short fading trails, over MapLibre, fed by a WebSocket emitting `{id, lon, lat, t}` (t in seconds).

```html
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.css">
<div id="map" style="height:100vh"></div>
<script type="module">
import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs';
import {MapLibreOverlay} from 'https://esm.sh/@deck.gl/maplibre@9.4.1';
import {ScatterplotLayer} from 'https://esm.sh/@deck.gl/layers@9.4.1';
import {TripsLayer} from 'https://esm.sh/@deck.gl/geo-layers@9.4.1';

const map = new maplibregl.Map({container: 'map', style: 'https://demotiles.maplibre.org/style.json', center: [8.55, 47.37], zoom: 10});
const overlay = new MapLibreOverlay({interleaved: false, layers: []});
map.addControl(overlay);
const tracks = new Map();
let now = 0;
new WebSocket('ws://localhost:8765').onmessage = (e) => {
  const m = JSON.parse(e.data);
  const tr = tracks.get(m.id) || {id: m.id, path: [], ts: []};
  tr.path.push([m.lon, m.lat]); tr.ts.push(m.t); tracks.set(m.id, tr);
  now = Math.max(now, m.t);
  const data = [...tracks.values()];
  overlay.setProps({layers: [
    new TripsLayer({id: 'trails', data, getPath: d => d.path, getTimestamps: d => d.ts, currentTime: now, trailLength: 120, widthMinPixels: 2}),
    new ScatterplotLayer({id: 'heads', data, getPosition: d => d.path.at(-1), radiusMinPixels: 4, pickable: true})
  ]});
};
</script>
```

Loading deck.gl modules from esm.sh is an untested assumption (a bundler such as Vite is the safer route); the README documents `npm install deck.gl` and the `dist.min.js` script tag. For many updates per second, batch messages and call `setProps` on `requestAnimationFrame` rather than per message.

## Wiring it into a nav stack

- ADS-B / Remote ID / AIS => COP: decode with [readsb](./wiedehopf__readsb.md), [DragonSync](./alphafox02__dragonsync.md) or AIS-catcher ([catalog](../../catalog/repos/jvde-github__ais-catcher.md)), push JSON over a WebSocket, render as `IconLayer` (heading via `getAngle`) plus `TripsLayer` trails. The same feed can go to TAK via [adsbcot](./snstac__adsbcot.md).
- Basemap: [MapLibre GL JS](./maplibre__maplibre-gl-js.md) with [PMTiles](./protomaps__pmtiles.md) or [Martin](./maplibre__martin.md); deck.gl's own `MVTLayer` can read Martin tiles directly.
- Estimator debugging: one `PathLayer` per source (GNSS, VIO, fused) to visualise divergence during a GNSS outage; [evo](./michaelgrupp__evo.md) stays the tool for numbers.
- Tracker output: [Stone Soup](./dstl__stone-soup.md) tracks converted to lon/lat render naturally as trips.
- Symbology: [milsymbol](./spatialillusions__milsymbol.md) canvases can feed `IconLayer` via `getIcon` returning `{url, width, height}`.

Catalog page: [catalog/repos/visgl__deck.gl.md](../../catalog/repos/visgl__deck.gl.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md), [gis-mapping](../../catalog/concepts/gis-mapping.md), [target-tracking](../../catalog/concepts/target-tracking.md).

## Gotchas

- MapLibre integration is mid-transition: `@deck.gl/maplibre` (`MapLibreOverlay`) appeared in 9.4 (peer `maplibre-gl ^4.5.1 || ^5 || ^6`); `MapboxOverlay` from `@deck.gl/mapbox` also works with MapLibre. Open bugs: #10733 (`@deck.gl/maplibre` `beforeId` regression vs `@deck.gl/mapbox`), #10688 (9.4.0 interleaved overlay desyncs after switching instances), #10681 (MapLibreOverlay under React StrictMode: "WebGL context already attached"), #10942 (MaskExtension with interleaved and multiple views). Start with `interleaved: false` unless you need labels drawn above deck layers.
- `TripsLayer` with a stationary vehicle: #6844 (division by zero when two consecutive coordinates are identical), #10387 and #9332 (rendering artifacts). Drop duplicate consecutive points before pushing.
- Version tags are confusing: GitHub "latest release" (v9.3.12) is older than npm `latest` (9.4.1); a v10 tracker (#10712) is open. Pin exact versions on every `@deck.gl/*` package; mixing minors breaks.
- Idle power and memory: #9084 ("very power hungry when idle"), #10355 (`Deck.finalize()` leaks the canvas context). Matters on a laptop GCS running all day.
- WebGPU is not production-ready (#9504, #11020, #10775); stay on WebGL2.
- `wrapLongitude` with trips across the antimeridian is an open issue (#5631).

## Alternatives

- [MapLibre GL JS](./maplibre__maplibre-gl-js.md) alone - enough for tens or low hundreds of features via GeoJSON sources; fewer moving parts.
- [CesiumJS](./cesiumgs__cesium.md) - prefer for true 3D airspace, orbits and time-dynamic CZML.
- [Leaflet](./leaflet__leaflet.md) - prefer for a minimal 2D view with few markers and no WebGL.

Sources: `gh api repos/visgl/deck.gl` (MIT, latest release v9.3.12 2026-10-30), npm registry for `deck.gl`, `@deck.gl/core`, `@deck.gl/layers`, `@deck.gl/mapbox`, `@deck.gl/maplibre` dist-tags, PyPI `pydeck` JSON, README.md, LICENSE, modules/maplibre/src/index.ts, modules/maplibre/src/overlay.ts, modules/maplibre/package.json, modules/mapbox/src/index.ts, modules/layers/src/index.ts, modules/geo-layers/src/index.ts, modules/geo-layers/src/trips-layer/trips-layer.ts, commit history of modules/maplibre (PR #10566), issues #10733, #10688, #10681, #10942, #6844, #10387, #9332, #9084, #10355, #9504, #11020, #10775, #10712, #5631.
