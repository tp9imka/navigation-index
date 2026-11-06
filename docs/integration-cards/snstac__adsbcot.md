# ADSBCOT - integration card
<!-- about: repo:snstac/adsbcot -->
One-line: PyTAK-based gateway that polls an ADS-B decoder (readsb/dump1090 JSON, raw or Beast TCP) or an aggregator API and pushes every aircraft as a CoT track to ATAK/WinTAK/iTAK or a TAK server; the fastest way to get the live air picture onto your common operating picture.

| | |
|---|---|
| Install | `sudo apt install adsbcot` from the signed snstac apt repo (keyring + sources commands in `docs/installation.md`; HTTP and file feeds only), or the `.deb`/`.rpm` assets on the GitHub release. `docs/installation.md` still says `python3 -m pip install adsbcot`, but PyPI returns 404 for `adsbcot` (checked 2026-11-06); install from source instead: `python3 -m pip install 'adsbcot[with_pymodes] @ git+https://github.com/snstac/adsbcot'` (the extra is needed for `tcp://` raw/Beast feeds; keep `pymodes>=2.18,<3`). Latest release v9.2.2 (2026-09-05, `src/adsbcot/VERSION`). |
| Runs on | Python >= 3.9 (`setup.cfg`), Linux, macOS, Windows. Pure Python; deps `aircot>=4.0.0`, `pytak>=7.3.12`, `aiohttp<4`, `websockets<11`. A Pi is plenty. |
| Inputs | `FEED_URL`: `file:///run/dump1090-fa/aircraft.json` (default), `http(s)://` aircraft JSON (readsb/piaware web, or aggregators such as airplanes.live `https://api.airplanes.live/v2/point/<lat>/<lon>/<radius>`), `ws(s)://` JSON, `tcp://`/`tcp+raw://` AVR on 30002, `tcp+beast://` on 30005. Port 30003 (SBS CSV) is not supported. Reads readsb/dump1090 keys (`hex`, `flight`, `lat`, `lon`, `alt_geom`, `gs`, `trk`, `squawk`, `category`, `NACp`/`nac_p`, `NACv`/`nac_v`) and Stratux keys. Optional `KNOWN_CRAFT` CSV for callsign/icon/CoT type overrides. |
| Outputs | CoT XML events (via PyTAK, so also protobuf if `TAK_PROTO=1`) with `<track course speed>`, `<contact callsign>`, `<remarks>` (flight, reg, squawk, ICAO hex, category, type), `<__adsb>` and `<_radio>` detail; CoT type from `aircot.set_cot_type(...)`. Plus a periodic receiver beacon `SENSOR.<id>` of type `a-f-G-E-S-E` (disable with `SENSOR_BEACON=0`). Destination is PyTAK `COT_URL`. |
| Key API / entry points | CLI `adsbcot -c config.ini` (`adsbcot.commands:main` => `pytak.cli("adsbcot")`); config keys `FEED_URL`, `POLL_INTERVAL` (default 3 s), `ALT_UPPER`/`ALT_LOWER`, `INCLUDE_TISB`, `KNOWN_CRAFT`, `SENSOR_BEACON` plus all PyTAK keys (`COT_URL`, `COT_STALE`, `TAK_PROTO`). Library: `adsbcot.adsb_to_cot_xml(craft: dict, config=None, known_craft=None) -> Optional[ET.Element]`, `adsbcot.adsb_to_cot(craft, config=None, known_craft=None) -> Optional[bytes]`, `gen_sensor_cot(config=None, lat=0.0, lon=0.0, hae=0.0, ce=..., le=...)`, `create_tasks(config, clitool)`. Workers: `ADSBWorker`, `ADSBNetWorker`, `ADSBNetReceiver`, `SensorWorker` (`classes.py`). |
| Time to first result | Estimate: 10-20 min to see aircraft on an ATAK/WinTAK device or OpenTAKServer map using an internet aggregator feed (no radio). 1-2 h with an RTL-SDR, a 1090 MHz antenna and readsb to install. Assumes a reachable TAK client/server and pip or apt access. |
| License | Apache-2.0. |

## Minimal usage
No-hardware path using a public aggregator, adapted from `docs/configuration.md`. Not run.

```ini
# adsbcot.ini - values without quotes, comments on their own line
[adsbcot]
FEED_URL = https://api.airplanes.live/v2/point/37.8/-122.0/25
POLL_INTERVAL = 5
COT_URL = tcp://127.0.0.1:8088
COT_STALE = 30
```
```bash
python3 -m pip install 'adsbcot @ git+https://github.com/snstac/adsbcot'
adsbcot -c adsbcot.ini
```
With a local SDR swap `FEED_URL` for your readsb JSON (`http://<host>:8080/data/aircraft.json` style, see the readsb card) or `tcp+beast://127.0.0.1:30005`.

Library form, if you already hold readsb JSON and run your own PyTAK sender (not run):

```python
import adsbcot
cot_bytes = adsbcot.adsb_to_cot({"hex": "a1b2c3", "flight": "TEST1", "lat": 37.8, "lon": -122.0,
                                 "alt_geom": 3500, "gs": 140, "trk": 90, "NACp": 9},
                                config={"COT_STALE": "30"})
```

## Wiring it into a nav stack
- Air picture: [readsb](./wiedehopf__readsb.md) or [dump1090-fa](../../catalog/repos/flightaware__dump1090.md) => ADSBCOT => [OpenTAKServer](./brian7704__opentakserver.md) / [GoATAK](./kdudkov__goatak.md) or multicast to ATAK. Transport and TLS are all [PyTAK](./snstac__pytak.md) config.
- Mixed C-UAS picture: run next to [DragonSync](./alphafox02__dragonsync.md) (drones) and a [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) bridge (bearings) into the same TAK server; DragonSync also has its own readsb ingest if you want one process instead of two.
- GNSS-interference overlay: ADSBCOT does not forward NIC/NACp as fields (see Gotchas). For a GPSJam-style layer, read `nic`/`nac_p` from readsb JSON directly and emit your own CoT (shapes or spot reports) via PyTAK, or post-process with [pyModeS](../../catalog/repos/junzis__pymodes.md).
- Protobuf encoding happens in PyTAK with [takproto](./snstac__takproto.md) when `TAK_PROTO=1`.
- Catalog: [ADSBCOT page](../../catalog/repos/snstac__adsbcot.md).

## Gotchas
- `ce`/`le` are not real uncertainties: `adsb_to_cot_xml` sets `ce = NACp + 56.57` (51.56 on ground) and `le = NACv + 12.5`, adding the NACp category number (0-11) to a constant. Higher NACp (better accuracy) gives a slightly larger `ce`. Do not present the TAK error circle as nav integrity; NIC is not read at all (`functions.py`).
- INI values must be unquoted and comments on their own line; `FEED_URL = "https://..."` keeps the quotes in the URL (`docs/configuration.md`).
- `tcp://host:30003` decodes nothing (SBS CSV); use 30002 or 30005. pyModeS 3 removed the streaming decoder, pre-2.18 raises `ValueError: too many values to unpack` (`docs/installation.md`). Open #51: pymodes wheel build errors.
- The apt package only does HTTP/file feeds. Open #45 (install instructions do not install pytak), #56 (Dockerfile and build instructions broken), #61 (broken tests). `docs/installation.md` still says the source repo is private; the GitHub repo is public (API `visibility=public`).
- Aggregator APIs have rate limits and terms of use; keep `POLL_INTERVAL` sane and do not build a product on them. Closed #44: large feeds overflow the queue ("Queue full, dropping oldest data").
- Aircraft linger until their CoT goes stale; lower `COT_STALE` for a busy airspace.

## Alternatives
- [DragonSync](./alphafox02__dragonsync.md) when you already run a WarDragon-style drone sensor; it ingests readsb `/?all_with_pos` and emits aircraft CoT alongside drones.
- [tar1090](../../catalog/repos/wiedehopf__tar1090.md) if you only need a web map of aircraft and not TAK.
- [node-cot](../../catalog/repos/dfpc-coe__node-cot.md) to write your own converter in a JavaScript stack.

Sources: `README.md`, `docs/configuration.md`, `docs/installation.md`, `docs/troubleshooting.md`, `setup.cfg`, `src/adsbcot/VERSION`, `src/adsbcot/commands.py`, `src/adsbcot/constants.py`, `src/adsbcot/functions.py` (`adsb_to_cot_xml`, `adsb_to_cot`, `gen_sensor_cot`, ce/le computation), `src/adsbcot/classes.py`, repo metadata and releases API, issue search (#44, #45, #51, #56, #61).
