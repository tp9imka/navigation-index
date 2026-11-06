"""Publishers: Cursor-on-Target XML for TAK, MAVLink v1 STATUSTEXT for a GCS, JSONL log.

Each returns the bytes it produced (or None) and hands them to an optional sink, so tests
run without a network and the demo can point at UDP.
"""
from __future__ import annotations

import json
import math
import socket
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, TextIO

from .geo import enu_to_geodetic
from .interfaces import Health, NavState, Verdict

Sink = Callable[[bytes], None]

# 95% radius of an isotropic 2D Gaussian = sqrt(-2 ln 0.05) * sigma
SIGMA_TO_R95 = math.sqrt(-2.0 * math.log(0.05))
COT_UNKNOWN_ERROR_M = 9999999.0
COT_FRIENDLY_UAV = "a-f-A-M-F-Q"
COT_HOW_FUSED = "m-f"              # machine, fused; verify against your TAK consumer
COT_STALE_S = 30

MAVLINK_V1_STX = 0xFE
STATUSTEXT_ID = 253
STATUSTEXT_CRC_EXTRA = 83
STATUSTEXT_TEXT_LEN = 50
MAV_SEVERITY = {Health.TRUSTED: 6, Health.SUSPECT: 4, Health.EXCLUDED: 2, Health.UNAVAILABLE: 3}
STATUS_PREFIX = "NAV"


class UdpSink:
    def __init__(self, host: str, port: int):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __call__(self, data: bytes) -> None:
        self.sock.sendto(data, self.addr)

    def close(self) -> None:
        self.sock.close()


def _cot_time(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class CotPublisher:
    def __init__(self, uid: str, lat0: float, lon0: float, hae: float = 0.0,
                 sink: Optional[Sink] = None, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
        self.uid, self.lat0, self.lon0, self.hae = uid, lat0, lon0, hae
        self.sink, self.clock = sink, clock

    def publish(self, state: NavState, verdict: Verdict) -> Optional[bytes]:
        if math.isnan(state.position.east):
            return None
        lat, lon = enu_to_geodetic(state.position.east, state.position.north, self.lat0, self.lon0)
        ce = SIGMA_TO_R95 * state.sigma_h if math.isfinite(state.sigma_h) else COT_UNKNOWN_ERROR_M
        now = self.clock()
        event = ET.Element("event", {
            "version": "2.0", "type": COT_FRIENDLY_UAV, "uid": self.uid, "how": COT_HOW_FUSED,
            "time": _cot_time(now), "start": _cot_time(now),
            "stale": _cot_time(now + timedelta(seconds=COT_STALE_S)),
        })
        ET.SubElement(event, "point", {"lat": f"{lat:.7f}", "lon": f"{lon:.7f}", "hae": f"{self.hae:.1f}",
                                       "ce": f"{ce:.1f}", "le": f"{COT_UNKNOWN_ERROR_M:.1f}"})
        detail = ET.SubElement(event, "detail")
        ET.SubElement(detail, "contact", {"callsign": self.uid})
        remarks = ET.SubElement(detail, "remarks")
        remarks.text = (f"nav={verdict.health.value} alarm={int(verdict.alarm)} "
                        f"sources={'+'.join(state.sources_used) or 'none'} {verdict.reason}").strip()
        data = ET.tostring(event, encoding="utf-8")
        if self.sink:
            self.sink(data)
        return data


def x25_crc(data: bytes, crc: int = 0xFFFF) -> int:
    for b in data:
        tmp = (b ^ (crc & 0xFF)) & 0xFF
        tmp = (tmp ^ (tmp << 4)) & 0xFF
        crc = ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    return crc


def statustext_v1(text: str, severity: int, seq: int = 0, sysid: int = 1, compid: int = 191) -> bytes:
    payload = struct.pack("<B50s", severity, text.encode("ascii", "replace")[:STATUSTEXT_TEXT_LEN])
    header = struct.pack("<BBBBB", len(payload), seq & 0xFF, sysid, compid, STATUSTEXT_ID)
    crc = x25_crc(header + payload + bytes([STATUSTEXT_CRC_EXTRA]))
    return bytes([MAVLINK_V1_STX]) + header + payload + struct.pack("<H", crc)


class MavlinkStatusPublisher:
    """Sends a STATUSTEXT only when nav health changes, so the GCS is not flooded."""

    def __init__(self, sink: Optional[Sink] = None, sysid: int = 1, compid: int = 191):
        self.sink, self.sysid, self.compid = sink, sysid, compid
        self.last: Optional[Health] = None
        self.seq = 0

    def publish(self, state: NavState, verdict: Verdict) -> Optional[bytes]:
        if verdict.health == self.last:
            return None
        self.last = verdict.health
        text = f"{STATUS_PREFIX}:{verdict.health.value.upper()} sig={state.sigma_h:.1f}m"
        frame = statustext_v1(text, MAV_SEVERITY[verdict.health], self.seq, self.sysid, self.compid)
        self.seq += 1
        if self.sink:
            self.sink(frame)
        return frame


def _num(x: Optional[float]) -> Optional[float]:
    return None if x is None or not math.isfinite(x) else round(x, 4)


class JsonlPublisher:
    """Writes the record format eval/metrics.py reads. Truth is attached by the pipeline."""

    def __init__(self, fh: TextIO):
        self.fh = fh

    def write_meta(self, meta: dict) -> None:
        self.fh.write(json.dumps({"meta": meta}) + "\n")

    def publish(self, state: NavState, verdict: Verdict, truth=None, fix_present: bool = False) -> dict:
        rec = {
            "t": state.t, "east": _num(state.position.east), "north": _num(state.position.north),
            "sigma_h": _num(state.sigma_h),
            "truth_east": _num(truth.east) if truth else None,
            "truth_north": _num(truth.north) if truth else None,
            "health": verdict.health.value, "alarm": verdict.alarm,
            "stat": _num(verdict.statistic), "threshold": _num(verdict.threshold),
            "fix_present": fix_present, "sources": list(state.sources_used),
        }
        self.fh.write(json.dumps(rec) + "\n")
        return rec
