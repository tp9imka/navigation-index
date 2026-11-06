# AIS-catcher - integration card
<!-- about: repo:jvde-github/ais-catcher -->
One-line: turn a cheap RTL-SDR (or Airspy, HackRF, SDRplay, serial dAISy) into a dual-channel AIS receiver with a built-in web map and NMEA/JSON out over UDP/TCP/HTTP - the local maritime picture for a demo.

| | |
|---|---|
| Install | Linux (Debian/Ubuntu/RPi OS/Fedora), from the docs: `sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/jvde-github/AIS-catcher/main/scripts/aiscatcher-install) -p"` (pre-built .deb/.rpm, sets up a service; add `-M` for browser-managed mode on port 8118, drop `-p` to build from source). Docker: `ghcr.io/jvde-github/ais-catcher:latest` (release) or `:edge` (main), e.g. `docker run --rm -it --device /dev/bus/usb ghcr.io/jvde-github/ais-catcher:latest <options>`. macOS: build from source with Homebrew deps (`cmake`, `librtlsdr`, ...). Latest release v0.70 (2026-06-19). Python binding `aiscat` on PyPI (0.68.16, not checked further). |
| Runs on | Linux x86_64/arm64/armhf, macOS, Windows (installer in docs), Android. Pre-built packages not compatible with Raspberry Pi 1 / Zero (docs note); Docker image lacks `linux/arm/v6` (open #656) and SDRplay support. CPU only. |
| Inputs | VHF IQ from RTL-SDR (`-d` / default device, `-gr` RTL settings), Airspy, Airspy HF+, HackRF, HydraSDR, SDRplay, SoapySDR, RTL-TCP, SpyServer, ZMQ; IQ file or stdin (`-r file` / `-r .`, `-s` sample rate); serial hardware receivers (dAISy); NMEA text (`-r txt .`); NMEA 2000. Station position from GPS NMEA or GPSD (`-t gpsd localhost 2947`). |
| Outputs | NMEA 0183 `!AIVDM` sentences; console formats via `-o` (1 NMEA, 3 JSON-wrapped NMEA, 5 full JSON decode); UDP `-u host port [msgformat JSON_FULL]`; TCP server `-S port`; TCP client `-P host port`; HTTP POST, MQTT, PostgreSQL (source build only); web viewer `-N 8100` with map, ship list, statistics and a REST/JSON API. Metadata (signal level, ppm, timestamps) with `-M DT`. |
| Key API / entry points | Binary `AIS-catcher` (Docker entrypoint `/usr/bin/AIS-catcher`). Most-used switches: `-l` list devices, `-v` verbose stats, `-N 8100` web viewer, `-u` UDP out, `-S` TCP server, `-o 5` JSON to stdout, `-q` quiet, `-M DT` metadata, `-X <key>` community feed, `FILTER on EXCLUDE_ERRORS undersized,checksum`. Managed mode: `-E /config/config.json 127.0.0.1:8118`. |
| Time to first result | Estimate: 30 min to ships on the web map with an RTL-SDR and a VHF antenna near water, using the install script or Docker. Reception depends entirely on antenna height and distance to shipping. |
| License | GPL-3.0 (LICENSE). README also: research/education use only, "DO NOT rely upon this software ... for navigation", and AIS reception legality varies by country. |

## Minimal usage

Not run. Commands from the docs, adapted.

```bash
AIS-catcher -l                                   # list SDRs
AIS-catcher -v 10 -N 8100                        # decode from first RTL-SDR, web map on :8100
AIS-catcher -N 8100 -u 127.0.0.1 10110 -o 5      # also send NMEA over UDP and print full JSON
```

Docker equivalent (manual mode):

```bash
docker run --rm -it --device /dev/bus/usb -p 8100:8100 ghcr.io/jvde-github/ais-catcher:latest -N 8100 -u 192.168.1.10 10110
```

No SDR: pipe recorded NMEA in with `cat log.nmea | AIS-catcher -r txt . -N 8100` (text input per docs `advanced/GPS.md`), or decode the NMEA directly with [pyais](./m0r13n__pyais.md).

## Wiring it into a nav stack

- AIS-catcher (UDP NMEA) => [pyais](./m0r13n__pyais.md) `UDPReceiver` => own tracker / fusion => [MapLibre](./maplibre__maplibre-gl-js.md) or CoT via [PyTAK](./snstac__pytak.md).
- AIS-catcher (UDP or TCP NMEA) => [Signal K server](./signalk__signalk-server.md) NMEA 0183 connection => `vessels.*` in Signal K => chartplotters such as [OpenCPN](../../catalog/repos/opencpn__opencpn.md).
- Own-ship position: feed GPSD (`-t gpsd`) so the web viewer and range stats use the moving station position ([gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md)).
- Same SDR family as ADS-B: one RTL-SDR per band; for a combined air + sea picture run [readsb](./wiedehopf__readsb.md) on a second dongle.
- Defensive use: AIS gaps, MMSI anomalies and position jumps are inputs for spoofing / dark-vessel detection; JSON output with signal level (`-M D`) helps separate RF issues from data issues.

Catalog page: [catalog/repos/jvde-github__ais-catcher.md](../../catalog/repos/jvde-github__ais-catcher.md). Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [situational-awareness](../../catalog/concepts/situational-awareness.md), [gnss-sdr](../../catalog/concepts/gnss-sdr.md).

## Gotchas

- Not for navigation: the README disclaimer is explicit. Use it for awareness and research only.
- Install script pipes curl to `sudo bash` and installs a systemd service; for a throwaway setup prefer Docker.
- Switching an install from manual to managed mode does not carry over `config.json` / `config.cmd` (docs warning).
- Web viewer basemap tiles come from online providers; offline or blocked networks show no map (closed #431 "OpenStreet Map Blocked").
- Docker networking: UDP/TCP outputs not received from the container in some setups (closed #247) - use `--network=host` or publish ports.
- SDRplay not in Docker images; PostgreSQL output only in source builds.
- Plugin API changed without a version bump once (closed #638); pin the version if you build web-viewer plugins.
- RTL-SDR v4 needs a recent librtlsdr; the pre-built packages link it statically (docs note), a distro librtlsdr may not.

## Alternatives

- [pyais](./m0r13n__pyais.md) - decoder only, no radio; prefer when you already have NMEA (hardware AIS receiver, recorded logs, public feeds).
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) - chartplotter that displays AIS from any NMEA source; prefer as the operator display.
- [schwehr/noaadata](../../catalog/repos/schwehr__noaadata.md) - Python AIS research tools for archived data.

Sources: `gh api repos/jvde-github/AIS-catcher` (GPL-3.0, release v0.70 2026-06-19), README.md, LICENSE, Dockerfile; AIS-catcher-docs repo: docs/installation/ubuntu-debian.md, docker.md, macos.md, docs/configuration/output/UDP.md, console.md, web-viewer.md, TCP-server.md, docs/configuration/input/file.md, rtlsdr.md, docs/advanced/GPS.md; PyPI JSON for `aiscat`; issues #247, #431, #638, #656.
