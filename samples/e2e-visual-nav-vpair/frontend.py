"""Expensive per-frame front end on the real VPAIR flight, cached to results/frontend.json.

1. Nadir VO (SIFT + RANSAC, ../relative-nav-benchmark/aerial) frame to frame, timed.
2. Map: VPAIR reference renders (nadir, north-up, rendered from orthophoto + elevation, so a
   different capture time than the flight) at their geo poses, plus the 200 distractor renders.
   A query never sees its own render (leave-one-out); `--strides` thins the map further.
3. Retrieval: DINOv2 ViT-S/14 GeM over the inscribed circle (../vpr-large-area/vpr.py) on the
   query rotated north-up with the recorded yaw; cosine top-k over the map.
4. Fine matching: ALIKED + LightGlue (../geoloc-license-clean) between the north-up query and each
   top-k tile; MAGSAC homography; the tile pixel under the query image centre is stored.

    python frontend.py --data <dir with vpair_sample/> [--device mps] [--top-k 5] [--strides 1 4]
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch

import nav_core as nc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "vpr-large-area"))
sys.path.insert(0, str(HERE.parent / "geoloc-license-clean"))
from geoloc import EXTRACTORS, MIN_INLIERS, RANSAC_REPROJ_PX, Localizer  # noqa: E402
from lightglue import LightGlue  # noqa: E402
from lightglue.utils import rbd  # noqa: E402
from run_nadir_vo import fit_attitude_model, similarity  # noqa: E402
from vpr import Dinov2Describer  # noqa: E402

VPR_CROP_PX = 600            # square around the image centre; the 300 px circle is valid at any yaw
VPR_IMG_PX = 224
MAX_KPTS = 2048
H_SCALE_RANGE = (0.67, 1.5)  # query and tile share altitude and camera: a homography far off scale 1 is wrong
CALIB_NEIGHBOURS = (-2, -1, 1, 2)
UTM32N = "EPSG:32632"


def north_up(img, yaw_rad):
    """Rotate a query north-up with the recorded yaw (sign found on the calibration frames, see README)."""
    return Localizer.prepare_query(None, img, 1.0, -math.degrees(yaw_rad), 1.0)


def centre_square(img, centre, side):
    c, r = int(round(centre[0] - side / 2)), int(round(centre[1] - side / 2))
    pad = cv2.copyMakeBorder(img, side, side, side, side, cv2.BORDER_CONSTANT)
    return pad[r + side:r + 2 * side, c + side:c + 2 * side]


def to_tensor(rgb, device):
    return torch.from_numpy(np.ascontiguousarray(rgb)).permute(2, 0, 1).float().div(255.0).to(device)


def distractor_en(names, lat0, lon0):
    """Distractor file names are UTM 32N east_north (VPAIR README); place them in the local frame."""
    from rasterio.warp import transform
    e = [float(n.split("_")[0]) for n in names]
    nn = [float(n.split("_")[1].split(".")[0]) for n in names]
    lon, lat = transform(UTM32N, "EPSG:4326", e, nn)
    return np.array([nc.common.ll_to_enu(lat0, lon0, la, lo) for la, lo in zip(lat, lon)])


def run_vo(root, names, att):
    sift = cv2.SIFT_create(nfeatures=3000)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    load = lambda n: cv2.cvtColor(cv2.imread(str(root / "queries" / n)), cv2.COLOR_BGR2GRAY)
    prev = load(names[0])
    h, w = prev.shape
    c = np.array([w / 2, h / 2])
    d_raw, inl, times, failed = [], [], [], 0
    for k in range(1, len(names)):
        t0 = time.perf_counter()
        cur = load(names[k])
        M, n = similarity(prev, cur, sift, matcher)
        if M is None:
            failed += 1
            M = np.hstack([np.eye(2), np.zeros((2, 1))])
        d_raw.append(np.linalg.solve(M[:, :2], c - M[:, 2]) - c)
        times.append(time.perf_counter() - t0)
        inl.append(n)
        prev = cur
    return np.array(d_raw), inl, times, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory containing vpair_sample/")
    ap.add_argument("--device", default=None)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--strides", type=int, nargs="+", default=[1, 4])
    ap.add_argument("--yaw-bias-deg", type=float, default=0.0, help="heading error applied to the north-up pre-rotation")
    ap.add_argument("--max-frames", type=int, default=0, help="debug: stop after this many queries")
    ap.add_argument("--out", default=str(HERE / "results" / "frontend.json"))
    a = ap.parse_args()
    root = Path(a.data) / "vpair_sample"
    P = nc.load_poses(root)
    names, att, en = P["names"], P["att"], P["en"]
    nq, nt = len(names), len(P["tile_names"])
    N = nc.CALIB_FRAMES
    t_all = time.perf_counter()

    print("VO ...", flush=True)
    d_raw, vo_inl, vo_t, vo_failed = run_vo(root, names, att)
    gt_steps = np.diff(en, axis=0)
    dtan = np.diff(np.tan(att[:, :2]), axis=0)
    body_gt = np.array([nc.r_yaw(att[k, 2]).T @ gt_steps[k] for k in range(len(gt_steps))])
    _, C, hagl, Pm, refl = fit_attitude_model(d_raw[:N], dtan[:N], body_gt[:N])

    device = a.device or ("mps" if torch.backends.mps.is_available() else "cpu")
    print("map descriptors on", device, flush=True)
    dist_names = sorted(p.name for p in (root / "distractors").glob("*.png"))
    tile_paths = [root / "reference_views" / n for n in P["tile_names"]] + [root / "distractors" / n for n in dist_names]
    tile_en = np.vstack([P["tile_en"], distractor_en(dist_names, P["lat0"], P["lon0"])])
    desc = Dinov2Describer(device=device)
    t0 = time.perf_counter()
    tiles = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in tile_paths]
    th, tw = tiles[0].shape[:2]
    tc = np.array([(tw - 1) / 2, (th - 1) / 2])
    small = [cv2.resize(centre_square(t, tc, VPR_CROP_PX), (VPR_IMG_PX, VPR_IMG_PX), interpolation=cv2.INTER_AREA) for t in tiles]
    tile_desc = desc.describe(np.stack(small))["gem"]
    t_map_desc = time.perf_counter() - t0
    depth_med = float(np.median([np.median(np.load(root / "reference_views" / f"depth_{n[:-4]}.npy")) for n in P["tile_names"][:20]]))

    extractor = EXTRACTORS["aliked"](MAX_KPTS).eval().to(device)
    lg = LightGlue(features="aliked").eval().to(device)
    tile_feat = {}

    def tile_features(j):
        if j not in tile_feat:
            with torch.inference_mode():
                tile_feat[j] = extractor.extract(to_tensor(tiles[j], device), resize=None)
        return tile_feat[j]

    def depth_at(j, p):
        if j >= nt:
            return depth_med
        d = np.load(root / "reference_views" / f"depth_{P['tile_names'][j][:-4]}.npy", mmap_mode="r")
        c = int(np.clip(round(p[0]), 0, d.shape[1] - 1))
        r = int(np.clip(round(p[1]), 0, d.shape[0] - 1))
        return float(d[r, c])

    queries, matches, timing = [], {}, {"describe_s": [], "search_s": [], "match_s": [], "prep_s": []}
    allowed = {s: nc.map_tiles(nt, s) for s in a.strides}
    for k in range(a.max_frames or nq):
        t0 = time.perf_counter()
        img = cv2.cvtColor(cv2.imread(str(root / "queries" / names[k])), cv2.COLOR_BGR2RGB)
        qimg, qmask, qcentre = north_up(img, att[k, 2] + math.radians(a.yaw_bias_deg))
        with torch.inference_mode():
            f0 = extractor.extract(to_tensor(qimg, device), resize=None)
        t1 = time.perf_counter()
        crop = cv2.resize(centre_square(qimg, qcentre, VPR_CROP_PX), (VPR_IMG_PX, VPR_IMG_PX), interpolation=cv2.INTER_AREA)
        qd = desc.describe(crop[None])["gem"][0]
        t2 = time.perf_counter()
        sims = tile_desc @ qd
        top = {}
        for s, keep in allowed.items():
            ids = [j for j in keep if j != k] + list(range(nt, len(tiles)))
            top[str(s)] = [int(x) for x in np.array(ids)[np.argsort(-sims[ids])[:a.top_k]]]
        t3 = time.perf_counter()
        todo = sorted({j for v in top.values() for j in v} |
                      ({k + o for o in CALIB_NEIGHBOURS if 0 <= k + o < nt} if k < N else set()))
        kp0 = rbd(f0)["keypoints"].cpu().numpy()
        tm = []
        for j in todo:
            tj = time.perf_counter()
            f1 = tile_features(j)
            with torch.inference_mode():
                out = rbd(lg({"image0": f0, "image1": f1}))
            m = out["matches"].cpu().numpy()
            kp1 = rbd(f1)["keypoints"].cpu().numpy()
            keep = qmask[np.clip(kp0[m[:, 0], 1].astype(int), 0, qmask.shape[0] - 1),
                         np.clip(kp0[m[:, 0], 0].astype(int), 0, qmask.shape[1] - 1)] > 0
            m = m[keep]
            rec = {"matches": int(len(m)), "inliers": 0, "p_tile": None, "depth": None, "h_scale": None}
            if len(m) >= 4:
                H, inl = cv2.findHomography(kp0[m[:, 0]], kp1[m[:, 1]], cv2.USAC_MAGSAC, RANSAC_REPROJ_PX)
                if H is not None:
                    p = H @ np.array([qcentre[0], qcentre[1], 1.0])
                    p = p[:2] / p[2]
                    J = H[:2, :2] - np.outer(p, H[2, :2])  # local Jacobian at the centre, up to 1/w
                    rec.update(inliers=int(inl.sum()), p_tile=[round(float(x), 2) for x in p],
                               h_scale=round(float(math.sqrt(abs(np.linalg.det(J))) / abs(H[2] @ [qcentre[0], qcentre[1], 1.0])), 4),
                               depth=round(depth_at(j, p), 2))
            dt = time.perf_counter() - tj
            rec["t_s"] = round(dt, 4)
            matches[f"{k}:{j}"] = rec
            tm.append((j, dt))
        timing["prep_s"].append(t1 - t0)
        timing["describe_s"].append(t2 - t1)
        timing["search_s"].append(t3 - t2)
        timing["match_s"].append({str(s): sum(dt for j, dt in tm if j in v) for s, v in top.items()})
        queries.append({"k": k, "top": {s: [[j, round(float(sims[j]), 4)] for j in v] for s, v in top.items()}})
        if k % 20 == 0:
            print(f"  frame {k}: top1 {top[str(a.strides[0])][0]} pairs {len(todo)} {time.perf_counter() - t0:.2f} s", flush=True)

    tsum = lambda xs: {"median_s": round(float(np.median(xs)), 4), "p95_s": round(float(np.percentile(xs, 95)), 4)}
    out = {
        "dataset": f"VPAIR sample (Zenodo 6473989): {nq} queries 800x600, {nt} reference renders + {len(dist_names)} distractors",
        "device": device, "torch": torch.__version__, "yaw_bias_deg": a.yaw_bias_deg, "top_k": a.top_k, "strides": a.strides,
        "min_inliers": MIN_INLIERS, "h_scale_range": H_SCALE_RANGE,
        "vo": {"d_raw_px": d_raw.round(4).tolist(), "C": C.tolist(), "hagl_m": float(hagl), "P": Pm.tolist(),
               "mount_reflection": bool(refl), "failed_pairs": vo_failed, "median_inliers": int(np.median(vo_inl)),
               "time": tsum(vo_t)},
        "tiles": {"names": P["tile_names"] + dist_names, "en": tile_en.round(3).tolist(), "n_renders": nt,
                  "centre_px": tc.tolist(), "distractor_depth_m": depth_med},
        "queries": queries, "matches": matches,
        "timing": {"map_descriptors_s": round(t_map_desc, 2), "map_tiles": len(tiles),
                   "prep_query_s": tsum(timing["prep_s"]), "describe_query_s": tsum(timing["describe_s"]),
                   "search_s": tsum(timing["search_s"]),
                   "match_topk_s": {str(s): tsum([x[str(s)] for x in timing["match_s"]]) for s in a.strides},
                   "match_pair_s": tsum([m["t_s"] for m in matches.values()]),
                   "wall_total_s": round(time.perf_counter() - t_all, 1),
                   "host": nc.common.RunStats().done()["host"]},
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out))
    print("wrote", a.out, "pairs", len(matches), "wall", out["timing"]["wall_total_s"], "s")


if __name__ == "__main__":
    main()
