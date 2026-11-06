# mil-sym-ts - integration card
<!-- about: repo:missioncommand/mil-sym-ts -->
One-line: the US Army Mission Command MIL-STD-2525 renderer in TypeScript - single-point unit/equipment icons as SVG and multi-point tactical graphics (boundaries, phase lines, areas) as GeoJSON/KML/GeoSVG for a web map, covering 2525D ch1, 2525E ch1 and APP-6D.

| | |
|---|---|
| Install | Browser/bundler: `npm install @armyc2.c5isr.renderer/mil-sym-ts-web` (latest 2.10.10, 2026-11-05, ESM `C5Ren.mjs`). Node: `npm install @armyc2.c5isr.renderer/mil-sym-ts` (latest 2.10.10, CommonJS `C5Ren.cjs`, depends on `canvas` ^3.1.0 = node-canvas). Building from source uses Windows `.bat` scripts (`buildWeb.bat`, `buildNode.bat`); default branch is `development`. |
| Runs on | Any modern browser (uses the browser canvas for text metrics) or Node.js with node-canvas (native module; prebuilt binaries for common platforms, otherwise Cairo build deps). No GPU. |
| Inputs | Symbol IDs (SIDC): 20-digit numeric 2525D/E codes (30-digit for 2525E with country code), version prefix 10 (APP-6D), 11 (2525D ch1), 15 (2525E ch1), 16 (APP-6E v2, icons only). Modifiers `Map<string,string>` keyed by `Modifiers.*` (e.g. `T_UNIQUE_DESIGNATION_1`, `Q_DIRECTION_OF_MOVEMENT`, `Z_SPEED`); attributes keyed by `MilStdAttributes.*` (`PixelSize`, `KeepUnitRatio`...). Multipoint control points as a string `"lon,lat[,alt] lon,lat ..."` in decimal degrees, plus map scale and bbox. |
| Outputs | Single point: `SVGSymbolInfo` (`getSVG()`, `getSVGDataURI()`, `getSymbolCenterPoint()`, `getSymbolBounds()`, `getImageBounds()`). Multipoint: string in KML (`OUTPUT_FORMAT_KML` 0), JSON (1), GeoJSON (2) or GeoSVG (3); or a `MilStdSymbol` object with shapes. `MSLookup` returns symbol metadata (draw rule, min/max points, applicable modifiers). |
| Key API / entry points | `MilStdIconRenderer.getInstance().RenderSVG(symbolID, modifiers, attributes): SVGSymbolInfo \| null`; `MilStdIconRenderer.getInstance().CanRender(symbolID, attributes)`; `WebRenderer.RenderSymbol(id, name, description, symbolCode, controlPoints, altitudeMode, scale, bbox, modifiers, attributes, format): string`; `WebRenderer.RenderSymbol2D(...)`, `WebRenderer.RenderMultiPointAsMilStdSymbol(...)`, `WebRenderer.RenderBasicShape(...)`; `MSLookup.getInstance()`; `SymbolID` helpers (`getSymbolSet`, ...); `RendererSettings.getInstance()`; `initialize()` is now deprecated and a no-op (data is bundled). |
| Time to first result | Estimate: 20 min to draw a unit icon on a MapLibre/Leaflet marker from npm; 1-2 h for multipoint graphics, which need scale/bbox plumbing and re-render on zoom. |
| License | Apache-2.0 (LICENSE file, npm metadata). Symbol content follows the public MIL-STD-2525 / APP-6 standards. |

## Minimal usage

Not run. Browser ESM: render a 2525D ch1 symbol as an SVG data URI for a map marker. The SIDC is an assumed example (version 11, friend, land unit, entity 121100 infantry) - check it in the [interactive tester](https://missioncommand.github.io/js-samples/singlePointTester4.html) before relying on it.

```js
import { MilStdIconRenderer, Modifiers, MilStdAttributes, WebRenderer }
  from '@armyc2.c5isr.renderer/mil-sym-ts-web';

const mods = new Map([[Modifiers.T_UNIQUE_DESIGNATION_1, 'B CO'],
                      [Modifiers.Q_DIRECTION_OF_MOVEMENT, '45']]);
const attrs = new Map([[MilStdAttributes.PixelSize, '48']]);
const info = MilStdIconRenderer.getInstance().RenderSVG('11031000001211000000', mods, attrs);
const img = new Image(); img.src = info.getSVGDataURI();          // use as marker element
const anchor = info.getSymbolCenterPoint();                        // pixel offset for the marker anchor

const geojson = WebRenderer.RenderSymbol('pl1', 'PL RED', '', '<2525D control-measure SIDC>',
  '8.50,47.36 8.56,47.38', 'clampToGround', 50000, '8.4,47.3,8.6,47.4',
  new Map(), new Map(), WebRenderer.OUTPUT_FORMAT_GEOJSON);         // string, parse and add as a source
```

## Wiring it into a nav stack

- COP map: render track icons for [MapLibre GL JS](./maplibre__maplibre-gl-js.md) markers or [CesiumJS](./cesiumgs__cesium.md) billboards; multipoint GeoJSON drops straight into a GeoJSON source (re-render on zoom since output depends on scale).
- From CoT: TAK CoT `type` strings (`a-f-G-U-C`...) map to 2525 SIDCs; [node-cot](./dfpc-coe__node-cot.md) `./2525` (`Type2525.to2525D(cotType)`) converts, then this library draws. Python/TAK side: [PyTAK](./snstac__pytak.md).
- Own-ship and estimator output: show own vehicle with a friendly symbol and its position uncertainty as a separate ellipse layer; mil symbology carries identity, not accuracy.
- Track sources: Remote ID detections ([opendroneid-core-c](./opendroneid__opendroneid-core-c.md), [drone-mesh-mapper](./colonelpanichacks__drone-mesh-mapper.md)) as unknown-affiliation air tracks; ADS-B from [readsb](./wiedehopf__readsb.md).

Catalog page: [catalog/repos/missioncommand__mil-sym-ts.md](../../catalog/repos/missioncommand__mil-sym-ts.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md), [standards](../../catalog/concepts/standards.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- Two npm packages: `-web` (ESM, browser canvas) and the plain one (CommonJS, Node, pulls native node-canvas). Installing the Node package into a browser bundle drags `canvas` in. The Node package also carries a stale dist-tag `web: 2.2.0`; do not install `...mil-sym-ts@web`.
- No 2525C: the old JavaScript 2525C renderer is retired (README). Many CoT tools and older datasets still use 2525B/C letter SIDCs (`SFGPUCI----`); convert to numeric 2525D first ([milsymbol](./spatialillusions__milsymbol.md) still draws letter SIDCs).
- APP-6E v2 (version 16) is icons only, partial.
- Multipoint rendering needs correct `scale` and `bbox`; wrong values give oversized or clipped arrowheads/teeth. Coordinates are `lon,lat` order in the control-point string.
- SSR frameworks hit `self is not defined` (#23, closed; check the version you install). Older code calling `initialize(location)` with asset URLs still works but does nothing now.
- Some basic IDs are only valid in specific versions (#21: an ID not recognised in D); pick the version prefix that matches the symbol's standard.
- Build scripts are Windows `.bat`; building from source on Linux/macOS means reading them and running the npm steps by hand. Use the npm releases.

## Alternatives

- [milsymbol](./spatialillusions__milsymbol.md) - small, fast, single-point SVG/canvas for 2525B/C/D/E and APP-6; prefer when you only need unit icons.
- [esri/joint-military-symbology-xml](../../catalog/repos/esri__joint-military-symbology-xml.md) - authoritative SIDC/symbol data tables; prefer as a lookup source, not a renderer.
- [node-cot](./dfpc-coe__node-cot.md) 2525 helpers - for CoT type <=> SIDC conversion only.

Sources: `gh api repos/missioncommand/mil-sym-ts` (Apache-2.0, default branch `development`, release v2.10.10 2026-11-05), README.md, LICENSE, package.json / package.packWeb.json / package.packNode.json, C5Ren.ts (exports, deprecated `initialize`), src/main/ts/armyc2/c5isr/renderer/MilStdIconRenderer.ts, web/render/WebRenderer.ts (`RenderSymbol` signature, output formats), renderer/utilities/SVGSymbolInfo.ts, MilStdAttributes.ts, Modifiers.ts, npm registry for both packages (2.10.10, dist-tags), issues #21, #23, #26, #28.
