# pyais - integration card
<!-- about: repo:m0r13n/pyais -->
One-line: pure-Python AIS (AIVDM/AIVDO) decoder and encoder with socket/file streams, filters and an in-memory vessel tracker - the fastest path from NMEA lines to ship tracks in Python.

| | |
|---|---|
| Install | `pip install pyais` (PyPI 3.3.1, MIT, `requires-python >=3.9`; only dependency `attrs`). `main` already says 3.4.0 in `pyais/__init__.py` (unreleased at time of reading). Releases carry `SHA256SUMS` for verification (README). |
| Runs on | Any OS, CPU, CPython 3.9+ and PyPy. |
| Inputs | NMEA 0183 AIS sentences as `bytes` or `str` (`!AIVDM`/`!AIVDO`, multi-part, optional tag blocks and Gatehouse wrappers); files (`FileReaderStream`), TCP client (`TCPConnection(host, port)`), UDP listener (`UDPReceiver(host, port)`), TCP server, any iterable (`IterMessages`). |
| Outputs | Typed message objects (`MessageType1` ... `MessageType27`) with fields such as `mmsi`, `lat`, `lon` (deg), `speed` (kn), `course`, `heading`, `shipname`; `.asdict()`; `AISTrack` records from `AISTracker`; encoded NMEA from `encode_dict` / `encode_msg`. |
| Key API / entry points | `pyais.decode(*parts)`; `pyais.stream.TCPConnection(host, port)`, `UDPReceiver(host, port)`, `FileReaderStream(path)`, `IterMessages(iterable)` (each yields `NMEAMessage`, call `.decode()`); `AISTracker(ttl_in_seconds=600, stream_is_ordered=False)` with `.update(msg, ts_epoch_ms=None)`, `.tracks`, `.get_track(mmsi)`, `.n_latest_tracks(n)`, `.register_callback(event, fn)`; `encode_dict(data, radio_channel="B", talker_id="AIVDM")`; filters `FilterChain`, `DistanceFilter`, `GridFilter`, `MessageTypeFilter`. CLIs `ais-decode`, `ais-encode`. |
| Time to first result | Estimate: 5 min to decoded ships from the public Norwegian Coastal Administration feed (`153.44.253.27:5631`, per README), assuming outbound TCP is allowed. |
| License | MIT (LICENSE). The Norwegian live feed is under the Norwegian Licence for Open Government Data (NLOD), per README. |

## Minimal usage

Not run. Adapted from README and `examples/live_stream.py`.

```python
from pyais import AISTracker
from pyais.stream import TCPConnection

with AISTracker(ttl_in_seconds=600) as tracker:
    for i, msg in enumerate(TCPConnection("153.44.253.27", port=5631)):
        tracker.update(msg)
        if i and i % 500 == 0:
            for t in tracker.n_latest_tracks(10):
                print(t.mmsi, t.shipname, t.lat, t.lon, t.speed, t.course)
```

Local receiver instead: `from pyais.stream import UDPReceiver; for msg in UDPReceiver("0.0.0.0", 10110): print(msg.decode())` with [AIS-catcher](./jvde-github__ais-catcher.md) sending `-u <this host> 10110`.

## Wiring it into a nav stack

- Source: [AIS-catcher](./jvde-github__ais-catcher.md) (SDR), a hardware AIS receiver on serial (read lines, pass to `decode`), [Signal K](./signalk__signalk-server.md)'s NMEA 0183 TCP output, or recorded logs.
- Tracks to the operator view: `AISTrack` => GeoJSON => [MapLibre](./maplibre__maplibre-gl-js.md); or CoT via [PyTAK](./snstac__pytak.md) for TAK clients ([goatak](./kdudkov__goatak.md), [OpenTAKServer](./brian7704__opentakserver.md)).
- Multi-target tracking and fusion with radar/camera detections: feed positions to [Stone Soup](./dstl__stone-soup.md); convert to local ENU with [pymap3d](./geospace-code__pymap3d.md).
- Test data generation: `encode_dict` produces valid AIS sentences for simulated vessels, useful for replaying scenarios into OpenCPN or Signal K without a radio.
- Spec background in the index: `res:itu-r-m1371-ais` (ITU-R M.1371).

Catalog page: [catalog/repos/m0r13n__pyais.md](../../catalog/repos/m0r13n__pyais.md). Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [situational-awareness](../../catalog/concepts/situational-awareness.md), [target-tracking](../../catalog/concepts/target-tracking.md).

## Gotchas

- "Not available" sentinels come through as numbers: per ITU-R M.1371, lat 91, lon 181, speed 102.3, heading 511 mean unavailable. The converters in `messages.py` (`from_lat_lon`, `from_speed`) do plain scaling; filter these before plotting or fusing (e.g. `NoneFilter` does not catch them, an `AttributeFilter` lambda does).
- Tracker time units: `AISTracker.update(msg, ts_epoch_ms=...)` names the argument milliseconds, but the default and `cleanup()` use `time.time()` (seconds) against `ttl_in_seconds` (`tracker.py`). Pass seconds. When replaying old logs with their original timestamps, cleanup compares against wall-clock now and prunes tracks immediately - set `ttl_in_seconds=None` for replay.
- `stream_is_ordered=True` raises `ValueError` on any out-of-order timestamp; leave it `False` with multiple receivers.
- Multi-part messages (type 5 static data, type 24) must be passed together to `decode(*parts)`; streams assemble them for you, single-line calls do not.
- Tag blocks are lazily parsed: call `msg.tag_block.init()` before reading them.
- Malformed payloads with unexpected bit length used to fail silently returning `None` (closed #46); check for `None` anyway when ingesting dirty feeds.
- Message timestamps: AIS position reports carry only a UTC second (0-59); full receive time must come from the receiver, tag block or your clock (closed #17, #139).

## Alternatives

- [AIS-catcher](./jvde-github__ais-catcher.md) `-o 5` / `JSON_FULL` - decoding done in C at the receiver; prefer when you only need JSON and no Python logic.
- [schwehr/noaadata](../../catalog/repos/schwehr__noaadata.md) - older pure-Python AIS research library; prefer only for its NOAA tooling.
- [Signal K server](./signalk__signalk-server.md) - decodes AIS into `vessels.*` JSON with REST/WebSocket APIs; prefer when other boat data is involved.

Sources: `gh api repos/M0r13n/pyais` (MIT, pushed 2026-11-01), PyPI JSON for `pyais` (3.3.1, >=3.9), README.md, LICENSE, pyproject.toml (deps, `[project.scripts]`), pyais/__init__.py (exports, version), pyais/stream.py (`UDPReceiver`, `TCPConnection`), pyais/tracker.py (`AISTracker`, `now()`, `cleanup`), pyais/messages.py (converters), examples/live_stream.py; issues #17, #46, #91, #139.
