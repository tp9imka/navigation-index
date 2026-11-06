# CesiumJS - integration card
<!-- about: repo:cesiumgs/cesium -->
One-line: a WebGL 3D globe in the browser (WGS84, terrain, 3D Tiles, time-dynamic tracks via CZML) for a situational-awareness display: true vs estimated trajectory, GNSS-denied segments, sensor footprints, all on real terrain.

| | |
|---|---|
| Install | `npm install cesium --save` (README), or the pre-built zip from cesium.com/downloads, or scoped packages `@cesium/engine` + `@cesium/widgets`. Latest release `1.147` (2026-11-02). |
| Runs on | Any modern browser with WebGL; plain static hosting. No server needed except to serve assets and data over HTTP (`file://` is treated as cross-origin, per the Offline Guide). |
| Inputs | Positions as `Cartesian3.fromDegrees(lon, lat, height_m)` (WGS84 ellipsoid height) or ECEF metres. Data sources: CZML (`CzmlDataSource`), GeoJSON (`GeoJsonDataSource`), KML/KMZ (`KmlDataSource`), glTF models, 3D Tiles tilesets (`tileset.json`). Imagery: WMS, TMS, XYZ URL templates, OpenStreetMap, Cesium ion. Terrain: quantized-mesh (`CesiumTerrainProvider`), Cesium ion world terrain, or flat ellipsoid. Time: `JulianDate`. |
| Outputs | Interactive 3D / 2D / Columbus view in a canvas; screenshots via the canvas; terrain heights via `sampleTerrain` / `sampleTerrainMostDetailed`; picking (`scene.pick`, `scene.pickPosition`) back to cartographic coordinates. |
| Key API / entry points | `new Viewer(container, {baseLayer, terrainProvider, baseLayerPicker:false, geocoder:false, timeline, animation})`; `viewer.entities.add({position, point, path, model, polyline})`; `SampledPositionProperty.addSample(JulianDate, Cartesian3)` for time-tagged tracks; `CzmlDataSource.load(urlOrJson)`; `Cesium3DTileset.fromUrl(url)`; `CesiumTerrainProvider.fromUrl(url)`; `TileMapServiceImageryProvider.fromUrl(url)` / `UrlTemplateImageryProvider`; `Transforms.eastNorthUpToFixedFrame(origin)` for local ENU to ECEF; `sampleTerrainMostDetailed(provider, cartographics)`. |
| Time to first result | Estimate: 30 min to a globe showing a CSV trajectory, assuming Node.js and a bundler (or the pre-built `Build/Cesium` folder dropped into a static page). Fully offline terrain and imagery adds hours of tile preparation. |
| License | Apache-2.0 (CesiumJS). Cesium ion content (Bing imagery, world terrain, Google photorealistic tiles) is a separate commercial service with its own terms. |

## Minimal usage

Offline viewer adapted from `Documentation/OfflineGuide/README.md`, plus a time-tagged track. Not run.

```js
import { Viewer, ImageryLayer, TileMapServiceImageryProvider, buildModuleUrl,
         SampledPositionProperty, JulianDate, Cartesian3, Color } from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

const viewer = new Viewer("cesiumContainer", {
  baseLayer: ImageryLayer.fromProviderAsync(
    TileMapServiceImageryProvider.fromUrl(buildModuleUrl("Assets/Textures/NaturalEarthII"))),
  baseLayerPicker: false,
  geocoder: false,
});

const t0 = JulianDate.fromIso8601("2026-11-06T10:00:00Z");
const est = new SampledPositionProperty();
for (const [s, lon, lat, h] of [[0, 30.50, 50.45, 300], [10, 30.51, 50.45, 300], [20, 30.52, 50.46, 310]]) {
  est.addSample(JulianDate.addSeconds(t0, s, new JulianDate()), Cartesian3.fromDegrees(lon, lat, h));
}
viewer.entities.add({ position: est, point: { pixelSize: 8, color: Color.ORANGE },
                      path: { width: 2, material: Color.ORANGE } });
viewer.clock.currentTime = t0;
viewer.zoomTo(viewer.entities);
```

## Wiring it into a nav stack

- Truth vs estimate replay: write two tracks (simulator truth and filter output) as CZML or `SampledPositionProperty` samples; colour the path segments where GNSS was denied or flagged as spoofed. Inputs typically come from [gz-sim](./gazebosim__gz-sim.md) / PX4 logs, [gym-pybullet-drones](./learnsyslab__gym-pybullet-drones.md), or GNSS outputs from [RTKLIB](./rtklibexplorer__rtklib.md).
- Local frames: simulators give ENU / NED metres. Convert with [pymap3d](./geospace-code__pymap3d.md) (`enu2geodetic`, `ned2geodetic`) before export, or use `Transforms.eastNorthUpToFixedFrame` in the browser. Note NED vs ENU sign flips.
- Heights: `Cartesian3.fromDegrees` takes height above the WGS84 ellipsoid. GNSS receivers often report MSL (geoid) heights; convert or your track floats or sinks by tens of metres depending on location.
- Live feeds: a small websocket server can push MAVLink `GLOBAL_POSITION_INT` (as in the [MAVLink to TAK sample](../../samples/mavlink-to-tak-cot/)) into a `SampledPositionProperty` or `CallbackProperty`.
- Offline terrain / basemaps: build quantized-mesh terrain from a DEM (fetched with [elevation](./bopen__elevation.md), reprojected with [GDAL](./osgeo__gdal.md)) via [cesium-terrain-builder](../../catalog/repos/geo-data__cesium-terrain-builder.md); serve imagery as TMS / XYZ tiles. [PMTiles](./protomaps__pmtiles.md) is mainly a MapLibre format; no file named like PMTiles exists in `packages/engine/Source/Scene` (checked 2026-11-06), so assume no built-in provider.

## Gotchas

- Default `Viewer` pulls Cesium ion imagery (Bing) and the geocoder from `api.cesium.com` and needs an ion access token. On an air-gapped or bad-network hackathon floor, set `baseLayer`, `baseLayerPicker:false`, `geocoder:false` up front (Offline Guide).
- Bundlers: CesiumJS loads Workers, Assets, Widgets and ThirdParty files at runtime and needs `window.CESIUM_BASE_URL` set and those folders copied to your build output (Cesium quickstart docs). Most "import Cesium with Webpack" issues (#8471, #6411 base URL regression) are this.
- Serve data over HTTP, not `file://` (issue #3935; Offline Guide).
- Ellipsoid vs geoid heights, and lon/lat argument order in `fromDegrees(lon, lat, h)`, are the usual sources of wrong-place tracks.
- Many individually animated entities get slow; the Entity API is convenient, primitives (`PointPrimitiveCollection`, `BillboardCollection`) scale better. This is general Cesium guidance, not measured here (related old issue: #1515 dynamic ellipse performance).
- Some tests and samples depend on network access (issue #9952, open).
- Google photorealistic 3D tiles and ion world terrain are licensed content; check terms before using in a public demo or derivative dataset.

## Alternatives

- [maplibre/maplibre-gl-js](./maplibre__maplibre-gl-js.md): 2D/2.5D vector maps, lighter, native PMTiles support; prefer when you do not need a globe or real 3D terrain.
- [visgl/deck.gl](../../catalog/repos/visgl__deck.gl.md): GPU data layers (many points, trips layer) over MapLibre; better for large tracks and heatmaps.
- [leaflet/leaflet](../../catalog/repos/leaflet__leaflet.md): simplest 2D raster map for a quick operator view.

Sources: `gh api repos/CesiumGS/cesium/readme`; `Documentation/OfflineGuide/README.md`; latest release metadata; `packages/engine/Source/{Core,Scene,DataSources}` listings; issue searches ("offline ion token", "CESIUM_BASE_URL", performance). Catalog: [record](../../catalog/repos/cesiumgs__cesium.md).
