"""Synthetic stream shaped like the VAARA u-blox logs (NMEA 4.11 + UBX RXM frames), with the effects the
real replay surfaced, so the tests run without the dataset (VAARA states no licence, so no real bytes
are redistributed here). Stdlib only.

  python3 make_fixture.py [out.ubx]   # default fixtures/vaara_shaped.ubx (git-ignored, ~0.45 MB)

Timeline, 1 Hz from 2024-09-12 07:00:00 UTC, static receiver, 10 SVs (GPS, Galileo, GLONASS):
    0-299  clean
  300-419  C/N0 staircase, -4 dB every 20 s to -24 dB (shaped on 2.4.3: each step stays under the 6 dB drop test)
  420-539  back to clean in one step (the scorer's cn0_rise then fires while the baseline is still low)
  540-599  C/N0 step -20 dB on every SV (shaped on 2.4.12 / 2.6.x)
  600-659  clean
  660-679  receiver UTC +900 s (shaped on 2.4.2); no fix for 660-669
  680-749  clean, receiver time back; 700-702 carry no time and no fix at all
Values are invented; only message layout, signal ids and the order of sentences follow the real logs.
"""

from __future__ import annotations

import random
import struct
import sys
import time
from pathlib import Path

START_UTC = 1726124400  # 2024-09-12 07:00:00
N_EPOCHS = 750
LAT, LON = 69.27576, 15.96789
SVS = [("GP", 2, 48), ("GP", 10, 33), ("GP", 17, 43), ("GP", 21, 38),
       ("GA", 13, 46), ("GA", 16, 31), ("GA", 28, 40),
       ("GL", 69, 44), ("GL", 76, 36), ("GL", 85, 42)]
L1_SIG = {"GP": "1", "GA": "7", "GL": "1"}
WINDOWS = {"staircase": (300, 419), "recover": (420, 539), "step_drop": (540, 599),
           "time_jump": (660, 679), "no_time": (700, 702)}
TIME_JUMP_S = 900
STAIR_STEP_DB, STAIR_EVERY_S, STAIR_STEPS = 4.0, 20, 6
STEP_DROP_DB = 20.0


def _ck(body: str) -> str:
    x = 0
    for c in body.encode():
        x ^= c
    return f"{x:02X}"


def nmea(body: str) -> bytes:
    return f"${body}*{_ck(body)}\r\n".encode()


def ubx(cls: int, mid: int, payload: bytes) -> bytes:
    head = struct.pack("<BBH", cls, mid, len(payload)) + payload
    a = b = 0
    for x in head:
        a = (a + x) & 0xFF
        b = (b + a) & 0xFF
    return b"\xb5\x62" + head + bytes([a, b])


def _dm(deg: float, lat: bool) -> str:
    d = int(deg)
    m = (deg - d) * 60
    return f"{d:02d}{m:08.5f}" if lat else f"{d:03d}{m:08.5f}"


def cn0_offset(k: int) -> float:
    if WINDOWS["staircase"][0] <= k <= WINDOWS["staircase"][1]:
        return -STAIR_STEP_DB * min(STAIR_STEPS, (k - WINDOWS["staircase"][0]) // STAIR_EVERY_S + 1)
    if WINDOWS["step_drop"][0] <= k <= WINDOWS["step_drop"][1]:
        return -STEP_DROP_DB
    return 0.0


def epoch_bytes(k: int, rng: random.Random) -> bytes:
    t = START_UTC + k
    no_time = WINDOWS["no_time"][0] <= k <= WINDOWS["no_time"][1]
    jumped = WINDOWS["time_jump"][0] <= k <= WINDOWS["time_jump"][1]
    fix = not no_time and not (jumped and k < WINDOWS["time_jump"][0] + 10)
    rt = t + (TIME_JUMP_S if jumped else 0)
    hms = "" if no_time else time.strftime("%H%M%S", time.gmtime(rt)) + ".00"
    date = "" if no_time else time.strftime("%d%m%y", time.gmtime(rt))
    lat = LAT + rng.gauss(0, 1.0) / 111000 if fix else None
    lon = LON + rng.gauss(0, 1.0) / 39000 if fix else None
    out = []
    # a RAWX-like frame first, as in the real logs; its payload holds '$' and a fake 'GNGGA' to trip naive parsers
    payload = struct.pack("<dHbBB3x", float(t % 604800), 2331, 18, 0, 1) + b"$GNGGA,\x97\xb3" + bytes(rng.randrange(256) for _ in range(16))
    out.append(ubx(0x02, 0x15, payload))
    if fix:
        out.append(nmea(f"GNRMC,{hms},A,{_dm(lat, True)},N,{_dm(lon, False)},E,0.020,,{date},,,A,V"))
        out.append(nmea("GNVTG,,T,,M,0.020,N,0.037,K,A"))
        out.append(nmea(f"GNGGA,{hms},{_dm(lat, True)},N,{_dm(lon, False)},E,1,12,0.52,40.1,M,34.3,M,,"))
    else:
        out.append(nmea(f"GNRMC,{hms},V,,,,,,,{date},,,N,V"))
        out.append(nmea("GNVTG,,,,,,,,,N"))
        out.append(nmea(f"GNGGA,{hms},,,,,0,00,99.99,,,,,,"))
    out.append(nmea("GNGSA,A,3,02,10,17,21,,,,,,,,,1.10,0.52,0.97,1"))
    off = cn0_offset(k)
    for talker in ("GP", "GA", "GL"):
        svs = [(sv, c) for tk, sv, c in SVS if tk == talker]
        fields = []
        for sv, c in svs:
            cno = max(0, round(c + off + rng.gauss(0, 1.0))) if not no_time else ""
            fields.append(f"{sv:02d},45,180,{cno}")
        out.append(nmea(f"{talker}GSV,1,1,{len(svs):02d},{','.join(fields)},{L1_SIG[talker]}"))
        if talker == "GP":  # L2 CM signal of the same SVs and an SBAS PRN: both must be ignored
            out.append(nmea(f"GPGSV,1,1,02,02,45,180,{30 + off:.0f},10,45,180,29,5"))
            out.append(nmea("GPGSV,1,1,01,49,12,192,38,1"))
    out.append(nmea(f"GNGLL,{_dm(lat, True) if fix else ''},{'N' if fix else ''},{_dm(lon, False) if fix else ''},"
                    f"{'E' if fix else ''},{hms},{'A' if fix else 'V'},{'A' if fix else 'N'}"))
    return b"".join(out)


def build(seed: int = 7) -> bytes:
    rng = random.Random(seed)
    return b"".join(epoch_bytes(k, rng) for k in range(N_EPOCHS)) + b"\xb5\x62\x02\x15\x10\x00garbage"


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "fixtures" / "vaara_shaped.ubx")
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    out.write_bytes(data)
    print(f"wrote {out} ({len(data)} bytes, {N_EPOCHS} epochs)")


if __name__ == "__main__":
    main()
