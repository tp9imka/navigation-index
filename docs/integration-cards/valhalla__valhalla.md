# Valhalla - integration card
<!-- about: repo:valhalla/valhalla -->
One-line: offline OSM routing engine with per-request costing (auto, truck, pedestrian, bicycle, avoid polygons), isochrones, time-distance matrices, elevation sampling and map matching (`trace_route`) - from Docker, an HTTP API, or an in-process Python `Actor`.

| | |
|---|---|
| Install | Docker (scripted, builds tiles from PBFs on start): `ghcr.io/valhalla/valhalla-scripted:3.9.1` (tags `3.9.1`, `-amd64`, `-arm64`, `latest` confirmed in GHCR). Python: `pip install pyvalhalla` (PyPI 3.9.1, 2026-10-06; abi3 wheels for manylinux_2_28 x86_64/aarch64, macOS arm64, Windows amd64; requires Python >=3.9). Node: `npm install @valhallajs/valhallajs` (README). Source: CMake, see docs "building". |
| Runs on | Linux and macOS fully; Windows builds the library, tools and Python bindings (README "Platform Compatibility"). Wheels need glibc >= 2.28. No GPU. Used on iOS/Android per README. |
| Inputs | OSM `.osm.pbf` extracts (for graph build); optional GTFS feeds (transit), elevation tiles, admin and timezone DBs. Requests are JSON: `locations: [{lat, lon}]`, `costing` + `costing_options`, `exclude_polygons`, `shape` / `encoded_polyline` for map matching. |
| Outputs | JSON (route legs with encoded polyline shape, manoeuvres and narrative, matrices, isochrone GeoJSON polygons, matched edges and attributes, heights). Tiles stored as a directory or `valhalla_tiles.tar`. |
| Key API / entry points | Tools (also exposed as `pyvalhalla` console scripts): `valhalla_build_config`, `valhalla_build_tiles -c valhalla.json file.osm.pbf`, `valhalla_build_extract`, `valhalla_build_elevation`, `valhalla_build_admins`, `valhalla_service` (HTTP server or one-shot `valhalla_service valhalla.json <action> '<json>'`). Python: `from valhalla import Actor, get_config, ValhallaError`; `Actor(config)` methods `route`, `locate`, `optimized_route`, `isochrone`, `matrix`, `trace_route`, `trace_attributes`, `height`, `expansion`, `centroid`, `status`, `tile` (read from src/bindings/python/valhalla/actor.py). HTTP default port 8002 in Docker. |
| Time to first result | Estimate: 15-30 min with the scripted Docker image on a small country extract (Andorra in the README) to a working `/route`; hours for a large country on a laptop. Assumes Docker and internet for the PBF download. |
| License | MIT (COPYING, "Copyright (c) 2018 Valhalla contributors, 2015-2017 Mapillary AB, Mapzen"). GitHub metadata shows NOASSERTION because LICENSE.md only links to COPYING. PyPI `pyvalhalla` lists COPYING as licence file. OSM data and test data are ODbL (README "License"). |

## Minimal usage

Not run. Scripted Docker image, from docker/README.md, then a route and a map-matching call.

```bash
mkdir custom_files
wget -O custom_files/andorra-latest.osm.pbf https://download.geofabrik.de/europe/andorra-latest.osm.pbf
docker run -dt --name valhalla -p 8002:8002 -v $PWD/custom_files:/custom_files ghcr.io/valhalla/valhalla-scripted:3.9.1
# wait for tile build to finish (docker logs -f valhalla), then:
curl -s localhost:8002/route --data '{"locations":[{"lat":42.5063,"lon":1.5218},{"lat":42.5445,"lon":1.5320}],"costing":"auto"}'
curl -s localhost:8002/trace_route --data '{"shape":[{"lat":42.5063,"lon":1.5218},{"lat":42.5080,"lon":1.5225},{"lat":42.5101,"lon":1.5231}],"costing":"auto","shape_match":"map_snap"}'
```

In-process Python, adapted from src/bindings/python/README.md:

```python
from valhalla import Actor, get_config
actor = Actor(get_config(tile_extract="./custom_files/valhalla_tiles.tar", verbose=True))
iso = actor.isochrone({"locations": [{"lat": 42.5063, "lon": 1.5218}], "costing": "pedestrian",
                       "contours": [{"time": 10}], "polygons": True})
```

## Wiring it into a nav stack

- Route => vehicle: decode the shape (encoded polyline, precision 6 per Valhalla API docs, not re-checked here) to lat/lon, convert to local ENU with [pymap3d](./geospace-code__pymap3d.md) or [GeographicLib](./geographiclib__geographiclib.md), and feed as waypoints to [Nav2](./ros-navigation__navigation2.md) via `navsat_transform` in [robot_localization](./cra-ros-pkg__robot_localization.md), or as a MAVLink mission via [MAVSDK-Python](./mavlink__mavsdk-python.md) for a ground rover.
- GNSS-degraded road vehicles: `trace_route` / `trace_attributes` snap a noisy or dead-reckoned track to the road graph and return edge attributes (speed limit, road class), usable as a pseudo-measurement or sanity check on an INS track ([KF-GINS](./i2nav-whu__kf-gins.md), [OB_GINS](./i2nav-whu__ob_gins.md)).
- Isochrones as reachability polygons for a COP layer in [MapLibre GL JS](./maplibre__maplibre-gl-js.md) or [deck.gl](./visgl__deck.gl.md); `exclude_polygons` to route around areas reported as jammed or blocked.
- `height` action samples the elevation tiles along a path when elevation was built.
- Basemap from the same PBF: [Martin](./maplibre__martin.md) / [PMTiles](./protomaps__pmtiles.md).

Catalog page: [catalog/repos/valhalla__valhalla.md](../../catalog/repos/valhalla__valhalla.md). Concepts: [path-planning](../../catalog/concepts/path-planning.md), [ground-vehicle-nav](../../catalog/concepts/ground-vehicle-nav.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- Tile build is the slow part and is memory-heavy; `server_threads` defaults to `nproc` and the docker README says to lower it if the build gets killed. A SIGSEGV in the enhance stage at concurrency > 1, worse with elevation, was reported and closed (#6331, 2026-09); stay on 3.9.x or later.
- Scripted image writes into `/custom_files`; a read-only mount fails (#5672, open). Multiple PBF URLs are marked "not recommended" (#3925 per docker README); merge extracts first.
- Map matching edge cases: `/trace_route` fails on trivially short traces (#5050), `trace_route` and `trace_attributes` can return different shapes (#4501), failures depending on coordinate pairs (#3675). Keep traces > a few points and check `ValhallaError.code`.
- Public demo server (valhalla.openstreetmap.de, FOSSGIS) has had outages (#6067) and asks apps to send `X-Client-Id`; do not depend on it in a demo.
- Wheels only for the four platforms above with glibc >= 2.28; other platforms build from sdist and need the full C++ toolchain.
- Memory growth in the long-running service (#5172, open) and a multimodal leak (#6412, open); restart long-lived services or use one-shot mode for batch jobs.
- Elevation sources and compressed HGT support are still being reworked (#6163, #6049).

## Alternatives

- [OSRM](./project-osrm__osrm-backend.md) - prefer for maximum query speed and large distance tables with a fixed profile.
- [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md) - prefer in a JVM stack or for its custom-model profiles.
- [OSMnx](./gboeing__osmnx.md) - prefer for quick Python graph experiments over a small AOI.

Sources: `gh api repos/valhalla/valhalla` (NOASSERTION, latest release 3.9.1 2026-10-06), GHCR tag list valhalla/valhalla-scripted, PyPI JSON `pyvalhalla` (3.9.1, wheel tags) and `pyvalhalla-weekly`, README.md, COPYING, LICENSE.md, pyproject.toml (`[project.scripts]`), docker/README.md, src/bindings/python/README.md, src/bindings/python/valhalla/actor.py, src/bindings/python/valhalla/__init__.py, issues #6331, #5672, #5050, #4501, #3675, #6067, #5172, #6412, #6163, #6049.
