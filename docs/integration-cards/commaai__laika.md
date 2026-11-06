# laika - integration card
<!-- about: repo:commaai/laika -->
comma.ai's Python GNSS processing library: `AstroDog` fetches orbits, clocks, DCBs and ionosphere maps on demand and turns raw pseudoranges into corrected measurements and satellite states, ready for your own WLS or Kalman filter. Useful when you want well-corrected code/Doppler measurements in Python without writing the correction models.

| | |
|---|---|
| Install | Install from git, not PyPI: the PyPI `laika` is version 0.0.1 from the "grey panda" era. `pip install numpy scipy && pip install git+https://github.com/commaai/laika` (README: clone then `pip install .`). Deps: numpy, scipy, requests, certifi, pycurl, tqdm, hatanaka, pycapnp, atomicwrites (pyproject). Notebooks: `sudo apt-get install libfreetype6-dev` and `pip install -r requirements_examples.txt`. No release tags. |
| Runs on | README: tested only on Ubuntu 24.04, Python 3.11.4 (pyproject allows >=3.8). `pycurl` and `pycapnp` need native libs; expect friction on macOS and Windows. No GPU. |
| Inputs | Raw observations as `GNSSMeasurement` objects from: RINEX **2.11 or lower** obs (`RINEXFile` raises on >2.11) via `raw_gnss.read_rinex_obs`, u-blox raw (`read_raw_ublox`, capnp messages from comma's logs), Qualcomm reports. Correction products downloaded automatically from NASA CDDIS and others; requires a NASA Earthdata account in `.netrc`. Time as `GPSTime(week, tow)`. Positions ECEF metres. |
| Outputs | Satellite position/velocity/clock (`get_sat_info`), per-satellite delay (tropo + iono + DCB, `get_delay`), corrected `GNSSMeasurement`s, WLS position fix and velocity fix (`calc_pos_fix`, `calc_vel_fix`), DOPs, pseudorange/range-rate residual functions for your own optimiser. |
| Key API / entry points | `laika.AstroDog(auto_update=True, cache_dir=None, dgps=False, valid_const=(GPS, GLONASS), valid_ephem_types=..., default_delays=False, clear_old_ephemeris=False)`; `dog.get_sat_info(prn, time)`, `dog.get_all_sat_info(time)`, `dog.get_delay(prn, time, rcv_pos, no_dgps=False, signal='C1C', freq=None)`; `laika.raw_gnss`: `read_rinex_obs(obsdata)`, `process_measurements(measurements, dog)`, `correct_measurements(measurements, est_pos, dog, correct_delay=True)`, `get_DOP(...)`; `laika.opt`: `calc_pos_fix(measurements, ..., signal='C1C', min_measurements=5)`, `calc_vel_fix(...)`, `pr_residual(...)`, `prr_residual(...)`; `laika.gps_time.GPSTime`; `laika.rinex_file.RINEXFile(filename)`; `laika.downloader.download_cors_station(time, station, cache_dir)`. |
| Time to first result | Estimate: 1-2 h to reproduce `examples/Compute_station_pos.ipynb` (assumes Ubuntu, a working Earthdata login in `.netrc`, and that the product downloads succeed; several open issues say they do not always). |
| License | MIT. |

## Minimal usage
Not run. Condensed from `examples/Compute_station_pos.ipynb`:

```python
from datetime import datetime
from laika import AstroDog
from laika.gps_time import GPSTime
from laika.downloader import download_cors_station
from laika.rinex_file import RINEXFile
from laika.dgps import get_station_position
import laika.raw_gnss as raw

dog = AstroDog()
t = GPSTime.from_datetime(datetime(2021, 1, 7))
obs = RINEXFile(download_cors_station(t, "slac", dog.cache_dir))
truth = get_station_position("slac")
fixes = []
for epoch in raw.read_rinex_obs(obs):
    proc = raw.process_measurements(epoch, dog=dog)
    corr = raw.correct_measurements(proc, truth, dog=dog)
    fix, _ = raw.calc_pos_fix(corr)
    fixes.append(fix)
```

The notebook copies a bundled `cors_station_positions` file into the cache first because building it "takes forever"; do the same. Note the notebook passes the uncorrected `meas` to `correct_measurements`; the snippet above passes `proc`, which is what the README's flow implies.

## Wiring it into a nav stack
- Corrected pseudoranges + satellite states => your own estimator: [filterpy](./rlabbe__filterpy.md) EKF (the `examples/Kalman.ipynb` + `examples/kalman/` folder show comma's approach) or [GTSAM](./borglab__gtsam.md) with custom pseudorange factors.
- Data sources: u-blox raw (UBX RXM-RAWX) logged with [pyubx2](./semuconsulting__pyubx2.md) needs conversion to RINEX 2 (RTKLIB `convbin -v 2.11`) or a small adapter into `GNSSMeasurement`; `read_raw_ublox` expects comma's capnp log format, not UBX bytes.
- Same org as [openpilot](../../catalog/repos/commaai__openpilot.md); whether current openpilot still uses laika was not checked.
- Coordinates: `laika.lib.coordinates.LocalCoord.from_ecef(...)`.`ecef2ned(...)` gives NED errors; [pymap3d](./geospace-code__pymap3d.md) is the general alternative.

## Gotchas
- **Earthdata login is mandatory** for CDDIS downloads (README). Missing or wrong `.netrc` => download errors that are hard to read (open #46 "Bad error reporting for download failures").
- Walkthrough/Kalman notebooks break on downloads: open #170 "No orbit data found" for 2018 dates, #163 "Cannot download gnss data from kalman tutorial", #133 "Walkthrough jupyter notebook doesn't work". Budget time or pick dates whose products you can fetch.
- Open #62: pycurl SSL cipher error (`DEFAULT@SECLEVEL=1`) on newer OpenSSL builds.
- RINEX >2.11 rejected; the notebook warns that older CORS files are Hatanaka-compressed and may fail to download.
- Default constellations GPS + GLONASS only; pass `valid_const` for Galileo/BeiDou and check product availability.
- DGPS corrections (`dgps=True`) are US CORS only (README).

## Alternatives
- [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) - better parser coverage (Android, RINEX 3, GSDC), FDE built in, actively maintained; prefer as default Python GNSS toolkit.
- [RTKLIB demo5](./rtklibexplorer__rtklib.md) - mature C engine with RTK/PPP; use when accuracy matters more than Python hackability.
- [rtklib-py](../../catalog/repos/rtklibexplorer__rtklib-py.md) - Python PPK when you need carrier phase in Python.

Sources: https://github.com/commaai/laika README.md, pyproject.toml, `laika/astro_dog.py`, `laika/raw_gnss.py`, `laika/opt.py`, `laika/gps_time.py`, `laika/rinex_file.py`, `examples/Compute_station_pos.ipynb`, issues #46 #62 #133 #163 #170, PyPI laika JSON (0.0.1).
