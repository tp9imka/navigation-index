"""Fetch the public data used by this sample into ./data (git-ignored).

radar: NRC UAV vs bird radar tracks (CC BY 4.0), labelled .xlsx sessions + metadata, ~42 MB.
rf:    DroneRF low-band subset (CC BY 4.0, Mendeley f4c2b4n755), 4 RAR files, ~0.67 GB.
       Extracted with bsdtar (libarchive, ships with macOS; `apt install libarchive-tools` on Debian).

Usage: python3 download_data.py radar|rf|all
"""
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

RADAR_REPO = "nrc-cnrc/CUAS-sensing-dataset"
RADAR_RAW = f"https://raw.githubusercontent.com/{RADAR_REPO}/main/"
RADAR_TREE = f"https://api.github.com/repos/{RADAR_REPO}/git/trees/main?recursive=1"
RADAR_LABELLED_DIRS = ("data/Demo-0/", "data/Demo-2/", "data/Demo-3/", "data/Demo-5/", "data/Demo-6/")
RADAR_EXTRA = ("metadata/track_labels.csv", "metadata/file_manifest.csv", "LICENSE")

USER_AGENT = "navigation-index-cuas-sample/1.0"  # Mendeley returns 403 to the default urllib agent
DRONERF_API = "https://data.mendeley.com/public-api/datasets/f4c2b4n755"
# BUI codes (DroneRF paper): 00000 background, 100xx Bebop, 101xx AR Drone, 11000 Phantom.
# One low-band (L) archive per class, mode 00 (drone on and connected) for Bebop/AR.
DRONERF_SUBSET = (
    "RF Data_00000_L1.rar",
    "RF Data_10000_L.rar",
    "RF Data_10100_L.rar",
    "RF Data_11000_L1.rar",
)


def urlopen(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}))


def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urlopen(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    tmp.rename(dest)
    print(f"{dest.relative_to(HERE)}  {dest.stat().st_size:,} B")


def radar():
    with urlopen(RADAR_TREE) as r:
        tree = json.load(r)["tree"]
    paths = [t["path"] for t in tree
             if t["type"] == "blob" and t["path"].endswith(".xlsx")
             and t["path"].startswith(RADAR_LABELLED_DIRS)]
    for p in list(paths) + list(RADAR_EXTRA):
        fetch(RADAR_RAW + urllib.request.quote(p), DATA / "radar" / p)


def rf():
    with urlopen(DRONERF_API) as r:
        meta = json.load(r)
    print("DroneRF licence:", meta["data_licence"]["short_name"])
    urls = {f["filename"]: f["content_details"]["download_url"] for f in meta["files"]}
    out = DATA / "dronerf"
    for name in DRONERF_SUBSET:
        rar = out / "rar" / name
        fetch(urls[name], rar)
        dest = out / "csv"
        dest.mkdir(parents=True, exist_ok=True)
        subprocess.run(["bsdtar", "-xf", str(rar), "-C", str(dest)], check=True)
    n = sum(1 for _ in (out / "csv").rglob("*.csv"))
    print(f"extracted {n} csv segments under {out / 'csv'}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("radar", "all"):
        radar()
    if what in ("rf", "all"):
        rf()
