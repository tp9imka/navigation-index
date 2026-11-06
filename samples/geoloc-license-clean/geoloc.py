"""Drone frame => georeferenced orthophoto => lat/lon, with permissively licensed parts only.

Extractors: ALIKED (BSD-3-Clause), DISK (Apache-2.0), SIFT (OpenCV, Apache-2.0).
Matcher: LightGlue weights for those three (Apache-2.0). SuperPoint is deliberately absent.
"""
import math
import time
from dataclasses import dataclass

import cv2
import numpy as np
import rasterio
import torch
from lightglue import ALIKED, DISK, SIFT, LightGlue
from lightglue.utils import rbd
from rasterio.warp import transform as warp_transform

EXTRACTORS = {
    "aliked": lambda n: ALIKED(max_num_keypoints=n),
    "disk": lambda n: DISK(max_num_keypoints=n),
    "sift": lambda n: SIFT(max_num_keypoints=n),
}
MIN_INLIERS = 25
RANSAC_REPROJ_PX = 4.0
WORK_MAX_SIDE_PX = 1024
BORDER_ERODE_PX = 7


@dataclass
class OrthoMap:
    rgb: np.ndarray
    transform: rasterio.Affine
    crs: object

    @classmethod
    def open(cls, path):
        with rasterio.open(path) as src:
            return cls(np.ascontiguousarray(src.read([1, 2, 3]).transpose(1, 2, 0)), src.transform, src.crs)

    @property
    def gsd(self):
        return abs(self.transform.a)

    def world_to_px(self, x, y):
        col, row = ~self.transform * (x, y)
        return col, row

    def px_to_world(self, col, row):
        return self.transform * (col, row)

    def lonlat_to_world(self, lon, lat):
        xs, ys = warp_transform("EPSG:4326", self.crs, [lon], [lat])
        return xs[0], ys[0]

    def world_to_lonlat(self, x, y):
        lons, lats = warp_transform(self.crs, "EPSG:4326", [x], [y])
        return lons[0], lats[0]


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def to_tensor(rgb):
    return torch.from_numpy(rgb).permute(2, 0, 1).float().div(255.0)


class Localizer:
    def __init__(self, features="aliked", max_kpts=2048):
        self.features = features
        self.extractor = EXTRACTORS[features](max_kpts).eval()
        self.matcher = LightGlue(features=features).eval()

    def prepare_query(self, frame_rgb, frame_gsd, heading_deg, work_gsd):
        """Rotate the frame north-up and resample it to work_gsd. Returns image, valid mask, centre px."""
        h0, w0 = frame_rgb.shape[:2]
        s = frame_gsd / work_gsd
        cu, cv = (w0 - 1) / 2, (h0 - 1) / 2
        if s < 1:
            # warpAffine has no area filter: downsample first or a 10x shrink aliases the texture away
            frame_rgb = cv2.resize(frame_rgb, (max(1, round(w0 * s)), max(1, round(h0 * s))),
                                   interpolation=cv2.INTER_AREA)
            sx = frame_rgb.shape[1] / w0
            cu, cv = (cu + 0.5) * sx - 0.5, (cv + 0.5) * sx - 0.5
            s /= sx
        h, w = frame_rgb.shape[:2]
        # Image y points down, so a camera yawed clockwise by heading needs a +heading (CCW) rotation in cv2.
        m = cv2.getRotationMatrix2D((w / 2, h / 2), heading_deg, s)
        corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], float) @ m.T
        x0, y0 = corners.min(0)
        x1, y1 = corners.max(0)
        m[:, 2] -= (x0, y0)
        size = (int(math.ceil(x1 - x0)), int(math.ceil(y1 - y0)))
        img = cv2.warpAffine(frame_rgb, m, size, flags=cv2.INTER_LINEAR)
        mask = cv2.warpAffine(np.full((h, w), 255, np.uint8), m, size, flags=cv2.INTER_NEAREST)
        mask = cv2.erode(mask, np.ones((BORDER_ERODE_PX, BORDER_ERODE_PX), np.uint8))
        centre = m @ np.array([cu, cv, 1.0])
        return img, mask, centre

    def localize(self, frame_rgb, frame_gsd, heading_deg, ortho: OrthoMap, prior_lonlat, search_radius_m,
                 min_work_gsd=0.0):
        t0 = time.perf_counter()
        footprint_m = math.hypot(*frame_rgb.shape[:2]) * frame_gsd
        half = footprint_m / 2 + search_radius_m
        work_gsd = max(ortho.gsd, 2 * half / WORK_MAX_SIDE_PX, frame_gsd, min_work_gsd)
        px, py = ortho.lonlat_to_world(*prior_lonlat)
        c0, r0 = ortho.world_to_px(px - half, py + half)
        c1, r1 = ortho.world_to_px(px + half, py - half)
        c0, r0 = max(int(c0), 0), max(int(r0), 0)
        c1, r1 = min(int(c1), ortho.rgb.shape[1]), min(int(r1), ortho.rgb.shape[0])
        crop = ortho.rgb[r0:r1, c0:c1]
        k = ortho.gsd / work_gsd
        ref = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        query, qmask, qcentre = self.prepare_query(frame_rgb, frame_gsd, heading_deg, work_gsd)
        t_prep = time.perf_counter()

        with torch.inference_mode():
            f0 = self.extractor.extract(to_tensor(query), resize=None)
            f1 = self.extractor.extract(to_tensor(ref), resize=None)
            out = self.matcher({"image0": f0, "image1": f1})
        f0, f1, out = rbd(f0), rbd(f1), rbd(out)
        kp0 = f0["keypoints"].numpy()
        kp1 = f1["keypoints"].numpy()
        m = out["matches"].numpy()
        keep = qmask[np.clip(kp0[m[:, 0], 1].astype(int), 0, qmask.shape[0] - 1),
                     np.clip(kp0[m[:, 0], 0].astype(int), 0, qmask.shape[1] - 1)] > 0
        m = m[keep]
        t_match = time.perf_counter()

        res = {"features": self.features, "kpts_query": len(kp0), "kpts_ref": len(kp1),
               "matches": int(len(m)), "inliers": 0, "fix": None,
               "work_gsd_m": round(work_gsd, 3), "ref_px": list(ref.shape[:2][::-1]),
               "query_px": list(query.shape[:2][::-1])}
        if len(m) >= 4:
            H, inl = cv2.findHomography(kp0[m[:, 0]], kp1[m[:, 1]], cv2.USAC_MAGSAC, RANSAC_REPROJ_PX)
            n_inl = int(inl.sum()) if inl is not None else 0
            res["inliers"] = n_inl
            if H is not None and n_inl >= MIN_INLIERS:
                p = H @ np.array([qcentre[0], qcentre[1], 1.0])
                # keypoints and cv2 put integers on pixel centres; the affine puts them on corners
                col = c0 + (p[0] / p[2] + 0.5) / k
                row = r0 + (p[1] / p[2] + 0.5) / k
                x, y = ortho.px_to_world(col, row)
                res["fix"] = ortho.world_to_lonlat(x, y)
        t_end = time.perf_counter()
        res["t_prep_s"] = round(t_prep - t0, 3)
        res["t_match_s"] = round(t_match - t_prep, 3)
        res["t_total_s"] = round(t_end - t0, 3)
        return res
