# Signal K Server - integration card
<!-- about: repo:signalk/signalk-server -->
One-line: Node.js hub that ingests NMEA 0183, NMEA 2000 (CAN), AIS and sensors, normalizes everything to one JSON data model in SI units, and serves it over REST and WebSocket - the vessel-side data bus for a maritime demo.

| | |
|---|---|
| Install | Docker (fastest, sample data): `docker run --init -it --rm --name signalk-server --publish 3000:3000 --entrypoint /home/node/signalk/node_modules/.bin/signalk-server cr.signalk.io/signalk/signalk-server --sample-nmea0183-data`. Persistent: `docker run -d --init --name signalk-server -p 3000:3000 -v $(pwd):/home/node/.signalk cr.signalk.io/signalk/signalk-server`. npm (README): `sudo npm install -g signalk-server --allow-scripts=@canboat/canboatjs && sudo signalk-server-setup` - npm `signalk-server` latest 2.36.0, `engines.node >=22`. Also prebuilt RPi images (OpenPlotter, HaLOS, BBN). |
| Runs on | Linux (incl. Raspberry Pi, Victron Cerbo GX Venus OS large), macOS, Windows (separate installer). Docker images: Node 22 on `linux/amd64`, `arm64`, `arm/v7`; Node 24 variant (`-24.x`) drops `arm/v7`. CPU only. |
| Inputs | Data connections configured in the Admin UI: NMEA 0183 over serial/TCP/UDP, NMEA 2000 via SocketCAN or Actisense/YDGW gateways (canboatjs), Signal K deltas from other servers or SensESP devices, raw log playback (`--data file.log`), sample data (`--sample-nmea0183-data`, `--sample-n2k-data`). Plugins add more (BLE, Victron, etc.). |
| Outputs | Signal K full model at `GET /signalk/v1/api/vessels/self/...`; delta stream at `ws://host:3000/signalk/v1/stream?subscribe=self|all|none`; v2 APIs under `/signalk/v2/api/` (course, resources, autopilot, history, notifications); NMEA 0183 over TCP on port 10110 (`NMEA0183PORT`); Signal K deltas over TCP (`TCPSTREAMPORT`); plugins convert back to NMEA 0183/2000. Values are SI: m/s, radians, Kelvin; position as `{latitude, longitude}` in degrees. |
| Key API / entry points | Binaries (`package.json` `bin`): `signalk-server`, `signalk-server-setup`, `signalk-generate-token`; repo `bin/` helpers `nmea-from-file`, `n2k-from-file`. Flags: `-s settings.json`, `-c configdir`, `--sample-nmea0183-data`, `--sample-n2k-data`, `--data <rawfile>`, `--override-timestamps`, `--securityenabled`, `--no-plugins`. Env: `PORT` (3000), `SSLPORT` (3443), `NMEA0183PORT` (10110), `ADMINUSER`, `ALLOW_READONLY`. Plugin API: `app.getSelfPath('navigation.position')`, `app.subscriptionmanager.subscribe(...)`, `app.handleMessage(pluginId, delta)`. |
| Time to first result | Estimate: 5 min to JSON from the Docker sample-data command (Admin UI on http://localhost:3000); 1-2 h to a real NMEA 2000 bus via a CAN adapter. |
| License | Apache-2.0 (LICENSE, npm metadata). Third-party plugins from the App Store carry their own licences. |

## Minimal usage

Not run. Start the Docker sample-data server (above), then:

```bash
curl -s http://localhost:3000/signalk/v1/api/vessels/self/navigation/position
```

```python
import asyncio, json, websockets   # pip install websockets

async def main():
    async with websockets.connect("ws://localhost:3000/signalk/v1/stream?subscribe=self") as ws:
        async for raw in ws:
            d = json.loads(raw)
            for u in d.get("updates", []):
                for v in u.get("values", []):
                    if v["path"] in ("navigation.position", "navigation.speedOverGround", "navigation.courseOverGroundTrue"):
                        print(v["path"], v["value"])   # SOG in m/s, COG in radians

asyncio.run(main())
```

## Wiring it into a nav stack

- Sensor side: GNSS (NMEA 0183 or N2K), heading, depth, wind => Signal K. AIS from [AIS-catcher](./jvde-github__ais-catcher.md) as an NMEA 0183 UDP/TCP connection lands in `vessels.<mmsi>` next to own ship. NMEA 2000 PGN decoding is canboat-based ([canboat](../../catalog/repos/canboat__canboat.md)).
- Consumer side: your fusion or anomaly detector subscribes to the WebSocket deltas; [OpenCPN](../../catalog/repos/opencpn__opencpn.md) and phone chart apps read the NMEA 0183 TCP output on 10110; a [MapLibre](./maplibre__maplibre-gl-js.md) view can subscribe directly from the browser.
- Writing results back: a plugin calls `app.handleMessage` to publish derived values (e.g. a GNSS integrity flag or an alternative-nav position under its own `$source`), which then flow to every client. Multiple sources per path are kept apart by `$source` (spec "multiple values").
- Bridge to robotics stacks: no built-in MAVLink or ROS bridge in this repo; use the WebSocket from a small Python node ([pymavlink](./ardupilot__pymavlink.md), rosbridge) - or [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) via the NMEA 0183 TCP output.
- Data model reference: [signalk/specification](../../catalog/repos/signalk__specification.md); NMEA 0183 output plugin: [signalk-to-nmea0183](../../catalog/repos/signalk__signalk-to-nmea0183.md).

Catalog page: [catalog/repos/signalk__signalk-server.md](../../catalog/repos/signalk__signalk-server.md). Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [sensor-fusion](../../catalog/concepts/sensor-fusion.md), [situational-awareness](../../catalog/concepts/situational-awareness.md).

## Gotchas

- SI units everywhere: speeds in m/s and angles in radians, not knots and degrees (spec `data_model.md`). Position is the exception, in degrees.
- Security is off unless enabled: the Docker quickstart runs without it; `--securityenabled` (or the setup script) forces an admin account. Do not expose an unsecured server on a shared hackathon network. With security on, unauthenticated read needs `ALLOW_READONLY`.
- Most config changes and App Store installs need a server restart; the Restart button only appears once an admin user exists (README).
- App Store needs Internet to list plugins; offline demos must pre-install plugins.
- Global npm install as root is the README path; prefer Docker to keep the host clean. Node >=22 required.
- Open N2K issues: intermittent ~4 s data loss and address-claim storms (#2877), reconnect after a CAN interface drops (#2821). Playback connections cannot subscribe to contexts other than self (#3043).
- Docker docs acknowledged as needing an overhaul (#2210); persist `/home/node/.signalk` or you lose config on container removal.

## Alternatives

- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) - chartplotter that reads NMEA/AIS directly; prefer when you only need a display, not a data API.
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - GNSS-only daemon with JSON output; prefer on a land or air vehicle with just a GNSS receiver.
- [canboat](../../catalog/repos/canboat__canboat.md) - raw NMEA 2000 analysis; prefer for PGN reverse-engineering without a server.

Sources: `gh api repos/SignalK/signalk-server` (Apache-2.0, release v2.36.0 2026-11-03), npm registry `signalk-server` (2.36.0), README.md, LICENSE, package.json (`bin`, `engines`), bin/signalk-server, bin/nmea-from-file, docker/README.md, docs/installation/command_line.md, docs/security.md, docs/develop/plugins/deltas.md, docs/develop/rest-api/README.md; signalk/specification mdbook/src/streaming_api.md, rest_api.md, data_model.md; issues #2210, #2821, #2877, #3043.
