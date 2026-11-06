# PROJ - integration card
<!-- about: repo:osgeo/proj -->
The coordinate reference system engine under GDAL, QGIS, pyproj and most GIS stacks: geodetic <=> projected <=> ECEF conversions, datum transformations (with shift grids), geoid heights, time-dependent frames and geodesics. In a hackathon it is what makes your nav estimate, the map tiles, the MGRS grid and the DEM agree on where a point is.

| | |
|---|---|
| Install | CLIs: `sudo apt-get install proj-bin` (Debian/Ubuntu; `libproj-dev` for headers), `conda install -c conda-forge proj` (+ `proj-data` for grids), `docker pull osgeo/proj`, `brew install proj` (install.rst). Python: `pip install pyproj` (separate project pyproj4/pyproj; PyPI 3.8.0, 2026-09-05, `requires_python >=3.12`; wheels bundle a PROJ build but "do not include transformation grids"). Source: CMake, `mkdir build && cd build && cmake .. && cmake --build . && cmake --build . --target install`; needs SQLite3 >= 3.11, optional libtiff >= 4.0 (grids) and curl >= 7.29 (network grids). Latest release 9.9.0 (2026-09-15). |
| Runs on | Linux, macOS, Windows (vcpkg/conda), any arch; also a WebAssembly build under discussion (issue #4327). CPU only. |
| Inputs | Coordinates as tuples/arrays with a source CRS given as `EPSG:xxxx`, WKT, PROJJSON or a PROJ pipeline string; optional epoch for time-dependent frames (cct takes x y z t). Units follow the CRS (deg for geographic, metres for projected/ECEF). Grids: GeoTIFF shift grids from PROJ-data (local `PROJ_DATA` dir or https://cdn.proj.org). |
| Outputs | Transformed coordinates; CRS / operation metadata (`projinfo`), geodesic distance and azimuth (`geod`). |
| Key API / entry points | CLIs (`src/apps/`): `cs2cs` (CRS to CRS), `cct` (pipeline, 4D), `projinfo` (find operations, show accuracy), `projsync` (download grids), `geod`, `proj`, `gie` (test runner). C API (`src/proj.h`): `proj_context_create`, `proj_create_crs_to_crs(ctx, src, dst, area)`, `proj_normalize_for_visualization(ctx, P)` (lon/lat order), `proj_trans(P, PJ_FWD, coord)`, `proj_trans_generic`, `proj_context_set_enable_network(ctx, 1)`. Python (pyproj): `pyproj.Transformer.from_crs(src, dst, always_xy=True).transform(x, y[, z])`, `pyproj.CRS`, `pyproj.Geod`. |
| Time to first result | Estimate: 5 min with `pip install pyproj` or `apt-get install proj-bin`. |
| License | MIT-style ("X/MIT") per `COPYING`; GitHub shows NOASSERTION because the file is a custom preamble + MIT text. Grid data (PROJ-data, cdn.proj.org) is a separate package; per its README.DATA all grids are under permissive licences (public domain, MIT, BSD, CC0, CC-BY, CC-BY-SA), so check each grid's attribution if you redistribute grids. `proj.db` embeds the EPSG dataset (v13.105, 2026-10-12 in `data/sql/metadata.sql`); EPSG publishes its own terms of use, which COPYING does not cover - not checked here. |

## Minimal usage
Not run. From README, install.rst, usage/network.rst and the pyproj Transformer API.

```sh
echo "50.45 30.52 180" | cs2cs EPSG:4979 EPSG:4978          # WGS84 lat lon h => ECEF metres
echo "30.52 50.45" | cs2cs +proj=longlat +datum=WGS84 +to EPSG:32636   # => UTM 36N
projinfo -s EPSG:4326 -t EPSG:5773 --spatial-test intersects   # list ops incl. geoid models
PROJ_NETWORK=ON cs2cs EPSG:4979 EPSG:4326+5773 <<< "50.45 30.52 180"   # ellipsoidal => EGM96 height, fetches grid
projsync --system-directory --area-of-use Ukraine              # prefetch grids for offline use
```

```python
from pyproj import Transformer
to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True)
e, n = to_utm.transform(30.52, 50.45)   # lon, lat because always_xy=True
```

## Wiring it into a nav stack
- GNSS / INS output (WGS84 lat/lon/ellipsoidal h) => local ENU or UTM for the planner and for map matching. [pymap3d](./geospace-code__pymap3d.md) is lighter for pure ECEF/ENU/NED math; use PROJ when datums, geoids or national grids are involved.
- DEM and terrain-referenced nav: [GDAL](./osgeo__gdal.md) and [rasterio](./rasterio__rasterio.md) reproject through PROJ; a mismatch between orthometric DEM heights and ellipsoidal GNSS/baro heights is a classic TERCOM / [python-tercom](./alti3__python-tercom.md) error source, fixed with a geoid grid (EGM96/EGM2008) via PROJ.
- Map front-ends: [Cesium](./cesiumgs__cesium.md) and [MapLibre](./maplibre__maplibre-gl-js.md) use Web Mercator / ECEF internally; PROJ converts mission data into those frames.
- MGRS for TAK-style reporting is not a PROJ CRS; use a separate converter and keep PROJ for the underlying UTM.

## Gotchas
- Axis order: EPSG:4326 is officially latitude, longitude. `cs2cs EPSG:4326 ...` and `proj_create_crs_to_crs` follow authority order; use `proj_normalize_for_visualization` (C) or `always_xy=True` (pyproj) to get lon, lat.
- Grids are not installed by pip wheels and network access is off unless enabled (`network = on` in proj.ini, `PROJ_NETWORK=ON`, or `proj_context_set_enable_network`). Without grids PROJ can fall back to a "ballpark" operation that applies no datum shift; the glossary says this can mean "errors of a few hundreds of metres" horizontally and "a few tens of metres" vertically. Check `projinfo -s ... -t ...` accuracy and operation names before trusting heights.
- Offline field kit: run `projsync` (or mirror cdn.proj.org) before deploying, since the CDN won't be reachable on a disconnected network.
- Several PROJ copies on one machine (system, conda, pyproj wheel, GDAL) each with its own `proj.db`; keep `PROJ_DATA` pointed at the matching data dir.
- Geodesy is static by default; plate motion between ITRF epochs (cm/yr) only matters if you compare against old survey control.

## Alternatives
- [pyproj](../../catalog/repos/pyproj4__pyproj.md) - the Python binding; usually what you actually import.
- [pymap3d](./geospace-code__pymap3d.md) - pure Python ECEF/ENU/NED/AER without datums or grids; zero install friction.
- [GDAL](./osgeo__gdal.md) - when the job is raster/vector reprojection rather than point transforms (uses PROJ internally).

Sources: `README.md`, `COPYING`, `docs/source/install.rst`, `docs/source/usage/network.rst`, `src/proj.h`, `src/apps/` listing, `Dockerfile`, release 9.9.0 (github.com/OSGeo/PROJ); `README.DATA` (github.com/OSGeo/PROJ-data); pyproj `docs/installation.rst`, `pyproj/transformer.py` (github.com/pyproj4/pyproj); https://pypi.org/pypi/pyproj/json.
