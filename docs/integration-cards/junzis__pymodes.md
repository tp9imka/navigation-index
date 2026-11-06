# pyModeS - integration card
<!-- about: repo:junzis/pymodes -->
One-line: pure-Python Mode S / ADS-B decoder - one `decode()` call gives position, velocity, identity and quality fields (NIC, NACp, SIL) from hex frames, and `modes live` streams a Beast feed to JSON lines.

| | |
|---|---|
| Install | `pip install "pyModeS>=3"` (PyPI name `pyModeS`, latest 3.6.1, GPL v3, `requires-python >=3.11`, no runtime dependencies). Optional TUI: `pip install "pyModeS[tui]"`. Old API: `pip install "pyModeS<3"` (2.x line). |
| Runs on | Any OS, CPU, Python 3.11-3.13 (classifiers). Pure Python since v3 (Cython extension and numpy dependency removed). |
| Inputs | Hex strings (14 or 28 hex chars), optionally with timestamps in seconds; airborne CPR reference `reference=(lat, lon)` (within 180 NM) or surface reference `surface_ref="EHAM"` / `(lat, lon)` (within 45 NM). CLI file input: one hex per line or `timestamp,hex` CSV. Network input: Mode-S Beast binary over TCP only (dump1090, readsb, piaware). Legacy AVR text not supported in v3. No direct SDR input in v3. |
| Outputs | `Decoded` dict per message: `df`, `icao`, `crc_valid`, `typecode`, `bds`, `callsign`, `latitude`, `longitude`, altitude, `groundspeed`, track, vertical rate, `nac_p`, `nac_v`, `nic_b`, `nic_baro`, `sil`, `version`, ... (`full_dict=True` fills all keys of a 123-field schema with nulls). Batch mode returns error-dicts instead of raising. CLI emits JSON / JSON lines. |
| Key API / entry points | `pyModeS.decode(msg: str, *, reference=None, surface_ref=None, known=None, include_meteo=False, full_dict=False, uplink=False)` for one message; `decode(msgs: list[str], *, timestamps=None, surface_ref=None, ...)` for a batch (no `reference` / `known` in batch mode); `pyModeS.PipeDecoder(*, surface_ref=None, include_meteo=False, full_dict=False, pair_window=10.0, eviction_ttl=300.0, max_speed_kt=1500.0, ...)` with `.decode(msg, timestamp=...)`; `pyModeS.util` helpers (`hex2bin`, `crc`, `icao`, `typecode`, `altcode`, `idcode`, `cprNL`); errors `DecodeError`, `InvalidHexError`. CLI `modes` (`pyModeS.cli:main`): `modes decode <hex>|--file F`, `modes live --network HOST:PORT [--dump-to F] [--tui]`. |
| Time to first result | Estimate: 5 min to decoded JSON from a hex string; 15 min from a live readsb/dump1090 Beast port, assuming the decoder is already receiving. |
| License | GPL-3.0 (LICENSE; PyPI "GNU GPL v3"). Linking it into a distributed program brings GPL obligations. |

## Minimal usage

Not run. From README examples.

```python
from pyModeS import decode, PipeDecoder

print(decode("8D406B902015A678D4D220AA4BDA")["callsign"])   # EZY85MH

pipe = PipeDecoder()
for ts, msg in [(3.0, "8D40058B58C901375147EFD09357"), (4.0, "8D40058B58C904A87F402D3B8C59")]:
    d = pipe.decode(msg, timestamp=ts)
    if d.get("latitude") is not None:
        print(d["icao"], d["latitude"], d["longitude"], d.get("nac_p"), d.get("nic_b"))
```

```bash
modes decode 8D406B902015A678D4D220AA4BDA
modes live --network 127.0.0.1:30005 --dump-to adsb.jsonl   # Beast output of a local readsb/dump1090
```

Port 30005 is the conventional Beast output port of readsb/dump1090 (see the [readsb card](./wiedehopf__readsb.md)); pyModeS docs only say `HOST:PORT`.

## Wiring it into a nav stack

- Receiver chain: RTL-SDR => [readsb](./wiedehopf__readsb.md) (or [dump1090](../../catalog/repos/flightaware__dump1090.md)) => Beast TCP => `modes live` / `PipeDecoder` => JSON lines => your tracker, map or CoT bridge ([PyTAK](./snstac__pytak.md)).
- GNSS interference monitoring: aircraft NIC/NACp drops across many ICAOs in one area are a classic jamming/spoofing indicator. pyModeS exposes `nic_b`, `nac_p`, `sil`, `version` per message; aggregate per grid cell and time window, render with [MapLibre](./maplibre__maplibre-gl-js.md). See [gnss-interference](../../catalog/concepts/gnss-interference.md).
- Air traffic as a sensor input for tracking: decoded positions feed [Stone Soup](./dstl__stone-soup.md) as detections.
- Cross-check against [OpenSky](./openskynetwork__opensky-api.md) for the same area.
- Background reading in the index: `res:junzis-1090mhz-riddle` (Mode S / ADS-B book by the same author).

Catalog page: [catalog/repos/junzis__pymodes.md](../../catalog/repos/junzis__pymodes.md). Concepts: [situational-awareness](../../catalog/concepts/situational-awareness.md), [standards](../../catalog/concepts/standards.md).

## Gotchas

- v3 broke the API: `pms.adsb.callsign(msg)`, `pms.adsb.position(...)`, `pms.commb`, `pyModeS.streamer` and the `modeslive` CLI are gone. Importing them raises `V2APIRemovedError`; `modeslive` prints a migration hint and exits 2 (CHANGELOG "Removed", `_v2_removed.py`). Almost every blog post, Stack Overflow answer and LLM completion uses the v2 API. Pin `pyModeS<3` for old code, or read `docs/migration.md`.
- Downstream pins: [adsbcot](./snstac__adsbcot.md) requires `pymodes>=2.18,<3` for raw/Beast feeds. Installing both in one env with `pyModeS>=3` breaks adsbcot; use separate venvs.
- No direct SDR input in v3; old issues #54 (HackRF), #179 (could not open SDR), #65 (raw IQ file) are about the v2-era RTL-SDR streamer. Use readsb as the front end.
- Timestamps are seconds (closed #201 on units). Airborne CPR needs an even/odd pair (`PipeDecoder` default `pair_window=10.0` s) or a `reference=(lat, lon)` within 180 NM; a lone airborne position message without either cannot be resolved globally.
- BDS 4,4 / 4,5 meteo inference is heuristic and off by default (`include_meteo=True`). Comm-B BDS 5,0 / 6,0 can be ambiguous; pass `known=` aircraft state to disambiguate.
- Python >=3.11 required; older Jetson images ship 3.8/3.10.
- PyPI name is `pyModeS`; `pymodes` resolves to the same project (pip normalizes case).

## Alternatives

- [readsb](./wiedehopf__readsb.md) - C decoder with aircraft.json output; prefer when you only need positions and want speed and a web map ([tar1090](../../catalog/repos/wiedehopf__tar1090.md)).
- [traffic](../../catalog/repos/xoolive__traffic.md) - trajectory analysis on top of decoded data and OpenSky.
- [OpenSky API](./openskynetwork__opensky-api.md) - already-decoded network data when you have no receiver.

Sources: `gh api repos/junzis/pymodes` (GPL-3.0, release v3.6.1 2026-10-19), PyPI JSON for `pyModeS` (3.6.1, >=3.11, release list), README.md, pyproject.toml (`[project.scripts]`, no deps), LICENSE, CHANGELOG.md (Removed section, Beast notes), docs/quickstart.md (`modes live`, AVR unsupported), src/pyModeS/__init__.py, src/pyModeS/cli/_args.py, src/pyModeS/_pipe.py, src/pyModeS/_schema.py (nac_p, nic_b, sil), src/pyModeS/_v2_removed.py; issues #54, #65, #179, #201; docs/integration-cards/snstac__adsbcot.md (pymodes<3 pin).
