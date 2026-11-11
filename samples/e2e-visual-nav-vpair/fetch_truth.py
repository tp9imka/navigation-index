"""Write results/navdash/truth.jsonl (VPAIR query poses) and put it back into the navdash manifest.

VPAIR is "academic use only", so the repo does not ship its poses. This script downloads the
VPAIR sample through ../relative-nav-benchmark/fetch_data.sh aerial (0.86 GB, skipped when
vpair_sample/ is already there) and rewrites the truth track exactly as run_fusion.py does.

Usage: .venv/bin/python fetch_truth.py [--data ../relative-nav-benchmark/data/vpair] [--out results/navdash]
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nav_core as nc  # noqa: E402

DEFAULT_DATA = nc.RELNAV / "data" / "vpair"
# truth.jsonl behind the README numbers (run 2026-11-06); identical in ../two-source-integrity-vpair.
TRUTH_SHA256 = "a18807ed3c72d1a1b5d5825c10e3c1ad92c50cb58e3d7dd6faac971f5ea3ad82"


def write_truth(data, nd):
    root = Path(data) / "vpair_sample"
    if not (root / "poses_query.txt").exists():
        if Path(data).resolve() != DEFAULT_DATA.resolve():
            sys.exit(f"{root}/poses_query.txt not found; run ../relative-nav-benchmark/fetch_data.sh aerial")
        subprocess.run([str(nc.RELNAV / "fetch_data.sh"), "aerial"], check=True)
    poses = nc.load_poses(root)
    lat0, lon0 = poses["lat0"], poses["lon0"]
    ll = lambda p: nc.common.enu_to_ll(lat0, lon0, float(p[0]), float(p[1]))
    nd = Path(nd)
    nd.mkdir(parents=True, exist_ok=True)
    nc.common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "VPAIR query poses (GNSS/INS)",
                            [{"t": float(k), "lat": ll(p)[0], "lon": ll(p)[1]} for k, p in enumerate(poses["en"])])
    mp = nd / "manifest.json"
    if mp.exists():
        m = json.loads(mp.read_text())
        if "truth.jsonl" not in m["tracks"]:
            m["tracks"].insert(0, "truth.jsonl")
            with open(mp, "w") as f:
                json.dump(m, f, indent=1)
    h = hashlib.sha256((nd / "truth.jsonl").read_bytes()).hexdigest()
    same = h == TRUTH_SHA256
    print(f"{'same as' if same else 'DIFFERENT from'} the committed run: {nd / 'truth.jsonl'}")
    return same


def main(default_out=HERE / "results" / "navdash"):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=str(DEFAULT_DATA), help="dir that contains vpair_sample/")
    ap.add_argument("--out", default=str(default_out))
    a = ap.parse_args()
    sys.exit(0 if write_truth(a.data, a.out) else 1)


if __name__ == "__main__":
    main()
