"""Raw AIS NMEA (AIVDM) in and out via pyais (M0r13n/pyais, MIT).

  python nmea_io.py stats FILE.nmea        # message mix, invalid positions, MMSI anomalies
Timestamps come from NMEA 4.10 tag blocks (\\c:<unix s>*hh\\). Lines without one decode
fine but cannot feed the kinematic detectors.
"""
import argparse
import functools
from collections import Counter

from pyais import encode_dict
from pyais.stream import FileReaderStream

from detectors import Fix, Track, mmsi_anomalies

POSITION_TYPES = {1: "Class A", 2: "Class A", 3: "Class A", 18: "Class B", 19: "Class B"}
LAT_NA, LON_NA, SOG_NA, COG_NA, HDG_NA = 91.0, 181.0, 102.3, 360.0, 511


def _checksum(s):
    return "%02X" % functools.reduce(lambda a, b: a ^ b, s.encode())


def tag_block(t):
    body = f"c:{int(t)}"
    return f"\\{body}*{_checksum(body)}\\"


def track_to_nmea(track):
    msg_type = 18 if track.mobile == "Class B" else 1
    out = []
    for f in track.fixes:
        d = {"msg_type": msg_type, "mmsi": track.mmsi, "lat": f.lat, "lon": f.lon,
             "speed": SOG_NA if f.sog is None else min(f.sog, 102.2),
             "course": COG_NA if f.cog is None else f.cog,
             "heading": HDG_NA if f.hdg is None else int(f.hdg) % 360}
        for s in encode_dict(d, talker_id="AI", sentence_type="VDM"):
            out.append(tag_block(f.t) + s)
    return out


def read_nmea(path):
    rows, errors = [], Counter()
    for msg in FileReaderStream(str(path)):
        try:
            d = msg.decode()
        except Exception as e:  # malformed payloads are common in real feeds
            errors[type(e).__name__] += 1
            continue
        t = None
        if msg.tag_block is not None:
            msg.tag_block.init()
            t = msg.tag_block.receiver_timestamp
        rows.append({"t": float(t) if t else None, "msg_type": d.msg_type, "mmsi": int(d.mmsi),
                     "lat": getattr(d, "lat", None), "lon": getattr(d, "lon", None),
                     "sog": getattr(d, "speed", None), "cog": getattr(d, "course", None),
                     "hdg": getattr(d, "heading", None)})
    return rows, errors


def rows_to_tracks(rows):
    per = {}
    for r in rows:
        if r["msg_type"] not in POSITION_TYPES or r["t"] is None:
            continue
        if r["lat"] is None or abs(r["lat"]) > 90 or abs(r["lon"]) > 180:
            continue
        sog = None if r["sog"] is None or r["sog"] >= SOG_NA else r["sog"]
        cog = None if r["cog"] is None or r["cog"] >= COG_NA else r["cog"]
        hdg = None if r["hdg"] is None or r["hdg"] == HDG_NA else float(r["hdg"])
        tr = per.setdefault(r["mmsi"], Track(r["mmsi"], [], mobile=POSITION_TYPES[r["msg_type"]]))
        tr.fixes.append(Fix(r["t"], r["lat"], r["lon"], sog, cog, hdg))
    for tr in per.values():
        tr.fixes.sort(key=lambda f: f.t)
    return list(per.values())


def stats(path):
    rows, errors = read_nmea(path)
    types = Counter(r["msg_type"] for r in rows)
    pos = [r for r in rows if r["msg_type"] in POSITION_TYPES]
    invalid = sum(1 for r in pos if r["lat"] is None or abs(r["lat"]) > 90 or abs(r["lon"]) > 180)
    mmsis = {(r["mmsi"], POSITION_TYPES.get(r["msg_type"], "other")) for r in rows}
    anomalies = Counter(k for m, mob in mmsis for k in mmsi_anomalies(m, mob))
    return {"messages": len(rows), "decode_errors": dict(errors), "types": dict(types.most_common()),
            "position_reports": len(pos), "position_not_available": invalid,
            "with_tag_block_time": sum(1 for r in rows if r["t"]),
            "distinct_mmsi": len({m for m, _ in mmsis}), "mmsi_anomalies": dict(anomalies)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stats"])
    ap.add_argument("path")
    a = ap.parse_args()
    for k, v in stats(a.path).items():
        print(f"{k}: {v}")
