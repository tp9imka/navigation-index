# GeoRinex - integration card
<!-- about: repo:geospace-code/georinex -->
One-line: load RINEX 2/3/4 OBS/NAV (plain, gz/Z/bz2/zip or Hatanaka) and SP3 orbits straight into `xarray.Dataset` in one call - the fastest way to get pseudoranges, C/N0 and ephemerides from public CORS/IGS data into numpy/pandas.

| | |
|---|---|
| Install | `pip install georinex` (PyPI latest 1.16.2, released 2023-11-15; PyPI metadata `requires_python >=3.8`). GitHub `main` still reports `__version__ = "1.16.2"` but requires Python >=3.10 and has unreleased commits to 2026-05 (RINEX 3.05 test file, SBAS header handling): `python -m pip install -e ./georinex` from a clone to get them. Deps: `python-dateutil numpy xarray hatanaka ncompress netcdf4`; extras `[plot]` (matplotlib, pymap3d, cartopy). |
| Runs on | Any OS with Python, pure Python plus compiled wheels of netcdf4/ncompress/hatanaka. No GPU. |
| Inputs | RINEX OBS/NAV 2.x, 3.x, 4.x files or `io.StringIO`; compressed `.gz .Z .bz2 .zip`, Hatanaka `.crx` (and `.crx.gz`); SP3-a/c/d; previously converted `.nc`. |
| Outputs | `xarray.Dataset`: OBS indexed by `time` x `sv` with one variable per observable (`C1C`, `L1C`, `S1C`...), optional LLI/SSI with `useindicators=True`; NAV with broadcast ephemeris parameters per `sv`/`time`; header attrs incl. `position` (ECEF m from APPROX POSITION XYZ). NetCDF4/HDF5 files via `out=` or `batch_convert`. |
| Key API / entry points | `georinex.load(rinexfn, out=None, use=None, tlim=None, useindicators=False, meas=None, verbose=False, *, overwrite=False, fast=True, interval=None)`; `rinexobs(...)`, `rinexnav(...)`; `rinexheader(fn)`; `gettime(fn)`; `load_sp3(fn, outfn)`; `keplerian2ecef(sv)` (satellite ECEF from NAV); `batch_convert(...)`. CLI via modules (no console scripts): `python -m georinex.read file [-p] [-u G] [-m C1C] [--tlim start stop]`, `python -m georinex.rinex2hdf5 dir "*o" -o outdir`, `python -m georinex.gtime file`, `python -m georinex.loc dir`. |
| Time to first result | Estimate: 10 min to a C/N0 or pseudorange plot from one daily CORS file; RINEX 3 OBS of a full day can take tens of seconds to load (README benchmark: 48.6 s for a 23 h mixed file, 17.6 s with `use='E', meas='C1C'`, on a Haswell laptop). |
| License | MIT (LICENSE.txt, copyright 2015 Michael Hirsch). |

## Minimal usage

Not run. Load Galileo + GPS code and C/N0 for a time window and dump to pandas (API from README and `base.py`):

```python
import georinex as gr

obs = gr.load("BASE00USA_R_20250010000_01D_30S_MO.crx.gz",
              use={"G", "E"}, meas=["C1C", "S1C"],
              tlim=("2025-01-01T12:00", "2025-01-01T13:00"))
print(obs)                              # dims: time, sv
cn0 = obs["S1C"].to_dataframe().dropna()
nav = gr.load("BRDC00IGS_R_20250010000_01D_MN.rnx.gz", use={"G"})
print(gr.rinexheader("BASE00USA_R_20250010000_01D_30S_MO.crx.gz").get("position"))
```

CLI equivalent: `python -m georinex.read BASE00USA...crx.gz -u G -m C1C -p`.

## Wiring it into a nav stack

- Data prep for the [RINEX processing sample](../../samples/gnss-rinex-processing/): load CORS/IGS OBS for inspection (data gaps, C/N0, cycle slips via LLI) before or after running [RTKLIB](./rtklibexplorer__rtklib.md); RTKLIB does the positioning, georinex does the looking.
- Receiver position: header `position` is ECEF metres; convert with [pymap3d](./geospace-code__pymap3d.md) `ecef2geodetic` / `ecef2enu`.
- Integrity / interference analysis: C/N0 (`S1C` etc.) per SV over time from a static station is a clean baseline for jamming detection experiments ([gnss-interference](../../catalog/concepts/gnss-interference.md)); compare with a phone log from [GPS Measurement Tools](./google__gps-measurement-tools.md).
- Positioning in Python: [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) has its own RINEX reader plus WLS; use georinex when you want xarray and NetCDF for big batches.
- Raw from your own receiver: u-blox RAWX via [pyubx2](./semuconsulting__pyubx2.md) or the [ublox ROS driver](./kumarrobotics__ublox.md) => RTKLIB `convbin` => RINEX => georinex.

Catalog page: [catalog/repos/geospace-code__georinex.md](../../catalog/repos/geospace-code__georinex.md). Concepts: [gnss](../../catalog/concepts/gnss.md), [geodesy](../../catalog/concepts/geodesy.md).

## Gotchas

- No console scripts are declared in pyproject.toml, so there is no `georinex` command after `pip install` (#41); use `python -m georinex.read`.
- PyPI 1.16.2 is from 2023; fixes on `main` (SBAS headers, RINEX 3.05) are not on PyPI. Install from git if a file fails.
- Mixed multi-GNSS broadcast nav from IGS (`BRDC00IGS_R_..._MN.rnx`) has open failures (#117, #105); Galileo I/NAV + F/NAV in one file is not fully handled (#86, #65); IRNSS and SBAS edge cases (#89, #106). Filter with `use={"G"}` or split by constellation first.
- #122 (open): some files are read incorrectly with no warning. Sanity-check satellite counts and value ranges.
- #107 (open): Keplerian satellite positions no longer computed on loaded NAV datasets; call `keplerian2ecef` yourself.
- RINEX 4 is listed as supported in the README but #83 "Rinex 4" is still open; test your files.
- Read-only: it does not write RINEX (#109). For conversion to RINEX use RTKLIB `convbin`.
- RINEX 3 OBS loading is the slow path (the fast reader covers OBS2/NAV2 only, per README); always pass `use=` and `meas=` and convert once to NetCDF with `out=`.

## Alternatives

- [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) - reads RINEX, Android logs, NMEA, SP3 and also computes positions; prefer when you need a solution, not just arrays.
- [RTKLIB](./rtklibexplorer__rtklib.md) / [rtklib-py](../../catalog/repos/rtklibexplorer__rtklib-py.md) - full processing engines; prefer for RTK/PPP.
- [commaai/laika](./commaai__laika.md) - fetches ephemerides/corrections automatically and models satellite positions; prefer when you need orbit products downloaded for you.

Sources: `gh api repos/geospace-code/georinex` (MIT, release v1.16.2 2023-11-15), README.md, LICENSE.txt, pyproject.toml (deps, requires-python, no scripts), src/georinex/__init__.py (exports, version), src/georinex/base.py (`load` signature), src/georinex/sp3.py, src/georinex/keplerian.py, commit log to 2026-05-27, PyPI JSON for georinex (1.16.2), issues #41, #83, #86, #65, #89, #105, #106, #107, #109, #117, #122.
