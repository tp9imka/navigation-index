"""Evaluate thermal => satellite fixes on the fetched Thermal-UAV subset.

Prior per frame: truth + PRIOR_OFFSET_M in a random direction, heading = GT yaw + N(0, 5 deg),
altitude = laser range from the metadata. Writes out/<tag>.jsonl (one row per frame x config)
and out/<tag>_summary.md.
"""
import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import cv2
import torch

from geom import GATES, frame_gsd_m, offset_latlon
from thermal_geoloc import EXTRACTORS, PREPROC, Localizer, OrthoMap

HERE = Path(__file__).resolve().parent
FALSE_FIX_M = 20.0
# Thermal-UAV frames are stored with gimbal roll 180: image top faces yaw + 180. Found by
# probing 8 day frames: offsets 0 / 90 / -90 gave 0 of 8 within 20 m, 180 gave 6 of 8.
CAMERA_YAW_OFFSET_DEG = 180.0


def load_frames(flights=None, limit=None, split="main"):
    man = json.loads((HERE / "data" / "manifest.json").read_text())
    cam = man["camera"]
    frames = [f for f in man["frames"] if (not flights or f["flight"] in flights)
              and split in ("all", f.get("split", "main"))]
    if limit:
        by = defaultdict(list)
        for f in frames:
            by[f["flight"]].append(f)
        frames = [f for fl in by.values() for f in fl[:limit]]
    return frames, cam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", nargs="*", default=list(EXTRACTORS))
    ap.add_argument("--preproc", nargs="*", default=list(PREPROC))
    ap.add_argument("--sgm", nargs="*", type=int, default=[], help="SGM input sizes, e.g. 512 110")
    ap.add_argument("--flights", nargs="*")
    ap.add_argument("--split", choices=["main", "heldout", "all"], default="main")
    ap.add_argument("--limit", type=int, help="frames per flight")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--prior-offset-m", type=float, default=100.0)
    ap.add_argument("--search-radius-m", type=float, default=150.0)
    ap.add_argument("--heading-sigma-deg", type=float, default=5.0)
    ap.add_argument("--heading-offset-deg", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--gate", choices=list(GATES), default="revised")
    ap.add_argument("--model", choices=["similarity", "homography"], default="similarity")
    ap.add_argument("--tag", default="results")
    args = ap.parse_args()

    frames, cam = load_frames(args.flights, args.limit, args.split)
    rng = random.Random(args.seed)
    priors = []
    for f in frames:
        plat, plon = offset_latlon(f["lat"], f["lon"], args.prior_offset_m, rng.uniform(0, 360))
        priors.append((plon, plat, f["yaw"] + CAMERA_YAW_OFFSET_DEG + args.heading_offset_deg + rng.gauss(0, args.heading_sigma_deg)))

    maps = {}
    configs = [(fe, pp) for fe in args.features for pp in args.preproc] + [("sgm", n) for n in args.sgm]
    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)
    rows = []
    torch.set_num_threads(8)
    for fe, pp in configs:
        if fe == "sgm":
            from sgm_baseline import SGMLocalizer
            loc = SGMLocalizer(device=args.device, input_px=pp)
        else:
            loc = Localizer(fe, device=args.device, model=args.model, gate=GATES[args.gate])
        warm = True
        t_cfg = time.time()
        for f, (plon, plat, head) in zip(frames, priors):
            if f["flight"] not in maps:
                maps[f["flight"]] = OrthoMap.open(HERE / "data" / "maps" / f"{f['flight']}.tif")
            gray = cv2.imread(str(HERE / f["path"]), cv2.IMREAD_GRAYSCALE)
            gsd = frame_gsd_m(f["rel_height"], cam["focal_len"], cam["cam_size"], gray.shape[1], gray.shape[0])
            kw = dict(truth_latlon=(f["lat"], f["lon"]))
            if fe != "sgm":
                kw["preproc"] = pp
            if warm:
                try:
                    loc.localize(gray, gsd, head, maps[f["flight"]], (plon, plat), args.search_radius_m, **kw)
                    warm = False
                except ValueError:
                    pass
            try:
                r = loc.localize(gray, gsd, head, maps[f["flight"]], (plon, plat), args.search_radius_m, **kw)
            except ValueError as e:
                # LightGlue's SIFT wrapper raises on some degenerate keypoint sets
                r = {"features": fe, "preproc": pp, "accepted": False, "fix": None, "err_m": None,
                     "reasons": [f"extractor error: {e}"], "t_total_s": float("nan")}
            r.update(gate=args.gate, flight=f["flight"], condition=f["condition"], frame=Path(f["path"]).name,
                     frame_gsd_m=round(gsd, 4), device=args.device)
            rows.append(r)
        print(f"{fe}/{pp}: {len(frames)} frames in {time.time() - t_cfg:.0f} s", flush=True)

    with open(out_dir / f"{args.tag}.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    import report
    report.main_tags([args.tag])


if __name__ == "__main__":
    main()
