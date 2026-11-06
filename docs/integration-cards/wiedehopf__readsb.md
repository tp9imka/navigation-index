# readsb - integration card
<!-- about: repo:wiedehopf/readsb -->
One-line: Mode S / ADS-B decoder for RTL-SDR and other SDRs whose `aircraft.json` exposes per-aircraft integrity fields (NIC, NACp, SIL, Rc) and an experimental `gpsOkBefore` flag, so a $30 receiver becomes a regional GNSS-interference monitor and an air-picture feed.

| | |
|---|---|
| Install | Recommended: install script at github.com/wiedehopf/adsb-scripts (wiki "Automatic installation for readsb"). Debian package build (README): `sudo apt install --no-install-recommends -y git build-essential debhelper libusb-1.0-0-dev pkg-config fakeroot libncurses-dev zlib1g-dev libzstd-dev librtlsdr-dev help2man && git clone --depth 20 https://github.com/wiedehopf/readsb.git && cd readsb && export DEB_BUILD_OPTIONS=noddebs && dpkg-buildpackage -b -ui -uc -us --build-profiles=rtlsdr && sudo dpkg -i ../readsb_*.deb`. macOS: Homebrew formula exists (`brew install readsb`). No GitHub releases; build from `dev` (default branch). |
| Runs on | Linux (RPi is the common host), macOS largely compatible (README). RTL-SDR, plus SoapySDR/HackRF/bladeRF/PlutoSDR with the `with_sdrs` build profile. 1090 MHz antenna. |
| Inputs | SDR samples, or network Beast/raw/SBS/ASTERIX/UAT input (`--net-connector host,port,beast_in`, `--net-bi-port`, `--net-ri-port`, `--net-sbs-in-port`). |
| Outputs | `aircraft.json` (and `receiver.json`, `stats.json`) in `--write-json=<dir>` every `--write-json-every` s; one JSON object per position on `--net-json-port`; HTTP API `--net-api-port`; Beast (`--net-bo-port`), raw, SBS/BaseStation (`--net-sbs-port`), ASTERIX out, VRS JSON, Kinetic SBS-3 binary. Per-aircraft keys (README-json.md): `hex`, `type` (`adsb_icao`, `adsr_icao`, `tisb_icao`, `mlat`, `adsc`, `mode_s`, ...), `flight`, `lat`, `lon`, `alt_baro`, `alt_geom`, `nic`, `rc` (m), `nac_p`, `nac_v`, `sil`, `sil_type`, `gva`, `sda`, `nic_baro`, `seen_pos`, `messages`, `lastPosition`, `gpsOkBefore` (experimental). |
| Key API / entry points | `readsb --net --device-type rtlsdr --gain auto --lat <deg> --lon <deg> --write-json=/run/readsb --write-json-every 0.5 [--interactive] [--net-json-port 30154] [--net-api-port 8042]`; `--net-connector IP,PORT,PROTOCOL` (push/pull); `--json-reliable`, `--json-trace-interval`, `--db-file`. |
| Time to first result | Estimate: 30-60 min on a Pi with an RTL-SDR dongle and a 1090 MHz antenna to see aircraft in `--interactive`. Needs real traffic overhead; no hardware => use a recorded Beast stream as input. |
| License | GPL-3.0-or-later per the repo `LICENSE` file ("see the individual source files and COPYING"); GitHub shows NOASSERTION. |

## Minimal usage
From README. Not run.

```bash
./readsb --quiet --net --device-type rtlsdr --gain auto --lat 51.5 --lon -0.1 \
         --write-json=/tmp/readsb --write-json-every 1 --interactive
```
GNSS-interference indicator (sketch, not run): read `/tmp/readsb/aircraft.json` each second; for aircraft with `type == "adsb_icao"`, flag `nac_p` dropping below 8 (our heuristic threshold, not from the repo), `nic` dropping or `gpsOkBefore` present; aggregate by position and time to map an interference area, as public GPS-jamming maps do with the same fields.

```python
import json, time
while True:
    ac = json.load(open("/tmp/readsb/aircraft.json"))["aircraft"]
    bad = [a for a in ac if a.get("type") == "adsb_icao" and
           (a.get("nac_p", 11) < 8 or "gpsOkBefore" in a)]
    print(len(ac), "aircraft,", len(bad), "with degraded GNSS integrity")
    time.sleep(1)
```

## Wiring it into a nav stack
- Air picture to TAK: `--net-sbs-port`/Beast => [adsbcot](../../catalog/repos/snstac__adsbcot.md) => [PyTAK](./snstac__pytak.md) => [OpenTAKServer](./brian7704__opentakserver.md) / [GoATAK](./kdudkov__goatak.md).
- Tracking and fusion with other sensors: aircraft positions as detections into [Stone Soup](./dstl__stone-soup.md) (its `OpenSky` demo shows the same kind of data).
- Web map: [tar1090](../../catalog/repos/wiedehopf__tar1090.md) reads the same JSON; or draw with [milsymbol](./spatialillusions__milsymbol.md).
- Decode Mode S yourself for research: [pyModeS](../../catalog/repos/junzis__pymodes.md).
- Catalog: [readsb page](../../catalog/repos/wiedehopf__readsb.md).

## Gotchas
- `gpsOkBefore` is explicitly "experimental, subject to change" and only shown for 15 min after GPS loss/degradation (README-json.md). Treat NIC/NACp trends as the primary signal.
- Integrity fields are what the aircraft reports about its own navigation; a drop means "this aircraft's GNSS is degraded", not where the jammer is. Spatial aggregation over many aircraft is needed before claiming an interference area.
- MLAT and TIS-B positions (`type` `mlat`, `tisb_*`) carry no aircraft-reported integrity; filter by `type`.
- Positions with low reliability are hidden from JSON by default (`--json-reliable`); for research you may want them.
- Running a second decoder on the same host needs different ports (README).

## Alternatives
- [dump1090 (FlightAware)](../../catalog/repos/flightaware__dump1090.md): the upstream lineage, fewer integrity outputs.
- [OpenSky API](../../catalog/repos/openskynetwork__opensky-api.md): network data without your own receiver (rate-limited, not live-local).

Sources: `README.md`, `README-json.md`, `LICENSE`, `readsb --help` text in README, branches/releases API (no releases), record notes in the index.
