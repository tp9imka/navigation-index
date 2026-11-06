# PyGPSClient - integration card
<!-- about: repo:semuconsulting/pygpsclient -->
One-line: pure-Python tkinter GUI for GNSS receivers (u-blox, Septentrio, Unicore, Quectel, NMEA) - live C/N0, sky view, RF spectrum, position scatter, NTRIP client/caster and receiver config - the bench tool for jamming and RTK tests.

| | |
|---|---|
| Install | `python3 -m venv pygpsclient && source pygpsclient/bin/activate && python3 -m pip install --upgrade pygpsclient` (PyPI `pygpsclient` 1.8.0, `requires_python >=3.10`). Needs Tk >= 8.6: Debian/Ubuntu/Pi OS `sudo apt install python3-tk python3-pil python3-pil.imagetk` (INSTALLATION.md lists more). Optional: `pip install rasterio` (custom map extents), `pip install cryptography` (SPARTN decryption). |
| Runs on | Any desktop with a window system: Windows 10+, macOS 13+ (Intel and Apple Silicon, python.org installer recommended), Linux incl. Raspberry Pi OS. INSTALLATION.md asks for >= 500 MB memory and >= 640x480 screen. No GPU. |
| Inputs | Serial (USB/UART), TCP/UDP socket (optional TLS), binary log file (`*.log`, u-center `*.ubx`), NTRIP caster (RTCM3 or SPARTN). Protocols NMEA, UBX, SBF, UNI, QGC, RTCM3, SPARTN, TTY. Optional fixed reference position for the scatterplot. |
| Outputs | GUI widgets; binary datalog; GPX track; spatialite database; socket server re-broadcasting the live stream (default port 50012, unauthenticated) or an NTRIP caster (mountpoint `pygnssutils`); RTCM/SPARTN written back to the receiver for RTK; receiver config commands (UBX CFG-VALSET etc.). |
| Key API / entry points | Console script `pygpsclient` => `pygpsclient.__main__:main` (pyproject.toml); same as `python3 -m pygpsclient`. CLI flags (`__main__.py`): `-C/--config <json>`, `-U/--userport <port>` (or env `PYGPSCLIENT_USERPORT`; value `ubxsimulator` starts a simulated UBX/NMEA stream), `--mqapikey`, `--ntripcasteruser`, `--ntripcasterpassword`, `--tlspempath`, `--tlscrtpath`, `--spartnkey`, `--spartnbasedate`, `--verbosity`, `--logtofile`. Scriptable equivalents live in [pygnssutils](./semuconsulting__pygnssutils.md) (`gnssstreamer`, `gnssntripclient`, `gnssserver`). |
| Time to first result | Estimate: 10 min from `pip install` to live C/N0 and sky view from a USB u-blox receiver; under 5 min with `--userport ubxsimulator` and no hardware. Assumes Python >= 3.10 with working tkinter. |
| License | BSD-3-Clause (LICENSE, pyproject.toml). |

## Minimal usage
Not run. From INSTALLATION.md and README.

```sh
python3 -m venv pygpsclient && source pygpsclient/bin/activate
python3 -m pip install --upgrade pygpsclient
pygpsclient --userport /dev/ttyACM0      # or: pygpsclient --userport ubxsimulator
# Menu..View: enable Levels (C/N0), Spectrum (needs UBX MON-SPAN), Signals (needs UBX NAV-SIG), Scatterplot
# Server Config: Socket Server mode => other tools read the live stream from tcp://<host>:50012
```

Jamming bench test in a shielded box: right-click the Spectrum chart to freeze a clean-sky snapshot, then compare against the live trace while the interference source is on; watch the Levels and Scatterplot widgets at the same time.

## Wiring it into a nav stack
- Use PyGPSClient as the operator view and its socket server as a tap: your integrity monitor reads the same stream over TCP with [pyubx2](./semuconsulting__pyubx2.md) or `GNSSReader` from [pygnssutils](./semuconsulting__pygnssutils.md) and pulls MON-HW / MON-RF jamming indicators and NAV-STATUS spoofing flags.
- RTK: NTRIP client => receiver; or turn a ZED-F9P (README also names ZED-X20P, Quectel LG, Septentrio Mosaic, Unicore UM9xx) into a base and serve it as an NTRIP caster for rovers. RTCM decoding detail: [pyrtcm](./semuconsulting__pyrtcm.md).
- Logs replay into PyGPSClient (file stream) or convert to RINEX with `pyrinexconv` from pygnssutils, then into [RTKLIB](./rtklibexplorer__rtklib.md) or [gnss_lib_py](./stanford-navlab__gnss_lib_py.md).
- Spatialite / GPX outputs open in QGIS or [GDAL](./osgeo__gdal.md) for track analysis.
- Concepts: [gnss](../../catalog/concepts/gnss.md), [gnss-rtk-ppp](../../catalog/concepts/gnss-rtk-ppp.md), [gnss-interference](../../catalog/concepts/gnss-interference.md). Catalog page: [catalog/repos/semuconsulting__pygpsclient.md](../../catalog/repos/semuconsulting__pygpsclient.md).

## Gotchas
- tkinter is not pip-installable: on Debian-family systems install `python3-tk`; on old macOS system Python Tk is 8.5 (deprecated), use python.org builds. macOS Python 3.14.5/3.14.6 ship Tk 9.0 with performance issues; >= 3.14.7 reported fixed (README troubleshooting).
- Online map needs a MapQuest API key, which since 2024-01-15 requires a payment card (15,000 free transactions/month) and refreshes once a minute; README says it is not for real-time navigation. Offline: import a georeferenced image as a "custom" map.
- Spectrum widget needs MON-SPAN, which some receivers (e.g. NEO-F10N) only emit at >= 57600 baud. Budget USB-UART adapters are unreliable above 230400 baud (README).
- Linux serial permissions: add the user to `dialout` (Debian) or `uucp` (Arch).
- Spatialite recording needs a Python built with loadable sqlite extensions (not the default on most macOS) plus `mod_spatialite`.
- Desktop quirks: XFCE `BadAlloc` (#236), window growing until crash on Linux (#234), HiDPI / scaled laptop layouts (#250, #260), memory use rising over long sessions (#257). All closed; use 1.8.x.
- The socket server is unauthenticated; do not expose it beyond the lab network.

## Alternatives
- [pygnssutils](./semuconsulting__pygnssutils.md) - same engine without GUI; prefer for headless logging or on the vehicle.
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - daemon plus `cgps`/`xgps`; prefer on Linux vehicles that already standardise on gpsd clients.
- [RTKLIB](./rtklibexplorer__rtklib.md) (`rtknavi`, `strsvr`) - prefer when you want RTKLIB to compute the RTK solution rather than the receiver.

Sources: PyPI JSON for `pygpsclient` (1.8.0, >=3.10, requires_dist), `gh api repos/semuconsulting/PyGPSClient` (BSD-3-Clause, v1.8.0 2026-10-26), pyproject.toml (`[project.scripts]`), src/pygpsclient/__main__.py (argparse flags), README.md (widgets, socket server, MapQuest, troubleshooting), INSTALLATION.md, LICENSE, issues #234, #236, #250, #257, #260.
