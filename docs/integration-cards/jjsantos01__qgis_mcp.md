# QGIS MCP (jjsantos01) - integration card
<!-- about: repo:jjsantos01/qgis_mcp -->
One-line: let an LLM client (Claude Desktop or any MCP client) drive a running QGIS Desktop - load an AOI, DEM or flight log, run Processing algorithms, render a map PNG - through 15 tools including arbitrary PyQGIS execution.

| | |
|---|---|
| Install | No PyPI package, no release tags. Two parts: (1) `git clone https://github.com/jjsantos01/qgis_mcp.git`; copy `qgis_mcp_plugin/` into the QGIS profile `python/plugins` folder (QGIS: Settings => User profiles => Open active profile folder), restart QGIS, enable "QGIS MCP" in Plugins => Manage and Install Plugins. (2) Register the MCP server in the client config: `"command": "uv", "args": ["--directory", "/ABS/PATH/qgis_mcp/src/qgis_mcp", "run", "qgis_mcp_server.py"]`. Needs `uv`. |
| Runs on | Any OS with QGIS 3.x Desktop (README: "only tested on 3.22"). Not working on QGIS 4 / Qt6 per open issues #27 and #35. Server: Python per `pyproject.toml` `requires-python = ">=3.12"` and `.python-version` 3.12 (README still says 3.10+); only dependency `mcp[cli]>=1.3.0`. No GPU. |
| Inputs | Tool calls over MCP stdio. Layers by file path: vector via OGR provider (shp, GeoJSON, GPKG, CSV...), raster via GDAL provider (GeoTIFF etc.). `execute_processing(algorithm, parameters: dict)` takes QGIS Processing ids such as `native:centroids`. |
| Outputs | JSON strings back to the LLM (project info, layer list, first N features); saved `.qgz` projects; files written by Processing algorithms; PNG from `render_map(path, width=800, height=600)`. |
| Key API / entry points | MCP tools in `src/qgis_mcp/qgis_mcp_server.py`: `ping`, `get_qgis_info`, `load_project(path)`, `create_new_project(path)`, `add_vector_layer(path, provider="ogr", name=None)`, `add_raster_layer(path, provider="gdal", name=None)`, `get_layers`, `get_layer_features(layer_id, limit=10)`, `execute_processing(algorithm, parameters)`, `render_map(path, width, height)`, `execute_code(code)`, `save_project(path=None)`. Plugin side: `QgisMCPServer` in `qgis_mcp_plugin/qgis_mcp_plugin.py`, TCP socket on `localhost:9876` (port selectable in the dock widget), polled by a `QTimer` in the QGIS GUI thread. |
| Time to first result | Estimate: 20-30 min to a rendered map from a chat prompt, assuming QGIS 3.x is already installed, `uv` present and an MCP-capable client configured. Longer if you are on QGIS 4. |
| License | None. No LICENSE file in the repo and GitHub metadata reports no license - default copyright applies, so reuse or redistribution is not granted. |

## Minimal usage

Not run. After the plugin is enabled and "Start Server" clicked in the QGIS MCP dock (port 9876), give the client a prompt adapted from the README demo:

```text
1. Ping to check the connection.
2. Create a new project and save it at "/data/aoi/aoi.qgz".
3. Load the vector layer "/data/aoi/flight_track.geojson" and name it "Track".
4. Load the raster layer "/data/aoi/dem.tif" and name it "DEM".
5. Zoom to the "DEM" layer.
6. Execute "native:buffer" on "Track" with DISTANCE 0.001 and save to "/data/aoi/track_buffer.geojson".
7. Render the map to "/data/aoi/overview.png" and save the project.
```

Client config (Claude Desktop `claude_desktop_config.json`, from README):

```json
{"mcpServers": {"qgis": {"command": "uv",
  "args": ["--directory", "/ABS/PATH/qgis_mcp/src/qgis_mcp", "run", "qgis_mcp_server.py"]}}}
```

## Wiring it into a nav stack

- File handoff, not live data: QGIS works on files. Export the estimator or flight log as GeoJSON/GPKG/CSV (lon/lat WGS84), then ask the agent to load and style it. For live tracks use a web map ([MapLibre card](./maplibre__maplibre-gl-js.md)).
- Basemap and DEM prep for terrain or visual nav: the agent can call GDAL-backed Processing algorithms (`gdal:warpreproject`, `gdal:hillshade`, clip by extent) to cut an AOI for [GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md) pipelines or a [PMTiles](./protomaps__pmtiles.md) basemap.
- Pairs with other MCP servers in the same client: [MAVLink MCP](./ion-g-ion__mavlinkmcp.md) for vehicle state, [ROS MCP server](./robotmcp__ros-mcp-server.md) for ROS graphs, [gis-mcp](./mahdin75__gis-mcp.md) for headless geometry/CRS math without QGIS. The LLM moves data between them as files.
- Desktop application: catalog page for [QGIS](../../catalog/repos/qgis__qgis.md).

Catalog page: [catalog/repos/jjsantos01__qgis_mcp.md](../../catalog/repos/jjsantos01__qgis_mcp.md). Concepts: [llm-agents-robotics](../../catalog/concepts/llm-agents-robotics.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- QGIS 4 / Qt6: plugin reported incompatible (open #27 "Qt5 or Qt6", open #35 "Broken plugin for QGIS version 4.01"). Use a QGIS 3.x LTR or the nkarasiak fork below.
- No licence: fine to try locally, not fine to vendor into a deliverable you hand over.
- `execute_code` runs `exec()` on LLM-generated Python inside QGIS with full user rights (plugin `execute_code`). The socket server has no auth; it binds `localhost`, keep it that way.
- Install friction: manual plugin copy; install-from-ZIP has small problems (open #5); "missing hammer" icon usually means the client config path is wrong (#6). Windows issues in #4.
- Repo last pushed 2025-10-01; plugin `metadata.txt` still carries placeholder author fields - treat as a demo-grade project.
- Calls are synchronous through the GUI thread; long Processing runs block QGIS and the MCP call until done.

## Alternatives

- [nkarasiak/qgis-mcp](../../catalog/repos/nkarasiak__qgis-mcp.md) - same plugin-plus-server pattern, about 125 tools, supports QGIS 3.28 to 4.x per its catalog entry; GPL-2.0. Prefer it on QGIS 4 or if you need a licence.
- [mahdin75/gis-mcp](./mahdin75__gis-mcp.md) - no QGIS needed, pip-installable, deterministic geometry/CRS/raster tools; prefer for headless or Docker setups.
- [gladcolor/llm-geo](../../catalog/repos/gladcolor__llm-geo.md) - research prototype that generates whole analysis programs rather than calling tools.

Sources: `gh api repos/jjsantos01/qgis_mcp` (license null, pushed 2025-10-01), README.md, pyproject.toml, .python-version, src/qgis_mcp/qgis_mcp_server.py (tool signatures, port 9876), qgis_mcp_plugin/qgis_mcp_plugin.py (socket server, QTimer, exec), qgis_mcp_plugin/metadata.txt, issues #4, #5, #6, #21, #27, #35.
