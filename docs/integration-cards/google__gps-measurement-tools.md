# GPS Measurement Tools (Google) - integration card
<!-- about: repo:google/gps-measurement-tools -->
One-line: Google's reference for Android raw GNSS - the GnssLogger app source (log pseudoranges, carrier phase, AGC, C/N0 on a phone) plus MATLAB code that turns those logs into pseudoranges, a GPS weighted-least-squares fix, and NMEA accuracy metrics. Mostly MATLAB, not Python.

| | |
|---|---|
| Install | No package. MATLAB: clone/unzip the repo, `addpath('<repo>/opensource')` (and `NmeaUtils`), edit `dirName` in `ProcessGnssMeasScript.m`, run it. GNU Octave: only `ReadGnssLogger.m` has an explicit compatibility fix (PR #40); the rest is untested on Octave. Phone app: build `GNSSLogger/` in Android Studio (Gradle, `minSdk 24`, `compileSdk 32`), or install Google's GnssLogger from the Play Store (README mentions a provided APK; none is in the current tree). Desktop "GNSS Analysis App" binaries for Linux/Mac/Windows are GitHub release assets (V4.6.0.1, 2023-02-10). Python path: the `gnss_analysis_with_skills/` Colab notebook + `SKILL.md` (Python 3.10+, 2026). |
| Runs on | MATLAB (any OS) for `opensource/` and `NmeaUtils/`; Android 7+ (API 24) phone with raw measurement support for GnssLogger; Colab/Jupyter for the notebook. No GPU. |
| Inputs | GnssLogger text/CSV logs with row prefixes `Raw`, `Fix`, `Nav`, `NMEA`, `Accel`/`Gyro`/`Mag` (+ uncalibrated), `OrientationDeg`, `GnssAntennaInfo`, `Status` (LOGGING_FORMAT.md); GPS broadcast ephemeris as RINEX nav (`hourDDD0.YYn`) fetched by `GetNasaHourlyEphemeris` or placed by hand; NMEA GGA/RMC files for `Nmea2RtkMetrics`. Demo logs in `opensource/demoFiles/` (2016). |
| Outputs | MATLAB structs: `gnssRaw`, `gnssMeas` (pseudoranges m, pseudorange rates m/s, C/N0, accumulated delta range), `gpsPvt` (WLS lat/lon/alt, velocity, clock bias, with uncertainty); plots of pseudoranges, C/N0, PVT, ADR residuals; `Nmea2RtkMetrics` table (50%/95% horizontal error, cross-track, time-to-first 1 m). |
| Key API / entry points | `[gnssRaw,gnssAnalysis] = ReadGnssLogger(dirName,fileName,dataFilter)`; `dataFilter = SetDataFilter`; `gnssMeas = ProcessGnssMeas(gnssRaw)`; `[allGpsEph,allGloEph] = GetNasaHourlyEphemeris(utcTime,dirName)`; `[gpsEph,iono] = ReadRinexNav(fileName)`; `gpsPvt = GpsWlsPvt(gnssMeas,allGpsEph)`; `ProcessAdr`, `GpsAdrResiduals`; `rtkMetrics = Nmea2RtkMetrics(testFileName,refFileName,dirName)`, `Nmea2ErrorPlot`. |
| Time to first result | Estimate: 15 min to plots from the bundled demo log if MATLAB is installed (ephemeris for the demo is in `demoFiles/`); 1 h+ for your own phone log because ephemeris download needs manual work (see Gotchas). |
| License | Apache-2.0 (LICENSE.txt, also `opensource/LICENSE.txt`). |

## Minimal usage

Not run. MATLAB, bundled demo data (from `opensource/ProcessGnssMeasScript.m`, trimmed):

```matlab
addpath('/path/to/gps-measurement-tools/opensource');
dirName = '/path/to/gps-measurement-tools/opensource/demoFiles';
prFileName = 'pseudoranges_log_2016_06_30_21_26_07.txt';
[gnssRaw,~] = ReadGnssLogger(dirName, prFileName, SetDataFilter);
utcTime = Gps2Utc([], 1e-3*double(gnssRaw.allRxMillis(end)));
allGpsEph = GetNasaHourlyEphemeris(utcTime, dirName);   % reads hour1820.16n from dirName
gnssMeas = ProcessGnssMeas(gnssRaw);
gpsPvt = GpsWlsPvt(gnssMeas, allGpsEph);
PlotPvt(gpsPvt, prFileName, [37.422578, -122.081678, -28], 'WLS');
PlotCno(gnssMeas, prFileName);
```

No MATLAB: parse the same log in Python with [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) (`AndroidRawGnss`), or open the `gnss_analysis_with_skills` Colab.

## Wiring it into a nav stack

- Phone as a cheap GNSS sensor: GnssLogger records raw GNSS + IMU on any supported Android phone; that log is the input format for the GSDC datasets and for [gnss_lib_py](./stanford-navlab__gnss_lib_py.md). Use it to collect your own field data at a hackathon venue.
- Interference / spoofing demos: `Raw` rows carry `Cn0DbHz` and `AgcDb`; a C/N0 drop with AGC drop is the classic jamming signature, consistent C/N0 with position jump is a spoofing cue. See [gnss-interference](../../catalog/concepts/gnss-interference.md) and [assured-pnt](../../catalog/concepts/assured-pnt.md).
- RINEX: for RTKLIB processing convert the log to RINEX (gnss_lib_py or third-party converters), then [RTKLIB](./rtklibexplorer__rtklib.md); read results with [georinex](./geospace-code__georinex.md).
- Accuracy scoring: `Nmea2RtkMetrics` compares any NMEA test track against a reference NMEA (e.g. SPAN truth), useful for scoring an estimator that can emit GGA ([pynmeagps](./semuconsulting__pynmeagps.md) generates it).
- Frames: positions come out WGS84 LLA / ECEF; `Lla2Ned`, `RotEcef2Ned` helpers are included, or use [pymap3d](./geospace-code__pymap3d.md) in Python.

Catalog page: [catalog/repos/google__gps-measurement-tools.md](../../catalog/repos/google__gps-measurement-tools.md). Concepts: [gnss](../../catalog/concepts/gnss.md), [datasets-benchmarks](../../catalog/concepts/datasets-benchmarks.md).

## Gotchas

- MATLAB required for the core tools (commercial licence); Octave support is partial. Plan on gnss_lib_py if the team has no MATLAB.
- `GetNasaHourlyEphemeris.m` downloads via anonymous FTP from `cddis.gsfc.nasa.gov`. NASA CDDIS ended anonymous FTP in 2020 and now requires an Earthdata login over HTTPS/FTPS (external knowledge, not stated in the repo). Expect the auto-download to fail; fetch the hourly nav file yourself and drop it in the log directory as the README describes.
- The MATLAB WLS is GPS L1 only (`GpsWlsPvt`, `GpsEph2Pvt`; GLONASS ephemeris marked TBD). Multi-constellation, multi-band WLS lives only in the 2026 Python Colab / `SKILL.md`.
- Not all phones expose raw measurements, carrier phase or AGC; duty cycling breaks carrier phase unless disabled in developer options (the demo log notes "with duty cycling, no carrier phase").
- GitHub issues are disabled; the repo is a Copybara export from Google's internal tree. Open PR #47 (RINEX triple-frequency/nav fixes) is unmerged.
- Demo data is from 2016; the GnssLogger log format has gained columns since, and old MATLAB parsers can lag the current app (`ReadGnssLogger.m` was updated in PRs #45/#46).

## Alternatives

- [gnss_lib_py](./stanford-navlab__gnss_lib_py.md) - Python, parses the same Android logs plus RINEX/NMEA/SP3, multi-GNSS WLS and FDE; prefer for almost any hackathon use.
- [taroz/gsdc2023](../../catalog/repos/taroz__gsdc2023.md) - winning smartphone GNSS/IMU factor-graph pipeline (MATLAB); prefer when chasing sub-metre phone accuracy.
- [RTKLIB](./rtklibexplorer__rtklib.md) - once data is in RINEX, the standard SPP/RTK/PPP engine.

Sources: `gh api repos/google/gps-measurement-tools` (Apache-2.0, issues disabled), README.md, LICENSE.txt, LOGGING_FORMAT.md, opensource/ProcessGnssMeasScript.m, opensource/GetNasaHourlyEphemeris.m, function headers of ReadGnssLogger.m, ProcessGnssMeas.m, GpsWlsPvt.m, ReadRinexNav.m, NmeaUtils/Nmea2RtkMetrics.m, GNSSLogger/app/build.gradle, gnss_analysis_with_skills/README.md and SKILL.md, releases V4.6.0.0/V4.6.0.1, commits to 2026-10-19, pull requests #40, #45, #46, #47.
