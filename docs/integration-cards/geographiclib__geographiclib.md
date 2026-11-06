# GeographicLib - integration card
<!-- about: repo:geographiclib/geographiclib -->
One-line: Charles Karney's small C++ library for nanometre-accurate geodesics plus the nav-relevant conversions (UTM/UPS/MGRS, geocentric, local tangent plane), EGM geoid heights, gravity and WMM/IGRF magnetic field - the dependency MAVROS and many INS stacks already pull in.

| | |
|---|---|
| Install | C++: `sudo apt install libgeographiclib-dev geographiclib-tools` (Ubuntu noble ships 2.3; Debian has 2.7-1), or build from source with CMake (`cmake -B build && cmake --build build && sudo cmake --install build`; current version 2.7, tag `v2.7` / release tag `r2.7`; users should take the `release` branch per README). Data: `sudo geographiclib-get-geoids egm96-5`, `geographiclib-get-magnetic wmm2025`, `geographiclib-get-gravity ...` (installed scripts). Python: `pip install geographiclib` (PyPI 2.1, 2025-08-21, MIT, requires Python >=3.7; pure Python, separate repo geographiclib/geographiclib-python). |
| Runs on | Anything with a C++17 compiler (`cxx_std_17`) and CMake >= 3.17 (CMakeLists.txt); header + small shared/static lib, no external deps. Pure-Python package runs anywhere. No arch-specific code noted; arm64 not separately checked. |
| Inputs | Geodetic lat/lon (degrees), heights above the ellipsoid (m), azimuths (degrees clockwise from north), distances (m), MGRS strings, UTM zone/hemisphere/easting/northing, time in fractional years for magnetic models. Data files: geoid `.pgm` grids, magnetic `.wmm` + `.cof`, gravity `.egm` (downloaded separately). |
| Outputs | Distances/azimuths, intermediate geodesic points, polygon areas, UTM/UPS/MGRS, ECEF and local ENU (`LocalCartesian`), geoid height N (m), magnetic field components (east, north, up, nT) and rates, gravity vectors. CLI tools print text. |
| Key API / entry points | C++ (headers in `include/GeographicLib/`): `Geodesic::WGS84().Inverse(lat1, lon1, lat2, lon2, s12, azi1, azi2)` / `.Direct(...)`; `LocalCartesian lc(lat0, lon0, h0); lc.Forward(lat, lon, h, x, y, z); lc.Reverse(...)`; `UTMUPS::Forward(lat, lon, zone, northp, x, y)`; `MGRS::Forward(zone, northp, x, y, prec, mgrs)` / `MGRS::Reverse(...)`; `Geoid g("egm96-5"); double N = g(lat, lon);`; `MagneticModel m("wmm2025"); m(t, lat, lon, h, Bx, By, Bz);`; CMake `find_package(GeographicLib)` => namespaced target `GeographicLib::GeographicLib` (namespace targets since 1.47 per cmake/project-config.cmake.in; `${GeographicLib_LIBRARIES}` still set for older consumers). CLIs (tools/): `GeoConvert`, `GeodSolve`, `CartConvert`, `GeoidEval`, `MagneticField`, `Gravity`, `RhumbSolve`, `Planimeter`, `IntersectTool`, `TransverseMercatorProj`. Python: `from geographiclib.geodesic import Geodesic; Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)` returns a dict (`s12`, `azi1`, `azi2`, ...); `.Direct`, `.InverseLine`, `.DirectLine`, `.Polygon`. |
| Time to first result | Estimate: 5 min with apt and the CLI tools (`echo "47.37 8.54" \| GeoConvert -m`); 30 min to link it into a C++ node with CMake. Geoid/magnetic data downloads add a few minutes (sizes in the get-scripts, e.g. egm96-5 is 11 MB download / 19 MB on disk). |
| License | MIT (LICENSE.txt, "Copyright (c) 2008-2025, Charles Karney"); GitHub metadata MIT; PyPI MIT. Geoid/gravity/magnetic datasets come from NGA/NOAA/IAGA sources fetched by the scripts; their terms are not restated in the repo files read. |

## Minimal usage

Not run. CLI first (geographiclib-tools), then the C++ calls a nav node needs.

```bash
echo "47.3769 8.5417" | GeoConvert -m             # => MGRS (default 1 m precision)
echo "47.3769 8.5417" | GeoConvert -u             # => UTM zone + easting/northing
echo "47.3769 8.5417 47.4000 8.6000" | GeodSolve -i   # => azi1 azi2 s12
sudo geographiclib-get-geoids egm96-5
echo "47.3769 8.5417" | GeoidEval -n egm96-5      # => geoid height N (m)
```

```cpp
#include <GeographicLib/Geodesic.hpp>
#include <GeographicLib/LocalCartesian.hpp>
#include <GeographicLib/Geoid.hpp>
#include <GeographicLib/MGRS.hpp>
#include <GeographicLib/UTMUPS.hpp>
using namespace GeographicLib;

LocalCartesian enu(47.3769, 8.5417, 450.0);          // origin lat, lon, h_ellipsoid
double x, y, z; enu.Forward(47.3800, 8.5450, 455.0, x, y, z);   // ENU metres
double s12, azi1, azi2; Geodesic::WGS84().Inverse(47.3769, 8.5417, 47.40, 8.60, s12, azi1, azi2);
Geoid egm("egm96-5"); double N = egm(47.3769, 8.5417);           // h_msl = h_ellipsoid - N
int zone; bool north; double e, n; std::string mgrs;
UTMUPS::Forward(47.3769, 8.5417, zone, north, e, n);
MGRS::Forward(zone, north, e, n, 5, mgrs);
```

```cmake
find_package(GeographicLib REQUIRED)
target_link_libraries(my_node GeographicLib::GeographicLib)
```

## Wiring it into a nav stack

- MAVROS: needs GeographicLib datasets installed (`ros2 run mavros install_geographiclib_datasets.sh`, which the [MAVROS card](./mavlink__mavros.md) marks as mandatory; skipping it makes the node fail at start).
- ENU for estimators: `LocalCartesian` gives the same ENU frame as `navsat_transform` style pipelines in [robot_localization](./cra-ros-pkg__robot_localization.md); in Python, [pymap3d](./geospace-code__pymap3d.md) is the lighter equivalent.
- C2 grid references: MGRS for TAK/C2 messages and operator UIs ([pytak](./snstac__pytak.md), [milsymbol](./spatialillusions__milsymbol.md)); [mgrs](../../catalog/repos/hobuinc__mgrs.md) is the Python alternative.
- Magnetic heading and magnetometer aiding: `MagneticModel("wmm2025")` gives declination and expected field vector for compass calibration or magnetic-anomaly navigation ([MagNav.jl](./mit-ai-accelerator__magnav.jl.md) uses its own models; this is the C++ route).
- Terrain-referenced navigation: geoid correction between GNSS ellipsoidal heights and DEM MSL heights before matching ([python-tercom](./alti3__python-tercom.md), [tercom_nav](./mzahana__tercom_nav.md)).
- Python geodesics: PROJ (and therefore [pyproj](./pyproj4__pyproj.md) `Geod`) uses Karney's geodesic C implementation, per the author in #7.

Catalog page: [catalog/repos/geographiclib__geographiclib.md](../../catalog/repos/geographiclib__geographiclib.md). Concepts: [geodesy](../../catalog/concepts/geodesy.md), [magnetic-nav](../../catalog/concepts/magnetic-nav.md), [terrain-nav](../../catalog/concepts/terrain-nav.md).

## Gotchas

- The Python package is geodesics only. `pip install geographiclib` gives `Geodesic`, `GeodesicLine`, `PolygonArea`; no UTM, MGRS, `LocalCartesian`, geoid or magnetic models. The author says he has no plans to expand it (#7). For those in Python use pyproj, pymap3d or mgrs, or call the CLI tools.
- Data is separate from code: `Geoid`, `MagneticModel` and `GravityModel` throw at construction if the dataset is not installed under the data dir (default `/usr/local/share/GeographicLib` for source installs per CMakeLists.txt; distro packages may use `/usr/share/GeographicLib`, not verified). Bake `geographiclib-get-geoids` into your Dockerfile.
- Geoid sign convention: `Geoid` returns N, the height of the geoid above the ellipsoid, so `h_msl = h_ellipsoid - N`; the `convertflag` of `ConvertHeight` confused users (#4).
- Magnetic model validity: WMM2020 covers 2020-2025, so on 2026 dates use `wmm2025` (2025-2030); the script lists `wmm2015` as deprecated. `MagneticModel::operator()` does not check the time argument (header comment), so a stale model silently extrapolates; compare `t` with `MinTime()` / `MaxTime()` yourself.
- Branches: default branch `main` is for developers; README says users should take `release` or a `r2.x` tag. Distro packages lag (Ubuntu noble 2.3 vs upstream 2.7).
- Big datasets: `egm2008-1` is 170 MB download / 470 MB on disk (get-geoids script table); `egm96-5` is usually enough for UAV height conversion.
- Windows MSVC debug builds broke once (#37, closed); an unexpected Boost dependency question (#42, closed) - the core library has no Boost dependency.
- Many language ports exist (C, Fortran, Java, JavaScript `geographiclib-geodesic` on npm 2.2.0, MATLAB, Python); the unscoped npm `geographiclib` stops at 1.52.2 (2022). They implement geodesics, not the full C++ feature set.

## Alternatives

- [pyproj](./pyproj4__pyproj.md) - prefer in Python for datum transformations, projections and vertical grids.
- [pymap3d](./geospace-code__pymap3d.md) - prefer for pure-Python ECEF/ENU/NED/AER math.
- [mgrs](../../catalog/repos/hobuinc__mgrs.md) - prefer for MGRS-only needs in Python.

Sources: `gh api repos/geographiclib/geographiclib` (MIT, tags v2.7, v2.6, branches devel/main/release), repos/geographiclib/geographiclib-python (MIT, file list), PyPI JSON `geographiclib` (2.1), npm registry `geographiclib` (1.52.2) and `geographiclib-geodesic` (2.2.0), sources.debian.org geographiclib versions, packages.ubuntu.com noble `libgeographiclib-dev` / `geographiclib-tools` (2.3-1build1), README.md, LICENSE.txt, CMakeLists.txt, src/CMakeLists.txt (targets and aliases), cmake/ listing, cmake/project-config.cmake.in, cmake/CMakeLists.txt (install EXPORT NAMESPACE), man/GeoConvert.pod, man/GeodSolve.pod, man/GeoidEval.pod, tools/ listing, tools/geographiclib-get-geoids.sh, tools/geographiclib-get-magnetic.sh, include/GeographicLib/{LocalCartesian,UTMUPS,MGRS,Geoid,MagneticModel}.hpp, geographiclib-python geographiclib/geodesic.py, issues #4, #7, #37, #42.
