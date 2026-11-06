# GoATAK - integration card
<!-- about: repo:kdudkov/goatak -->
One-line: Go TAK server / CoT router plus a browser-based TAK client (Leaflet + milsymbol); one Docker command gives judges a live map without anyone installing ATAK.

| | |
|---|---|
| Install | Docker (README): `docker run -p 8088:8088 -p 8080:8080 -p 8999:8999 ghcr.io/kdudkov/goatak_server:latest`. Or release binaries (latest seen v0.23.0, 2025-08-06), or `go build` of `cmd/goatak_server` and `cmd/webclient`. |
| Runs on | Anywhere Go or Docker runs (Linux, macOS, Windows, ARM SBCs). |
| Inputs | CoT v1 XML and v2 protobuf over TCP and UDP (`tcp_addr`/`udp_addr` default `:8999` in `goatak_server.yml`), TLS for ATAK on `tls_addr` `:8089`, Marti API on `api_addr` `:8080`, cert enrollment on `cert_addr` `:8446`. |
| Outputs | Routed CoT to clients within the same visibility scope, admin web UI on `admin_addr` `:8088`, optional CoT log files (convertible to JSON or GPX with the bundled CLI), mission packages/datasync basics. |
| Key API / entry points | `cmd/goatak_server` (config `goatak_server.yml`: `admin_addr`, `api_addr`, `cert_addr`, `tcp_addr`, `udp_addr`, `tls_addr`, `log`, `data_dir`, `webtak_root`, `welcome_msg`, `me`), `cmd/webclient` (config `goatak_client.yml`), `cmd/takreplay` (reads logged CoT; has broadcast, contacts, stats and dump modes per its source file names), `cmd/mm` (separate CLI with an API client; purpose not checked). |
| Time to first result | Estimate: 10 min with Docker to see a PyTAK marker on the admin map. Assumes Docker installed. |
| License | AGPL-3.0. |

## Minimal usage
Not run.

```bash
docker run -p 8088:8088 -p 8080:8080 -p 8999:8999 ghcr.io/kdudkov/goatak_server:latest
# feed: PyTAK script with COT_URL=tcp://127.0.0.1:8999
# view: http://127.0.0.1:8088  (admin UI with map)
```
For a richer operator view run the `webclient` against the server (README: "ideal for big screen situation awareness center usage").

## Wiring it into a nav stack
- Same feeds as any TAK server: [PyTAK](./snstac__pytak.md) scripts for own-ship and detections, [adsbcot](../../catalog/repos/snstac__adsbcot.md) + [readsb](./wiedehopf__readsb.md) for air traffic, DF and Remote ID detections as markers.
- `takreplay` plus logged CoT gives a reproducible demo replay; CoT logs export to GPX for comparison against a ground-truth track with [evo](./michaelgrupp__evo.md) after conversion.
- Web client draws with [milsymbol](./spatialillusions__milsymbol.md) on Leaflet.
- Catalog: [GoATAK page](../../catalog/repos/kdudkov__goatak.md).

## Gotchas
- AGPL-3.0: running a modified server for others over a network obliges you to offer source.
- The README advertises a free public TAK server run by the author with shared test credentials. For any defence-flavoured demo keep traffic on your own instance; do not send positions or detections to a third-party public server.
- GitHub issues are disabled on the repo (`has_issues: false`); support is via a Telegram chat per README, so expect to read code for answers.
- Docker example maps 8999 TCP only; add `-p 8999:8999/udp` if you send UDP CoT.

## Alternatives
- [OpenTAKServer](./brian7704__opentakserver.md): more features (video, LDAP, Meshtastic, data sync), heavier install.
- [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md), [TAK Server](../../catalog/repos/tak-product-center__server.md).
- [CloudTAK](../../catalog/repos/dfpc-coe__cloudtak.md) for a browser TAK client against an existing server.

Sources: `README.md`, `goatak_server.yml`, repo tree (`cmd/`), releases API, issue search (0 results).
