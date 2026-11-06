"""Build an offline test pair from one public OpenAerialMap orthophoto (CC-BY 4.0).

map:   the orthophoto read at a coarse overview (~0.4 m/px) => data/map_tile.tif (GeoTIFF)
frame: a finer (~0.2 m/px) window of the same orthophoto, rotated, perspective-warped,
       re-lit, blurred and noised => data/drone_frame.jpg
truth: the ground point under the frame centre => data/pair.json, with a prior offset by
       --prior-offset-m to stand in for INS drift.

Both images come from the same survey, so this checks the pipeline and geometry end to
end; it is not a cross-season or cross-sensor test.

    python3 make_test_pair.py                     # defaults below, needs internet once
    python3 make_test_pair.py --yaw-deg 60 --out data/yaw60
"""

import argparse
import json
import math
import os

import cv2
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform as warp_transform
from rasterio.windows import Window

# OpenAerialMap: "Tbilisi (GE) - Saburtalo", SJRC F22s Pro, 2023-10-08, CC-BY 4.0, EPSG:3857 COG
DEFAULT_URL = ("https://oin-hotosm-temp.s3.us-east-1.amazonaws.com/"
               "6523b171ceb34f0001f3742f/0/6523b171ceb34f0001f37430.tif")
MAP_DECIMATION = 4          # native 0.1 m (EPSG:3857 units) => 0.4 m map
FRAME_DECIMATION = 2        # => 0.2 m frame, 2x finer than the map, like a low drone
FRAME_W, FRAME_H = 1600, 1200
SEED = 3


def read_decimated(src, window, factor):
    out_shape = (src.count, int(window.height // factor), int(window.width // factor))
    img = src.read(window=window, out_shape=out_shape, resampling=Resampling.average)
    t = src.window_transform(window) * rasterio.Affine.scale(window.width / out_shape[2],
                                                             window.height / out_shape[1])
    return np.transpose(img[:3], (1, 2, 0)), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--out", default="data")
    ap.add_argument("--center-frac", type=float, nargs=2, default=(0.45, 0.55),
                    help="frame centre as a fraction of the ortho width/height")
    ap.add_argument("--yaw-deg", type=float, default=25.0)
    ap.add_argument("--tilt", type=float, default=0.08, help="perspective strength (0 = nadir)")
    ap.add_argument("--prior-offset-m", type=float, default=60.0)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rng = np.random.default_rng(SEED)

    with rasterio.open(args.url) as src:
        crs = src.crs
        full = Window(0, 0, src.width, src.height)
        map_img, map_t = read_decimated(src, full, MAP_DECIMATION)
        with rasterio.open(os.path.join(args.out, "map_tile.tif"), "w", driver="GTiff",
                           width=map_img.shape[1], height=map_img.shape[0], count=3,
                           dtype="uint8", crs=crs, transform=map_t, compress="deflate") as dst:
            dst.write(np.transpose(map_img, (2, 0, 1)))

        # source window large enough to hold the rotated frame
        side = int(math.hypot(FRAME_W, FRAME_H) * FRAME_DECIMATION) + 64
        cx, cy = args.center_frac[0] * src.width, args.center_frac[1] * src.height
        win = Window(int(cx - side / 2), int(cy - side / 2), side, side)
        patch, patch_t = read_decimated(src, win, FRAME_DECIMATION)

    ph, pw = patch.shape[:2]
    # frame corners in patch pixels: a rotated rectangle around the patch centre, then a tilt
    c, s = math.cos(math.radians(args.yaw_deg)), math.sin(math.radians(args.yaw_deg))
    hw, hh = FRAME_W / 2, FRAME_H / 2
    corners = []
    for (u, v), k in zip([(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)], [1, 1, -1, -1]):
        shrink = 1 + k * args.tilt  # far edge looks shorter in a forward-tilted camera
        corners.append((pw / 2 + c * u * shrink - s * v, ph / 2 + s * u * shrink + c * v))
    dst_corners = np.float32([(0, 0), (FRAME_W, 0), (FRAME_W, FRAME_H), (0, FRAME_H)])
    H_patch_to_frame = cv2.getPerspectiveTransform(np.float32(corners), dst_corners)
    frame = cv2.warpPerspective(patch, H_patch_to_frame, (FRAME_W, FRAME_H),
                                flags=cv2.INTER_LINEAR)

    frame = frame.astype(np.float32) * 0.85 + 18                      # exposure / gain change
    frame = cv2.GaussianBlur(frame, (0, 0), 1.2)
    frame += rng.normal(0, 4, frame.shape)
    frame = np.clip(frame, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(args.out, "drone_frame.jpg"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, 85])

    # truth = ground point under the frame centre (pixel-centre convention, +0.5)
    H_inv = np.linalg.inv(H_patch_to_frame)
    q = H_inv @ np.array([FRAME_W / 2, FRAME_H / 2, 1.0])
    px, py = q[0] / q[2], q[1] / q[2]
    wx, wy = patch_t * (px, py)
    lons, lats = warp_transform(crs, "EPSG:4326", [wx], [wy])
    truth = (lats[0], lons[0])
    m_per_deg = 111_320.0
    bearing = rng.uniform(0, 2 * math.pi)
    prior = (truth[0] + args.prior_offset_m * math.cos(bearing) / m_per_deg,
             truth[1] + args.prior_offset_m * math.sin(bearing)
             / (m_per_deg * math.cos(math.radians(truth[0]))))
    meta = {"source": args.url, "license": "CC-BY 4.0 (OpenAerialMap contributors)",
            "map_res_m": abs(map_t.a), "frame_res_m": abs(patch_t.a), "yaw_deg": args.yaw_deg,
            "tilt": args.tilt, "truth_latlon": truth, "prior_latlon": prior,
            "prior_offset_m": args.prior_offset_m}
    with open(os.path.join(args.out, "pair.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"map {map_img.shape[1]}x{map_img.shape[0]} px @ {abs(map_t.a):.2f} m, "
          f"frame {FRAME_W}x{FRAME_H} px @ {abs(patch_t.a):.2f} m (EPSG:3857 units)")
    print(f"--truth {truth[0]:.7f} {truth[1]:.7f}  --prior {prior[0]:.7f} {prior[1]:.7f}")


if __name__ == "__main__":
    main()
