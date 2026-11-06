"""Mixed u-blox UBX + NMEA byte stream => scorer Epochs. Stdlib only.

The VAARA Jammertest 2024 u-blox logs carry NMEA (RMC, GGA, GSA, GSV, GLL) plus UBX RXM-RAWX,
RXM-MEASX, RXM-SFRBX and MON-SPAN, but no UBX NAV-* messages, so the gnss-interference-monitor
pyubx2 adapter (NAV-PVT / NAV-SAT / NAV-CLOCK / MON-RF) has nothing to read. pyubx2 1.4.1 also
raises on a '$' byte inside binary payloads of these files. This module frames both protocols itself
and builds one Epoch per NMEA epoch:

- lat / lon / fix_ok / hdop from GGA (quality > 0) and RMC (status A);
- vel_e / vel_n from RMC speed over ground and course;
- cn0: L1-band signals only (GPS L1 C/A, GLONASS L1OF, Galileo E1, BeiDou B1I, QZSS L1), from GSV
  with NMEA 4.11 signal ids, so a dual-band receiver does not double-count an SV;
- clk_bias_ns / clk_drift_ns_s stay None here; replay.py can merge them from an RTKLIB SPP run.

Time: receiver UTC from RMC/GGA. Under time spoofing that clock jumps, so `t` is a reconstructed
monotonic axis: start at the first valid receiver time, advance by the receiver's own step when
it is within MAX_STEP_S of the nominal elapsed time, else by the nominal period. `rx_t` keeps the raw receiver time.
"""

from __future__ import annotations

import calendar
import math
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gnss-interference-monitor"))
from scorer import Epoch  # noqa: E402

KNOT_MPS = 0.514444
MAX_STEP_S = 5.0  # a larger receiver-time step is treated as a time jump, not elapsed time
NOMINAL_PERIOD_S = 1.0
DECIMATE_SLACK_S = 0.05
L1_SIGNALS = {"GP": "1", "GL": "1", "GA": "7", "GB": "1", "GQ": "1"}  # NMEA 4.11 signal ids (u-blox)
CONST_LETTER = {"GP": "G", "GL": "R", "GA": "E", "GB": "C", "GQ": "J"}
GPS_SBAS_FIRST, GPS_SBAS_LAST = 33, 64  # u-blox puts SBAS PRNs in the GP talker
UBX_SYNC = b"\xb5\x62"


def frames(buf: bytes):
    """Yield ('ubx', cls, msg_id, payload) or ('nmea', sentence_without_checksum) in file order.
    Frames with a bad checksum are skipped byte by byte."""
    i, n = 0, len(buf)
    while i < n:
        b = buf[i]
        if b == 0xB5 and buf[i:i + 2] == UBX_SYNC and i + 8 <= n:
            ln = struct.unpack_from("<H", buf, i + 4)[0]
            end = i + 8 + ln
            if end <= n:
                ck_a = ck_b = 0
                for x in buf[i + 2:i + 6 + ln]:
                    ck_a = (ck_a + x) & 0xFF
                    ck_b = (ck_b + ck_a) & 0xFF
                if buf[end - 2] == ck_a and buf[end - 1] == ck_b:
                    yield "ubx", buf[i + 2], buf[i + 3], buf[i + 6:i + 6 + ln]
                    i = end
                    continue
        elif b == 0x24:  # '$'
            j = buf.find(b"\r\n", i, i + 100)
            if j > 0:
                line = buf[i + 1:j]
                star = line.rfind(b"*")
                if star > 5 and line[:5].isalpha() and line[:5].isupper() and line.isascii() \
                        and _nmea_ok(line[:star], line[star + 1:]):
                    yield "nmea", line[:star].decode("ascii")
                    i = j + 2
                    continue
        i += 1


def _nmea_ok(body: bytes, ck: bytes) -> bool:
    try:
        want = int(ck, 16)
    except ValueError:
        return False
    x = 0
    for c in body:
        x ^= c
    return x == want


def _deg(v: str, hemi: str) -> float | None:
    if not v:
        return None
    dot = v.index(".")
    d = float(v[:dot - 2]) + float(v[dot - 2:]) / 60.0
    return -d if hemi in ("S", "W") else d


def _tod(v: str) -> float | None:
    if len(v) < 6:
        return None
    return int(v[0:2]) * 3600 + int(v[2:4]) * 60 + float(v[4:])


@dataclass
class RawEpoch:
    tod: float | None = None  # receiver UTC seconds of day
    date: str | None = None  # ddmmyy from RMC
    lat: float | None = None
    lon: float | None = None
    fix_quality: int = 0
    rmc_valid: bool = False
    hdop: float | None = None
    sog_mps: float | None = None
    cog_deg: float | None = None
    n_used: int | None = None
    cn0: dict[str, float] = field(default_factory=dict)
    seen: set = field(default_factory=set)


def raw_epochs(buf: bytes):
    """Group NMEA sentences into receiver epochs. A sentence with a different time, or a second
    RMC/GGA, starts a new epoch; GSV/GSA attach to the current one."""
    cur: RawEpoch | None = None
    for kind, *rest in frames(buf):
        if kind != "nmea":
            continue
        s = rest[0]
        f = s.split(",")
        talker, typ = f[0][:2], f[0][2:]
        if typ in ("RMC", "GGA", "GLL"):
            tval = f[1] if typ != "GLL" else (f[5] if len(f) > 5 else "")
            tod = _tod(tval)
            new = cur is None or (typ in cur.seen and typ != "GLL") or (
                tod is not None and cur.tod is not None and tod != cur.tod)
            if new:
                if cur is not None:
                    yield cur
                cur = RawEpoch()
            if cur.tod is None:
                cur.tod = tod
            cur.seen.add(typ)
            if typ == "RMC" and len(f) >= 10:
                cur.rmc_valid = f[2] == "A"
                cur.date = f[9] or None
                if f[7]:
                    cur.sog_mps = float(f[7]) * KNOT_MPS
                if f[8]:
                    cur.cog_deg = float(f[8])
                if cur.lat is None and f[3]:
                    cur.lat, cur.lon = _deg(f[3], f[4]), _deg(f[5], f[6])
            elif typ == "GGA" and len(f) >= 9:
                cur.fix_quality = int(f[6] or 0)
                cur.n_used = int(f[7] or 0)
                cur.hdop = float(f[8]) if f[8] else None
                if f[2]:
                    cur.lat, cur.lon = _deg(f[2], f[3]), _deg(f[4], f[5])
        elif typ == "GSV" and cur is not None and talker in L1_SIGNALS:
            sig = f[-1] if (len(f) - 4) % 4 == 1 else None
            if sig != L1_SIGNALS[talker]:
                continue
            for k in range(4, len(f) - 1, 4):
                svid, cno = f[k], f[k + 3] if k + 3 < len(f) else ""
                if not svid or not cno:
                    continue
                sv = int(svid)
                letter = CONST_LETTER[talker]
                if talker == "GP" and GPS_SBAS_FIRST <= sv <= GPS_SBAS_LAST:
                    continue
                cur.cn0[f"{letter}{sv:02d}"] = float(cno)
    if cur is not None:
        yield cur


def to_epochs(buf: bytes, day_utc: str, period_s: float = NOMINAL_PERIOD_S, decimate_to_s: float | None = 1.0):
    """Yield (Epoch, info) with Epoch.t = reconstructed UTC seconds since the Unix epoch.
    day_utc is the recording date 'YYYY-MM-DD' (first epochs may lack an RMC date).
    info: rx_t (receiver UTC, s since epoch, or None), time_jump_s, n_used, fix_quality."""
    day0 = calendar.timegm(tuple(int(x) for x in day_utc.split("-")) + (0, 0, 0))
    wall = prev_rx = wall_at_rx = last_kept = None
    since_rx = 0  # epochs since the last one with a receiver time
    for r in raw_epochs(buf):
        rx = None
        if r.tod is not None:
            if r.date:
                d = r.date
                rx = calendar.timegm((2000 + int(d[4:6]), int(d[2:4]), int(d[0:2]), 0, 0, 0)) + r.tod
            else:
                rx = day0 + r.tod
        jump = 0.0
        if wall is None:
            if rx is None:
                continue
            wall = rx
        else:
            since_rx += 1
            wall += period_s
            if rx is not None and prev_rx is not None:
                step, expected = rx - prev_rx, since_rx * period_s
                if 0 < step and abs(step - expected) <= MAX_STEP_S:
                    wall = wall_at_rx + step
                else:
                    jump = step - expected
        if rx is not None:
            prev_rx, wall_at_rx, since_rx = rx, wall, 0
        if decimate_to_s and last_kept is not None and wall - last_kept < decimate_to_s - DECIMATE_SLACK_S:
            continue
        last_kept = wall
        fix = r.fix_quality > 0 and r.lat is not None and (r.rmc_valid or "RMC" not in r.seen)
        ve = vn = None
        if fix and r.sog_mps is not None:
            c = math.radians(r.cog_deg or 0.0)
            ve, vn = r.sog_mps * math.sin(c), r.sog_mps * math.cos(c)
        ep = Epoch(t=round(wall, 3), cn0=dict(r.cn0), lat=r.lat if fix else None, lon=r.lon if fix else None,
                   fix_ok=fix, vel_e=ve, vel_n=vn, hdop=r.hdop if fix else None)
        yield ep, {"rx_t": rx, "time_jump_s": jump, "n_used": r.n_used, "fix_quality": r.fix_quality}
