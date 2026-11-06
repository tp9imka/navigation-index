# AllanTools - integration card
<!-- about: repo:aewallin/allantools -->
`pip install allantools` and get ADEV/OADEV/MDEV/TDEV/HDEV/TOTDEV/MTIE/TIE-rms on numpy arrays of phase or fractional frequency, with confidence intervals and noise generators. Use it to characterise clocks (GPSDO, chrony/PTP offsets, CSAC holdover) and, with care, IMU noise.

| | |
|---|---|
| Install | `pip install allantools` (PyPI name `AllanTools`, latest 2024.6 uploaded 2024-07-04, `requires_python >= 3.8`, deps numpy, scipy >= 1.6.0, matplotlib). Also `conda install -c conda-forge allantools` (README badge). Repo `pyproject.toml` on master still says `2024.06`; commits continue (last push 2026-10) without a newer PyPI release. |
| Runs on | Pure Python + numpy, any OS/arch. |
| Inputs | Evenly spaced samples, either phase in seconds (`data_type="phase"`, default) or dimensionless fractional frequency (`data_type="freq"`); normalising frequency is the user's job (README). `rate` = sample rate in Hz (default 1.0). `taus` = array of tau seconds or `"octave"`, `"decade"`, `"all"` (default octave per README). Gap-tolerant variant `gradev` accepts NaN gaps. |
| Outputs | Tuple `(taus_used, devs, deverrs, ns)` from each deviation function. `Dataset.write_results(path)` writes a text table; `Plot` wraps matplotlib. |
| Key API / entry points | `allantools.adev/oadev/mdev/tdev/hdev/ohdev/totdev/mtotdev/ttotdev/htotdev/theo1/pdev/mtie/tierms(data, rate=1.0, data_type="phase", taus=None)`, `gradev(data, rate, data_type, taus, ci=0.9, noisetype='wp')`, `gcodev(data_1, data_2, ...)` and `three_cornered_hat_phase(...)` for comparing three clocks, `frequency2phase(freqdata, rate)`, `phase2frequency(phase, rate)`. Classes `allantools.Dataset(data, rate, data_type, taus)` with `.compute("oadev")`, `allantools.Plot()`. `allantools.noise.white/pink/brown/violet(N)`, `noise_kasdin`. Confidence: `ci.confidence_interval`, `ci.edf_greenhall`, `ci.autocorr_noise_id`. Streaming: `realtime.oadev_realtime`, `ohdev_realtime`, `tdev_realtime`. |
| Time to first result | Estimate: 5 min (pip install, run the README snippet on synthetic noise); 20 min on a real PPS-offset log. |
| License | LGPL-3.0 (`LICENSE.txt`; README says "LGPL v3+"). Test data in `tests/` (e.g. Cs5071A phase files) has no separate licence. |

## Minimal usage
Not run. From README:

```python
import numpy as np, allantools
# phase data in seconds at 1 Hz, e.g. PPS offset of a GPSDO vs reference
x = allantools.noise.white(10000)
taus, adevs, errs, ns = allantools.oadev(x)                  # rate=1.0, taus="octave"

# fractional-frequency data at 12.3 Hz
y = allantools.noise.white(10000)
t2, ad, ade, adn = allantools.oadev(y, rate=12.3, data_type="freq",
                                    taus=np.logspace(0, 3, 50))
```

IMU use: gyro rate in rad/s is not a fractional frequency, but `oadev(gyro, rate=fs, data_type="freq")` still returns the Allan deviation of that series in rad/s; read angle random walk at tau = 1 s and bias instability at the curve minimum yourself.

## Wiring it into a nav stack
- Timing/PNT: log `chronyc tracking` / `chronyc sourcestats` offsets or [linuxptp](../../catalog/repos/nwtime__linuxptp.md) `ptp4l` master offsets as phase in seconds, then `oadev`/`tdev`/`mtie` to compare holdover of oscillators when GNSS is jammed. See [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) and [satpulse](../../catalog/repos/jclark__satpulse.md).
- Inertial: cross-check [allan_variance_ros](./ori-drs__allan_variance_ros.md) output, or produce Kalibr noise numbers outside ROS.
- Three-cornered hat (`three_cornered_hat_phase`, `gcodev`) separates the noise of three clocks measured pairwise, handy when no reference is better than the units under test.

## Gotchas
- Default `data_type` is phase; passing frequency without `data_type="freq"` gives wrong curves silently (open #67 on the wording).
- `adev()` is the classic non-overlapping estimator; README recommends `oadev()` as first choice.
- Evenly spaced data only; timestamped data with gaps or outliers has no built-in handling beyond `gradev` (open #6, #112, #56). `gradev` has a reported bug with frequency data (open #60).
- `mtie()` can allocate huge arrays on long series and crash (open #82); use `mtie_phase_fast`.
- Total deviations lack bias correction (open #22); confidence intervals need explicit calls (#47, #135).
- Not an IMU tool: no automatic VRW/ARW/bias-instability fit and no Kalibr output.

## Alternatives
- [allan_variance_ros](./ori-drs__allan_variance_ros.md) - when the data is an IMU rosbag and you want a Kalibr `imu.yaml`.
- [nmayorov allan-variance](../../catalog/repos/nmayorov__allan-variance.md) - small Python package that also fits IMU noise parameters from the AV curve.
- Stable32 (closed source, Windows) is the reference AllanTools tests compare against (README).

Sources: `README.rst`, `LICENSE.txt`, `pyproject.toml`, `allantools/__init__.py`, `allantools/allantools.py` (function signatures), `allantools/ci.py`, `allantools/realtime.py`, repo tree, open issues #6 #22 #47 #56 #60 #67 #82 #112 #135 (github.com/aewallin/allantools); pypi.org/pypi/AllanTools/json.
