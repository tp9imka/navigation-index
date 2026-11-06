# MapLibre GL JS - integration card
<!-- about: repo:maplibre/maplibre-gl-js -->
One-line: open-source WebGL2 map in the browser for the operator view - offline vector or raster basemap, live vehicle track and uncertainty, 3D terrain and globe - with no API key.

| | |
|---|---|
| Install | `npm install maplibre-gl` (latest v6.16.0), or ESM from a CDN pinned to a version: `import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs'` plus the matching `dist/maplibre-gl.css`. Since 6.0.0 (2026-07-22) only the ESM build is published. |
| Runs on | Any browser or webview with WebGL2 (WebGL1 dropped in 6.0.0). No server needed beyond static file hosting. Native mobile/desktop is the separate maplibre-native project. |
| Inputs | Style JSON (MapLibre style spec v8): vector tiles (MVT via XYZ, TileJSON or `pmtiles://`), raster tiles, `raster-dem` (terrarium or mapbox terrain-RGB) for 3D terrain, GeoJSON (in-memory or URL), images/video/canvas sources. Coordinates are `[lng, lat]` WGS84. |
| Outputs | Rendered interactive map; events (click, move); `queryRenderedFeatures` results; canvas for screenshots. |
| Key API / entry points | `new maplibregl.Map({container, style, center:[lng,lat], zoom})`; `map.on('load', fn)`; `map.addSource(id, spec)` / `map.addLayer(layer, beforeId?)`; `map.getSource(id).setData(geojson): Promise<void>` and `updateData(diff)` for incremental GeoJSON updates; `new maplibregl.Marker().setLngLat(ll).setRotation(deg).addTo(map)`; `map.setTerrain({source, exaggeration})`; `map.setProjection({type: 'globe'})`; `maplibregl.addProtocol(name, loadFn)` (custom URL schemes, used by PMTiles); `maplibregl.setWorkerUrl(url)`. |
| Time to first result | Estimate: 15 min to a map with a moving marker using the demo style; 1-2 h to a fully offline map (local PMTiles, glyphs, sprites, style). Assumes Node or a static HTTP server. |
| License | BSD-3-Clause (LICENSE.txt); GitHub metadata reports NOASSERTION. |

## Minimal usage

Not run. Draw an estimator track and current pose, updating from a WebSocket that emits `{lon, lat, heading_deg}` JSON.

```html
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.css">
<div id="map" style="height:100vh"></div>
<script type="module">
import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.16.0/dist/maplibre-gl.mjs';
const map = new maplibregl.Map({container: 'map', style: 'https://demotiles.maplibre.org/style.json', center: [8.55, 47.37], zoom: 13});
const track = {type: 'FeatureCollection', features: [{type: 'Feature', geometry: {type: 'LineString', coordinates: []}}]};
const pose = new maplibregl.Marker().setLngLat([8.55, 47.37]).addTo(map);
map.on('load', () => {
  map.addSource('track', {type: 'geojson', data: track});
  map.addLayer({id: 'track', type: 'line', source: 'track', paint: {'line-width': 3}});
  new WebSocket('ws://localhost:8765').onmessage = (e) => {
    const m = JSON.parse(e.data);
    track.features[0].geometry.coordinates.push([m.lon, m.lat]);
    map.getSource('track').setData(track);
    pose.setLngLat([m.lon, m.lat]).setRotation(m.heading_deg);
  };
});
</script>
```

For an offline basemap swap the demo style for a local style whose source is `pmtiles://...` after registering the PMTiles protocol (see the [PMTiles card](./protomaps__pmtiles.md)).

## Wiring it into a nav stack

- Estimator => browser: publish fused position (from [robot_localization](./cra-ros-pkg__robot_localization.md), a [GTSAM](./borglab__gtsam.md) smoother, an autopilot EKF over MAVLink) as JSON on a WebSocket; ROS users typically go through rosbridge. Convert local ENU/NED to lon/lat first with [pymap3d](./geospace-code__pymap3d.md) - MapLibre only takes WGS84 `[lng, lat]`.
- Side-by-side truth vs estimate vs GNSS: one GeoJSON source per stream, distinct line colours. Covariance ellipses are just polygons you compute and push the same way. This is the cheapest compelling demo of a GNSS-outage or spoofing detector.
- Basemap: [PMTiles](./protomaps__pmtiles.md) AOI extract for vector; orthophoto or hillshade from [GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md) as raster tiles; DEM as `raster-dem` for 3D terrain.
- For TAK-based teams, MapLibre is the custom web view; the CoT route is in [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/).
- For true 3D (airspace volumes, orbits, sensor frusta), [CesiumJS](./cesiumgs__cesium.md) is the better fit.

Catalog page: [catalog/repos/maplibre__maplibre-gl-js.md](../../catalog/repos/maplibre__maplibre-gl-js.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- v6 is ESM-only: `<script src=".../maplibre-gl.js">` and the `maplibregl` global from UMD are gone (CHANGELOG 6.0.0). Most tutorials and Stack Overflow answers predate this; pin `@5` if you must copy UMD examples, or use `type="module"` as above.
- Worker loading under bundlers: v6 loads its worker as a separate module; issues #8018 (map hangs silently when the worker fails to load) and #8126 (Next.js Turbopack) were closed, but if `load` never fires, check the worker URL first (`setWorkerUrl`).
- `GeoJSONSource.setData` lost its second argument and now returns a Promise (6.0.0). For high-rate tracks use `updateData(diff)` or throttle to a few Hz; re-sending a growing LineString every message gets slow.
- WebGL2 required; the `Map` constructor throws `GPUInitializationError` when the context cannot be created. Some locked-down or VM browsers fail here.
- Offline is more than tiles: the style also references `glyphs` (fonts) and `sprite` URLs. Without local copies, labels and icons silently disappear.
- Coordinate order is `[lng, lat]` everywhere, the opposite of most nav code that writes lat first.
- Do not backport code from mapbox-gl-js v2+ (non-OSS license); the README calls this out explicitly.

## Alternatives

- [OpenLayers](../../catalog/repos/openlayers__openlayers.md) - better for OGC services (WMS/WMTS), arbitrary projections and raster analysis in the browser; prefer for GIS-heavy views.
- [CesiumJS](./cesiumgs__cesium.md) - 3D globe with time-dynamic entities; prefer for air and space tracks with altitude.
- [maplibre/martin](../../catalog/repos/maplibre__martin.md) or [tileserver-gl](../../catalog/repos/maptiler__tileserver-gl.md) - not alternatives but the server half if a PMTiles file is not enough.

Sources: `gh api repos/maplibre/maplibre-gl-js` (license, release v6.16.0, v6.0.0 date 2026-07-22), README.md, LICENSE.txt, CHANGELOG.md (6.0.0 and 4.0.0 breaking changes), src/index.ts (exports), src/ui/map.ts and src/ui/marker.ts (method signatures), src/source/geojson_source.ts (setData/updateData), issues #8018, #8126, #8168.
