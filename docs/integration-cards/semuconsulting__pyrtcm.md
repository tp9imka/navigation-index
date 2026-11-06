# pyrtcm - integration card
<!-- about: repo:semuconsulting/pyrtcm -->
One-line: pure-Python RTCM3 parser and serializer - decode NTRIP or base-station correction streams into named data fields (MSM observables, 1005 base position, ephemerides, SSR) for RTK plumbing and correction-stream sanity checks.

| | |
|---|---|
| Install | `python3 -m pip install --upgrade pyrtcm` (PyPI `pyrtcm` 1.2.1, `requires_python >=3.10`, only dependency `pynmeagps>=1.1.8`). Also `conda install -c conda-forge pyrtcm`. |
| Runs on | Any OS with Python 3.10+; pure Python, no compiled extensions, no GPU. |
| Inputs | Any stream with `read(n) -> bytes`: file, pyserial port, socket (via `pynmeagps.SocketWrapper`, re-exported). Single messages as bytes for `RTCMReader.parse()`. |
| Outputs | `RTCMMessage` objects with attributes named after RTCM data fields (`DF002`, `DF025`, `DF404_07`, ...), already scaled (e.g. `DF012` scale 0.0001); repeating groups get `_01`, `_02` suffixes. `serialize()` back to framed bytes with CRC-24Q. |
| Key API / entry points | `RTCMReader(datastream, validate=VALCKSUM, quitonerror=ERR_LOG, labelmsm=1, bufsize=4096, parsed=PARSE_FULL, errorhandler=None, encoding=ENCODE_NONE, msgfilter="")` - iterator yielding `(raw, parsed)`; `RTCMReader.parse(message, validate=VALCKSUM, labelmsm=1)`; `RTCMMessage(payload=...)` with `.identity`, `.payload`, `.ismsm`, `.serialize()`; helpers `parse_msm(msg) -> (meta, sat_array, cell_array)`, `parse_4076_201(msg)` (SSR harmonic coefficients), `datadesc("DF012")`, `RTCM_DATA_FIELDS`, `calc_crc24q`; `ecef2llh` / `llh2ecef` (from pynmeagps). No console script of its own; the CLI is `gnssstreamer` in [pygnssutils](./semuconsulting__pygnssutils.md). |
| Time to first result | Estimate: 10 min to print decoded 1005/1077 messages from a public caster using the bundled `examples/rtcm_ntrip_client.py` or `gnssntripclient`. Assumes network access and caster credentials. |
| License | BSD-3-Clause (LICENSE, pyproject.toml). Note: the RTCM 10403.x standard itself is a paid document; pyrtcm is an independent implementation (README). |

## Minimal usage
Not run. Adapted from README examples A-C and the MSM helpers.

```python
from pyrtcm import RTCMReader, ERR_LOG, parse_msm, ecef2llh

with open("rtcm_capture.bin", "rb") as stream:          # or a Serial / socket stream
    for raw, msg in RTCMReader(stream, quitonerror=ERR_LOG, labelmsm=1):
        if msg is None:
            continue
        if msg.identity in ("1005", "1006"):              # base station ARP, ECEF metres
            print("base", ecef2llh(msg.DF025, msg.DF026, msg.DF027))
        elif msg.ismsm:
            meta, sats, cells = parse_msm(msg)
            print(msg.identity, meta.get("gnss"), len(sats), "sats", len(cells), "cells")
```

`parse_msm` returns `meta` with keys `identity`, `gnss`, `station`, `epoch`, `sats`, `cells`; each sat dict holds `PRN`, `DF397`-`DF399`, `DF419`, `ExtSatInfo` where present; each cell dict holds `CELLPRN`, `CELLSIG`, `DF400`-`DF408`, `DF420` where present (`rtcmhelpers.py`). Use `datadesc("DF408")` to confirm what a field means.

## Wiring it into a nav stack
- Correction path: caster => [pygnssutils](./semuconsulting__pygnssutils.md) `gnssntripclient` => receiver. pyrtcm sits in that path when you need to inspect, filter or log what is being injected; the receiver (u-blox, see [pyubx2](./semuconsulting__pyubx2.md)) or [RTKLIB](./rtklibexplorer__rtklib.md) does the RTK solution.
- Correction integrity check (defensive): track the 1005/1006 base position and MSM signal counts per epoch; a jump in base ARP or a sudden change in tracked satellites from a fixed base is a cheap flag for a swapped or spoofed correction source before it reaches the autopilot.
- Base-station QC: MSM cells carry per-signal CNR and lock-time fields (check which DF via `datadesc`); trend them at the base to see local interference before rovers degrade.
- Autopilots: RTCM from pyrtcm `serialize()` can be wrapped in MAVLink `GPS_RTCM_DATA` with [pymavlink](./ardupilot__pymavlink.md) (what [Rpanion-server](./stephendade__rpanion-server.md) does in Node.js).
- GUI view of the same stream: [PyGPSClient](./semuconsulting__pygpsclient.md).
- Concepts: [gnss](../../catalog/concepts/gnss.md), [gnss-rtk-ppp](../../catalog/concepts/gnss-rtk-ppp.md), [standards](../../catalog/concepts/standards.md). Catalog page: [catalog/repos/semuconsulting__pyrtcm.md](../../catalog/repos/semuconsulting__pyrtcm.md).

## Gotchas
- `RTCMReader.read()` silently discards every byte that is not an RTCM3 preamble (0xD3), so a mixed UBX/NMEA/RTCM stream "works" but drops the other protocols. Use `GNSSReader` from pygnssutils, or pyubx2 with RTCM enabled, for mixed streams.
- Only message types in `RTCM_MSGIDS` (`rtcmtypes_core.py`) are decoded; proprietary types raised KeyError in older versions (#33, #10, closed). Default `ERR_LOG` keeps going; `ERR_RAISE` stops the iterator on the first bad frame.
- MSM parsing bugs when the signal set differs per satellite were fixed (#21, #27, closed); BeiDou signal map and BDS TGD scale errors fixed in #85 and #89 (closed). Pin >= 1.2.1 if you compare against RTKLIB.
- `labelmsm=1` gives RINEX codes (`1C`, `2W`), `labelmsm=2` gives band names (`L1`, `L2`); pick one before writing downstream code.
- Corrupt or zero-length frames: #82 and #91 (closed) changed how short payloads are treated; use `validate=VALCKSUM` (default) on radio links.
- `RTCMMessage` objects are immutable once created (README); build a new one from a payload to modify.

## Alternatives
- [RTKLIB](./rtklibexplorer__rtklib.md) (`str2str`, `convbin`) - C, decodes and converts RTCM to RINEX and computes RTK/PPP; prefer when you need a solution, not just fields.
- [go-gnss/ntrip](../../catalog/repos/go-gnss__ntrip.md) - Go NTRIP client/caster when the correction server should be a single binary.
- [pygnssutils](./semuconsulting__pygnssutils.md) - wraps pyrtcm with NTRIP, socket server and CLI; prefer for anything beyond parsing.

Sources: PyPI JSON for `pyrtcm` (1.2.1, >=3.10, requires `pynmeagps>=1.1.8`), `gh api repos/semuconsulting/pyrtcm` (BSD-3-Clause, v1.2.1 2026-10-19), pyproject.toml, LICENSE, README.md (reading, parsing, generating, examples, extensibility), src/pyrtcm/__init__.py (exports), src/pyrtcm/rtcmreader.py (constructor signature, 0xD3 sync), src/pyrtcm/rtcmhelpers.py (`parse_msm`, `parse_4076_201`), issues #10, #21, #27, #33, #82, #85, #89, #91.
