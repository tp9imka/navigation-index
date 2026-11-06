# Martin - integration card
<!-- about: repo:maplibre/martin -->
One-line: single Rust binary that serves vector tiles from PostGIS tables (live, generated per request), PMTiles, MBTiles and GeoJSON, plus fonts, sprites and styles - the offline map server behind a MapLibre or deck.gl operator view.

| | |
|---|---|
| Install | Stable: Docker `ghcr.io/maplibre/martin:1.16.1` (tag confirmed in GHCR; crates.io max stable 1.16.1), or a release tarball from GitHub releases (`martin-x86_64-unknown-linux-gnu.tar.gz`, `martin-aarch64-unknown-linux-gnu.tar.gz`, `martin-aarch64-apple-darwin.tar.gz`, Windows zip, `.deb`), or `cargo binstall martin`. Pre-release: `martin-v2.0.0-beta.6` (2026-11-05); docs on `main` already show `ghcr.io/maplibre/martin:2.0.0-beta.6`. |
| Runs on | Linux x86_64 / aarch64 (gnu and musl), macOS arm64, Windows x64, FreeBSD. x86_64 prebuilt binaries and images need an x86-64-v3 CPU (AVX2/BMI2/FMA, Haswell 2013+); older CPUs use the `-legacycpu` tarball or image. Server-side raster rendering only in the `-full` image/tarball (Linux). PostGIS sources: 1.x needs PostgreSQL 11+/PostGIS 3.0+, 2.0 needs PostgreSQL 15+/PostGIS 3.5+ (migration guide). |
| Inputs | PostgreSQL connection string (auto-discovers tables with geometry columns and tile functions), directories or paths of `.pmtiles` / `.mbtiles`, PMTiles over HTTP(S), GeoJSON files, Cloud Optimized GeoTIFF (`cog` feature, default on), sprite SVG dirs, font dirs, a YAML config file. |
| Outputs | HTTP: `/catalog`, `/{source}` TileJSON, `/{source}/{z}/{x}/{y}` tiles (MVT, or raster for raster sources), composite `/{a},{b}/{z}/{x}/{y}`, `/sprite/...`, `/font/{font}/{start}-{end}`, `/style/{style}`, `/health`, `/_/metrics` (Prometheus), OGC API Tiles under `/ogc` (docs/content/using.md on `main`). Bulk export to MBTiles with `martin-cp` (1.x) / `martin cp` (2.0). |
| Key API / entry points | `martin <conn-string-or-paths...>` (auto-config); `martin --config config.yaml`; `martin --save-config out.yaml` to dump the discovered config (listed in docs/content/help/martin.txt on `main`); `-l/--listen-addresses`; `martin-cp --output-file out.mbtiles --min-zoom 0 --max-zoom 14 --bbox=... --source <id> <conn>` (1.x) / `martin cp ...` (2.0); `mbtiles` CLI (`copy`, `diff`, `apply-patch`, `validate`, `summary`, `meta-get`/`meta-set`). Binary targets confirmed in `martin/Cargo.toml` (`[[bin]] martin`). Default port 3000. |
| Time to first result | Estimate: 5 min to serve an existing PMTiles/MBTiles file and see it in the built-in web UI (localhost only by default in 2.0); 30-60 min to point it at PostGIS and style live tables in MapLibre. Assumes Docker and a tile file in hand. |
| License | Dual MIT OR Apache-2.0 (README "Licensed under either of", LICENSE-MIT and LICENSE-APACHE); GitHub metadata shows Apache-2.0 only. Tile data you serve keeps its own licence (OSM-derived => ODbL attribution). |

## Minimal usage

Not run. Serve every PMTiles/MBTiles in `./tiles` with the stable image and check the catalogue.

```bash
docker run --rm -p 3000:3000 -v "$PWD/tiles:/files" ghcr.io/maplibre/martin:1.16.1 /files
curl -s localhost:3000/catalog
curl -s localhost:3000/<source_id> | head -c 400      # TileJSON for MapLibre
```

Live PostGIS layer (for example a table of tracks or no-go polygons written by your estimator or planner):

```bash
docker run --rm --net=host ghcr.io/maplibre/martin:1.16.1 postgres://postgres:pw@localhost/nav
# MapLibre source: {"type": "vector", "url": "http://localhost:3000/<table_name>"}
```

Pre-bake an AOI so the field box needs no database (1.x name; `martin cp` in 2.0):

```bash
martin-cp --output-file aoi.mbtiles --mbtiles-type normalized \
  "--bbox=8.4,47.3,8.7,47.45" --min-zoom 0 --max-zoom 14 \
  --source <table_name> postgres://postgres:pw@localhost/nav
```

## Wiring it into a nav stack

- Basemap: AOI extract as [PMTiles](./protomaps__pmtiles.md) (or Planetiler output, [catalog](../../catalog/repos/onthegomap__planetiler.md)) served by Martin => [MapLibre GL JS](./maplibre__maplibre-gl-js.md) style `sources` pointing at `http://<host>:3000/<id>`. Martin also serves the `glyphs` and `sprite` URLs the style needs, which closes the usual offline-labels gap.
- Live overlays from PostGIS: write fused positions, uncertainty polygons, GNSS-interference detections or geofences into PostGIS; Martin turns each table into a vector tile layer with no extra code. Good for many clients reading the same picture.
- Elevation and imagery: COG sources (orthophoto, DEM hillshade) prepared with [GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md) can be served directly.
- Clients: [deck.gl](./visgl__deck.gl.md) `MVTLayer`, OpenLayers ([catalog](../../catalog/repos/openlayers__openlayers.md)), QGIS ([catalog](../../catalog/repos/qgis__qgis.md)) via XYZ.

Catalog page: [catalog/repos/maplibre__martin.md](../../catalog/repos/maplibre__martin.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- 1.x vs 2.0 docs: the website/`main` docs describe 2.0 (beta). In 2.0 `martin-cp` becomes `martin cp`, `--tui` is on by default, the web UI defaults to `enable` for loopback clients, `DATABASE_URL` / `DEFAULT_SRID` / `PGSSL*` env vars are replaced by CLI flags or config keys, and PMTiles/MBTiles responses get `Cache-Control: max-age=0, stale-while-revalidate=86400` (migration-guide.md). Pin the image tag and read the docs for that version.
- x86-64-v3 requirement: old NUCs or VMs with a generic CPU model will fail on the standard image; use `:latest-legacycpu` / `-legacycpu` (installation.md).
- 2.0 refuses to start against PostgreSQL < 15 or PostGIS < 3.5; distro-default Postgres on older LTS images is too old.
- Web UI behind a reverse proxy: 2.0 checks the TCP peer, so a proxy on loopback exposes the UI to everyone unless `--webui disable` (migration-guide.md).
- Server-side style rendering is not in the default image; use the `-full` variant (Linux only).
- GeoParquet/DuckDB sources are unstable and not in released binaries (martin-cp.md).
- Remote PMTiles behind auth: bearer token support is an open request (#2353).
- Duplicate source IDs get suffixes like `points.1`; reserved IDs (`catalog`, `health`, `font`, ...) are renamed (using.md). Read `/catalog` rather than guessing URLs.

## Alternatives

- [tileserver-gl](./maptiler__tileserver-gl.md) - prefer when you need server-rendered raster tiles or static map images from a GL style (for Leaflet, ATAK or reports); no PostGIS.
- [PMTiles](./protomaps__pmtiles.md) with no server - a single file on any static host read by MapLibre via the `pmtiles://` protocol; prefer when nothing is dynamic.
- GDAL `gdal2tiles` ([card](./osgeo__gdal.md)) - prefer for a static raster tile folder from imagery.

Sources: `gh api repos/maplibre/martin` (Apache-2.0 metadata), releases list (martin-v1.16.0, martin-v2.0.0-beta.6 2026-11-05), crates.io API `martin` (max_stable 1.16.1, max 2.0.0-beta.6), GHCR tag list for maplibre/martin (1.16.1, latest), README.md, LICENSE-MIT, martin/Cargo.toml, docs/content/installation.md, run-with-docker.md, martin-cp.md, using.md, migration-guide.md, help/martin.txt, mbtiles-*.md, issues #2353, #2269, #655.
