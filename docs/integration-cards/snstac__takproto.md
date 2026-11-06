# takproto - integration card
<!-- about: repo:snstac/takproto -->
One-line: small Python library that turns CoT XML into TAK Protocol Version 1 protobuf (Mesh/UDP or Stream/TCP framing) and parses protobuf back into a `TakMessage` object; what PyTAK uses under `TAK_PROTO=1`, and what you need to read protobuf traffic from modern ATAK/TAK Server.

| | |
|---|---|
| Install | `python3 -m pip install takproto` (latest release v3.0.1, 2024-08-30; `__version__ = "3.0.1"` in `takproto/__init__.py`). Also a `.deb` from releases: `wget https://github.com/snstac/takproto/releases/latest/download/takproto_latest_all.deb && sudo apt install -f ./takproto_latest_all.deb`. |
| Runs on | Any OS with Python 3 (docs say 3.6+); single dependency `protobuf >= 4.21.0` (`setup.cfg`). Generated `_pb2` modules are committed, so `protoc` is not needed. |
| Inputs | Encode: CoT XML as `str`/`bytes` (`<event>` with `<point>` and optional `<detail>`). Decode: one framed TAK message as `bytearray`, starting with `0xbf 0x01 0xbf` (Mesh) or `0xbf <varint length>` (Stream); plain XML starting `<?xml` is also accepted and converted. |
| Outputs | `bytearray` with header + protobuf payload; or a `TakMessage` (`takproto.proto`) with `.takControl` and `.cotEvent` (`type`, `uid`, `sendTime`/`startTime`/`staleTime` in ms, `how`, `lat`, `lon`, `hae`, `ce`, `le`, `.detail.contact/.group/.precisionLocation/.status/.takv/.track/.xmlDetail`). |
| Key API / entry points | Exports (`takproto/__init__.py`): `xml2proto(xml: str, protover: Optional[TAKProtoVer] = None)` (default Mesh), `parse_proto(msg: bytearray) -> Optional[TakMessage]` (dispatches on header), `parse_mesh(msg)`, `parse_stream(msg) -> TakMessage`, `format_time(time: str) -> int` (ms since epoch), enum `TAKProtoVer.XML=0 / MESH=1 / STREAM=2`. Not exported but in `takproto.functions`: `xml2message(xml) -> TakMessage`, `msg2proto(msg, protover=None) -> bytearray`. Header constants in `constants.py`: `DEFAULT_MESH_HEADER = b"\xbf\x01\xbf"`, `DEFAULT_PROTO_HEADER = b"\xbf"`. |
| Time to first result | Estimate: 5-10 min to round-trip a CoT XML string through `xml2proto` and `parse_proto` in a Python shell. Assumes pip access; no TAK device needed for that step. |
| License | MIT (GitHub metadata). `delimited_protobuf.py` is Apache-2.0; the bundled `.proto` sources in `src-protobuf/` carry a GPL-3.0 `LICENSE.md` (from ATAK-CIV). |

## Minimal usage
Adapted from `docs/usage.md`. Not run.

```python
import takproto
from takproto import TAKProtoVer

cot = b"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<event version='2.0' uid='drone-ABC123' type='a-u-A-M-H-R' how='m-g'
 time='2026-11-06T10:00:00.000Z' start='2026-11-06T10:00:00.000Z' stale='2026-11-06T10:01:00.000Z'>
 <point lat='42.3601' lon='-71.0589' hae='120' ce='15' le='10'/>
 <detail><contact callsign='RID ABC123'/><track course='90' speed='8'/></detail>
</event>"""

mesh = takproto.xml2proto(cot)                      # UDP multicast (Mesh SA), b'\xbf\x01\xbf...'
stream = takproto.xml2proto(cot, TAKProtoVer.STREAM)  # TCP to TAK Server, varint length-delimited

msg = takproto.parse_proto(mesh)
print(msg.cotEvent.uid, msg.cotEvent.lat, msg.cotEvent.detail.contact.callsign)
```
In practice set `TAK_PROTO=1` in [PyTAK](./snstac__pytak.md) and let it call takproto for you.

## Wiring it into a nav stack
- Encoding layer under every Python CoT producer in the index: [PyTAK](./snstac__pytak.md) => [ADSBCOT](./snstac__adsbcot.md), Remote ID bridges, [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) bearing bridges.
- Decode side: a Python listener on the ATAK SA multicast group (239.2.3.1:6969) or a TAK server stream can `parse_proto` each datagram/frame to log friendly positions or feed them to a fusion node ([Stone Soup](./dstl__stone-soup.md)).
- Server side: [OpenTAKServer](./brian7704__opentakserver.md), [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md), [TAK Server](../../catalog/repos/tak-product-center__server.md) accept both XML and protobuf; [ATAK-CIV](../../catalog/repos/tak-product-center__atak-civ.md) is where the `.proto` files and `protocol.txt` come from.
- Catalog: [takproto page](../../catalog/repos/snstac__takproto.md).

## Gotchas
- No protobuf => XML function. `parse_proto` returns a protobuf object; if a downstream tool needs CoT XML you rebuild it yourself.
- Protobuf `detail` holds only `contact`, `__group`, `precisionlocation`, `status`, `takv`, `track` as typed fields; everything else (your custom sensor tags, `remarks`, `__adsb`, Remote ID extras) is stringified into `xmlDetail` (`xml2message`). Consumers that only read typed fields will miss them. Open #5: CoT detail extensions in protocol v1.
- `parse_proto` decodes one message. On a TCP stream you must split frames yourself (Stream is `0xbf` + varint length + payload); `parse_stream` reads only the first.
- Streaming to a TAK server is not protobuf from byte one: `src-protobuf/protocol.txt` describes a negotiation starting in XML. Use PyTAK or plain XML unless you implement that handshake.
- `docs/usage.md` calls `parse_proto(pb)` without the `takproto.` prefix; import it explicitly.
- `__init__.py` wraps imports in `try/except ImportError` and only warns; a broken protobuf install shows up later as `AttributeError: module 'takproto' has no attribute 'xml2proto'` (closed #14 asked to stop swallowing it, code still does).
- Licensing: package MIT, but the `.proto` schema sources are under GPL-3.0 (`src-protobuf/LICENSE.md`). Check with your counsel before shipping the generated `_pb2` code in a closed product; fine for a hackathon.
- No release since 2024-08; repo still receives pushes (2026-11-02).

## Alternatives
- [node-cot](../../catalog/repos/dfpc-coe__node-cot.md) for JavaScript/TypeScript, which also does GeoJSON conversion and protobuf.
- [cotlib](../../catalog/repos/nervsystems__cotlib.md) for Go.
- Stay on XML CoT (PyTAK default `TAK_PROTO=0`): every TAK client must still decode version 0 (`protocol.txt`), so protobuf is an optimisation, not a requirement.

Sources: `README.md`, `docs/usage.md`, `docs/installation.md`, `setup.cfg`, `takproto/__init__.py` (exports), `takproto/functions.py` (signatures, framing, detail mapping), `takproto/constants.py`, `src-protobuf/LICENSE.md`, `src-protobuf/protocol.txt`, repo metadata and releases API, issue search (#5, #14).
