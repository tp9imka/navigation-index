# pynmeagps - integration card
<!-- about: repo:semuconsulting/pynmeagps -->
One-line: zero-dependency Python parser/generator for NMEA 0183 - the quickest way to turn any receiver's serial/TCP/log NMEA into typed lat/lon/fix-quality/DOP values, or to emit fake NMEA for a test rig.

| | |
|---|---|
| Install | `python3 -m pip install --upgrade pynmeagps` (PyPI latest 1.1.8, `requires_python >=3.10`, `dependencies = []`). Also `conda install -c conda-forge pynmeagps`. Add `pyserial` yourself for live ports. Installing `pyubx2` pulls it in automatically. |
| Runs on | Any OS with Python 3.10+, pure Python, no GPU. Fine on Raspberry Pi / Jetson. |
| Inputs | Any object with `read(n) -> bytes` / `readline()`: serial port, file opened `rb`, or a socket (wrapped internally by `SocketWrapper`). Single sentences as `str`/`bytes` via `parse()`. Talkers GP/GN/GL/GA/GB etc.; proprietary sentences (u-blox PUBX, Quectel PAIR, others in `nmeatypes_get_prop.py`) plus user-defined dicts. |
| Outputs | `(raw_bytes, NMEAMessage)` tuples. Attributes per message ID: GGA => `lat`, `lon` (signed decimal degrees), `quality`, `numSV`, `HDOP`, `alt` (m MSL), `sep`, `diffAge`; GST => `stdLat`, `stdLong`, `stdAlt`; RMC => `spd` (knots), `cog`, `date`. Repeating groups get 2-digit suffixes (`svid_01`). Outbound: `msg.serialize()` bytes with checksum and CRLF. |
| Key API / entry points | `NMEAReader(stream, msgmode=GET, nmeaonly=False, validate=VALCKSUM, quitonerror=ERR_LOG, userdefined=None)`; `NMEAReader.read() -> (bytes, NMEAMessage)` and iteration `for raw, msg in nmr`; static `NMEAReader.parse(message, msgmode=0, validate=VALCKSUM)`; `NMEAMessage(talker, msgID, msgmode, hpnmeamode=False, **kwargs)` + `.serialize()`; helpers `ecef2llh`, `llh2ecef`, `haversine`, `planar`, `bearing`, `utc2wnotow`, `wnotow2utc`, `latlon2dms`. No CLI of its own - `gnssstreamer` lives in [pygnssutils](./semuconsulting__pygnssutils.md). |
| Time to first result | Estimate: 5 min to print GGA from a USB GNSS dongle or an NMEA log file; assumes the receiver outputs NMEA by default (most do) and you know the port/baud. |
| License | BSD-3-Clause (LICENSE file, copyright semuadmin / Steve Smith). |

## Minimal usage

Not run. Read a live receiver, print fix and per-axis sigma, adapted from the README serial example; GGA/GST field names checked against `src/pynmeagps/nmeatypes_get.py`.

```python
from serial import Serial
from pynmeagps import NMEAReader

with Serial("/dev/ttyACM0", 9600, timeout=3) as s:
    for raw, msg in NMEAReader(s):
        if msg is None:
            continue
        if msg.msgID == "GGA":
            print(msg.time, msg.lat, msg.lon, msg.alt, "q", msg.quality, "sv", msg.numSV, "hdop", msg.HDOP)
        elif msg.msgID == "GST":
            print("sigma lat/lon/alt m:", msg.stdLat, msg.stdLong, msg.stdAlt)
```

Generate a sentence (for a simulated receiver feeding a GCS or an NTRIP caster):

```python
from pynmeagps import NMEAMessage, GET
print(NMEAMessage("GN", "GGA", GET, lat=47.37, lon=8.55, quality=1, numSV=12, HDOP=0.9, alt=410.0).serialize())
```

## Wiring it into a nav stack

- GNSS as one fusion input: parse GGA/RMC/GST, convert to local ENU with [pymap3d](./geospace-code__pymap3d.md), feed a [FilterPy](./rlabbe__filterpy.md) EKF or a [GTSAM](./borglab__gtsam.md) GPS factor. GST sigmas give you a measurement covariance; GGA `quality` and `HDOP` are cheap gating signals.
- u-blox receivers: use [pyubx2](./semuconsulting__pyubx2.md) instead (it parses NMEA too and adds UBX NAV-PVT / MON-RF jamming flags). For a mixed NMEA/UBX/RTCM stream to file, socket or MQTT, `gnssstreamer` in [pygnssutils](./semuconsulting__pygnssutils.md).
- RTK: NTRIP casters want a GGA from the rover; [lord-microstrain/ntrip_client](./lord-microstrain__ntrip_client.md) and pygnssutils' `gnssntripclient` handle that, pynmeagps is the right tool if you hand-roll one.
- Spoofing/consistency checks: NMEA lacks raw measurements, but GSV C/N0 per satellite and position jumps vs INS are enough for a simple detector demo; see [gnss-interference](../../catalog/concepts/gnss-interference.md).
- Ardupilot/PX4 accept NMEA on a GPS port, so a generated stream can drive SITL-adjacent hardware-in-the-loop tests.

Catalog page: [catalog/repos/semuconsulting__pynmeagps.md](../../catalog/repos/semuconsulting__pynmeagps.md). Concepts: [gnss](../../catalog/concepts/gnss.md), [standards](../../catalog/concepts/standards.md).

## Gotchas

- `pyserial` is not a dependency (`dependencies = []` in pyproject.toml); `from serial import Serial` fails until you install it.
- Open issue #102: `NMEAReader` calls `readline()` without a size limit, so a stream that starts `$` and never sends CR/LF buffers forever. On untrusted or noisy links (radio telemetry, fuzzing), bound the input yourself.
- Default `quitonerror=ERR_LOG` logs and continues; a bad checksum yields `msg is None` silently unless you set `ERR_RAISE`. Unknown sentence IDs parse as `NOMINAL` with `field_01...` unless `validate` includes `VALMSGID`.
- Lat/lon are already signed decimal degrees; do not re-apply `NS`/`EW` (issue #37 was a confusion around GLL latitude).
- Default precision is 5 dp of minutes when generating; pass `hpnmeamode=True` for 7 dp (cm-level RTK output), issue #17.
- Proprietary sentence definitions are community-contributed and occasionally wrong (#89 HDM, #52 ASHR); check against the vendor manual before trusting a field.

## Alternatives

- [knio/pynmea2](../../catalog/repos/knio__pynmea2.md) - older, widely used NMEA parser; fine for basics, less maintained, no generator helpers as rich.
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - daemon that owns the device and serves JSON to many clients; prefer when several processes need the GNSS feed.
- [pyubx2](./semuconsulting__pyubx2.md) - superset when the receiver is u-blox and you want UBX binary as well.

Sources: `gh api repos/semuconsulting/pynmeagps` (BSD-3-Clause, release v1.1.8 2026-10-19), README.md, LICENSE, pyproject.toml (requires-python, dependencies, no scripts), src/pynmeagps/__init__.py, src/pynmeagps/nmeareader.py, src/pynmeagps/nmeatypes_get.py (GGA, GST), PyPI JSON for pynmeagps (1.1.8), issues #102, #37, #17, #89, #52, #81.
