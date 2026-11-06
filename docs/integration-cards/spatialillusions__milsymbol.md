# milsymbol - integration card
<!-- about: repo:spatialillusions/milsymbol -->
One-line: dependency-free JavaScript that renders MIL-STD-2525 / APP-6 unit symbols to SVG or Canvas from a SIDC string; drop it into a Leaflet/MapLibre/Cesium marker to give your web COP proper symbology in minutes.

| | |
|---|---|
| Install | `npm install milsymbol` (package.json version 3.0.5 on master). ESM `index.js`, UMD `dist/milsymbol.js`, types `index.d.ts`. CDN: `https://cdn.jsdelivr.net/npm/milsymbol@3.0.5/dist/milsymbol.js`. |
| Runs on | Any browser or Node.js; README also lists Java ScriptEngine and QtJSEngine. No external deps. |
| Inputs | SIDC: 30-digit numeric (2525D/E, APP-6 D/E) or 15-character letter codes (2525C/APP-6 B); options object: `size`, `quantity`, `direction` (deg), `speed`, `uniqueDesignation`, `staffComments`, `additionalInformation`, `type`, `dtg`, `location`, `fill`, `frame`, `outlineWidth`, ... |
| Outputs | `asSVG()` string, `asCanvas()` element, `getAnchor()` {x, y} offset for correct placement, `getSize()`. |
| Key API / entry points | `new ms.Symbol(sidc, options)`, `.setOptions(options)`, `.asSVG()`, `.asCanvas()`, `.getAnchor()`, `.getSize()`, `.isValid()`. Examples under `examples/`: `leaflet-divicons`, `leaflet-imageicons`, `openlayers`, `arcgis3d`, `es6-import`, `d3-list`, `situation.json`. |
| Time to first result | Estimate: 15-30 min to show symbols on a Leaflet map from a JSON track list, starting from `examples/leaflet-divicons`. |
| License | MIT. |

## Minimal usage
Based on README calls; Leaflet divIcon pattern as in `examples/leaflet-divicons`. Not run.

```html
<script src="https://cdn.jsdelivr.net/npm/milsymbol@3.0.5/dist/milsymbol.js"></script>
<script>
  // track = {lat, lon, sidc, course_deg, id} e.g. from your Stone Soup / ADS-B / Remote ID feed
  function marker(track) {
    const sym = new ms.Symbol(track.sidc, { size: 30, direction: track.course_deg,
                                             uniqueDesignation: track.id });
    const a = sym.getAnchor();
    const icon = L.divIcon({ className: "", html: sym.asSVG(), iconAnchor: [a.x, a.y] });
    return L.marker([track.lat, track.lon], { icon });
  }
</script>
```

## Wiring it into a nav stack
- Map libraries: [Leaflet](../../catalog/repos/leaflet__leaflet.md) (examples ship), [MapLibre GL JS](./maplibre__maplibre-gl-js.md) (render `asCanvas()` to an image and `map.addImage`), [Cesium](./cesiumgs__cesium.md) billboards for 3D.
- Track sources: [Stone Soup](./dstl__stone-soup.md) tracks, [readsb](./wiedehopf__readsb.md) `aircraft.json`, Remote ID detections, own-ship from [MAVROS](./mavlink__mavros.md) / [pymavlink](./ardupilot__pymavlink.md). [GoATAK](./kdudkov__goatak.md)'s web client already uses milsymbol with Leaflet.
- SIDC lookup tables and official names: [joint-military-symbology-xml](../../catalog/repos/esri__joint-military-symbology-xml.md).
- Catalog: [milsymbol page](../../catalog/repos/spatialillusions__milsymbol.md).

## Gotchas
- Since 3.0 all SIDC versions are rendered as close as possible to 2525E / APP-6 E / FM 1-02.2, so older-standard reference figures may look slightly different (README).
- Known symbology bugs: open #317 (wrong SIDC codes for cyberspace main icon parts); closed #316 (Suspect colour vs APP-6(E)).
- Package is `"type": "module"`; old `require('milsymbol')` code may need the UMD `dist/` file.
- Stack, reinforced/reduced and country-flag extensions shown on the author's unit generator are closed source (README).

## Alternatives
- [joint-military-symbology-xml](../../catalog/repos/esri__joint-military-symbology-xml.md): Esri's symbol definitions and SVG assets, for GIS desktop styles.
- Let the TAK client do symbology: send correct CoT types via [PyTAK](./snstac__pytak.md) and ATAK renders them.

Sources: `README.md`, `package.json`, repo tree (`examples/`), issue search (#317, #316).
