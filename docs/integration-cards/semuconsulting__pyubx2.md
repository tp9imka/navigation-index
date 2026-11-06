# pyubx2 - integration card
<!-- about: repo:semuconsulting/pyubx2 -->
Pure-Python reader/writer for u-blox UBX (plus NMEA and RTCM3 via sister libs): the fastest way to get PVT, raw measurements and the receiver's own jamming/spoofing flags out of a u-blox module or log file.

| | |
|---|---|
| Install | `python3 -m pip install --upgrade pyubx2` (latest GitHub release v1.4.1; `requires-python >=3.10`; deps `pynmeagps>=1.1.8`, `pyrtcm>=1.2.1`). Add `pyserial` for live ports. |
| Runs on | Any OS with Python 3.10+, pure Python, no GPU. Fine on Raspberry Pi / Jetson. |
| Inputs | Byte stream with a `read(n)` method: serial port, socket, or binary log opened `rb` (`.ubx` from u-center, PyGPSClient, `gnssstreamer`). UBX, NMEA 0183, RTCM3 mixed in one stream. |
| Outputs | `(raw_bytes, parsed)` tuples; `UBXMessage` objects with scaled attributes (e.g. NAV-PVT `lat`/`lon` in deg, `hMSL` in mm). Repeating groups flattened with 2-digit suffixes (`jamInd_01`, `cno_05`). Outbound: serialized UBX commands (`msg.serialize()`). |
| Key API / entry points | `UBXReader(stream, protfilter=NMEA_PROTOCOL\|UBX_PROTOCOL\|RTCM3_PROTOCOL, quitonerror=ERR_LOG, validate=VALCKSUM, msgmode=GET)`; `UBXReader.read() -> (bytes, msg)`; `UBXReader.parse(data, msgmode=GET)` (static); `UBXMessage(ubxClass, ubxID, mode, **kwargs)`; `UBXMessage.config_set(layers, transaction, cfgData)` / `config_del` / `config_poll` (Gen9+ CFG-VALSET/VALGET); helpers `ecef2llh`, `llh2ecef`, `haversine`, `utc2wnotow`. |
| Time to first result | Estimate: 10 min to print NAV-PVT from a USB-connected F9P/M10 or a recorded `.ubx` file; assumes the needed messages are already enabled on the receiver. |
| License | BSD-3-Clause |

## Minimal usage
Not run. Live interference telemetry from a u-blox Gen9+ receiver (message and field names checked against `src/pyubx2/ubxtypes_get.py`):

```python
from serial import Serial
from pyubx2 import UBXReader, UBXMessage, UBX_PROTOCOL, SET_LAYER_RAM, TXN_NONE

with Serial("/dev/ttyACM0", 38400, timeout=3) as s:
    cfg = [("CFG_MSGOUT_UBX_MON_RF_USB", 1), ("CFG_MSGOUT_UBX_NAV_STATUS_USB", 1),
           ("CFG_MSGOUT_UBX_NAV_PVT_USB", 1)]
    s.write(UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfg).serialize())
    for raw, msg in UBXReader(s, protfilter=UBX_PROTOCOL):
        if msg.identity == "MON-RF":
            print("jam", msg.jammingState_01, "cw", msg.jamInd_01, "agc", msg.agcCnt_01)
        elif msg.identity == "NAV-STATUS":
            print("spoofDetState", msg.spoofDetState)
        elif msg.identity == "NAV-PVT":
            print(msg.lat, msg.lon, msg.fixType, msg.numSV)
```

The `CFG_MSGOUT_UBX_*_USB` keys used above exist in `UBX_CONFIG_DATABASE` (`ubxtypes_configdb.py`, checked); swap `_USB` for `_UART1` if the receiver is on a UART. Add `CFG_MSGOUT_UBX_SEC_SIG_USB` and `CFG_MSGOUT_UBX_RXM_SFRBX_USB` for SEC-SIG and OSNMA input.

## Wiring it into a nav stack
- Telemetry source for the interference monitor sample: [samples/gnss-interference-monitor](../../samples/gnss-interference-monitor/) already parses NAV-PVT, NAV-SAT, NAV-STATUS, MON-RF and SEC-SIG with pyubx2 and scores epochs.
- Raw measurements: enable RXM-RAWX + RXM-SFRBX, log with [pygnssutils](./semuconsulting__pygnssutils.md) `gnssstreamer`, convert to RINEX, then post-process with [RTKLIB](./rtklibexplorer__rtklib.md) or [gnss_lib_py](./stanford-navlab__gnss_lib_py.md).
- Authentication: RXM-SFRBX (Galileo I/NAV pages) is the input to [OSNMAlib](./algafix__osnma.md).
- Fusion: NAV-PVT position/velocity plus `hAcc`/`vAcc` feed a loosely coupled filter ([filterpy](./rlabbe__filterpy.md), [robot_localization](./cra-ros-pkg__robot_localization.md) via a NavSatFix bridge, [GTSAM](./borglab__gtsam.md) GPSFactor). Convert to a local frame with [pymap3d](./geospace-code__pymap3d.md).
- For ROS, a C++ driver is usually simpler: see [kumarrobotics/ublox](../../catalog/repos/kumarrobotics__ublox.md).

## Gotchas
- Factory UART baud is 38400, not 9600 (README troubleshooting). `Unknown Protocol` errors usually mean wrong baud or a second process (gpsd) on the port.
- Linux: user must be in `dialout` (Debian) / `uucp` (Arch).
- Legacy CFG-MSG/CFG-PRT are deprecated on Gen9 and removed on Gen10 (X20); use `config_set`.
- MON-RF and SEC-SIG field layouts changed over time: issue #216 (MON-RF decoding on ZED-F9R HPS 1.30), #186 (SEC-SIG repeated group), #122 (jammingState width). Pin a recent version and check firmware.
- SEC-SIG has two variants (`SEC-SIG-V1`, `SEC-SIG-V2`); code must handle both attribute sets.
- `spoofDetState` and `jammingState` are the receiver's heuristic verdicts, not ground truth; the flags exist only on firmware that implements them (not stated per model in the README).
- u-center recordings include undocumented DBG/TRK/SEC messages; answer "No" to adding receiver config when recording.

## Alternatives
- [pygnssutils](./semuconsulting__pygnssutils.md) - wraps pyubx2 with CLI streaming, NTRIP and multi-protocol reading; prefer it when you want no code.
- [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md) - GUI on the same stack for interactive receiver config and spectrum (MON-SPAN) view.
- [kumarrobotics/ublox](../../catalog/repos/kumarrobotics__ublox.md) - ROS driver when everything else is ROS.

Sources: `gh api repos/semuconsulting/pyubx2/readme`, `src/pyubx2/ubxtypes_configdb.py` (CFG_MSGOUT keys), `src/pyubx2/ubxtypes_get.py` (MON-RF, NAV-STATUS, SEC-SIG definitions), `pyproject.toml`, releases/latest, issue search (jamming/spoof/MON-RF).
