"""Download the plate-solving inputs into data/ (stdlib only).

1. The 24 test images shipped in smroid/cedar-solve examples/data/medium_fov (8 of them are
   the ESA tetra3 images, CC BY-SA 3.0 IGO; the rest are released as tetra3 test images,
   see credits.txt there).
2. Real survey cutouts with a known WCS from NASA SkyView (Mellinger Red all-sky optical
   mosaic, (c) Axel Mellinger, research and personal non-commercial use), at seeded random
   sky pointings and roll angles, for two fields of view. The requested centre and rotation
   are the reference attitude.
3. JPL DE421 ephemeris (16 MB) for skyfield, used by position_fix_sim.py.
"""
import argparse
import concurrent.futures as cf
import json
import math
import os
import random
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CEDAR_REF = "v0.6.0"
CEDAR_RAW = f"https://raw.githubusercontent.com/smroid/cedar-solve/{CEDAR_REF}/examples/data/"
CEDAR_LIST = f"https://api.github.com/repos/smroid/cedar-solve/contents/examples/data/medium_fov?ref={CEDAR_REF}"
SKYVIEW = ("https://skyview.gsfc.nasa.gov/current/cgi/pskcall?Survey=Mellinger+Red"
           "&Position={ra:.4f},{dec:.4f}&Coordinates=J2000&Size={fov}&Pixels={px}"
           "&Rotation={rot:.2f}&Return=FITS")
DE421 = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp"
PIXELS = 1024
RETRY_WAIT_S = 20


def get(url, path, timeout=180, magic=None, retries=4):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    req = urllib.request.Request(url, headers={"User-Agent": "navigation-index-sample"})
    for attempt in range(retries):
        with urllib.request.urlopen(req, timeout=timeout) as r:
            blob = r.read()
        if magic is None or blob.startswith(magic):
            break
        # SkyView answers an HTML "Too Many Processes" page when overloaded
        time.sleep(RETRY_WAIT_S * (attempt + 1))
    else:
        raise RuntimeError("server did not return the expected file")
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, path)
    return path


def skyview_pointings(n, fovs, seed):
    rng = random.Random(seed)
    out = []
    for fov in fovs:
        for i in range(n):
            ra = rng.uniform(0, 360)
            dec = math.degrees(math.asin(rng.uniform(-1, 1)))
            rot = rng.uniform(0, 360)
            out.append({"name": f"sv_fov{fov:02d}_{i:02d}", "ra": ra, "dec": dec, "rot": rot,
                        "fov": fov, "pixels": PIXELS})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="SkyView cutouts per FOV")
    ap.add_argument("--fovs", default="12,20")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(os.path.join(DATA, "cedar"), exist_ok=True)
    os.makedirs(os.path.join(DATA, "skyview"), exist_ok=True)

    with urllib.request.urlopen(CEDAR_LIST, timeout=60) as r:
        names = [e["name"] for e in json.load(r) if e["name"].endswith(".jpg")]
    get(CEDAR_RAW + "credits.txt", os.path.join(DATA, "cedar", "credits.txt"))
    for n in names:
        get(CEDAR_RAW + "medium_fov/" + n, os.path.join(DATA, "cedar", n))
    print(f"cedar-solve test images: {len(names)}")

    pts = skyview_pointings(a.n, [int(x) for x in a.fovs.split(",")], a.seed)
    with open(os.path.join(DATA, "skyview", "pointings.json"), "w") as f:
        json.dump(pts, f, indent=1)

    def one(p):
        url = SKYVIEW.format(ra=p["ra"], dec=p["dec"], fov=p["fov"], px=p["pixels"], rot=p["rot"])
        try:
            get(url, os.path.join(DATA, "skyview", p["name"] + ".fits"), magic=b"SIMPLE")
            return None
        except Exception as e:  # network errors are reported, not fatal
            return f"{p['name']}: {e}"

    with cf.ThreadPoolExecutor(a.jobs) as ex:
        errs = [e for e in ex.map(one, pts) if e]
    print(f"SkyView cutouts: {len(pts) - len(errs)} of {len(pts)}")
    for e in errs:
        print("  failed", e)

    get(DE421, os.path.join(DATA, "de421.bsp"), timeout=600)
    print("de421.bsp ok")


if __name__ == "__main__":
    main()
