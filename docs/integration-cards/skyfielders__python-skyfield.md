# Skyfield - integration card
<!-- about: repo:skyfielders/python-skyfield -->
Pure-Python astrometry: precise apparent positions of Sun, Moon, planets and catalog stars from JPL ephemerides, SGP4 satellite propagation from TLE/OMM, and observer geometry on WGS84. For alt-nav it is the truth model behind celestial fixes (star tracker / sun sensor => position), LEO satellite visibility and pass prediction for signals-of-opportunity work.

| | |
|---|---|
| Install | `pip install skyfield` (PyPI name `skyfield`, 1.55 released 2026-08-07; deps `certifi>=2017.4.17`, `jplephem>=2.13`, `numpy`, `sgp4>=2.13`). No compiled code of its own (sgp4 ships wheels with a C++ accelerator). |
| Runs on | Any OS, CPU. `setup.py` classifiers list Python 2.7 and 3.7-3.13. |
| Inputs | Time: `ts.utc(...)`, `ts.from_datetime(...)`, `ts.tt_jd(...)` (numpy arrays for vectorised time). Ephemerides: JPL SPK `.bsp` files (e.g. `de421.bsp`, `de440s.bsp`) via `load()`. Satellites: TLE line pairs or OMM dicts / CelesTrak URLs. Stars: `Star(ra_hours=..., dec_degrees=...)` or a Hipparcos dataframe (`skyfield.data.hipparcos.load_dataframe`). Observer: `wgs84.latlon(lat_deg, lon_deg, elevation_m)`. |
| Outputs | Positions in ICRS/GCRS/ITRS/TEME (`.position.km`, `.velocity.km_per_s`), apparent `altaz()` (Angle objects; optional refraction with `temperature_C`, `pressure_mbar`), `radec()`, sub-satellite point (`wgs84.subpoint_of`, `latlon_of`, `height_of`), event times (rise/culminate/set). |
| Key API / entry points | `skyfield.api`: `load` (= `Loader('.')`), `load.timescale(delta_t=None, builtin=True)`, `load('de421.bsp')`, `load.tle_file(url, reload=False, filename=None)`, `Loader(directory)`, `load_file(path)`, `EarthSatellite(line1, line2, name=None, ts=None)`, `EarthSatellite.from_omm(ts, element_dict)`, `.find_events(topos, t0, t1, altitude_degrees=0.0)`, `wgs84`, `Star`, `Angle`. Positions: `observer.at(t).observe(body).apparent().altaz()`. Modules `skyfield.almanac` (`find_risings`, `find_settings`; `find_discrete` lives in `skyfield.searchlib`), `skyfield.data.hipparcos`. |
| Time to first result | Estimate: 5-10 min including the first ephemeris download (file size not checked). |
| License | MIT (`LICENSE`, "Copyright 2013-2018 Brandon Rhodes"; `setup.py` license='MIT'). Data is fetched from third parties at runtime and carries their terms: JPL ephemerides from `ssd.jpl.nasa.gov`/`naif.jpl.nasa.gov`, IERS Earth-orientation files (`finals2000A.all` from `datacenter.iers.org`), Hipparcos catalog from CDS `cdsarc.cds.unistra.fr` (URLs in `skyfield/iokit.py`, `skyfield/data/hipparcos.py`). The repo root also commits `de405.bsp`, `de421.bsp`, `hip_main.dat` for tests; they are not in the PyPI package (`package_data` only ships `skyfield/data/*.gz|*.npy|*.npz`). |

## Minimal usage
Not run. Built from `skyfield/api.py`, `skyfield/sgp4lib.py`, `skyfield/toposlib.py` signatures.

```python
from skyfield.api import load, wgs84, Star
ts = load.timescale()                         # builtin leap-second / delta-T tables, no download
eph = load("de421.bsp")                       # downloads once to the current directory
earth, sun = eph["earth"], eph["sun"]
here = earth + wgs84.latlon(50.45, 30.52, elevation_m=180)
t = ts.utc(2026, 11, 6, 18, 0)

alt, az, _ = here.at(t).observe(sun).apparent().altaz()
print("sun", alt.degrees, az.degrees)

sirius = Star(ra_hours=(6, 45, 8.917), dec_degrees=(-16, 42, 58.02))
alt, az, _ = here.at(t).observe(sirius).apparent().altaz()

sats = load.tle_file("https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
sat = sats[0]
topo = wgs84.latlon(50.45, 30.52)
times, events = sat.find_events(topo, t, t + 0.5, altitude_degrees=10.0)   # 0 rise, 1 culminate, 2 set
```

## Wiring it into a nav stack
- Celestial fix: a star tracker such as [tetra3](./esa__tetra3.md) or [cedar-solve](./smroid__cedar-solve.md) gives the camera boresight in RA/Dec; Skyfield gives the expected alt/az of those stars for a hypothesised lat/lon/time, so a least-squares over lat/lon (plus attitude from an IMU) yields position. Related code: [celestial-navigation](../../catalog/repos/alinnman__celestial-navigation.md), [celestial_navigation_pi](../../catalog/repos/seandepagnier__celestial_navigation_pi.md).
- Sun compass / sun sensor heading: Sun azimuth from Skyfield vs measured body-frame Sun vector => heading without a magnetometer.
- LEO signals of opportunity: TLE propagation + `find_events` to predict which Starlink/Iridium/Orbcomm satellites are visible, feeding a Doppler positioning prototype ([starlink-leo-pnt](../../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md), [UT Starlink signal simulator](../../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md)).
- GNSS geometry: for GNSS satellite positions use broadcast ephemerides via [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) or [RTKLIB](./rtklibexplorer__rtklib.md); TLE/SGP4 is km-level, not ranging grade.

## Gotchas
- Downloads go to the current working directory by default (`load = Loader('.')`); use `Loader('/path/to/cache')` and pre-fetch files for an offline field laptop.
- `load.timescale()` uses builtin tables (no network) but they age; for long deployments ship a recent Skyfield or use `builtin=False` with a pre-downloaded `finals2000A.all`.
- SGP4 accuracy degrades with TLE age (km after days); refresh TLEs before any pass-dependent test. Check `sat.epoch` against your test time before trusting a pass prediction.
- `altaz()` without arguments gives geometric altitude, no refraction; pass `temperature_C`/`pressure_mbar` for low-elevation star sights.
- Pure-Python vectorised numpy: fast for arrays of times, slow if you loop per sample in Python.

## Alternatives
- [tetra3](./esa__tetra3.md) - the star-identification half of celestial nav; Skyfield is the ephemeris half.
- Astropy (`astropy.coordinates`) - not in the index; prefer when you already use Astropy units and frames.
- python-sgp4 alone (Skyfield's dependency) - when you only need raw TEME propagation at maximum speed.

Sources: `LICENSE`, `setup.py`, `CHANGELOG.rst` (v1.55), `skyfield/api.py`, `skyfield/iokit.py`, `skyfield/sgp4lib.py`, `skyfield/toposlib.py`, `skyfield/positionlib.py`, `skyfield/almanac.py`, `skyfield/searchlib.py`, `skyfield/data/hipparcos.py`, repo root listing (github.com/skyfielders/python-skyfield); https://pypi.org/pypi/skyfield/json.
