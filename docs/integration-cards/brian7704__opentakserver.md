# OpenTAKServer - integration card
<!-- about: repo:brian7704/opentakserver -->
One-line: Python/Flask TAK server with a web map UI that ATAK, iTAK, WinTAK and PyTAK clients connect to; gives a hackathon team a shared common operating picture, data packages, video and a REST API in about an hour.

| | |
|---|---|
| Install | Ubuntu: `curl https://i.opentakserver.io/ubuntu_installer -Ls \| bash -`; Raspberry Pi: `curl https://i.opentakserver.io/raspberry_pi_installer -Ls \| bash -`; Windows via WSL + the Ubuntu script (README). A `Dockerfile` is in the repo. Latest release seen: 1.8.0 (2026-11-05). |
| Runs on | Linux servers and SBCs (RPi). Needs RabbitMQ, nginx, openssl; MediaMTX for video (README requirements). |
| Inputs | CoT from clients over TCP (default `OTS_TCP_STREAMING_PORT` 8088), TLS (8089), UDP (8087); Marti API HTTP 8080 / HTTPS 8443; OTS REST API (`blueprints/ots_api/*`: markers, missions, data packages, video, Meshtastic, federation, CasEvac). |
| Outputs | Rebroadcast CoT to connected clients and groups/channels, CoT saved to a database, web UI live map ([OpenTAKServer-UI](https://github.com/brian7704/OpenTAKServer-UI)), video via MediaMTX. |
| Key API / entry points | Config keys in `opentakserver/defaultconfig.py` (env-overridable): `OTS_LISTENER_PORT` 8081 (internal), `OTS_MARTI_HTTP_PORT` 8080, `OTS_MARTI_HTTPS_PORT` 8443, `OTS_TCP_STREAMING_PORT` 8088, `OTS_SSL_STREAMING_PORT` 8089, `OTS_UDP_PORT` 8087, `OTS_ENABLE_TCP_STREAMING_PORT`, `OTS_MEDIAMTX_ENABLE`, `OTS_ENABLE_MESHTASTIC`, `OTS_ENABLE_LDAP`. Blueprints: `blueprints/marti_api/` (TAK-compatible), `blueprints/ots_api/` (OTS REST), `blueprints/cli.py`. Docs: docs.opentakserver.io. |
| Time to first result | Estimate: about 1 h with the installer on a fresh Ubuntu VM to a web map plus one ATAK client (README hackathon note in the index says the same). Docker path not tried. |
| License | GPL-3.0. |

## Minimal usage
Not run.

```bash
curl https://i.opentakserver.io/ubuntu_installer -Ls | bash -
# then: open the web UI served by nginx, create a user, connect ATAK/WinTAK (TLS 8089, cert enrollment)
# quick test feed without certificates, from another shell:
python3 -m pip install pytak
```
Point a [PyTAK](./snstac__pytak.md) script at `tcp://<server>:8088` (plain TCP is enabled by default) and the marker should appear on the web map and on connected clients.

## Wiring it into a nav stack
- Feeds in: own-ship from autopilot telemetry via [PyTAK](./snstac__pytak.md), ADS-B via [readsb](./wiedehopf__readsb.md) + [adsbcot](../../catalog/repos/snstac__adsbcot.md), Remote ID from [receiver-android](./opendroneid__receiver-android.md) or a sniffer, DF bearings from [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) (its start script launches a Kraken-to-TAK service if installed), fused tracks from [Stone Soup](./dstl__stone-soup.md).
- Meshtastic integration (`OTS_ENABLE_MESHTASTIC`, `meshtastic_api.py`) bridges low-bandwidth LoRa mesh nodes into the TAK picture, relevant for comms-degraded scenarios.
- Symbology on the web map is done client-side; for your own web view use [milsymbol](./spatialillusions__milsymbol.md) with [MapLibre](./maplibre__maplibre-gl-js.md) or [Cesium](./cesiumgs__cesium.md).
- Catalog: [OpenTAKServer page](../../catalog/repos/brian7704__opentakserver.md).

## Gotchas
- Open issues on the message path: #438 CoT silently dropped when published from the socket-reader thread (thread-unsafe pika channel), #424 dead EUD connections never cleaned up so messages round-robin to dead sockets, #357 EUDs not generated for ADS-B CoT before insertion. If markers vanish under load, restart services before debugging your feed.
- Docker: #416 images for `ots_cot_parser` / `ots_eud_handler` install from a stale branch rather than the release tag; #15 bcrypt error in Docker. The bare-metal installer is the documented path.
- `curl | bash` installer modifies the host (nginx, RabbitMQ, certs); use a throwaway VM.
- Federation is listed as planned in the README; do not plan a demo on server-to-server federation.
- GPL-3.0.

## Alternatives
- [GoATAK](./kdudkov__goatak.md): single Go binary server plus a web client, fastest to stand up.
- [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md): older Python TAK server.
- [TAK Server](../../catalog/repos/tak-product-center__server.md): the official server, heavier setup.

Sources: `README.md`, repo tree (`blueprints/`), `opentakserver/defaultconfig.py`, KrakenSDR `util/kraken_doa_start.sh` (Kraken-to-TAK hook), releases API, issue search (#438, #424, #416, #357, #15).
