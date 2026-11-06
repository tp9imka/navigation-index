"""Geolocate a nadir drone frame against a georeferenced orthophoto / satellite tile.

SuperPoint + LightGlue matches -> OpenCV homography -> frame centre in tile pixels
-> GeoTIFF geotransform -> lat/lon.

Unverified sketch: requires torch, lightglue (pip install -e cvg/LightGlue),
opencv-python, rasterio, numpy.

    python3 geolocalize.py --frame drone.jpg --tile ortho.tif [--truth LAT LON]
"""

import argparse

import cv2
import numpy as np
import rasterio
import torch
from lightglue import LightGlue, SuperPoint
from lightglue.utils import numpy_image_to_torch, rbd, read_image
from rasterio.warp import transform as warp_transform

import geo_math

MAX_KEYPOINTS = 2048
RANSAC_REPROJ_PX = 4.0
MIN_INLIERS = 25
ROTATIONS_K = (0, 1, 2, 3)  # SuperPoint is not rotation invariant: try 0/90/180/270 deg


def load_tile(path):
    with rasterio.open(path) as src:
        bands = src.read([1, 2, 3]) if src.count >= 3 else np.repeat(src.read([1]), 3, axis=0)
        img = np.transpose(bands, (1, 2, 0))
        if img.dtype != np.uint8:
            lo, hi = np.percentile(img, (2, 98))
            img = np.clip((img - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
        t = src.transform
        return img, (t.a, t.b, t.c, t.d, t.e, t.f), src.crs


def match(extractor, matcher, img0, img1, device):
    feats0 = extractor.extract(numpy_image_to_torch(img0).to(device))
    feats1 = extractor.extract(numpy_image_to_torch(img1).to(device))
    out = matcher({"image0": feats0, "image1": feats1})
    feats0, feats1, out = [rbd(x) for x in (feats0, feats1, out)]
    m = out["matches"]
    return feats0["keypoints"][m[:, 0]].cpu().numpy(), feats1["keypoints"][m[:, 1]].cpu().numpy()


def best_homography(extractor, matcher, frame, tile, device):
    best = None
    for k in ROTATIONS_K:
        rotated = np.ascontiguousarray(np.rot90(frame, k))
        p0, p1 = match(extractor, matcher, rotated, tile, device)
        if len(p0) < 4:
            continue
        H, mask = cv2.findHomography(p0, p1, cv2.USAC_MAGSAC, RANSAC_REPROJ_PX)
        if H is None:
            continue
        inliers = int(mask.sum())
        if best is None or inliers > best[1]:
            best = (H, inliers, rotated.shape[1], rotated.shape[0], k * 90)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", required=True)
    ap.add_argument("--tile", required=True)
    ap.add_argument("--truth", type=float, nargs=2, metavar=("LAT", "LON"))
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    extractor = SuperPoint(max_num_keypoints=MAX_KEYPOINTS).eval().to(device)
    matcher = LightGlue(features="superpoint").eval().to(device)

    frame = read_image(args.frame)
    tile, tile_transform, crs = load_tile(args.tile)

    with torch.inference_mode():
        best = best_homography(extractor, matcher, frame, tile, device)
    if best is None or best[1] < MIN_INLIERS:
        print(f"no reliable fix (inliers={0 if best is None else best[1]}, need {MIN_INLIERS})")
        return
    H, inliers, w, h, rot = best

    # The centre of a rotated frame is still the frame centre, so rotation needs no undo.
    x, y = geo_math.frame_center_to_world(H, w, h, tile_transform)
    if crs.is_geographic:
        lon, lat = x, y
    else:
        lons, lats = warp_transform(crs, "EPSG:4326", [x], [y])
        lon, lat = lons[0], lats[0]
    print(f"fix lat={lat:.6f} lon={lon:.6f} inliers={inliers} frame_rotation={rot}deg")
    if args.truth:
        print(f"error vs truth: {geo_math.haversine_m(lat, lon, *args.truth):.1f} m")


if __name__ == "__main__":
    main()
