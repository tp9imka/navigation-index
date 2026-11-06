# pyproj - integration card
<!-- about: repo:pyproj4/pyproj -->
One-line: the Python front-end to PROJ - correct datum, projection, UTM, ECEF and vertical (geoid) transformations plus ellipsoidal geodesics, with self-contained wheels; the default answer to "convert these coordinates" in a Python nav stack.

| | |
|---|---|
| Install | `pip install pyproj` (PyPI 3.8.0, 2026-09-05, MIT, requires Python >=3.12). Wheels bundle PROJ 9.8.1 (history.rst 3.8.0) for manylinux_2_28 and musllinux x86_64/aarch64, macOS arm64 and x86_64, Windows x64/x86/arm64. Older Pythons: 3.7.2 needs >=3.11, 3.7.0/3.7.1 need >=3.10, 3.6.1 needs >=3.9. Optional `pyproj[shapely]` is on `main` only (unreleased). |
| Runs on | Any platform with a wheel; source builds need PROJ (env `PROJ_DIR`, `PROJ_VERSION`). Free-threaded Python classified "2 - Beta". No GPU. |
| Inputs | CRS as EPSG codes (`"EPSG:4326"`, `"EPSG:4978"` ECEF, `"EPSG:326zz"` UTM north), WKT, PROJ strings, PROJJSON, or PROJ pipelines; numeric scalars, lists or numpy arrays; optional `AreaOfInterest`. Units follow the CRS (degrees, metres). |
| Outputs | Transformed coordinates (same shape as input), forward/back azimuths and distances (m) from `Geod`, CRS metadata (axis info, area of use, datum), transformation descriptions and accuracy. |
| Key API / entry points | `Transformer.from_crs(crs_from, crs_to, always_xy=False, area_of_interest=None, ...)`; `transformer.transform(xx, yy[, zz], direction=...)` and `itransform`; `Transformer.from_pipeline(pipeline, always_xy=False)`; `TransformerGroup` (all candidate operations, grid availability); `CRS.from_user_input(...)` / `CRS.from_epsg(code)`; `Geod(ellps="WGS84")` with `inv(lons1, lats1, lons2, lats2)`, `fwd(lons, lats, az, dist)`, `npts`, `line_length`; `pyproj.network.set_network_enabled(True)`; CLI `pyproj sync` (`--area-of-use`, `--bbox`, `--source-id`, `--file`, `--list-files`, `--all`, `--target-directory`) for grid downloads (read from transformer.py, geod.py, network.py, `__main__.py`). |
| Time to first result | Estimate: 5 min from `pip install` to a lat/lon => UTM or ECEF conversion. Vertical (geoid) transforms need the grid files: plan another 15-30 min for `pyproj sync` or network setup. |
| License | MIT (LICENSE), plus LICENSE_proj (PROJ's MIT-style licence) for the bundled library; both declared in pyproject `license-files`. GitHub metadata MIT. Grid files fetched from cdn.proj.org carry per-grid licences (not reviewed here). |

## Minimal usage

Not run. WGS84 => UTM and ECEF, a geodesic range/bearing, and a guarded ellipsoid => EGM2008 height.

```python
from pyproj import CRS, Transformer, Geod
from pyproj.transformer import TransformerGroup

lat, lon, h = 47.3769, 8.5417, 450.0
utm = CRS.from_epsg(32632)
to_utm = Transformer.from_crs("EPSG:4326", utm, always_xy=True)   # input order lon, lat
e, n = to_utm.transform(lon, lat)

to_ecef = Transformer.from_crs("EPSG:4979", "EPSG:4978", always_xy=True)
x, y, z = to_ecef.transform(lon, lat, h)

az12, az21, dist_m = Geod(ellps="WGS84").inv(lon, lat, 8.60, 47.40)

grp = TransformerGroup("EPSG:4979", "EPSG:9518", always_xy=True)  # WGS84 3D => WGS84 + EGM2008 height
print(grp.best_available, grp.transformers[0].description)       # False => grid missing, height would be wrong
_, _, h_msl = grp.transformers[0].transform(lon, lat, h)
```

EPSG:9518 as the WGS 84 + EGM2008 compound CRS is from a maintainer comment in #1593; check with `CRS("EPSG:9518").name` before relying on it.

## Wiring it into a nav stack

- Frames: GNSS fixes (lat/lon/h) => UTM or local tangent plane for an EKF; for ENU/NED around a reference point, [pymap3d](./geospace-code__pymap3d.md) is simpler, pyproj covers the datum side (ITRF realisations, national grids, time-dependent transforms via PROJ).
- Heights: barometric/AGL vs GNSS ellipsoidal vs map MSL heights are the classic bug in terrain-referenced navigation ([TERCOM card](./alti3__python-tercom.md), [tercom_nav](./mzahana__tercom_nav.md)); convert DEM and fix heights with a vertical transform, or use [GeographicLib](./geographiclib__geographiclib.md) `Geoid` explicitly.
- Rasters: [rasterio](./rasterio__rasterio.md) and [GDAL](./osgeo__gdal.md) use PROJ underneath; pyproj CRS objects pass straight to rasterio and geopandas.
- Military grid: MGRS is not in pyproj; use [mgrs](../../catalog/repos/hobuinc__mgrs.md) or GeographicLib `MGRS`.
- Routing outputs ([OSRM](./project-osrm__osrm-backend.md), [Valhalla](./valhalla__valhalla.md), [OSMnx](./gboeing__osmnx.md)) are lon/lat; project once into metric coordinates for controllers.

Catalog page: [catalog/repos/pyproj4__pyproj.md](../../catalog/repos/pyproj4__pyproj.md). Underlying library: [osgeo/proj](../../catalog/repos/osgeo__proj.md). Concept: [geodesy](../../catalog/concepts/geodesy.md).

## Gotchas

- Axis order: EPSG:4326 is officially latitude, longitude. Without `always_xy=True`, `transform(lon, lat)` silently swaps (#1368, #1377 "Inverted x/y"). Set `always_xy=True` everywhere and pass lon first, or pass lat first consistently.
- Grids are not in the wheels ("pyproj 3+ wheels do not include transformation grids", installation.rst). Without them PROJ may pick a ballpark or no-op transformation and return a plausible but wrong value: #1593 reports EGM2008 geoid undulation always 0 after an update (open). Check `TransformerGroup(...).best_available`, inspect `.description`, or download grids with `pyproj sync --area-of-use ...` / enable `PROJ_NETWORK` (`pyproj.network.set_network_enabled(True)`) before the field test.
- Offline field kit: network grid fetching needs internet on first use; a thread's first grid download used to fail and return `inf` (#1644, fixed 2026-10, unreleased at 3.8.0 per history.rst "Latest"). Pre-sync grids.
- Threads: `Transformer` objects across threads have had crashes and random errors (#1499 open since 3.7.0; #1622 use-after-free fixed; #1642 macOS fork segfault open). Create one transformer per thread or protect with a lock.
- Python floor: 3.8.0 needs Python >=3.12; on older Jetson/ROS images pin `pyproj<3.8` (3.7.2 for 3.11, 3.7.1 for 3.10, 3.6.1 for 3.9).
- Mixing PROJ installs: a system PROJ (from GDAL or conda) and the wheel's bundled PROJ can disagree on `PROJ_DATA`; env var precedence changed (#1448). `pyproj.show_versions()` shows which one is loaded.
- `Geod.inv` argument order is lons first, then lats (`inv(lons1, lats1, lons2, lats2)`).

## Alternatives

- [GeographicLib](./geographiclib__geographiclib.md) - prefer for C++ nav code, MGRS/UPS, geoid, gravity and magnetic models without PROJ grids; the geodesic part is what pyproj's `Geod` uses via PROJ.
- [pymap3d](./geospace-code__pymap3d.md) - prefer for pure-Python geodetic/ECEF/ENU/NED/AER conversions with no compiled dependency.
- [PROJ](../../catalog/repos/osgeo__proj.md) directly (C API or `cs2cs`/`projinfo` CLIs) - prefer in C/C++ or shell pipelines.

Sources: `gh api repos/pyproj4/pyproj` (MIT, latest release 3.8.0 2026-09-05), PyPI JSON `pyproj` (3.8.0 files; requires_python of 3.7.2, 3.7.1, 3.7.0, 3.6.1), README.md, LICENSE, LICENSE_proj, pyproject.toml (`license-files`, `[project.scripts] pyproj`), docs/installation.rst, docs/history.rst (Latest, 3.8.0, 3.7.2), pyproj/__init__.py, pyproj/__main__.py, pyproj/network.py, pyproj/geod.py, pyproj/transformer.py, issues #1593, #1368, #1377, #1644, #1499, #1622, #1642, #1448.
