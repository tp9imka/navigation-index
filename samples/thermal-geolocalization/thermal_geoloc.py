"""Thermal UAV frame => RGB satellite GeoTIFF => lat/lon with license-clean local features.

Extractors: ALIKED (BSD-3), DISK (Apache-2.0), SIFT (OpenCV). Matcher: LightGlue (Apache-2.0).
Modality bridging is a preprocessing choice applied to both images:
  raw   - thermal 8-bit as delivered, map converted to luma
  clahe - CLAHE on both
  grad  - blurred Sobel gradient magnitude on both (sign-free, so hot/cold inversions cancel)
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

from geom import Gate, affine_scale_rot, haversine_m

EXTRACTORS = {
    "aliked": lambda n: ALIKED(max_num_keypoints=n),
    "disk": lambda n: DISK(max_num_keypoints=n),
    "sift": lambda n: SIFT(max_num_keypoints=n),
}
PREPROC = ("raw", "clahe", "grad")
RANSAC_REPROJ_PX = 4.0
RANSAC_ITERS = 5000
WORK_MAX_SIDE_PX = 1024
BORDER_ERODE_PX = 9
CLAHE_CLIP = 3.0
CLAHE_TILE = 8
GRAD_BLUR_SIGMA = 1.2
GRAD_CLIP_PCT = 99.0


def preprocess(gray, mode):
    if mode == "raw":
        return gray
    if mode == "clahe":
        return cv2.createCLAHE(CLAHE_CLIP, (CLAHE_TILE, CLAHE_TILE)).apply(gray)
    if mode == "grad":
        g = cv2.GaussianBlur(gray.astype(np.float32), (0, 0), GRAD_BLUR_SIGMA)
        mag = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
        hi = np.percentile(mag, GRAD_CLIP_PCT) + 1e-6
        return np.clip(mag / hi * 255.0, 0, 255).astype(np.uint8)
    raise ValueError(mode)


@dataclass
class OrthoMap:
    gray: np.ndarray
    transform: rasterio.Affine
    crs: object

    @classmethod
    def open(cls, path):
        with rasterio.open(path) as src:
            rgb = src.read([1, 2, 3]).transpose(1, 2, 0)
            return cls(cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2GRAY), src.transform, src.crs)

    @property
    def gsd(self):
        return abs(self.transform.a)

    def lonlat_to_world(self, lon, lat):
        xs, ys = warp_transform("EPSG:4326", self.crs, [lon], [lat])
        return xs[0], ys[0]

    def world_to_lonlat(self, x, y):
        lons, lats = warp_transform(self.crs, "EPSG:4326", [x], [y])
        return lons[0], lats[0]

    def window(self, lon, lat, half_m, work_gsd):
        """Map crop around (lon, lat) resampled to work_gsd. Returns image, col0, row0, scale k."""
        x, y = self.lonlat_to_world(lon, lat)
        c0, r0 = ~self.transform * (x - half_m, y + half_m)
        c1, r1 = ~self.transform * (x + half_m, y - half_m)
        c0, r0 = max(int(c0), 0), max(int(r0), 0)
        c1, r1 = min(int(c1), self.gray.shape[1]), min(int(r1), self.gray.shape[0])
        k = self.gsd / work_gsd
        img = cv2.resize(self.gray[r0:r1, c0:c1], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        return img, c0, r0, k


def north_up(gray, frame_gsd, heading_deg, work_gsd):
    """Rotate a frame north-up and resample to work_gsd. Returns image, valid mask, centre px, matrix."""
    h0, w0 = gray.shape[:2]
    s = frame_gsd / work_gsd
    cu, cv_ = (w0 - 1) / 2, (h0 - 1) / 2
    if s < 1:
        gray = cv2.resize(gray, (max(1, round(w0 * s)), max(1, round(h0 * s))), interpolation=cv2.INTER_AREA)
        sx = gray.shape[1] / w0
        cu, cv_ = (cu + 0.5) * sx - 0.5, (cv_ + 0.5) * sx - 0.5
        s /= sx
    h, w = gray.shape[:2]
    # image y points down, so a frame whose top faces heading needs a +heading (CCW) rotation in cv2
    m = cv2.getRotationMatrix2D((w / 2, h / 2), heading_deg, s)
    corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], float) @ m.T
    x0, y0 = corners.min(0)
    x1, y1 = corners.max(0)
    m[:, 2] -= (x0, y0)
    size = (int(math.ceil(x1 - x0)), int(math.ceil(y1 - y0)))
    img = cv2.warpAffine(gray, m, size, flags=cv2.INTER_LINEAR)
    mask = cv2.warpAffine(np.full((h, w), 255, np.uint8), m, size, flags=cv2.INTER_NEAREST)
    mask = cv2.erode(mask, np.ones((BORDER_ERODE_PX, BORDER_ERODE_PX), np.uint8))
    return img, mask, m @ np.array([cu, cv_, 1.0])


def to_tensor(gray, device):
    return torch.from_numpy(np.repeat(gray[None], 3, 0)).float().div(255.0).to(device)


class Localizer:
    def __init__(self, features="aliked", max_kpts=2048, device="cpu", gate=None, model="similarity"):
        self.features = features
        self.model = model
        self.device = torch.device(device)
        self.extractor = EXTRACTORS[features](max_kpts).eval().to(self.device)
        self.matcher = LightGlue(features=features).eval().to(self.device)
        self.gate = gate or Gate()

    def localize(self, thermal_gray, frame_gsd, heading_deg, ortho, prior_lonlat, search_radius_m,
                 preproc="raw", truth_latlon=None):
        t0 = time.perf_counter()
        footprint_m = math.hypot(*thermal_gray.shape[:2]) * frame_gsd
        half = footprint_m / 2 + search_radius_m
        work_gsd = max(ortho.gsd, 2 * half / WORK_MAX_SIDE_PX, frame_gsd)
        ref, c0, r0, k = ortho.window(*prior_lonlat, half, work_gsd)
        query, qmask, qcentre = north_up(thermal_gray, frame_gsd, heading_deg, work_gsd)
        query, ref = preprocess(query, preproc), preprocess(ref, preproc)
        query[qmask == 0] = 0
        t_prep = time.perf_counter()

        with torch.inference_mode():
            f0 = self.extractor.extract(to_tensor(query, self.device), resize=None)
            f1 = self.extractor.extract(to_tensor(ref, self.device), resize=None)
            out = self.matcher({"image0": f0, "image1": f1})
        f0, f1, out = rbd(f0), rbd(f1), rbd(out)
        kp0, kp1 = f0["keypoints"].cpu().numpy(), f1["keypoints"].cpu().numpy()
        m = out["matches"].cpu().numpy()
        keep = qmask[np.clip(kp0[m[:, 0], 1].astype(int), 0, qmask.shape[0] - 1),
                     np.clip(kp0[m[:, 0], 0].astype(int), 0, qmask.shape[1] - 1)] > 0
        m = m[keep]
        t_match = time.perf_counter()

        res = {"features": self.features, "preproc": preproc, "model": self.model, "matches": int(len(m)), "inliers": 0,
               "accepted": False, "reasons": [], "fix": None, "err_m": None, "work_gsd_m": round(work_gsd, 3)}
        H = None
        if len(m) >= 4:
            if self.model == "homography":
                H, inl = cv2.findHomography(kp0[m[:, 0]], kp1[m[:, 1]], cv2.USAC_MAGSAC, RANSAC_REPROJ_PX)
            else:
                # Query is already north-up at map GSD, so 4 DOF suffice; a full homography fit on a
                # small correct cluster picks up a spurious perspective term
                A, inl = cv2.estimateAffinePartial2D(kp0[m[:, 0]], kp1[m[:, 1]], method=cv2.RANSAC,
                                                     ransacReprojThreshold=RANSAC_REPROJ_PX,
                                                     maxIters=RANSAC_ITERS, confidence=0.999)
                H = None if A is None else np.vstack([A, [0.0, 0.0, 1.0]])
            res["inliers"] = int(inl.sum()) if inl is not None else 0
        if H is not None:
            p = H @ np.array([qcentre[0], qcentre[1], 1.0])
            # keypoints and cv2 put integers on pixel centres; the affine puts them on corners
            col = c0 + (p[0] / p[2] + 0.5) / k
            row = r0 + (p[1] / p[2] + 0.5) / k
            lon, lat = ortho.world_to_lonlat(*(ortho.transform * (col, row)))
            res["fix"] = (lat, lon)
            sc, rot, _ = affine_scale_rot(H.tolist())
            res["h_scale"], res["h_rot_deg"] = round(sc, 3), round(rot, 2)
            shift = haversine_m(prior_lonlat[1], prior_lonlat[0], lat, lon)
            ok, reasons = self.gate.check(res["inliers"], res["matches"], H.tolist(), shift, search_radius_m,
                                          math.hypot(*query.shape[:2]) / 2)
            res["accepted"], res["reasons"] = ok, reasons
            if truth_latlon is not None:
                res["err_m"] = haversine_m(truth_latlon[0], truth_latlon[1], lat, lon)
        else:
            res["reasons"] = ["no homography"]
        res["t_prep_s"] = round(t_prep - t0, 3)
        res["t_match_s"] = round(t_match - t_prep, 3)
        res["t_total_s"] = round(time.perf_counter() - t0, 3)
        return res
