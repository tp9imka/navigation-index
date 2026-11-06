# Leaflet - integration card
<!-- about: repo:leaflet/leaflet -->
One-line: the smallest, simplest 2D web map for an operator view - raster or WMS basemap, a vehicle marker and a track polyline in a dozen lines, huge plugin ecosystem, no WebGL needed.

| | |
|---|---|
| Install | Stable: `npm install leaflet@1.9.4` (npm `latest`, released 2023-05-18), or CDN `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js` + `leaflet.css`. Next major: `npm install leaflet@2.0.0-beta.1` (npm `beta` tag, 2026-11-02; `main` branch package.json is `2.0.0-beta.1`). |
| Runs on | Any browser; DOM/SVG/Canvas rendering, no WebGL. 2.0 targets Baseline 2022 browsers (Safari 15.4+), IE dropped (MIGRATION.md). |
| Inputs | Raster XYZ tiles (`{z}/{x}/{y}.png`), WMS (`WMSTileLayer` in 2.0, `L.tileLayer.wms` in 1.x), GeoJSON, image overlays. Coordinates are `[lat, lng]` WGS84; default CRS EPSG:3857, others via `crs` option or Proj4Leaflet plugin. No native vector tiles (plugin needed). |
| Outputs | Interactive map in a `<div>`; events (click, move, zoom); `latLngToContainerPoint` for pixel math. |
| Key API / entry points | 1.x: `L.map(id).setView([lat,lng], z)`, `L.tileLayer(url, opts)`, `L.marker(ll)`, `L.polyline(lls)`, `L.geoJSON(obj)`, `layer.setLatLng(ll)` / `polyline.addLatLng(ll)`. 2.0 (ESM, classes): `new LeafletMap(id)`, `new TileLayer(url, opts)`, `new Marker(ll)`, `new Polyline(lls)`, `new GeoJSON(obj)`, `new Circle(ll, {radius})` (exports confirmed in `src/Leaflet.js` on `main`). |
| Time to first result | Estimate: 10 min to a map with a moving marker fed from a WebSocket, assuming any static HTTP server and an online tile source; 1 h to a fully offline map if you already have a raster tile folder or a tile server. |
| License | BSD-2-Clause (LICENSE, "Copyright (c) 2010-2026, Volodymyr Agafonkin"); GitHub metadata agrees. Basemap tiles carry their own terms (OSM tiles: ODbL data + OSMF tile usage policy). |

## Minimal usage

Not run. Leaflet 1.9.4 (global `L`), track and pose from a WebSocket emitting `{lat, lon}` JSON.

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<div id="map" style="height:100vh"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map').setView([47.37, 8.55], 14);
L.tileLayer('http://localhost:8080/styles/basic-preview/{z}/{x}/{y}.png', {maxZoom: 19}).addTo(map);
const track = L.polyline([], {weight: 3}).addTo(map);
const pose = L.circleMarker([47.37, 8.55], {radius: 6}).addTo(map);
new WebSocket('ws://localhost:8765').onmessage = (e) => {
  const m = JSON.parse(e.data);
  track.addLatLng([m.lat, m.lon]);
  pose.setLatLng([m.lat, m.lon]);
};
</script>
```

The tile URL above assumes a local [tileserver-gl](./maptiler__tileserver-gl.md) rendering raster tiles; any XYZ raster source works.

## Wiring it into a nav stack

- Estimator => browser: publish fused lat/lon (from [robot_localization](./cra-ros-pkg__robot_localization.md), an autopilot EKF via [MAVROS](./mavlink__mavros.md) or [pymavlink](./ardupilot__pymavlink.md)) as JSON over a WebSocket. Convert local ENU to geodetic with [pymap3d](./geospace-code__pymap3d.md) or [GeographicLib](./geographiclib__geographiclib.md) `LocalCartesian` first.
- Basemap offline: raster tiles from [tileserver-gl](./maptiler__tileserver-gl.md) (renders vector MBTiles/PMTiles to PNG) or [Martin](./maplibre__martin.md) serving a raster MBTiles; orthophotos tiled with [GDAL](./osgeo__gdal.md) (`gdal2tiles`).
- Military symbology: [milsymbol](./spatialillusions__milsymbol.md) renders SVG/canvas icons you pass to `L.divIcon` / `L.icon`.
- Routes: draw [OSRM](./project-osrm__osrm-backend.md) or [Valhalla](./valhalla__valhalla.md) geometry (`geometries=geojson`) with `L.geoJSON`.
- Python notebooks: folium (PyPI `folium` 0.20.0) and ipyleaflet (PyPI 0.20.0) wrap Leaflet; not indexed here.

Catalog page: [catalog/repos/leaflet__leaflet.md](../../catalog/repos/leaflet__leaflet.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- 1.x vs 2.0 split: almost every tutorial and plugin targets 1.x (`L.marker(...)`, global `L`). 2.0 `dist/leaflet.js` is an ES module, a plain `<script>` tag fails, the factory functions are gone and there is no default export (MIGRATION.md sections 1-2). Use `dist/leaflet-global.js` in 2.0 if you need `L`. Plugins expecting `window.L` break under the ESM build. Pin `1.9.4` for a hackathon unless you need 2.0.
- OSM tile servers now block requests without a referrer: issue #10156 ("OpenStreetMap Foundation servers now enforced referer policy", closed 2026-03-19) and #9882. 1.9.4 defaults `referrerPolicy: false`; pass `referrerPolicy: 'strict-origin-when-cross-origin'` to `L.tileLayer` (option exists in 1.9.4 `TileLayer.js`). 2.0 makes that the default. Better: use your own tiles for anything offline or heavy.
- Coordinate order is `[lat, lng]`, the opposite of GeoJSON, MapLibre, deck.gl and OSRM (`lon,lat`). `L.geoJSON` handles the swap for GeoJSON input; hand-built arrays do not.
- No rotation of the map and no built-in marker heading: core has no bearing support (feature request #9537 closed). Use a rotated `divIcon` (CSS transform) or a plugin; if you need map rotation or 3D, use [MapLibre GL JS](./maplibre__maplibre-gl-js.md).
- Thousands of live markers in DOM mode get slow; use `circleMarker` with `renderer: L.canvas()` (2.0: `renderer: new Canvas()`; `preferCanvas` removed in 2.0) or switch to [deck.gl](./visgl__deck.gl.md).
- 2.0 silent changes worth knowing for track rendering: `smoothFactor` default 1 => 0.5, `latLngToContainerPoint` returns fractional pixels (MIGRATION.md section 9).

## Alternatives

- [MapLibre GL JS](./maplibre__maplibre-gl-js.md) - vector tiles, rotation, 3D terrain, globe; prefer when you have vector tiles or need heading-up display.
- [OpenLayers](../../catalog/repos/openlayers__openlayers.md) - prefer for OGC services (WMS/WMTS/WFS) and non-Web-Mercator projections.
- [CesiumJS](./cesiumgs__cesium.md) - prefer for 3D air tracks with altitude.

Sources: `gh api repos/Leaflet/Leaflet` (license BSD-2-Clause, latest release v1.9.4 2023-05-18), npm registry `leaflet` dist-tags (latest 1.9.4, beta 2.0.0-beta.1), README.md, LICENSE, package.json (main), MIGRATION.md (sections 1-3, 9), src/Leaflet.js (main), src/layer/tile/TileLayer.js at v1.9.4 (referrerPolicy), PyPI folium/ipyleaflet JSON, issues #10156, #9882, #9537, #10435.
