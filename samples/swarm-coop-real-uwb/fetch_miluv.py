"""Fetch only the CSV files of one MILUV experiment from figshare, without the images.

Each experiment zip is 1-11 GB, almost all of it camera frames. The zip central directory sits
at the end of the file, so HTTP range requests read the directory, then only the CSV members.

python3 fetch_miluv.py                       default_3_zigzag_0 => data/default_3_zigzag_0/
python3 fetch_miluv.py --list                print members and sizes, download nothing
python3 fetch_miluv.py --exp cirObstacles_3_random_0    obstacles (NLOS), sparse ranging
"""
import argparse
import io
import os
import sys
import urllib.request
import zipfile

FIGSHARE_ARTICLE = 28386041
FILE_IDS = {  # figshare file ids, from api.figshare.com/v2/articles/28386041 (2026-11-06)
    "default_3_zigzag_0": 52317935,
    "default_3_random_0": 52291625,
    "default_3_random_0b": 52291628,
    "cirObstacles_3_random_0": 52317539,
    "oneTagPerRobot_3_random_0": 52289807,
}
WANTED = ("mocap.csv", "uwb_range.csv", "height.csv")
HERE = os.path.dirname(os.path.abspath(__file__))


class HttpRangeFile(io.RawIOBase):
    """Seekable read-only view of a remote file over HTTP Range requests. figshare redirects to
    an S3 URL signed for 10 s, so every read goes back through the redirect."""

    def __init__(self, url):
        self.url = url
        self.pos = 0
        self.fetched = 0
        req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            cr = r.headers.get("Content-Range")
            if not cr:
                raise RuntimeError("server ignored Range; refusing to download the full zip")
            self.size = int(cr.split("/")[-1])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        self.pos += len(data)
        self.fetched += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="default_3_zigzag_0", choices=sorted(FILE_IDS))
    ap.add_argument("--out", default=os.path.join(HERE, "data"))
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    url = f"https://ndownloader.figshare.com/files/{FILE_IDS[args.exp]}"
    rf = HttpRangeFile(url)
    zf = zipfile.ZipFile(io.BufferedReader(rf, buffer_size=1 << 20))
    infos = zf.infolist()
    csvs = [i for i in infos if i.filename.endswith(".csv")]
    print(f"{args.exp}: zip {rf.size / 1e9:.2f} GB, {len(infos)} members, {len(csvs)} CSV "
          f"({sum(i.file_size for i in csvs) / 1e6:.1f} MB uncompressed)")
    if args.list:
        for i in csvs:
            print(f"{i.file_size:12d}  {i.filename}")
        return
    total = 0
    for i in csvs:
        if os.path.basename(i.filename) not in WANTED:
            continue
        parts = i.filename.split("/")
        robot = next((p for p in parts if p.startswith("ifo00")), None)
        if robot is None:
            continue
        dst = os.path.join(args.out, args.exp, robot, os.path.basename(i.filename))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with zf.open(i) as src, open(dst, "wb") as f:
            f.write(src.read())
        total += i.file_size
        print(f"  {dst} ({i.file_size / 1e6:.1f} MB)")
    print(f"wrote {total / 1e6:.1f} MB; fetched {rf.fetched / 1e6:.1f} MB over HTTP of a {rf.size / 1e9:.2f} GB zip")


if __name__ == "__main__":
    sys.exit(main())
