"""Ephemeris consistency: receiver-decoded GPS LNAV ephemerides vs an independent broadcast source. Stdlib only.

A spoofer transmits its own navigation data. When it is not a copy of the live broadcast, the
receiver decodes ephemerides that disagree with what the real satellites send, and anything that
post-processes the logged navigation data (RTKLIB `convbin -n`) inherits them. This module:

- decodes GPS L1 C/A subframes 1-3 from u-blox UBX-RXM-SFRBX payloads (24 data bits per 30-bit
  word, parity checked; a full set needs matching IODC/IODE across the three subframes);
- parses GPS records from a RINEX 3 navigation file (e.g. the IGS BRDC merge, `.rnx` or `.rnx.gz`);
- computes each decoded ephemeris' satellite position and clock at the evaluation time and the
  same from the reference record (same IODE when available, else the nearest toe), and reports
  the larger of the orbit and clock disagreement in metres per SV.

No reference record for an SV, or no decoded set yet, means "not measured": the SV is absent from
the result, never reported as consistent. Feed the result as `Epoch.eph_mismatch_m`.
"""

from __future__ import annotations

import calendar
import gzip
import math
import struct
from pathlib import Path

GPS_EPOCH = calendar.timegm((1980, 1, 6, 0, 0, 0))
GPS_UTC_LEAP_S = 18  # valid since 2017-01-01
WEEK_S = 604800
MU = 3.986005e14
OMEGA_E = 7.2921151467e-5
C_LIGHT = 299792458.0
REL_F = -4.442807633e-10
REF_MAX_AGE_S = 4 * 3600  # reference records further than this from the evaluation time are not used
LNAV_PREAMBLE = 0x8B
UBX_GNSS_GPS = 0
GPS_L1CA_SIG = 0

# IS-GPS-200 parity: (which of D29*/D30*, data bit indices 1..24) for D25..D30
_PARITY = ((29, (1, 2, 3, 5, 6, 10, 11, 12, 13, 14, 17, 18, 20, 23)),
           (30, (2, 3, 4, 6, 7, 11, 12, 13, 14, 15, 18, 19, 21, 24)),
           (29, (1, 3, 4, 5, 7, 8, 12, 13, 14, 15, 16, 19, 20, 22)),
           (30, (2, 4, 5, 6, 8, 9, 13, 14, 15, 16, 17, 20, 21, 23)),
           (30, (1, 3, 5, 6, 7, 9, 10, 14, 15, 16, 17, 18, 21, 22, 24)),
           (29, (3, 5, 6, 8, 9, 10, 11, 13, 15, 19, 22, 23, 24)))


def utc_to_gps(t_utc: float) -> float:
    return t_utc - GPS_EPOCH + GPS_UTC_LEAP_S


def word_parity_ok(word: int) -> bool:
    """u-blox SFRBX GPS word: data bits 29..6 (already de-inverted), parity 5..0, and the previous
    word's D29* in bit 31 and D30* in bit 30 (D30* is 0 after de-inversion). Convention found by
    brute force on the VAARA logs: every word of 300 subframes matched it."""
    d = (word >> 6) & 0xFFFFFF
    star = {29: (word >> 31) & 1, 30: (word >> 30) & 1}
    out = 0
    for which, idx in _PARITY:
        x = star[which]
        for i in idx:
            x ^= (d >> (24 - i)) & 1
        out = (out << 1) | x
    return out == word & 0x3F


class _Bits:
    def __init__(self, words24: list[int]):
        self.v = 0
        for w in words24:
            self.v = (self.v << 24) | w
        self.n = 24 * len(words24)

    def u(self, pos: int, ln: int) -> int:
        return (self.v >> (self.n - pos - ln)) & ((1 << ln) - 1)

    def s(self, pos: int, ln: int) -> int:
        x = self.u(pos, ln)
        return x - (1 << ln) if x >> (ln - 1) else x

    def u2(self, p1, l1, p2, l2):
        return (self.u(p1, l1) << l2) | self.u(p2, l2)

    def s2(self, p1, l1, p2, l2):
        x = self.u2(p1, l1, p2, l2)
        n = l1 + l2
        return x - (1 << n) if x >> (n - 1) else x


def decode_lnav(sf1: list[int], sf2: list[int], sf3: list[int], near_week: int) -> dict | None:
    """Subframes as 10 x 24-bit data words. Bit offsets follow RTKLIB rcvraw.c (24-bit word layout).
    near_week: full GPS week near the data, to resolve the 10-bit week number."""
    b1, b2, b3 = _Bits(sf1), _Bits(sf2), _Bits(sf3)
    iodc = (b1.u(70, 2) << 8) | b1.u(168, 8)
    iode2, iode3 = b2.u(48, 8), b3.u(216, 8)
    if not (iode2 == iode3 == iodc & 0xFF):
        return None
    pi = math.pi
    week10 = b1.u(48, 10)
    week = week10 + 1024 * round((near_week - week10) / 1024)
    return {
        "week": week, "iode": iode2, "iodc": iodc, "svh": b1.u(64, 6),
        "tgd": b1.s(160, 8) * 2 ** -31, "toc": b1.u(176, 16) * 16.0,
        "af2": b1.s(192, 8) * 2 ** -55, "af1": b1.s(200, 16) * 2 ** -43, "af0": b1.s(216, 22) * 2 ** -31,
        "crs": b2.s(56, 16) * 2 ** -5, "deln": b2.s(72, 16) * 2 ** -43 * pi,
        "m0": b2.s2(88, 8, 96, 24) * 2 ** -31 * pi, "cuc": b2.s(120, 16) * 2 ** -29,
        "e": b2.u2(136, 8, 144, 24) * 2 ** -33, "cus": b2.s(168, 16) * 2 ** -29,
        "sqrta": b2.u2(184, 8, 192, 24) * 2 ** -19, "toe": b2.u(216, 16) * 16.0,
        "cic": b3.s(48, 16) * 2 ** -29, "omg0": b3.s2(64, 8, 72, 24) * 2 ** -31 * pi,
        "cis": b3.s(96, 16) * 2 ** -29, "i0": b3.s2(112, 8, 120, 24) * 2 ** -31 * pi,
        "crc": b3.s(144, 16) * 2 ** -5, "omg": b3.s2(160, 8, 168, 24) * 2 ** -31 * pi,
        "omgd": b3.s(192, 24) * 2 ** -43 * pi, "idot": b3.s(224, 14) * 2 ** -43 * pi,
    }


def _week_time(eph: dict, sow: float) -> float:
    return eph["week"] * WEEK_S + sow


def sat_pos_clk(eph: dict, t_gps: float) -> tuple[float, float, float, float]:
    """ECEF position (m) and clock offset (s) at GPS time t_gps (s since the GPS epoch). IS-GPS-200."""
    a = eph["sqrta"] ** 2
    toe = _week_time(eph, eph["toe"])
    tk = t_gps - toe
    n = math.sqrt(MU / a ** 3) + eph["deln"]
    m = eph["m0"] + n * tk
    e = eph["e"]
    ea = m
    for _ in range(30):
        nxt = m + e * math.sin(ea)
        if abs(nxt - ea) < 1e-13:
            ea = nxt
            break
        ea = nxt
    v = math.atan2(math.sqrt(1 - e * e) * math.sin(ea), math.cos(ea) - e)
    phi = v + eph["omg"]
    s2, c2 = math.sin(2 * phi), math.cos(2 * phi)
    u = phi + eph["cus"] * s2 + eph["cuc"] * c2
    r = a * (1 - e * math.cos(ea)) + eph["crs"] * s2 + eph["crc"] * c2
    inc = eph["i0"] + eph["idot"] * tk + eph["cis"] * s2 + eph["cic"] * c2
    om = eph["omg0"] + (eph["omgd"] - OMEGA_E) * tk - OMEGA_E * eph["toe"]
    xp, yp = r * math.cos(u), r * math.sin(u)
    x = xp * math.cos(om) - yp * math.cos(inc) * math.sin(om)
    y = xp * math.sin(om) + yp * math.cos(inc) * math.cos(om)
    z = yp * math.sin(inc)
    dt = t_gps - _week_time(eph, eph["toc"])
    clk = eph["af0"] + eph["af1"] * dt + eph["af2"] * dt * dt + REL_F * e * eph["sqrta"] * math.sin(ea)
    return x, y, z, clk


def _f(s: str) -> float:
    s = s.strip().replace("D", "E").replace("d", "e")
    return float(s) if s else 0.0


def parse_rinex3_gps_nav(path: str | Path) -> dict[str, list[dict]]:
    """GPS records of a RINEX 3.0x navigation file => {'G05': [eph, ...]} sorted by toe."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", errors="replace") as fh:
        lines = fh.read().splitlines()
    i = next(k for k, ln in enumerate(lines) if "END OF HEADER" in ln) + 1
    out: dict[str, list[dict]] = {}
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        sys_ = ln[0]
        nlines = {"G": 8, "E": 8, "C": 8, "J": 8, "I": 8, "R": 4, "S": 4}.get(sys_, 1)
        if sys_ != "G":
            i += nlines
            continue
        rec = lines[i:i + 8]
        i += 8
        vals = [_f(rec[0][23 + 19 * k:42 + 19 * k]) for k in range(3)]
        for r in rec[1:]:
            vals += [_f(r[4 + 19 * k:23 + 19 * k]) for k in range(4)]
        y, mo, d, hh, mi, ss = (int(rec[0][4:8]), int(rec[0][9:11]), int(rec[0][12:14]),
                                int(rec[0][15:17]), int(rec[0][18:20]), int(rec[0][21:23]))
        toc_abs = calendar.timegm((y, mo, d, hh, mi, ss)) - GPS_EPOCH
        week = int(vals[21])
        eph = {"af0": vals[0], "af1": vals[1], "af2": vals[2], "iode": int(vals[3]), "crs": vals[4],
               "deln": vals[5], "m0": vals[6], "cuc": vals[7], "e": vals[8], "cus": vals[9],
               "sqrta": vals[10], "toe": vals[11], "cic": vals[12], "omg0": vals[13], "cis": vals[14],
               "i0": vals[15], "crc": vals[16], "omg": vals[17], "omgd": vals[18], "idot": vals[19],
               "week": week, "svh": int(vals[24]), "tgd": vals[25], "iodc": int(vals[26]),
               "toc": toc_abs - week * WEEK_S}
        out.setdefault(rec[0][:3].replace(" ", "0"), []).append(eph)
    for v in out.values():
        v.sort(key=lambda e: _week_time(e, e["toe"]))
    return out


def disagreement_m(eph: dict, ref: dict, t_gps: float) -> tuple[float, float]:
    """(orbit 3-D difference, clock difference x c), metres."""
    a, b = sat_pos_clk(eph, t_gps), sat_pos_clk(ref, t_gps)
    return math.dist(a[:3], b[:3]), abs(a[3] - b[3]) * C_LIGHT


def pick_reference(refs: list[dict], eph: dict, t_gps: float) -> dict | None:
    same = [r for r in refs if r["iode"] == eph["iode"] and abs(_week_time(r, r["toe"]) - t_gps) <= REF_MAX_AGE_S]
    if same:
        return min(same, key=lambda r: abs(_week_time(r, r["toe"]) - _week_time(eph, eph["toe"])))
    near = [r for r in refs if abs(_week_time(r, r["toe"]) - t_gps) <= REF_MAX_AGE_S]
    return min(near, key=lambda r: abs(_week_time(r, r["toe"]) - t_gps)) if near else None


class EphemerisChecker:
    """Feed UBX-RXM-SFRBX payloads in stream order; ask `mismatch_m(t_utc)` once per epoch."""

    def __init__(self, reference: dict[str, list[dict]]):
        self.reference = reference
        self.subframes: dict[str, dict[int, list[int]]] = {}
        self.current: dict[str, dict] = {}  # latest complete decoded set per SV
        self.decoded = 0
        self.parity_fail = 0

    def feed_sfrbx(self, payload: bytes, t_utc: float) -> str | None:
        """Returns the SV id when this payload completed a new ephemeris set."""
        if len(payload) < 8 or payload[0] != UBX_GNSS_GPS or payload[2] != GPS_L1CA_SIG or payload[4] != 10:
            return None
        words = [struct.unpack_from("<I", payload, 8 + 4 * k)[0] for k in range(10)]
        if not all(word_parity_ok(w) for w in words):
            self.parity_fail += 1
            return None
        d = [(w >> 6) & 0xFFFFFF for w in words]
        if d[0] >> 16 != LNAV_PREAMBLE:
            return None
        sfid = (d[1] >> 2) & 7
        if sfid not in (1, 2, 3):
            return None
        sv = f"G{payload[1]:02d}"
        sfs = self.subframes.setdefault(sv, {})
        sfs[sfid] = d
        if len(sfs) < 3:
            return None
        near_week = int(utc_to_gps(t_utc) // WEEK_S)
        eph = decode_lnav(sfs[1], sfs[2], sfs[3], near_week)
        if eph is None:
            return None
        old = self.current.get(sv)
        if old is not None and all(old[k] == eph[k] for k in ("iode", "iodc", "toe", "m0", "sqrta", "af0")):
            return None
        self.current[sv] = eph
        self.decoded += 1
        return sv

    def mismatch_m(self, t_utc: float) -> dict[str, float]:
        t = utc_to_gps(t_utc)
        out = {}
        for sv, eph in self.current.items():
            ref = pick_reference(self.reference.get(sv, []), eph, t)
            if ref is None:
                continue
            orbit, clock = disagreement_m(eph, ref, t)
            out[sv] = max(orbit, clock)
        return out
