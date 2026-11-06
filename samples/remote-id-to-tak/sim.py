"""Synthetic Remote ID traffic for exercising the tracker without a radio.

encode_* follow opendroneid-core-c's encoder rounding; test_tracker.py checks that core-c
(when built) and odid.py decode them back to the intended values. The scenario is made up:
one normal flight plus one example of each anomaly the tracker looks for.
"""
import math
import struct

import odid

PROTO_VERSION = 2
M_PER_DEG_LAT = 111_320.0


def cround(x):
    """C round(): half away from zero (Python's round() is half to even)."""
    return int(math.copysign(math.floor(abs(x) + 0.5), x))


def _hdr(mtype):
    return bytes([(mtype << 4) | PROTO_VERSION])


def _alt(m):
    return max(0, min(0xFFFF, cround((m + odid.ALT_ADDER) / odid.ALT_DIV)))


def encode_basic_id(uas_id: str, id_type=odid.IDTYPE_SERIAL, ua_type=2) -> bytes:
    return _hdr(odid.BASIC_ID) + bytes([(id_type << 4) | ua_type]) + uas_id.encode()[:20].ljust(20, b"\0") + bytes(3)


def encode_location(lat, lon, alt_geo, course, speed, vspeed=0.0, height=None, status=2,
                    ts_after_hour=None, h_acc=10, v_acc=4, speed_acc=3) -> bytes:
    direction = cround(course) % 360
    ew = 1 if direction >= 180 else 0
    direction -= 180 * ew
    if speed <= 255 * odid.SPEED_DIV[0]:
        mult, sp = 0, cround(speed / odid.SPEED_DIV[0])
    else:
        mult, sp = 1, min(255, cround((speed - 255 * odid.SPEED_DIV[0]) / odid.SPEED_DIV[1]))
    flags = mult | (ew << 1) | (status << 4)
    ts = odid.INV_TIMESTAMP if ts_after_hour is None else cround(ts_after_hour * odid.TS_TENTHS)
    body = struct.pack("<BBBbiiHHHBBHBB", flags, direction, sp, max(-128, min(127, cround(vspeed / odid.VSPEED_DIV))),
                       cround(lat * odid.LATLON_MULT), cround(lon * odid.LATLON_MULT),
                       _alt(odid.INV_ALT), _alt(alt_geo), _alt(odid.INV_ALT if height is None else height),
                       (v_acc << 4) | h_acc, speed_acc, ts, 0, 0)
    return _hdr(odid.LOCATION) + body


def encode_system(op_lat, op_lon, op_alt=odid.INV_ALT, timestamp=0, loc_type=0) -> bytes:
    body = struct.pack("<BiiHBHHBHIB", loc_type, cround(op_lat * odid.LATLON_MULT), cround(op_lon * odid.LATLON_MULT),
                       1, 0, _alt(odid.INV_ALT), _alt(odid.INV_ALT), 0, _alt(op_alt), timestamp, 0)
    return _hdr(odid.SYSTEM) + body


def encode_operator_id(op_id: str) -> bytes:
    return _hdr(odid.OPERATOR_ID) + b"\0" + op_id.encode()[:20].ljust(20, b"\0") + bytes(3)


def encode_self_id(text: str) -> bytes:
    return _hdr(odid.SELF_ID) + b"\0" + text.encode()[:23].ljust(23, b"\0")


def encode_pack(messages) -> bytes:
    return _hdr(odid.PACKED) + bytes([odid.MESSAGE_SIZE, len(messages)]) + b"".join(messages)


def offset(lat, lon, north_m, east_m):
    return lat + north_m / M_PER_DEG_LAT, lon + east_m / (M_PER_DEG_LAT * math.cos(math.radians(lat)))


BASE_LAT, BASE_LON = 51.4700, -0.4543
T0 = 1_762_430_400.0  # 2025-11-06T12:00:00Z, receiver clock for the scenario


def _frame(t, mac, uas_id, lat, lon, alt, course, speed, op, op_id="GBR-OP-DEMO0001", desc="survey"):
    pack = encode_pack([encode_basic_id(uas_id), encode_location(lat, lon, alt, course, speed,
                                                                  ts_after_hour=t % 3600),
                        encode_system(*op), encode_operator_id(op_id), encode_self_id(desc)])
    return t, mac, pack


def scenario(duration_s=30, rate_hz=1.0):
    """Yield (t, mac, pack) in time order."""
    out = []
    op_a = offset(BASE_LAT, BASE_LON, -150, -100)
    for k in range(int(duration_s * rate_hz)):
        t = T0 + k / rate_hz
        ang = 2 * math.pi * k / 40
        # A: normal 120 m orbit at 9.4 m/s, operator 180 m away
        la, lo = offset(BASE_LAT, BASE_LON, 120 * math.cos(ang), 120 * math.sin(ang))
        out.append(_frame(t, "a0:00:00:00:00:0a", "SIMA-0001", la, lo, 150, math.degrees(ang) + 90, 9.4, op_a))
        # B: second transmitter cloning A's serial, parked 3 km away (from t+10 s)
        if k >= 10:
            lb, lob = offset(BASE_LAT, BASE_LON, 3000, 0)
            out.append(_frame(t + 0.3, "b0:00:00:00:00:0b", "SIMA-0001", lb, lob, 120, 0, 0,
                              offset(lb, lob, -100, 0)))
        # C: claims 12 m/s eastbound but teleports 2 km at k == 15
        east = 12 * k + (2000 if k >= 15 else 0)
        lc, loc = offset(BASE_LAT, BASE_LON, -800, -1500 + east)
        out.append(_frame(t + 0.1, "c0:00:00:00:00:0c", "SIMC-0003", lc, loc, 90, 90, 12, offset(lc, loc, 0, -60)))
        # D: operator reported 8 km from the aircraft
        ld, lod = offset(BASE_LAT, BASE_LON, 900, 900)
        out.append(_frame(t + 0.2, "d0:00:00:00:00:0d", "SIMD-0004", ld, lod, 60, 0, 0, offset(ld, lod, -8000, 0)))
        # E: one transmitter rotates its claimed serial at k == 12
        le, loe = offset(BASE_LAT, BASE_LON, -400, 600)
        out.append(_frame(t + 0.4, "e0:00:00:00:00:0e", "SIME-0005" if k < 12 else "SIME-9999", le, loe, 80, 45, 0.5,
                          offset(le, loe, -50, -50)))
        # F: stops transmitting after 8 s (goes stale, then dropped)
        if k < 8:
            lf, lof = offset(BASE_LAT, BASE_LON, 300, -700)
            out.append(_frame(t + 0.5, "f0:00:00:00:00:0f", "SIMF-0006", lf, lof, 40, 180, 3, offset(lf, lof, 20, 20)))
    out.sort(key=lambda r: r[0])
    return out
