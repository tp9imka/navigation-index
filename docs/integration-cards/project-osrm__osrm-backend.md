# OSRM - integration card
<!-- about: repo:project-osrm/osrm-backend -->
One-line: fastest open road router on OSM - offline route, nearest, distance/duration table, trip (TSP) and HMM map matching over HTTP, Node or Python, from a one-time preprocessed extract.

| | |
|---|---|
| Install | Docker: `ghcr.io/project-osrm/osrm-backend:v26.11.0-debian` (release v26.11.0, 2026-11-01). GHCR tags for v26.x all carry a `-debian` suffix (also `-amd64-debian`, `-arm64-debian`, `-debug-`, `-assertions-`); `latest` = master. Node: `npm install @project-osrm/osrm` (npm `latest` 26.10.0, 2026-10-01; engines `node ^20.17.0 \|\| >=22.9.0`). The unscoped npm `osrm` package stopped at 5.26.0 (2021). Python: `pip install osrm-bindings` (PyPI 26.10.0; module `import osrm`). Source: CMake + vcpkg (`cmake --preset ci-linux`). |
| Runs on | Linux x86_64/arm64 (Docker, Debian-based), macOS arm64, Windows (source/vcpkg). Python wheels on PyPI 26.10.0: cp312-abi3 for manylinux_2_28 x86_64/aarch64 and macOS 15 arm64 only (no Windows wheel in that release, although the README lists Windows x86_64). Node prebuilt binaries need `GLIBCXX_3.4.26`+. No GPU. |
| Inputs | `.osm.pbf` + a Lua profile (`/opt/car.lua`, `foot.lua`, `bicycle.lua` in the image) for preprocessing. Queries: coordinates as `lon,lat` (URL) or `[lon, lat]` (Node/Python), optional `bearings`, `radiuses`, `exclude` classes, timestamps for match. |
| Outputs | JSON (or FlatBuffers) routes with polyline/polyline6/GeoJSON geometry, legs/steps, annotations (duration, distance, speed, nodes); duration/distance matrices; matched tracepoints with confidence; Mapbox Vector Tiles of the routing graph (`/tile`). |
| Key API / entry points | Preprocess MLD: `osrm-extract -p profile.lua x.osm.pbf` => `osrm-partition x.osrm` => `osrm-customize x.osrm`; or CH: `osrm-contract x.osrm`. Serve: `osrm-routed --algorithm mld x.osrm` (port 5000). HTTP: `/route/v1/{profile}/{lon,lat;lon,lat}`, `/nearest/v1`, `/table/v1`, `/match/v1`, `/trip/v1`, `/tile/v1`. Node: `new OSRM({path, algorithm: 'MLD'})` with `route`, `nearest`, `table`, `match`, `trip`, `tile` (docs/nodejs/api.md). Python: `osrm.OSRM(path)`, `osrm.RouteParameters(coordinates=[(lon, lat), ...])`, `.Route(params)` (src/python/README.md). |
| Time to first result | Estimate: 15 min with Docker on a city extract (Berlin in the README) to a `curl` route; preprocessing a large country can take hours and tens of GB RAM (no official figure; see #6560). |
| License | BSD-2-Clause (LICENSE.TXT, "Copyright (c) 2017, Project OSRM contributors"); GitHub metadata, npm and PyPI agree. Routing data from OSM => ODbL attribution. |

## Minimal usage

Not run. From the README Quick Start (MLD pipeline), pinned tag:

```bash
wget http://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf
IMG=ghcr.io/project-osrm/osrm-backend:v26.11.0-debian
docker run -t -v "${PWD}:/data" $IMG osrm-extract -p /opt/car.lua /data/berlin-latest.osm.pbf
docker run -t -v "${PWD}:/data" $IMG osrm-partition /data/berlin-latest.osrm
docker run -t -v "${PWD}:/data" $IMG osrm-customize /data/berlin-latest.osrm
docker run -t -i -p 5000:5000 -v "${PWD}:/data" $IMG osrm-routed --algorithm mld /data/berlin-latest.osrm
curl "http://127.0.0.1:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?geometries=geojson&overview=full"
# map-match a noisy track (lon,lat;...), unix timestamps optional:
curl "http://127.0.0.1:5000/match/v1/driving/13.3889,52.5170;13.3895,52.5162;13.3901,52.5153?geometries=geojson&radiuses=25;25;25"
```

Node (adapted from docs/nodejs/api.md; note `algorithm` must match the preprocessing):

```javascript
const OSRM = require('@project-osrm/osrm');
const osrm = new OSRM({path: 'berlin-latest.osrm', algorithm: 'MLD'});
osrm.route({coordinates: [[13.38886, 52.517037], [13.385983, 52.496891]], geometries: 'geojson'},
  (err, res) => console.log(err || res.routes[0].distance));
```

## Wiring it into a nav stack

- Convoy/UGV routing: route geometry (GeoJSON) => ENU waypoints via [pymap3d](./geospace-code__pymap3d.md) or [pyproj](./pyproj4__pyproj.md) => [Nav2](./ros-navigation__navigation2.md) through `navsat_transform` in [robot_localization](./cra-ros-pkg__robot_localization.md), or a rover mission via [MAVSDK-Python](./mavlink__mavsdk-python.md).
- GNSS-denied ground vehicles: `/match` snaps a dead-reckoned or degraded-GNSS track to roads and returns per-point `confidence`; a cheap road-constraint check on an INS solution ([KF-GINS](./i2nav-whu__kf-gins.md)). OSRM matching does not use heading or speed beyond timestamps (#4301 discusses time in confidence).
- `/table` gives travel-time matrices for multi-vehicle task allocation; `/trip` gives a greedy TSP ordering.
- Display: GeoJSON routes on [MapLibre GL JS](./maplibre__maplibre-gl-js.md) / [Leaflet](./leaflet__leaflet.md); `/tile` debug tiles show the routing graph.
- Python glue for research: [OSMnx](./gboeing__osmnx.md) for graph experiments, OSRM for production queries.

Catalog page: [catalog/repos/project-osrm__osrm-backend.md](../../catalog/repos/project-osrm__osrm-backend.md). Concepts: [path-planning](../../catalog/concepts/path-planning.md), [ground-vehicle-nav](../../catalog/concepts/ground-vehicle-nav.md), [gis-mapping](../../catalog/concepts/gis-mapping.md).

## Gotchas

- npm package name: use `@project-osrm/osrm`. The unscoped `osrm` package is frozen at 5.26.0 (2021); the README says "Prior to v5.27.0, the `osrm` Node package was unscoped". docs/nodejs/api.md still shows binary paths like `node_modules/osrm/lib/binding_napi_v8/osrm-extract` and profiles under `node_modules/osrm/profiles/`; adjust the path to `node_modules/@project-osrm/osrm/...` (not verified on disk).
- Version scheme jumped from v6.0.0 to calendar-style v26.N (the GitHub release list shows monthly v26.6 to v26.11 in 2026). npm (26.10.0) and PyPI (26.10.0) lag the GitHub release (v26.11.0). Data must be re-preprocessed with the same version that serves it.
- Docker tags: README says `<tag>`, but v26.x tags in GHCR are `v26.11.0-debian` etc.; a plain `v26.11.0` tag does not exist. `latest` follows master.
- Algorithm mismatch: Node binding defaults to `CH`; if you ran `osrm-partition`/`osrm-customize` you must pass `algorithm: 'MLD'`. Running CH against MLD data via shared memory can leave the lock held (#5003).
- Memory: `osrm-extract` is RAM-hungry; Docker exit 137 (OOM kill) is common (#6560); planet foot profile segfault (#6625). Use a regional extract.
- arm64: an MLD partition bug on AWS Graviton was fixed (#7501, closed 2026-04); arm64 Node prebuilt binaries were added (#7651, closed 2026-07). Use a recent release on Jetson/Graviton.
- Open regressions in the newest line: JSON `/table` latency regression in v26.10.0 vs v5.27.1 (#7761), JSON vs FlatBuffers mismatch on unreachable pairs (#7762).
- Map matching: invalid node id (#6482), half-route matches (#5934), legs not collapsed without waypoints (#7209). Tune `radiuses` to your GNSS error, not the default.
- Demo server `router.project-osrm.org` has a usage policy; not for production or heavy demos.

## Alternatives

- [Valhalla](./valhalla__valhalla.md) - prefer for per-request costing changes (avoid polygons, truck dimensions), isochrones and elevation without re-preprocessing.
- [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md) - prefer in a JVM stack; custom models per request.
- [OSMnx](./gboeing__osmnx.md) - prefer for algorithm prototyping on small areas in Python.

Sources: `gh api repos/Project-OSRM/osrm-backend` (BSD-2-Clause, releases v26.6.2 to v26.11.0), GHCR tag list project-osrm/osrm-backend, npm registry `@project-osrm/osrm` and `osrm` dist-tags, PyPI JSON `osrm-bindings` (26.10.0, wheel files), README.md, LICENSE.TXT, package.json (name, engines, binary), docs/nodejs/api.md, src/python/README.md, issues #6560, #6625, #5003, #7501, #7651, #7761, #7762, #6482, #5934, #7209, #4301.
