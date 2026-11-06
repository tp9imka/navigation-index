# PMTiles - integration card
<!-- about: repo:protomaps/pmtiles -->
One-line: a single-file tile archive you can cut to your AOI and serve from a laptop or static storage, giving an offline basemap (vector, raster or terrain-RGB) for a ground-station or C2 map without a tile server.

| | |
|---|---|
| Install | CLI (lives in the separate `protomaps/go-pmtiles` repo): download a binary from its releases (latest v1.31.2). JS: `npm add pmtiles`. Python: `pip install pmtiles` (reader/writer) and `pip install rio-pmtiles` (raster => PMTiles). |
| Runs on | CLI: static Go binary per OS/arch. JS: browser or Node. No GPU. |
| Inputs | Existing archives (local path or HTTP/S3 URL), MBTiles (`pmtiles convert`), GeoJSON polygon or bbox for extraction. Producing tiles from raw data needs another tool: tippecanoe or [planetiler](../../catalog/repos/onthegomap__planetiler.md) for vector, rio-pmtiles or [GDAL](./osgeo__gdal.md) (PMTiles driver, GDAL >= 3.8) for raster. |
| Outputs | `.pmtiles` archive (spec v3): MVT vector tiles, PNG/JPEG/WebP raster tiles, or terrain-RGB/terrarium DEM tiles; Z/X/Y HTTP endpoints via `pmtiles serve`; TileJSON via `pmtiles show --tilejson`. |
| Key API / entry points | CLI subcommands (go-pmtiles main.go): `show`, `tile <path> z x y`, `extract <in> <out> [--bbox=min_lon,min_lat,max_lon,max_lat] [--region=aoi.geojson] [--minzoom] [--maxzoom] [--dry-run]`, `convert`, `merge`, `cluster`, `verify`, `serve <path> [--port=8080] [--cors=...]`, `upload`. JS: `new PMTiles(urlOrSource)`, `FileSource`, `FetchSource`, `new Protocol()` + `maplibregl.addProtocol("pmtiles", protocol.tile)`, `leafletRasterLayer(p, opts)`. |
| Time to first result | Estimate: 20-30 min to an offline basemap of a city-sized AOI: download CLI, `extract` from a public planet build with `--maxzoom`, open in the MapLibre example. Assumes network for the extract step and that you pick a basemap build URL yourself (not given in this repo's README). |
| License | Reference implementations BSD-3-Clause; the spec is public domain / CC0 (LICENSE). GitHub metadata reports NOASSERTION. Map data inside archives carries its own license (OpenStreetMap-derived basemaps are ODbL and need attribution). |

## Minimal usage

Not run. Cut an AOI out of a remote archive, serve it locally, and inspect.

```bash
pmtiles extract https://example.com/basemap.pmtiles aoi.pmtiles \
  --bbox=8.40,47.30,8.70,47.45 --maxzoom=14 --dry-run   # size estimate first
pmtiles extract https://example.com/basemap.pmtiles aoi.pmtiles \
  --bbox=8.40,47.30,8.70,47.45 --maxzoom=14
pmtiles show aoi.pmtiles
pmtiles serve . --port=8080 --cors='*'
```

MapLibre side (from js/README.md):

```js
import { Protocol } from "pmtiles";
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);
// style source: { type: "vector", url: "pmtiles://http://localhost:8000/aoi.pmtiles" }
```

`js/examples/maplibre_raster_dem.html` shows the same protocol feeding a `raster-dem` source with `encoding: "terrarium"` - the route to 3D terrain from a PMTiles DEM.

## Wiring it into a nav stack

- Offline ground-station map: AOI `.pmtiles` on disk => browser via `pmtiles://` in [MapLibre GL JS](./maplibre__maplibre-gl-js.md) => live vehicle track drawn from your estimator (GeoJSON source fed over a WebSocket, or a MAVLink bridge). For the TAK route see [samples/mavlink-to-tak-cot](../../samples/mavlink-to-tak-cot/).
- Orthophoto and DEM tiles: produce raster PMTiles with GDAL or rio-pmtiles from the same GeoTIFFs used by a matcher or TRN filter ([rasterio](./rasterio__rasterio.md), [elevation](./bopen__elevation.md)), so the operator sees exactly the map the estimator uses.
- Serving alternatives: if you need server-side styling or PostGIS, [martin](../../catalog/repos/maplibre__martin.md) also serves PMTiles; [tileserver-gl](../../catalog/repos/maptiler__tileserver-gl.md) serves MBTiles plus server-side rendered raster. `pmtiles convert` goes MBTiles => PMTiles; keep the source MBTiles if you need both. Both martin (README) and tileserver-gl (docs/config.rst) mention PMTiles inputs.

Catalog page: [catalog/repos/protomaps__pmtiles.md](../../catalog/repos/protomaps__pmtiles.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- The CLI is not in this repo. `protomaps/pmtiles` holds the spec, JS, Python and serverless code; the `pmtiles` binary is `protomaps/go-pmtiles`.
- Browsers fetch archives with HTTP Range requests. `file://` URLs and some static hosts break this: issue #584 (GitHub Pages content-encoding vs Firefox's `Accept-Encoding` on Range requests) and #272 (Firefox range caching). Serve over `http://` with `pmtiles serve` or a range-capable static server.
- Cloud storage needs CORS configured for your page origin (README, js/README.md).
- A vector basemap also needs a style, fonts (glyphs) and sprites. Extracting tiles alone gives a blank or label-less map offline; bundle glyphs and sprites locally too.
- `extract` with no `--maxzoom` pulls every zoom level of the AOI; use `--dry-run` first.
- Leaflet only gets raster layers from this package; vector in Leaflet needs protomaps-leaflet.
- Python and rio-pmtiles are separate PyPI packages from this repo; issue #177 (GDAL/OGR + QGIS support) is still open in this repo, but GDAL itself ships a PMTiles driver since 3.8 (GDAL doc/source/drivers/vector/pmtiles.rst).

## Alternatives

- [maplibre/martin](../../catalog/repos/maplibre__martin.md) - tile server (PostGIS, MBTiles, PMTiles); prefer when the data is live in a database.
- [maptiler/tileserver-gl](../../catalog/repos/maptiler__tileserver-gl.md) - serves MBTiles and server-side rendered raster for non-WebGL clients.
- [onthegomap/planetiler](../../catalog/repos/onthegomap__planetiler.md) - when you must build the vector basemap yourself from an OSM extract; its README shows `planetiler --download --area=monaco --output=monaco.pmtiles`.

Sources: `gh api repos/protomaps/pmtiles` (license), README.md, LICENSE, js/README.md, js/src/index.ts and js/src/adapters.ts (exported classes), js/examples listing and maplibre_raster_dem.html, `protomaps/go-pmtiles` README and main.go (CLI subcommands and flags, release v1.31.2), issues #584, #272, #177, #395; planetiler and martin READMEs, tileserver-gl docs/config.rst (PMTiles mentions only).
