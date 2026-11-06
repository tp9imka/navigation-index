# node-cot - integration card
<!-- about: repo:dfpc-coe/node-cot -->
One-line: TypeScript library (npm `@tak-ps/node-cot`) that converts Cursor-on-Target between XML, TAK Protobuf, a typed JSON object and GeoJSON, plus TAK data packages - the shortest path from a GeoJSON track in a Node/web app to something ATAK/WinTAK/TAK Server displays.

| | |
|---|---|
| Install | `npm install @tak-ps/node-cot` (npm latest 14.56.0, 2026-10-22; package.json `"type": "module"`, `engines.node >= 22`). ESM only. Subpath exports: `@tak-ps/node-cot/cot`, `/2525`, `/normalize_geojson`, `/from_geojson`, `/to_geojson`. |
| Runs on | Node.js 22+ (any OS/arch). Pure TS/JS, no native deps. Browser use is plausible through a bundler but not documented. |
| Inputs | CoT XML (`string`/`Buffer`), TAK Protobuf v1 `TakMessage` (`Uint8Array`), GeoJSON `Feature` (Point, LineString, Polygon; no Multi*) with properties `type`, `how`, `callsign`, `time`/`start`/`stale`, `speed` (m/s), `course` (deg), `remarks`, simplestyle colours; TAK data package `.zip`. |
| Outputs | `CoT` object (`.raw` is xml-js compact JSON), CoT XML string, Protobuf `Uint8Array`, GeoJSON `Feature` (WGS84 `[lon, lat, hae]`), data packages, basemap and iconset XML. Only serialization - no TCP/TLS/UDP transport. |
| Key API / entry points | `CoTParser.from_xml(raw, opts?) => CoT`; `CoTParser.to_xml(cot, opts?) => string`; `await CoTParser.from_geojson(feature, opts?) => CoT`; `await CoTParser.to_geojson(cot, opts?) => Feature`; `await CoTParser.to_proto(cot, version = 1) => Uint8Array`; `await CoTParser.from_proto(raw, version = 1) => CoT`; `CoTParser.validate(...)`, `CoTParser.normalize_geojson(...)`; on `CoT`: `uid()`, `type()`, `callsign()`, `position()`, `sensor()`, `addDest()`, `addLink()`, `is_stale()`, `is_uav()`, `is_hostile()`..., `CoT.ping()`; `DataPackage`; builders for chat, route, fileshare, force-delete. CLI `cot` (`cli.ts`, shebang `tsx`): `package validate <file>.zip`, `feature convert <input.geojson\|input.cot>`. |
| Time to first result | Estimate: 15 min to convert a GeoJSON point to CoT XML and see it in ATAK/WinTAK, assuming a reachable TAK Server or ATAK on the same LAN and Node 22 installed. |
| License | MIT (LICENSE, "Copyright (c) 2021 Vidterra"; package.json `license: MIT`). Dependencies include milsymbol (MIT) and others; check transitive licences if redistributing. |

## Minimal usage

Not run. GeoJSON detection => CoT XML and Protobuf, then back to GeoJSON. API names from `lib/parser.ts`.

```js
import { CoTParser } from '@tak-ps/node-cot';

const feature = {
  type: 'Feature', id: 'rid-aa-bb-cc-dd-ee-ff',
  properties: { type: 'a-u-A-M-F-Q', how: 'm-g', callsign: 'RID TEST-SERIAL',
                speed: 12.0, course: 270, remarks: 'Remote ID self-report',
                stale: new Date(Date.now() + 60_000).toISOString() },
  geometry: { type: 'Point', coordinates: [8.5421, 47.3712, 520] }
};

const cot = await CoTParser.from_geojson(feature);
console.log(CoTParser.to_xml(cot));                 // <event ...><point lat=.. lon=.. hae=../>...
const proto = await CoTParser.to_proto(cot);        // TakMessage bytes, no stream framing
const back = await CoTParser.to_geojson(CoTParser.from_xml(CoTParser.to_xml(cot)));
```

Send the XML string over TCP/TLS to a TAK Server (8087/8089) or as UDP multicast `239.2.3.1:6969` for mesh SA; that transport is your code.

## Wiring it into a nav stack

- Estimator / sensor => TAK: publish vehicle pose or detections as GeoJSON in a Node service, convert with `from_geojson`, send to [OpenTAKServer](./brian7704__opentakserver.md), [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md) or the TAK Product Center server. The Python counterpart is [PyTAK](./snstac__pytak.md); MAVLink-sourced CoT is shown in [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/).
- Remote ID / C-UAS: map receiver output ([drone-mesh-mapper](./colonelpanichacks__drone-mesh-mapper.md) `/api/detections`, [opendroneid-core-c](./opendroneid__opendroneid-core-c.md) structs) to an air-track CoT type with `speed`/`course`; set `stale` to a few seconds beyond the broadcast interval.
- TAK => web map: consume CoT from a TAK Server stream, `to_geojson`, render in [MapLibre GL JS](./maplibre__maplibre-gl-js.md); use [mil-sym-ts](./missioncommand__mil-sym-ts.md) or [milsymbol](./spatialillusions__milsymbol.md) for 2525 icons (the `./2525` subpath exposes SIDC/CoT-type helpers).
- [dfpc-coe/CloudTAK](../../catalog/repos/dfpc-coe__cloudtak.md) is built on this library and is the reference for a browser COP with ETL connectors.

Catalog page: [catalog/repos/dfpc-coe__node-cot.md](../../catalog/repos/dfpc-coe__node-cot.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md), [standards](../../catalog/concepts/standards.md).

## Gotchas

- The README usage example `new CoT(\`<event ...>\`)` is stale: the `CoT` constructor now takes the compact-JSON object (`Static<typeof JSONCoT>`), not an XML string. Parse XML with `CoTParser.from_xml()`.
- Fast-moving major versions (v14.x, several releases per month per CHANGELOG); pin an exact version for a hackathon build.
- `engines.node >= 22` and ESM only; CommonJS `require()` and older Node fail. The `cot` CLI is a `.ts` file with `#!/usr/bin/env tsx`, so it needs `tsx` available.
- `to_proto` returns the bare `TakMessage`; TAK stream/mesh protocol headers (magic byte, version, length) are not added by the library (not found in `lib/parser.ts`). Check your server's expected framing, or send XML.
- Open #141: `normalize_geojson()` overwrites `time`/`start`/`stale` with a hard-coded 1-hour expiry; set stale explicitly after normalising for live tracks. Open #140: `marti_archive: false` dropped by `from_geojson()`. Open #144: unknown `<detail>` elements are not round-tripped to GeoJSON.
- Multi-geometries must be split first; non-Point geometries override `properties.type` (README).
- CoT `type` affiliation letters (`a-f`, `a-h`, `a-u`) drive how clients colour tracks; for unverified detections use unknown (`a-u-...`), not hostile.

## Alternatives

- [PyTAK](./snstac__pytak.md) + [takproto](./snstac__takproto.md) - Python, includes TCP/TLS/UDP transport and proto framing; prefer for Python backends.
- [nervsystems/cotlib](../../catalog/repos/nervsystems__cotlib.md) - Go, with input-size limits and schema validation; prefer for a hardened ingest service.
- [kdudkov/goatak](./kdudkov__goatak.md) - Go TAK server/client; prefer when you need the server too.

Sources: `gh api repos/dfpc-coe/node-CoT` (MIT, release v14.56.0 2026-10-22), README.md, LICENSE, package.json (name, bin, exports, engines), CHANGELOG.md (v14.52-v14.56), index.ts, cli.ts, lib/cot.ts (constructor, methods), lib/parser.ts (CoTParser statics), repo tree of lib/, npm registry for `@tak-ps/node-cot` (latest 14.56.0, MIT), issues #140, #141, #144.
