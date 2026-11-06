# OSMnx - integration card
<!-- about: repo:gboeing/osmnx -->
One-line: one Python call turns an OSM area into a NetworkX road/path graph with lengths, speeds and travel times - fastest way to prototype ground-vehicle route planning, task allocation or road-constrained map matching in a notebook.

| | |
|---|---|
| Install | `pip install osmnx` (PyPI 2.1.1, 2026-07-21, MIT, requires Python >=3.11). Extras: `osmnx[neighbors]` (scikit-learn + scipy for nearest-node/edge search), `osmnx[raster]` (rasterio for DEM elevations), `osmnx[visualization]` (matplotlib), `osmnx[all]` (pyproject.toml). Python 3.9/3.10: last compatible line is 2.0.x (2.0.7 requires >=3.9). |
| Runs on | Pure Python on top of geopandas, shapely, networkx, pandas, numpy, requests; any OS/arch with wheels for those. No GPU. |
| Inputs | Place names (Nominatim geocode), `(lat, lon)` point + distance, bbox `(left, bottom, right, top)` in EPSG:4326, shapely polygon, or an OSM XML file. Online by default: Overpass API (`settings.overpass_url = "https://overpass-api.de/api"`) and Nominatim. |
| Outputs | `networkx.MultiDiGraph` with node `x`/`y` (lon/lat), edge `length` (m), optional `speed_kph`, `travel_time` (s), `grade`; GeoDataFrames of nodes/edges; GraphML / GeoPackage / OSM XML files; matplotlib plots. |
| Key API / entry points | `ox.graph_from_place(query, network_type="drive")`; `ox.graph_from_point((lat, lon), dist, network_type=...)`; `ox.graph_from_bbox((left, bottom, right, top), network_type=...)`; `ox.graph_from_xml(path)`; `ox.distance.nearest_nodes(G, X=lon, Y=lat)`; `ox.routing.add_edge_speeds(G)` + `ox.routing.add_edge_travel_times(G)`; `ox.routing.shortest_path(G, orig, dest, weight="travel_time")`; `ox.convert.graph_to_gdfs(G)`; `ox.io.save_graphml` / `load_graphml`; `ox.projection.project_graph(G)`; `ox.features.features_from_place(query, tags)`. Signatures read from osmnx/graph.py, distance.py, routing.py; top-level `ox.*` shortcuts come from `_api_v1.py`. |
| Time to first result | Estimate: 10 min from `pip install` to a plotted shortest path in a small town, with internet access. Large areas take much longer and are bounded by Overpass. |
| License | MIT (LICENSE.txt, pyproject `license = "MIT"`); GitHub metadata MIT. Downloaded data is OSM => ODbL, attribution required (README "License"). |

## Minimal usage

Not run. Drive-time shortest path between two fixes, cached to disk so the field run needs no network.

```python
import osmnx as ox

G = ox.graph_from_point((47.3769, 8.5417), dist=3000, network_type="drive")
G = ox.routing.add_edge_speeds(G)
G = ox.routing.add_edge_travel_times(G)
ox.io.save_graphml(G, "aoi_drive.graphml")          # later: ox.io.load_graphml(...)

orig = ox.distance.nearest_nodes(G, X=8.5300, Y=47.3700)   # X=lon, Y=lat
dest = ox.distance.nearest_nodes(G, X=8.5550, Y=47.3850)
route = ox.routing.shortest_path(G, orig, dest, weight="travel_time")
coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]   # (lat, lon) list
print(len(route), sum(G.edges[u, v, 0]["length"] for u, v in zip(route[:-1], route[1:])))
```

Unprojected `nearest_nodes` needs scikit-learn (`pip install "osmnx[neighbors]"`); on a projected graph it uses scipy (distance.py).

## Wiring it into a nav stack

- Planner prototype => production engine: prototype costs and constraints in OSMnx/NetworkX, then move to [OSRM](./project-osrm__osrm-backend.md) or [Valhalla](./valhalla__valhalla.md) for speed and turn restrictions.
- Road-constrained localization: the edge GeoDataFrame is a ready road prior for a particle filter or for snapping a dead-reckoned ground track during GNSS outage (project with `project_graph` to UTM first so distances are metric). Frame conversion via [pyproj](./pyproj4__pyproj.md) or [pymap3d](./geospace-code__pymap3d.md).
- ROS: export the route as a list of lat/lon and feed it as waypoints through `navsat_transform` in [robot_localization](./cra-ros-pkg__robot_localization.md) to [Nav2](./ros-navigation__navigation2.md) (Nav2 itself plans on costmaps, not OSM graphs).
- Display: `ox.convert.graph_to_gdfs` => GeoJSON => [MapLibre GL JS](./maplibre__maplibre-gl-js.md) or [Leaflet](./leaflet__leaflet.md).
- Terrain: `ox.elevation.add_node_elevations_raster(G, dem.tif)` then `add_edge_grades` with a DEM prepared in [GDAL](./osgeo__gdal.md).

Catalog page: [catalog/repos/gboeing__osmnx.md](../../catalog/repos/gboeing__osmnx.md). Concepts: [gis-mapping](../../catalog/concepts/gis-mapping.md), [path-planning](../../catalog/concepts/path-planning.md), [ground-vehicle-nav](../../catalog/concepts/ground-vehicle-nav.md).

## Gotchas

- Needs internet by default (Overpass + Nominatim). For offline: pre-download and `save_graphml`, or point `ox.settings.overpass_url` at your own Overpass instance (#1377), or load OSM XML with `graph_from_xml`. `graph_from_xml` reads OSM XML, not `.osm.pbf`; convert PBF first (for example with osmium, not covered here). Do not reload XML that OSMnx itself wrote (docstring).
- Argument order traps: `graph_from_point` takes `(lat, lon)`, `nearest_nodes` takes `X=lon, Y=lat`, and since 2.0 `graph_from_bbox` takes one tuple `(left, bottom, right, top)`. Many tutorials still use the 1.x `north, south, east, west` form.
- Python >=3.11 for 2.1.x; Jetson images on Python 3.8-3.10 need an older line.
- Big areas: Overpass rate limits and timeouts (#1266 "Max retries exceeded"), and memory blow-up on country-scale graphs (#1311: crash with 180 GB RAM on a China network). Keep the AOI small or use OSRM/Valhalla for regional scale.
- `custom_filter` behaviour surprised users (#1255, #1256); test the filter on a small area first.
- NetworkX shortest paths are pure Python; fine for a few thousand queries, not for real-time replanning at scale.

## Alternatives

- [OSRM](./project-osrm__osrm-backend.md) - prefer for fast road routing, tables and map matching over a whole region.
- [Valhalla](./valhalla__valhalla.md) - prefer for per-request costing (truck, pedestrian, avoid areas), isochrones, elevation.
- [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md) - JVM routing engine with custom profiles; prefer in a Java stack.

Sources: `gh api repos/gboeing/osmnx` (MIT, tags v2.1.1), PyPI JSON `osmnx` (2.1.1 >=3.11; 2.0.7 >=3.9; 1.9.4), README.md, LICENSE.txt, pyproject.toml, osmnx/__init__.py, osmnx/_api_v1.py, osmnx/graph.py (graph_from_bbox, graph_from_point, graph_from_xml), osmnx/distance.py (optional scipy/scikit-learn), osmnx/routing.py, osmnx/settings.py, issues #1377, #1266, #1311, #1255, #1256, #1363.
