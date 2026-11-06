"""Danish Maritime Authority (DMA) historical AIS: partial download + pandas loader.

Daily files are http://aisdata.ais.dk/aisdk-YYYY-MM-DD.zip (0.5-0.9 GB zipped, one CSV,
roughly time-ordered). fetch() pulls only the first N MB with an HTTP Range request and
inflates the leading part of the deflate stream, giving the first hours of the day.
"""
import argparse
import struct
import urllib.request
import zlib
from pathlib import Path

from detectors import Fix, Track

DMA_URL = "http://aisdata.ais.dk/aisdk-{date}.zip"
LOCAL_HEADER_LEN = 30
UNAVAILABLE_LAT, UNAVAILABLE_LON = 91.0, 181.0
COLS = {"# Timestamp": "ts", "Type of mobile": "mobile", "MMSI": "mmsi", "Latitude": "lat",
        "Longitude": "lon", "SOG": "sog", "COG": "cog", "Heading": "hdg", "Ship type": "ship_type",
        "Length": "length", "Name": "name"}


def fetch(date, mb, out_dir):
    url = DMA_URL.format(date=date)
    req = urllib.request.Request(url, headers={"Range": f"bytes=0-{mb * 1024 * 1024 - 1}"})
    raw = urllib.request.urlopen(req, timeout=600).read()
    if raw[:4] != b"PK\x03\x04":
        raise ValueError("not a zip local file header")
    name_len, extra_len = struct.unpack("<HH", raw[26:30])
    data = zlib.decompressobj(-zlib.MAX_WBITS).decompress(raw[LOCAL_HEADER_LEN + name_len + extra_len:])
    data = data[: data.rfind(b"\n") + 1]
    out = Path(out_dir) / f"aisdk-{date}.head{mb}mb.csv"
    out.write_bytes(data)
    return out


def load_frame(csv_path, hours=None):
    import pandas as pd
    df = pd.read_csv(csv_path, usecols=list(COLS), low_memory=False).rename(columns=COLS)
    ts = pd.to_datetime(df.ts, format="%d/%m/%Y %H:%M:%S", utc=True)
    df["t"] = (ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
    if hours:
        df = df[df.t < df.t.min() + hours * 3600]
    df = df[(df.lat.abs() <= 90) & (df.lon.abs() <= 180)
            & (df.lat != UNAVAILABLE_LAT) & (df.lon != UNAVAILABLE_LON)
            & ~((df.lat == 0) & (df.lon == 0))]
    df = df.drop_duplicates(["mmsi", "t", "lat", "lon"]).sort_values(["mmsi", "t"], kind="stable")
    return df


def frame_to_tracks(df):
    import pandas as pd
    stats = {"rows": len(df), "mmsi": int(df.mmsi.nunique()),
             "same_second_conflicts": int(df.duplicated(["mmsi", "t"]).sum())}
    df = df.drop_duplicates(["mmsi", "t"])
    tracks = []
    for mmsi, g in df.groupby("mmsi", sort=False):
        st = g.ship_type[g.ship_type.notna() & (g.ship_type != "Undefined")]
        ln = g.length.dropna()
        nm = g.name.dropna()
        fixes = [Fix(float(t), float(la), float(lo),
                     None if pd.isna(s) else float(s),
                     None if pd.isna(c) else float(c),
                     None if pd.isna(h) else float(h))
                 for t, la, lo, s, c, h in zip(g.t.values, g.lat.values, g.lon.values,
                                               g.sog.values, g.cog.values, g.hdg.values)]
        tracks.append(Track(int(mmsi), fixes,
                            ship_type=st.mode().iat[0] if len(st) else "Undefined",
                            length_m=float(ln.max()) if len(ln) else None,
                            mobile=g.mobile.mode().iat[0],
                            name=nm.iat[0] if len(nm) else ""))
    return tracks, stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Download the first N MB of a DMA AIS day file")
    ap.add_argument("--date", default="2026-11-03")
    ap.add_argument("--mb", type=int, default=100)
    ap.add_argument("--out-dir", default="data")
    a = ap.parse_args()
    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    print(fetch(a.date, a.mb, a.out_dir))
