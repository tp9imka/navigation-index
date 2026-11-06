# GIS MCP Server - integration card
<!-- about: repo:mahdin75/gis-mcp -->
One-line: pip-installable MCP server that gives an LLM agent deterministic geometry, CRS, geodesic and raster tools (Shapely, PyProj, GeoPandas, Rasterio, PySAL) so it computes distances, buffers and reprojections instead of guessing them.

| | |
|---|---|
| Install | `pip install gis-mcp` (PyPI 0.15.0, MIT, `requires-python >=3.10`); extras `gis-mcp[visualize]`, `[movement]` (osmnx), `[satellite-imagery]`, `[land-cover]`, `[all]`. Docker: `docker build -t gis-mcp . && docker run -p 9010:9010 gis-mcp` (builds from `python:3.12-slim`, installs `gis-mcp[all]` from PyPI, HTTP transport on 9010). No pre-built image named in the README. |
| Runs on | Linux / macOS / Windows, CPU only. Hard pins in `pyproject.toml`: `numpy<2.0`, `rasterio==1.3.9`, `fiona==1.9.6`, `geopandas==1.1.1`, `fastmcp==2.13.1`. Classifiers list Python 3.10 and 3.11; the Dockerfile uses 3.12; README examples use `uv venv --python=3.10`. |
| Inputs | MCP tool calls. Geometries as WKT strings; points as `[lon, lat]` lists (e.g. `calculate_geodetic_distance(point1, point2, ellps="WGS84")` unpacks `lon1, lat1 = point1`); CRS as strings (`"EPSG:4326"`); vector/raster files by path (shp, GeoJSON, GPKG, GeoTIFF). |
| Outputs | Dicts with `status`, result fields and units (geodesic distance in metres plus forward/back azimuth); written files (GeoJSON, rasters, PNG/PDF maps, Folium HTML) in the storage path; HTTP mode adds `/storage/upload`, `/storage/download`, `/storage/list`. |
| Key API / entry points | CLI `gis-mcp` (`gis_mcp.main:main`; flags `--storage-path`, `--debug`; env `GIS_MCP_TRANSPORT=stdio|http|sse`, `GIS_MCP_HOST` default `0.0.0.0`, `GIS_MCP_PORT` default `8080`). Tools (README lists 92+): `transform_coordinates(coordinates, source_crs, target_crs)`, `project_geometry(geometry, source_crs, target_crs)`, `calculate_geodetic_distance(point1, point2, ellps)`, `calculate_geodetic_point(start_point, azimuth, distance, ellps)`, `get_utm_crs(coordinates)`, `buffer(geometry, distance, resolution=16, ...)`, `sjoin_gpd`, `clip_raster_with_shapefile`, `hillshade`, `create_web_map`. |
| Time to first result | Estimate: 10-15 min from `pip install` to an MCP client calling `calculate_geodetic_distance`, assuming Python 3.10-3.12 and wheels for the pinned rasterio/fiona exist for your platform. |
| License | MIT (LICENSE file and PyPI metadata). Optional extras pull data-source terms of their own (GADM, Copernicus CDS, GBIF, Planetary Computer). |

## Minimal usage

Not run. Install and wire to an MCP client over stdio:

```bash
uv venv --python=3.11 && source .venv/bin/activate
uv pip install gis-mcp
which gis-mcp   # absolute path goes in the client config
```

```json
{"mcpServers": {"gis-mcp": {"command": "/ABS/PATH/.venv/bin/gis-mcp", "args": []}}}
```

Prompt: "Using gis-mcp, compute the geodesic distance and azimuth from [8.5500, 47.3700] to [8.6200, 47.4100] (lon, lat), then the UTM CRS for the first point." Expected tool calls: `calculate_geodetic_distance`, `get_utm_crs`.

HTTP mode for a shared agent backend:

```bash
GIS_MCP_TRANSPORT=http GIS_MCP_PORT=8080 gis-mcp   # endpoint http://host:8080/mcp
```

## Wiring it into a nav stack

- Agent-side geodesy: when an LLM planner (see [ROSA](./nasa-jpl__rosa.md), [MAVLink MCP](./ion-g-ion__mavlinkmcp.md)) proposes waypoints or reports offsets, route the math through `calculate_geodetic_point` / `transform_coordinates` instead of letting the model do arithmetic. The same operations in plain code: [pymap3d](./geospace-code__pymap3d.md), [pyproj](../../catalog/repos/pyproj4__pyproj.md).
- AOI prep: `clip_raster_with_shapefile`, `reproject_raster`, `hillshade` on a DEM for terrain-referenced nav ([GDAL](./osgeo__gdal.md), [rasterio](./rasterio__rasterio.md)); `download_street_network` (osmnx extra, OSM data under ODbL) for ground routing.
- Output to an operator view: GeoJSON files => [MapLibre](./maplibre__maplibre-gl-js.md); or ask [QGIS MCP](./jjsantos01__qgis_mcp.md) to load them.

Catalog page: [catalog/repos/mahdin75__gis-mcp.md](../../catalog/repos/mahdin75__gis-mcp.md). Concepts: [llm-agents-robotics](../../catalog/concepts/llm-agents-robotics.md), [gis-mapping](../../catalog/concepts/gis-mapping.md), [geodesy](../../catalog/concepts/geodesy.md).

## Gotchas

- Silent CRS accuracy loss: open #45 (external correctness suite) reports `project_geometry` hands the CRS pair to `Transformer.from_crs` and accepts PROJ's ballpark transform - a Monte Mario => WGS84 point came back 74 m off with `status: success`. Same issue: `read_file_gpd` takes no layer name, so on a multi-layer GeoPackage it answers about the first layer. For datum-sensitive work check results or call pyproj with `allow_ballpark=False` yourself.
- Pinned rasterio 1.3.9 / fiona 1.9.6 cannot build against GDAL >= 3.11 (open #35, which ties this to a GDAL CVE). On newer Python versions or distros without matching wheels the install may fall back to a source build; stay on Python 3.10-3.12 or use the Dockerfile.
- `gis-mcp: command not found` after following the README (closed #21) - the venv was not activated or the client points at the wrong path; use the absolute path to the venv binary.
- Missing `yaml` module in an older release (closed #25); upgrade to current.
- Port differs by launch path: 8080 default from `main.py`, 9010 in both Dockerfiles.
- Coordinate order is `[lon, lat]` in the PyProj tools. LLMs often pass lat first.
- HTTP mode binds `0.0.0.0` with file upload/download endpoints and no auth described in the README; keep it on a private network.

## Alternatives

- [jjsantos01/qgis_mcp](./jjsantos01__qgis_mcp.md) or [nkarasiak/qgis-mcp](../../catalog/repos/nkarasiak__qgis-mcp.md) - drive full QGIS (styling, layouts, any Processing algorithm); prefer when a human also needs the map in QGIS.
- Plain [pyproj](../../catalog/repos/pyproj4__pyproj.md) + [pymap3d](./geospace-code__pymap3d.md) in your own code - prefer when no LLM is in the loop; fewer pins, explicit transform control.
- [gladcolor/llm-geo](../../catalog/repos/gladcolor__llm-geo.md) - code-generating GIS agent research prototype.

Sources: `gh api repos/mahdin75/gis-mcp` (MIT, pushed 2026-08-21), PyPI JSON for `gis-mcp` (0.15.0, MIT, >=3.10), README.md, pyproject.toml (deps, extras, `[project.scripts]`), LICENSE, Dockerfile, src/gis_mcp/main.py (transport env vars, defaults), src/gis_mcp/pyproj_functions.py and shapely_functions.py (signatures), issues #21, #25, #35, #45.
