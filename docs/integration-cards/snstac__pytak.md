# PyTAK - integration card
<!-- about: repo:snstac/pytak -->
One-line: pure-Python asyncio library and CLI for sending and receiving Cursor on Target (CoT) over TCP, TLS, UDP multicast, WebSockets or the Marti REST API; the lowest-friction way to put your vehicle position, a DF bearing line or a Remote ID detection on an ATAK/WinTAK/iTAK map.

| | |
|---|---|
| Install | `python3 -m pip install pytak` (latest release seen v7.6.1, 2026-08-23). Optional extras for TLS enrollment and Protobuf (`takproto`). |
| Runs on | Any OS with Python 3 asyncio; no required external deps for the core (README). Runs fine on a Raspberry Pi. |
| Inputs | Your data turned into CoT XML (`<event>` with `type`, `uid`, `how`, `time/start/stale`, `<point lat lon hae ce le>`). Config via `ConfigParser` section or env: `COT_URL` (`tcp://`, `tls://`, `udp://`, `udp+wo://` write-only multicast, `ws://`, `marti://`, `tak://` onboarding URL), `TAK_PROTO` (0 XML, 1 Protobuf), cert paths. |
| Outputs | CoT on the network; received CoT handed to an `RXWorker`. CLI `pytak dp ...` writes ATAK/iTAK onboarding data packages. |
| Key API / entry points | `pytak.CLITool(config)` with `await setup()`, `add_tasks({...})`, `await run()`; `pytak.QueueWorker` subclass with `async def run(self)` and `await self.put_queue(data)`; `pytak.TXWorker`, `pytak.RXWorker`; helpers `pytak.cot_time(cot_stale=None)`, `pytak.gen_cot(lat, lon, ce, hae, le, uid, stale, cot_type, callsign)`, `pytak.gen_cot_xml(...)`, `pytak.cot_event(...)`, `pytak.hello_event()`. Defaults (`constants.py`): `DEFAULT_COT_URL = "udp+wo://239.2.3.1:6969"` (ATAK SA multicast), `DEFAULT_COT_STALE = "120"`, `DEFAULT_TAK_PROTO = "0"`. |
| Time to first result | Estimate: 15-30 min to see a marker from a script on an ATAK/WinTAK device on the same LAN via multicast, or on an OpenTAKServer web map. Assumes a TAK client or server already reachable. |
| License | Apache-2.0. |

## Minimal usage
Adapted from the README quick example; sends own-ship position from a MAVLink vehicle every 2 s. Not run.

```python
import asyncio, pytak
from configparser import ConfigParser
from pymavlink import mavutil

class OwnShip(pytak.QueueWorker):
    async def run(self):
        m = mavutil.mavlink_connection("udpin:0.0.0.0:14551")
        while True:
            g = m.recv_match(type="GLOBAL_POSITION_INT", blocking=False)
            if g:
                cot = pytak.gen_cot(lat=g.lat / 1e7, lon=g.lon / 1e7, hae=g.alt / 1e3,
                                    ce=10, le=10, uid="uav-1", stale=30,
                                    cot_type="a-f-A-M-F-Q", callsign="UAV1")
                await self.put_queue(cot)
            await asyncio.sleep(2)

async def main():
    cfg = ConfigParser(); cfg["uav"] = {"COT_URL": "tcp://127.0.0.1:8088"}
    tool = pytak.CLITool(cfg["uav"]); await tool.setup()
    tool.add_tasks({OwnShip(tool.tx_queue, cfg["uav"])})
    await tool.run()

asyncio.run(main())
```
`a-f-A-M-F-Q` is the CoT type for a friendly military fixed-wing/UAV-class air track as commonly used; choose the type that matches your symbol (MIL-STD-2525 mapping, see [milsymbol](./spatialillusions__milsymbol.md)).

## Wiring it into a nav stack
- Own-ship from autopilot telemetry: [pymavlink](./ardupilot__pymavlink.md) or [MAVSDK-Python](./mavlink__mavsdk-python.md) => PyTAK => TAK server ([OpenTAKServer](./brian7704__opentakserver.md), [GoATAK](./kdudkov__goatak.md)) or straight to multicast for ATAK on the LAN.
- Air picture: [readsb](./wiedehopf__readsb.md) JSON => [adsbcot](../../catalog/repos/snstac__adsbcot.md) (same author, built on PyTAK). Remote ID: [receiver-android](./opendroneid__receiver-android.md) or a WiFi/BLE sniffer => CoT. DF: [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) bearings => CoT line/marker, or fused tracks from [Stone Soup](./dstl__stone-soup.md).
- Use `ce`/`le` (circular/linear error, metres) honestly: put the estimator's 1-sigma or 95% radius there so the TAK user sees nav uncertainty, which is the PNT story in a demo.
- Protobuf encoding via [takproto](../../catalog/repos/snstac__takproto.md).
- Catalog: [PyTAK page](../../catalog/repos/snstac__pytak.md).

## Gotchas
- Default URL is write-only multicast (`udp+wo://239.2.3.1:6969`); many hackathon Wi-Fi networks and Docker bridges drop multicast. Use `tcp://` to a server if markers do not appear.
- Stale time: CoT disappears after `stale`; a too-short stale with a slow loop makes markers blink.
- TLS: open issues #74 (`NoneType` has no `private_bytes`), #101 (cert cache gaps after #100), closed #116 (cert and key in one file). Test enrollment early; plain TCP to a local server is the fallback.

## Alternatives
- [node-cot](../../catalog/repos/dfpc-coe__node-cot.md) for a JavaScript/TypeScript stack.
- [cotlib](../../catalog/repos/nervsystems__cotlib.md) for Go.
- Writing raw CoT XML over a socket is possible but you lose enrollment, TLS and protobuf handling.

Sources: `README.md`, `src/pytak/functions.py` (signatures), `src/pytak/classes.py` (worker classes), `src/pytak/__init__.py` (exports), `src/pytak/constants.py` (defaults), releases API, issue search (#74, #101, #116).
