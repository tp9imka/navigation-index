# pymap3d - integration card
<!-- about: repo:geospace-code/pymap3d -->
Pure-Python geodetic / ECEF / ENU / NED / AER / ECI conversions with a Matlab-like API: the glue for turning GNSS lat/lon/alt into the local metric frame your filter, map or simulator works in, and back.

| | |
|---|---|
| Install | `python3 -m pip install pymap3d` (PyPI 3.2.0, `requires-python >=3.9`). Numpy optional (needed for arrays), AstroPy optional (higher-accuracy ECI / sky conversions). Body-frame functions need `pip install git+https://github.com/geospace-code/pymap3d` (see Gotchas). |
| Runs on | Anything that runs Python; no compiled deps. Stdlib-only mode handles scalars. |
| Inputs | Geodetic lat/lon in degrees by default (`deg=False` for radians), heights in metres above the ellipsoid; ECEF/ENU/NED/AER in metres and degrees; scalars or N-D numpy arrays; `ell=Ellipsoid.from_name('wgs84')` etc.; `datetime` for ECI. |
| Outputs | Tuples of the same shape as the input: `(x, y, z)`, `(e, n, u)`, `(n, e, d)`, `(az, el, srange)`, `(lat, lon, alt)`. Rotation matrices via `*_matrix` helpers. |
| Key API / entry points | `geodetic2ecef(lat, lon, alt, ell=None, deg=True)`, `ecef2geodetic(x, y, z, ell=None, deg=True)`, `geodetic2enu(lat, lon, h, lat0, lon0, h0, ...)`, `enu2geodetic(e, n, u, lat0, lon0, h0, ...)`, `geodetic2ned` / `ned2geodetic`, `geodetic2aer` / `aer2geodetic`, `ecef2enuv` (vectors), `ecef2enu_matrix(lat0, lon0)`, `Ellipsoid.from_name(name)`, `pymap3d.vincenty.vdist` / `vreckon`; CLI `python -m pymap3d geodetic2ecef 40 -105 1600`. |
| Time to first result | Estimate: under 5 min (pip install + one call). |
| License | BSD-2-Clause |

## Minimal usage
Not run. GNSS fixes into a local NED frame anchored at the first fix:

```python
import numpy as np
import pymap3d as pm

lat = np.array([47.3977, 47.3979, 47.3982]); lon = np.array([8.5456, 8.5459, 8.5463])
h = np.array([488.0, 489.2, 490.1])                       # ellipsoidal height, metres
n, e, d = pm.geodetic2ned(lat, lon, h, lat[0], lon[0], h[0])
lat2, lon2, h2 = pm.ned2geodetic(n, e, d, lat[0], lon[0], h[0])   # round trip
az, el, rng = pm.geodetic2aer(lat[-1], lon[-1], h[-1], lat[0], lon[0], h[0])
```

CLI (README shows the output `-1266643.13... -4727176.53... 4079014.03...`):

```sh
python -m pymap3d geodetic2ecef 40.0 -105.0 1600.0
```

## Wiring it into a nav stack
- Between GNSS and the filter: [pyubx2](./semuconsulting__pyubx2.md) NAV-PVT or RINEX-derived fixes => `geodetic2ned` => position measurement for [filterpy](./rlabbe__filterpy.md) / the stdlib EKF in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/) / a [GTSAM](./borglab__gtsam.md) GPSFactor (which expects a local-frame point).
- ROS: `robot_localization`'s `navsat_transform_node` already does UTM-based conversion ([card](./cra-ros-pkg__robot_localization.md)); use pymap3d for offline analysis or non-ROS code.
- PX4 / MAVLink use NED; ArduPilot local frames are NED; Gazebo and ROS REP-103 use ENU. `geodetic2enu` vs `geodetic2ned` is the only switch, but axis order and sign of the vertical differ.
- Satellite geometry: `ecef2aer` from receiver ECEF to satellite ECEF gives elevation/azimuth for masks and skyplots (alongside [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) or [laika](./commaai__laika.md)).
- Map/terrain: convert to lat/lon before handing points to [GDAL](./osgeo__gdal.md) / [rasterio](./rasterio__rasterio.md) DEM lookups, which work in a CRS, not a local tangent plane.

## Gotchas
- Heights are ellipsoidal. MAVLink `GLOBAL_POSITION_INT.alt` and NMEA GGA altitude are above MSL (geoid); mixing them injects a geoid-undulation offset of tens of metres in the vertical. Apply a geoid model (e.g. via pyproj) first.
- Body-frame functions documented in the README (`ned2body`, `body2ned`, `body2enu`, x-forward/y-right/z-down with zyx yaw/pitch/roll) are on `main` but `body.py` is absent from the v3.2.0 tag that PyPI ships; install from git or write the rotation yourself.
- Without numpy only scalars work; pass lists and you get errors rather than vectorised output (README "array vs scalar").
- `ecef2enuv` treats a vector rotation, not a point transform; issue #95 notes a spherical-earth assumption there. #49: `geodetic2enu` vs `ecef2enu` results differ if you pass inconsistent heights.
- ECI conversions without AstroPy use Vallado/Meeus approximations; no atmospheric refraction anywhere (README caveats). Open issue #87: test failures on 32-bit ARM (armel).
- Ellipsoid instances are cached; call `clear_ellipsoid_caches()` in tests that mutate them.

## Alternatives
- [pyproj](../../catalog/repos/pyproj4__pyproj.md) - full PROJ CRS/datum/geoid support; prefer it when you need EPSG codes, UTM, vertical datums or datum shifts.
- [pyubx2](./semuconsulting__pyubx2.md) helpers (`llh2ecef`, `ecef2llh`, `haversine`) - enough if you only need ECEF<=>LLH next to a u-blox parser.
- [ahrs](../../catalog/repos/mayitzin__ahrs.md) - includes WGS84 utilities; enough if you already use it for attitude.

Sources: `gh api repos/geospace-code/pymap3d/readme`, `pyproject.toml`, `src/pymap3d/ecef.py` (signatures), `src/pymap3d/__init__.py` on main vs `?ref=v3.2.0` (body.py 404), PyPI JSON (version 3.2.0), issues #49, #87, #95.
