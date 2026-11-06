# pygnssutils - integration card
<!-- about: repo:semuconsulting/pygnssutils -->
CLI and Python glue for GNSS streams: log or forward any receiver stream (`gnssstreamer`), pull RTCM corrections from an NTRIP caster (`gnssntripclient`), run your own caster (`gnssserver`), and convert u-blox raw logs to RINEX (`pyrinexconv`).

| | |
|---|---|
| Install | `python3 -m pip install --upgrade pygnssutils` (latest GitHub release v1.3.1; `>=3.10`). Pulls pyubx2>=1.4.0, pyrtcm, pynmeagps, pyspartn, pysbf2, pyunigps, pyqgc, pyubxutils, pyserial, certifi. Also on conda-forge. |
| Runs on | Any OS with Python 3.10+; pure Python except `cryptography` (via pyspartn), which can fail to build on 32-bit Linux. |
| Inputs | Serial port, TCP socket, binary file, or NTRIP caster (HTTP/HTTPS). Protocols NMEA, UBX, SBF (Septentrio), UNI (Unicore), QGC, RTCM3, SPARTN. NTRIP credentials via flags or env `PYGPSCLIENT_USER` / `PYGPSCLIENT_PASSWORD`. |
| Outputs | Parsed text, JSON, raw binary to file/socket/serial, or a Python lambda per message. RTCM3 written back into the receiver for RTK. RINEX 3.05 / 4.02 obs + nav files. |
| Key API / entry points | CLIs from `pyproject.toml`: `gnssstreamer`, `gnssserver`, `gnssntripclient`, `pyrinexconv`. Classes: `GNSSReader(**kwargs)` (multi-protocol reader), `GNSSStreamer(**kwargs)`, `GNSSNTRIPClient(app=None, **kwargs)`, `GNSSSocketServer(**kwargs)`, `RinexConvertor(app, rinex_version, rinex_type, gnssfilter, obsfilter, minobs, verbosity, logtofile, **kwargs)`. |
| Time to first result | Estimate: 5 min to see RTCM frames from a public caster with `gnssntripclient` (assumes network and a caster account, e.g. rtk2go needs an email as user); 30+ min for RINEX because the README asks for 15-30 min of logged raw data. |
| License | BSD-3-Clause |

## Minimal usage
Not run. Commands adapted from the README.

```sh
# 1. Find the nearest mountpoint, then stream RTCM
gnssntripclient --server rtk2go.com --port 2101 --https 0 --datatype RTCM \
  --ntripversion 2.0 --ggainterval -1 --reflat 52.0 --reflon 4.0 \
  --ntripuser you@example.com --ntrippassword none --verbosity 2

# 2. RTK: receiver on serial, NTRIP corrections injected, print GGA fix quality
gnssstreamer --port /dev/ttyACM0 --msgfilter GNGGA --cliinput 1 \
  --input "http://rtk2go.com:2101/MOUNT" --rtkuser you@example.com --rtkpassword none \
  --rtkggaint 10 --clioutput 4 --output "lambda msg: print(msg.lat, msg.lon, msg.quality)"

# 3. Log raw data, then convert to RINEX
gnssstreamer --port /dev/ttyACM0 --baudrate 38400 --format 2 --clioutput 1 \
  --msgfilter RXM-RAWX,RXM-SFRBX,NAV-PVT,GGA --limit 5400 --output raw.log
pyrinexconv -I raw.log --minobs 10 --obsfilter 1C
```

## Wiring it into a nav stack
- Corrections path for RTK: caster => `gnssntripclient`/`gnssstreamer --cliinput 1` => receiver serial. Use RTKLIB `str2str` ([RTKLIB card](./rtklibexplorer__rtklib.md)) instead if you want RTKLIB to compute the RTK solution rather than the receiver.
- Base station for a field demo: base receiver => `gnssserver --ntripmode 1` (built-in caster) => rovers running `gnssntripclient`.
- RINEX output feeds [RTKLIB](./rtklibexplorer__rtklib.md) `rnx2rtkp`, [gnss_lib_py](./stanford-navlab__gnss_lib_py.md), [laika](./commaai__laika.md) or [georinex](../../catalog/repos/geospace-code__georinex.md).
- Lambda/JSON output is a cheap bridge into a MAVLink or ROS publisher without writing a parser; parsing itself is [pyubx2](./semuconsulting__pyubx2.md).

## Gotchas
- RINEX conversion is labelled experimental in the README and covers only u-blox RXM-RAW/RAWX obs, SFRBX nav, RTCM ephemerides and NMEA met data.
- `gnssdump` was renamed `gnssstreamer`; older tutorials break.
- README troubleshooting still mentions a `gnssmqttclient` (SPARTN over MQTT), but no such script is in `pyproject.toml` or `src/pygnssutils/` on main; treat SPARTN MQTT as moved elsewhere (likely PyGPSClient; not verified).
- SPARTN decryption keys are valid ~4 weeks; parse errors usually mean a stale key or basedate (README).
- macOS `SSL: CERTIFICATE_VERIFY_FAILED` for TLS endpoints: upgrade certifi and run Python's `Install Certificates.command`.
- NTRIP issues closed in the tracker (#118 thread stop on Python <=3.9, #98 socket persists after stop, #85 messages occasionally omitted by some casters) - use a current release.
- Many public casters require GGA upload (`--ggainterval`) before they send data for VRS mountpoints.

## Alternatives
- RTKLIB `str2str` / `rtknavi` ([card](./rtklibexplorer__rtklib.md)) - C, also does the positioning, better for post-processing comparisons.
- [nunojpg/ntripcaster](../../catalog/repos/nunojpg__ntripcaster.md) or [goblimey/ntripcaster](../../catalog/repos/goblimey__ntripcaster.md) - dedicated caster if `gnssserver` NTRIP mode is too thin for many clients.
- [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md) - same stack with a GUI.

Sources: `gh api repos/semuconsulting/pygnssutils/readme`, `pyproject.toml` (deps, `[project.scripts]`), `src/pygnssutils/` listing, releases/latest, issue search "ntrip".
