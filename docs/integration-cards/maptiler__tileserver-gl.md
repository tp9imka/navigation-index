# TileServer GL - integration card
<!-- about: repo:maptiler/tileserver-gl -->
One-line: serve MBTiles/PMTiles vector tiles with GL styles and render them server-side to PNG/JPEG/WebP raster tiles, WMTS and static map images - the bridge from a vector basemap to raster-only clients (Leaflet, ATAK-style tools, reports).

| | |
|---|---|
| Install | Docker: `maptiler/tileserver-gl:v5.7.0` (Docker Hub, amd64 + arm64, 2026-10-23) or `maptiler/tileserver-gl-light` (no native rendering). npm: `npm install -g tileserver-gl` (5.7.0) or `tileserver-gl-light` (5.7.0, pure JS). Node `^20.19.0 \|\| ^22.13.0 \|\| 24` (package.json `engines`; README recommends Node 24). |
| Runs on | Linux x86_64/arm64 via Docker (image built on `ubuntu:noble`). Full npm install needs native deps for MapLibre Native, `canvas` and `sharp`; headless rendering from the CLI uses `xvfb-run` (README). `-light` runs anywhere Node runs but cannot render rasters. |
| Inputs | `.mbtiles` or `.pmtiles` (local, HTTP, or S3) via `--file`, or a `config.json` listing `data`, `styles`, `fonts`, `sprites`. Styles are MapLibre style JSON. Fonts as PBF glyph ranges. |
| Outputs | `/styles/{id}/style.json`, `/styles/{id}[/{tileSize}]/{z}/{x}/{y}[@2x].{png,jpg,webp}` rendered tiles, `/styles/{id}/wmts.xml`, `/styles/{id}/static/{lon},{lat},{zoom}/{w}x{h}.png` and bbox / `auto` static images, `/data/{id}/{z}/{x}/{y}.pbf` raw tiles, `/data/{id}.json` TileJSON, `/data/{id}/elevation/{z}/{lon}/{lat}` for DEM sources, `/fonts/{fontstack}/{start}-{end}.pbf`, `/health` (docs/endpoints.rst). Rendered and static endpoints are absent in `-light`. |
| Key API / entry points | CLI `tileserver-gl` (package.json `bin` => `src/main.js`): `--file <mbtiles\|pmtiles>`, `-c/--config <file>`, `-p/--port` (default 8080), `-b/--bind`, `-u/--public_url`, `--no-cors`, `-V/--verbose`, `--metrics`, `--ignore-missing-files`. Env `TILESERVER_GL_ALLOWED_HOSTS`. Docker mounts the data dir at `/data`. |
| Time to first result | Estimate: 5 min with Docker and the sample `zurich_switzerland.mbtiles` from the README; 1-2 h to a custom AOI with your own style, fonts and sprites. |
| License | Code: BSD-2-Clause (first section of LICENSE.md, npm `license` field). GitHub reports NOASSERTION because LICENSE.md (73 KB) also concatenates bundled third-party licences (MapLibre Native BSD-2, ISC/Boost/MIT parts, RapidJSON incl. a JSON-licence component, Leaflet, PMTiles). Default styles and fonts come from the separate npm package `tileserver-gl-styles` 2.0.0 with different terms - see Gotchas. |

## Minimal usage

Not run. From the README, Docker variant:

```bash
mkdir tiles && cd tiles
wget https://github.com/maptiler/tileserver-gl/releases/download/v1.3.0/zurich_switzerland.mbtiles
docker run --rm -it -v "$(pwd)":/data -p 8080:8080 maptiler/tileserver-gl:v5.7.0 --file zurich_switzerland.mbtiles
# browse http://localhost:8080 ; raster XYZ for Leaflet:
#   http://localhost:8080/styles/<style-id>/{z}/{x}/{y}.png
# static snapshot for a report:
curl -o snap.png "http://localhost:8080/styles/<style-id>/static/8.54,47.37,13/800x600.png"
```

`<style-id>` comes from `http://localhost:8080/styles.json`; with `--file` and an OpenMapTiles-schema file the server builds a config from the bundled default styles (`src/main.js` reads `node_modules/tileserver-gl-styles/`).

## Wiring it into a nav stack

- Raster-only clients: [Leaflet](./leaflet__leaflet.md) operator views, TAK-family clients that accept an XYZ raster map source (check the client's map-source format; [goatak](./kdudkov__goatak.md), [OpenTAKServer](./brian7704__opentakserver.md) cards cover the TAK side), and WMTS-capable GIS ([QGIS](../../catalog/repos/qgis__qgis.md)).
- Vector clients ([MapLibre GL JS](./maplibre__maplibre-gl-js.md), [deck.gl](./visgl__deck.gl.md)) can use the same server for `style.json`, glyphs and sprites, so one container covers both.
- Static images: `/static/...` endpoints give a map snapshot around a position fix or a bbox for mission reports or for a vision pipeline that needs rendered map tiles (for example a coarse map-matching reference; check the style is close to what the camera sees).
- Elevation: a DEM MBTiles/PMTiles exposed as `/data/{id}/elevation/...` gives point heights over HTTP; for terrain-referenced navigation prefer raw DEM rasters via [GDAL](./osgeo__gdal.md) or [rasterio](./rasterio__rasterio.md).
- Data: AOI tiles from [PMTiles](./protomaps__pmtiles.md) extracts or Planetiler ([catalog](../../catalog/repos/onthegomap__planetiler.md)).

Catalog page: [catalog/repos/maptiler__tileserver-gl.md](../../catalog/repos/maptiler__tileserver-gl.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- Three licences, not one. Server code is BSD-2-Clause. The default styles package `tileserver-gl-styles` (npm 2.0.0, source repo klokantech/tileserver-gl-styles, last pushed 2019) says its styles derive from Mapbox Open Styles: style JSON under BSD, visual design under CC BY 3.0 (attribution expected), icons CC0. That LICENSE.md lists Open Sans and Arial Unicode MS, while the repo's `fonts/` folder holds `Noto Sans Regular`; the Noto licence is not stated in that file (not verified further). Tile data is separate again: OSM-derived tiles are ODbL (attribution required, share-alike on derived databases); OpenMapTiles downloads from data.maptiler.com carry MapTiler's own terms (not reviewed here).
- Host header poisoning: without `--public_url`, URLs in TileJSON/WMTS/style responses are built from `Host` / `X-Forwarded-*`. Set `--public_url` or `TILESERVER_GL_ALLOWED_HOSTS` on anything network-facing (README "Security").
- Native install pain on bare metal: libpng mismatches (#2015, #2261, closed 2026), Ubuntu 24.04 + Node 20+ ESM import failure (#1956, closed 2026-01), libicu60 missing on Ubuntu 24 (#1290, open), Windows Server install failure (#1385, open). Use the Docker image.
- Rendering hangs or misses: raster rendering deadlock with 0% CPU for certain symbol+fill/line combinations (#2340, open 2026-08), some raster tiles fail to render fonts (#1399, open), memory growth during raster rendering (#1565, open). Watch `/health` and restart on timeout.
- PMTiles at scale: fetch timeouts when loading many remote PMTiles sources (#1468, open); a container crash via PMTiles was fixed (#1778, closed 2025-10).
- arm64: images are published for arm64; an earlier broken arm64 image (#1031) was closed in 2023. `-light` in Docker had separate failures (#785 open, #1448 closed).
- README sample data links are to the v1.3.0 release assets; they are tiny demo extracts, not a real AOI.

## Alternatives

- [Martin](./maplibre__martin.md) - prefer for vector-only serving, live PostGIS layers and lower resource use; raster rendering only in its `-full` build.
- [PMTiles](./protomaps__pmtiles.md) with no server - prefer when clients speak vector tiles and a static file host is enough.
- GDAL `gdal2tiles` ([card](./osgeo__gdal.md)) - prefer for imagery-only raster tile pyramids with no style rendering.

Sources: `gh api repos/maptiler/tileserver-gl` (NOASSERTION, latest release v5.7.0 2026-10-23), npm registry `tileserver-gl`, `tileserver-gl-light`, `tileserver-gl-styles`, Docker Hub tag list `maptiler/tileserver-gl`, README.md, LICENSE.md (section headings and first section), package.json (`bin`, `engines`, deps), Dockerfile, src/main.js (CLI options, default styles path), docs/endpoints.rst, klokantech/tileserver-gl-styles LICENSE.md and file listing, issues #2015, #2261, #1956, #1290, #1385, #2340, #1399, #1565, #1468, #1778, #1031, #785, #1448.
