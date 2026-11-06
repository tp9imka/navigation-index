# gnss_lib_py - integration card
<!-- about: repo:stanford-navlab/gnss_lib_py -->
Pure-Python GNSS measurement toolkit: parse Android raw logs, RINEX, NMEA, SP3/CLK into one `NavData` table, compute satellite states, then run WLS, a GNSS EKF and fault detection/exclusion. The quickest place to write and test your own integrity or spoofing check on real pseudoranges.

| | |
|---|---|
| Install | `pip install gnss-lib-py` (PyPI 1.1.0, matches latest GitHub release `1.1.0`). Requires Python >=3.10,<3.15. Pulls numpy 2, pandas 2, scipy, georinex <=1.16.1, xarray <=2024.7.0, pynmea2, matplotlib, plotly, kaleido 0.2.1 (pyproject). Colab notebook linked from README. |
| Runs on | Linux, macOS, Windows (pure Python). No GPU. Internet needed for automatic ephemeris download. |
| Inputs | Android GnssLogger `gnss_log.txt` (`AndroidRawGnss`, plus `AndroidRawFixes`, `AndroidRawAccel/Gyro/Mag/Orientation`), Google Smartphone Decimeter Challenge 2021/2022/2023 derived CSVs and ground truth, TU Chemnitz smartLoc, NMEA, RINEX 3 obs (`RinexObs`) and nav, SP3, CLK. Units: metres, ECEF, time as `gps_millis`. |
| Outputs | `NavData` objects (row names like `x_rx_wls_m`, `b_rx_wls_m`, `lat_rx_wls_deg`, `x_sv_m`, `b_sv_m`, `raw_pr_m`, `corr_pr_m`, `el_sv_deg`), residuals, FDE fault flags, DOP, skyplots and plotly maps, Kaggle submission CSV. |
| Key API / entry points | `glp.AndroidRawGnss(input_path, filter_measurements=True, ...)`, `glp.RinexObs(path)`, `glp.add_sv_states(navdata, source='precise'|..., file_paths=None, download_directory=..., verbose=False)`, `glp.add_sv_states_rinex(measurements, ephemeris_path=..., constellations=['gps'], delta_t_dec=-2)`, `glp.solve_wls(measurements, weight_type=None, only_bias=False, receiver_state=None, ...)`, `glp.solve_gnss_ekf(measurements, init_dict=None, ...)`, `glp.solve_fde(navdata, method="residual", remove_outliers=False, max_faults=None, threshold=None, ...)`, `glp.evaluate_fde(...)`, `glp.load_ephemeris(file_type, gps_millis, ...)`. All re-exported in `gnss_lib_py/__init__.py`. |
| Time to first result | Estimate: 30-60 min to a WLS track from a GnssLogger file or public RINEX 3 obs (assumes pip works and FTPS to CDDIS/IGS is reachable for ephemeris). |
| License | MIT. |

## Minimal usage
Not run. Condensed from this repo's [gnss-rinex-processing sample](../../samples/gnss-rinex-processing/README.md) (`glp_spp.py`, itself a syntax-checked sketch against 1.1.0):

```python
import gnss_lib_py as glp
obs = glp.RinexObs("p730_r3.rnx")                       # RINEX 3 obs
obs = obs.where("gnss_id", "gps").where("signal_type", "l1")
full = glp.add_sv_states_rinex(obs, ephemeris_path="ephem", constellations=["gps"])
full["corr_pr_m"] = full["raw_pr_m"] + full["b_sv_m"]  # SV clock only, no iono/tropo
state = glp.solve_wls(full)
fde = glp.solve_fde(full, method="residual")    # adds fault flags; tune threshold per docs
print(state["x_rx_wls_m"], state["y_rx_wls_m"], state["z_rx_wls_m"])
```

For Android logs swap the first line for `glp.AndroidRawGnss("gnss_log.txt")` and use `glp.add_sv_states(raw, source="precise")` (see the readthedocs tutorials).

## Wiring it into a nav stack
- Data in: GnssLogger from [GPS Measurement Tools](../../catalog/repos/google__gps-measurement-tools.md) on any Android phone, RINEX from [RTKLIB](./rtklibexplorer__rtklib.md) `convbin` or [GNSS-SDR](./gnss-sdr__gnss-sdr.md), GSDC datasets ([GSDC 2023](../../catalog/resources/google-gsdc-2023.md)).
- Integrity / anti-spoofing: `solve_fde` (residual chi-square, greedy residual, EDM) is a ready baseline; add your own test (clock jump, C/N0 vs elevation, Doppler-position consistency) as extra `NavData` rows. Pairs with the [interference monitor sample](../../samples/gnss-interference-monitor/README.md).
- Fusion: WLS ECEF output => convert with [pymap3d](./geospace-code__pymap3d.md) to local ENU => feed a [filterpy](./rlabbe__filterpy.md) EKF or a [GTSAM](./borglab__gtsam.md) `GPSFactor` with IMU from the phone's `AndroidRawAccel/Gyro`.
- Scoring: compare against RTKLIB RTK or GSDC ground truth (`AndroidGroundTruth2023`).

## Gotchas
- Ephemeris auto-download uses FTPS to CDDIS/IGS. Corporate or venue networks that block FTP break it (closed issues #168 "Can't connect to gdc.cddis.eosdis.nasa.gov", #174 "Unable to retrieve ephemeris data"). SP3 "rapid" products appear about a day late; maintainers suggest `rinex_nav` for recent data. Pre-download files and pass `file_paths`.
- RINEX 2 obs: open issue #182 reports a crash loading a `.26o` file with `RinexObs`. Convert to RINEX 3 first (`convbin`), as the sample does.
- Open #161: `add_sv_states_rinex` handles one signal type per constellation at a time; filter to one band before calling.
- Pinned `xarray<=2024.7.0` and `georinex<=1.16.1` can conflict with other geo packages in a shared env; use a dedicated venv.
- WLS without iono/tropo correction gives metre-level bias, mostly vertical. Fine for relative tests, not for accuracy claims.
- Closed #138: older Colab images needed a pandas pin; check if Colab install fails.

## Alternatives
- [laika](./commaai__laika.md) - stronger correction pipeline (DCB, IONEX, DGPS from CORS) but RINEX 2 only and less maintained; prefer for corrected pseudoranges on US data.
- [RTKLIB demo5](./rtklibexplorer__rtklib.md) - when you need carrier-phase RTK/PPK or PPP rather than code-only positioning.
- [GPS Measurement Tools](../../catalog/repos/google__gps-measurement-tools.md) - Google's MATLAB processing and the GnssLogger app itself.

Sources: https://github.com/Stanford-NavLab/gnss_lib_py README.md, pyproject.toml, `gnss_lib_py/__init__.py`, `algorithms/snapshot.py`, `algorithms/fde.py`, `algorithms/gnss_filters.py`, `parsers/android.py`, `parsers/google_decimeter.py`, `utils/sv_models.py`, `utils/ephemeris_downloader.py` (def lines), issues #168 #174 #182 #161 #138, PyPI gnss-lib-py JSON (1.1.0), samples/gnss-rinex-processing in this repo.
