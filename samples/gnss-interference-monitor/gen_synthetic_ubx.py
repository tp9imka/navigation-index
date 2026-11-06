"""Write a synthetic u-blox UBX capture with a jamming and a spoofing episode. Requires pyubx2.

Each 1 Hz epoch carries NAV-PVT, NAV-SAT, NAV-STATUS, NAV-CLOCK, MON-RF and SEC-SIG, the
messages ubx_monitor.py reads. Values are invented to exercise the scorer, not recorded.

  python3 gen_synthetic_ubx.py fixtures/synthetic.ubx

Timeline (seconds from start): 0-59 clean, 60-89 broadband jamming, 90-119 clean,
120-159 spoofing (takeover with clock and position step, uniform C/N0, receiver flag from
130 s), 160-179 clean again.
"""

from __future__ import annotations

import argparse
import math
import random
import struct

from pyubx2 import GET, UBXMessage

SEED = 11
DURATION_S = 180
JAM = (60, 90)
SPOOF = (120, 160)
SPOOF_RX_FLAG_FROM_S = 130
JAM_RX_FLAG_FROM_S = 70
START_ITOW_MS = 216_000_000

LAT0, LON0, HEIGHT_MM = 52.0, 4.37, 30_000
DEG_PER_M_LAT = 1 / 111_320.0
SPOOF_STEP_M = 300.0
SPOOF_WALK_MPS = 20.0
AGC_NOMINAL = 5000
AGC_JAMMED = 2700
JAM_IND_NOMINAL = 10
JAM_IND_JAMMED = 160
CLK_DRIFT_NS_S = 100
SPOOF_CLK_STEP_NS = 5000
SPOOF_CN0 = 48
# (gnssId, svId, elevation deg); C/N0 follows elevation on a real sky
SKY = [(0, 2, 70), (0, 5, 45), (0, 12, 30), (0, 15, 15), (0, 24, 60), (0, 29, 20),
       (2, 4, 55), (2, 11, 35), (2, 19, 25), (2, 30, 10)]


def cn0_for(elev, rng):
    return 30 + 17 * math.sin(math.radians(elev)) + rng.gauss(0, 0.7)


def mon_rf_payload(jamming_state: int, agc_cnt: int, jam_ind: int) -> bytes:
    # pyubx2 picks the MON-RF layout from payload length, so it must be built as bytes:
    # 4-byte header + one 24-byte block (blockId, flags, antStatus, antPower, postStatus,
    # reserved, noisePerMS, agcCnt, jamInd, ofsI, magI, ofsQ, magQ, reserved[3]).
    header = struct.pack("<BBBB", 0, 1, 0, 0)
    block = struct.pack("<BBBBIIHHBbBbB3s", 0, jamming_state & 0x3, 2, 1, 0, 0, 90, agc_cnt,
                        jam_ind, 0, 120, 0, 120, b"\0\0\0")
    return header + block


def epoch_messages(k: int, rng: random.Random):
    itow = START_ITOW_MS + k * 1000
    jammed = JAM[0] <= k < JAM[1]
    spoofed = SPOOF[0] <= k < SPOOF[1]

    lat, lon = LAT0 + rng.gauss(0, 1.0) * DEG_PER_M_LAT, LON0
    if spoofed:
        lat += (SPOOF_STEP_M + SPOOF_WALK_MPS * (k - SPOOF[0])) * DEG_PER_M_LAT

    sats = []
    for gnss_id, sv_id, elev in SKY:
        if spoofed:
            cno = SPOOF_CN0 + rng.gauss(0, 0.4)
        else:
            cno = cn0_for(elev, rng)
            if jammed:
                cno -= 14 + rng.uniform(0, 6)
        if cno >= 20:
            sats.append((gnss_id, sv_id, round(cno), elev))
    fix_type = 3 if len(sats) >= 4 else 0

    clk_b = 20_000 + CLK_DRIFT_NS_S * k + round(rng.gauss(0, 5))
    if spoofed:
        clk_b += SPOOF_CLK_STEP_NS

    pvt = UBXMessage("NAV", "NAV-PVT", GET, iTOW=itow, year=2026, month=11, day=6, hour=12,
                     validDate=1, validTime=1, fixType=fix_type, gnssFixOk=int(fix_type == 3),
                     numSV=len(sats), lon=lon, lat=lat, height=HEIGHT_MM, hMSL=HEIGHT_MM)
    sat_kw = {"iTOW": itow, "version": 1, "numSvs": len(sats)}
    for i, (gnss_id, sv_id, cno, elev) in enumerate(sats, start=1):
        sat_kw.update({f"gnssId_{i:02d}": gnss_id, f"svId_{i:02d}": sv_id,
                       f"cno_{i:02d}": cno, f"elev_{i:02d}": elev, f"svUsed_{i:02d}": 1})
    sat = UBXMessage("NAV", "NAV-SAT", GET, **sat_kw)
    spoof_state = 2 if spoofed and k >= SPOOF_RX_FLAG_FROM_S else 1
    status = UBXMessage("NAV", "NAV-STATUS", GET, iTOW=itow, gpsFix=fix_type,
                        gpsFixOk=int(fix_type == 3), spoofDetState=spoof_state)
    clock = UBXMessage("NAV", "NAV-CLOCK", GET, iTOW=itow, clkB=clk_b, clkD=CLK_DRIFT_NS_S)
    jam_state = 2 if jammed and k >= JAM_RX_FLAG_FROM_S else 1
    agc = (AGC_JAMMED if jammed else AGC_NOMINAL) + round(rng.gauss(0, 40))
    jam_ind = JAM_IND_JAMMED if jammed else JAM_IND_NOMINAL + rng.randint(0, 5)
    rf = UBXMessage("MON", "MON-RF", GET, payload=mon_rf_payload(jam_state, agc, jam_ind))
    sec = UBXMessage("SEC", "SEC-SIG", GET, version=1, jamDetEnabled=1, jammingState=jam_state,
                     spfDetEnabled=1, spoofingState=spoof_state)
    return [pvt, sat, status, clock, rf, sec]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    n = 0
    with open(args.out, "wb") as fh:
        for k in range(DURATION_S):
            for msg in epoch_messages(k, rng):
                fh.write(msg.serialize())
                n += 1
    print(f"wrote {n} UBX messages, {DURATION_S} epochs => {args.out}")


if __name__ == "__main__":
    main()
