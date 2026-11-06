"""Fetch one NCLT session's sensor CSVs and ground truth (42.3 MB for 2013-01-10).

python3 fetch_nclt.py              => data/2013-01-10/{gps,gps_rtk,ms25,ms25_euler,wheels,kvh}.csv
                                      + data/2013-01-10/groundtruth.csv
python3 fetch_nclt.py --keep-tar   keep the 21.7 MB tarball after extraction

Both downloads are checked against SHA-256 values recorded on 2026-11-06. Only the named CSV
members are extracted, by name, so a hostile tarball cannot write outside data/.
"""
import argparse
import hashlib
import os
import sys
import tarfile
import urllib.request

BASE = "https://s3.us-east-2.amazonaws.com/nclt.perl.engin.umich.edu"
SESSIONS = {
    "2013-01-10": {
        "sen_sha256": "3ec1a5ac27ee716e6e5da0cd4e8fee96241d6a21ac63d14a844c40d2410d5ffb",
        "sen_bytes": 21669014,
        "gt_sha256": "4301c74fecc9578353a2f373f50320de97542962240fc314389bf6fdd9063b63",
        "gt_bytes": 20669309,
    },
}
MEMBERS = ("gps.csv", "gps_rtk.csv", "ms25.csv", "ms25_euler.csv", "wheels.csv", "kvh.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
CHUNK = 1 << 20


def download(url, path, expected_sha, expected_bytes):
    if os.path.exists(path) and sha256(path) == expected_sha:
        print(f"ok (cached) {os.path.basename(path)}")
        return
    tmp = path + ".part"
    h = hashlib.sha256()
    n = 0
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        while True:
            b = r.read(CHUNK)
            if not b:
                break
            f.write(b)
            h.update(b)
            n += len(b)
    if n != expected_bytes or h.hexdigest() != expected_sha:
        os.remove(tmp)
        sys.exit(f"checksum mismatch for {url}: {n} bytes, sha256 {h.hexdigest()}")
    os.replace(tmp, path)
    print(f"ok {os.path.basename(path)} {n / 1e6:.1f} MB sha256 verified")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def extract(tar_path, session, out_dir):
    with tarfile.open(tar_path, "r:gz") as tf:
        for name in MEMBERS:
            info = tf.getmember(f"{session}/{name}")
            if not info.isfile():
                sys.exit(f"{info.name} is not a regular file")
            src = tf.extractfile(info)
            with open(os.path.join(out_dir, name), "wb") as dst:
                for b in iter(lambda: src.read(CHUNK), b""):
                    dst.write(b)
            print(f"extracted {name} {info.size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", default="2013-01-10", choices=sorted(SESSIONS))
    ap.add_argument("--out", default=os.path.join(HERE, "data"))
    ap.add_argument("--keep-tar", action="store_true")
    args = ap.parse_args()
    s = SESSIONS[args.session]
    out_dir = os.path.join(args.out, args.session)
    os.makedirs(out_dir, exist_ok=True)
    tar_path = os.path.join(out_dir, f"{args.session}_sen.tar.gz")
    gt_path = os.path.join(out_dir, "groundtruth.csv")
    download(f"{BASE}/ground_truth/groundtruth_{args.session}.csv", gt_path, s["gt_sha256"], s["gt_bytes"])
    if all(os.path.exists(os.path.join(out_dir, m)) for m in MEMBERS) and not os.path.exists(tar_path):
        print("sensor CSVs already extracted")
        return
    download(f"{BASE}/sensor_data/{args.session}_sen.tar.gz", tar_path, s["sen_sha256"], s["sen_bytes"])
    extract(tar_path, args.session, out_dir)
    if not args.keep_tar:
        os.remove(tar_path)


if __name__ == "__main__":
    main()
