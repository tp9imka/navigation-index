"""Fetch the open mobile-network PTP dataset (Kalnins, Zenodo 14230741, CC BY 4.0, ~60 MB)
into ./data/, check its MD5 against the Zenodo record, and unpack it.

Usage: python3 fetch_data.py [--keep-zip]
"""
import argparse
import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

RECORD = "https://zenodo.org/records/14230741"
ZIP_NAME = "Clock Synchronization Accuracy over Mobile Networks.zip"
URL = "https://zenodo.org/api/records/14230741/files/" + urllib.request.quote(ZIP_NAME) + "/content"
MD5 = "945aefa3013bc926d748f7e820275069"   # from https://zenodo.org/api/records/14230741
SIZE = 59977118
DATA = Path(__file__).resolve().parent / "data"
UNPACKED = DATA / "mobile-ptp"


def md5sum(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--keep-zip", action="store_true")
    p.add_argument("--force", action="store_true", help="download again even if already unpacked")
    a = p.parse_args(argv)
    DATA.mkdir(exist_ok=True)
    if (UNPACKED / "Clock Synchronization Accuracy over Mobile Networks" / "README.txt").exists() and not a.force:
        print(f"already unpacked in {UNPACKED} (use --force to fetch again)")
        return 0
    zpath = DATA / "mobile-ptp.zip"
    if not (zpath.exists() and zpath.stat().st_size == SIZE and md5sum(zpath) == MD5):
        print(f"downloading {SIZE / 1e6:.0f} MB from {RECORD}")
        tmp = zpath.with_suffix(".part")
        with urllib.request.urlopen(URL, timeout=120) as r, open(tmp, "wb") as out:
            shutil.copyfileobj(r, out, 1 << 20)
        tmp.replace(zpath)
    got = md5sum(zpath)
    if got != MD5:
        print(f"MD5 mismatch: {got} != {MD5}", file=sys.stderr)
        return 1
    print(f"md5 ok {MD5}")
    root = UNPACKED.resolve()
    with zipfile.ZipFile(zpath) as z:
        for m in z.infolist():
            dest = (UNPACKED / m.filename).resolve()
            if root not in dest.parents and dest != root:
                print(f"skipping unsafe member {m.filename}", file=sys.stderr)
                continue
            z.extract(m, UNPACKED)
    if not a.keep_zip:
        zpath.unlink()
    print(f"unpacked into {UNPACKED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
