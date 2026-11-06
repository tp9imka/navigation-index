"""Coarse visual place recognition over a large geo-referenced orthophoto, license-clean parts only.

Tile grid + renderer (geo math), descriptors (DINOv2 CLS / GeM / VLAD, and a classic rotation-invariant
ring histogram), and a cosine-similarity index (FAISS IndexFlatIP, numpy fallback).

Yaw convention is the one of ../geoloc-license-clean: a frame made by synth_frames.make_frame with yaw
psi becomes north-up after cv2.getRotationMatrix2D(centre, +psi, 1), and Localizer.localize takes
heading=psi. Tiles rendered at yaw psi look like such a frame.
"""
import math
import time

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from geo import recall_at, tile_centres  # noqa: F401  re-exported for the runners
from index import TileIndex  # noqa: F401


DINOV2_REPO = "facebookresearch/dinov2:7764ea0f912e53c92e82eb78a2a1631e92725fc8"
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], np.float32)
PATCH = 14
GEM_P = 3.0
RING_COUNT = 4
RING_BINS = 8


# ---------------------------------------------------------------- geo math

def yaw_matrix(yaw_deg):
    """2x2 map from frame pixel offsets to source pixel offsets (synth_frames.make_frame convention)."""
    t = math.radians(yaw_deg)
    return np.array([[math.cos(t), math.sin(t)], [-math.sin(t), math.cos(t)]])


def render_tile(map_rgb, map_gsd, centre_px, tile_m, out_px, yaw_deg=0.0):
    """Square tile of tile_m metres around centre_px (col, row in map_rgb), resampled to out_px.

    map_rgb should already be close to tile_m / out_px metres per pixel: warpAffine has no area filter.
    """
    s = tile_m / out_px / map_gsd
    a = yaw_matrix(yaw_deg) * s
    c = (out_px - 1) / 2
    t = np.asarray(centre_px, float) - a @ np.array([c, c])
    m = np.hstack([a, t[:, None]])
    return cv2.warpAffine(map_rgb, m, (out_px, out_px), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REFLECT)


def rotate_square(img, angle_deg):
    """Rotate about the centre with cv2's convention (positive = counter-clockwise on screen)."""
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D(((w - 1) / 2, (h - 1) / 2), angle_deg, 1.0)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def query_crop(frame_rgb, frame_gsd, ground_m, out_px):
    """Central square of ground_m metres (or the largest that fits) from a frame, area-resampled to out_px."""
    h, w = frame_rgb.shape[:2]
    side = min(int(round(ground_m / frame_gsd)), h, w)
    r0, c0 = (h - side) // 2, (w - side) // 2
    crop = frame_rgb[r0:r0 + side, c0:c0 + side]
    interp = cv2.INTER_AREA if side > out_px else cv2.INTER_LINEAR
    return cv2.resize(crop, (out_px, out_px), interpolation=interp), side * frame_gsd


# ---------------------------------------------------------------- descriptors

def circle_patch_mask(n):
    """Weights over an n x n patch grid: 1 inside the inscribed circle, 0 outside (corners hold rotation fill)."""
    c = (np.arange(n) + 0.5) / n - 0.5
    gx, gy = np.meshgrid(c, c)
    return (gx ** 2 + gy ** 2 <= 0.25).astype(np.float32).ravel()


def best_device():
    if torch.backends.mps.is_available():
        return "mps"
    return "cuda" if torch.cuda.is_available() else "cpu"


class Dinov2Describer:
    """DINOv2 backbone (Apache-2.0) with three heads: CLS token, GeM over patches, VLAD over patches."""

    def __init__(self, arch="dinov2_vits14", img_px=224, device=None, vlad_k=16):
        self.device = device or best_device()
        self.model = torch.hub.load(DINOV2_REPO, arch, verbose=False).eval().to(self.device)
        self.img_px = img_px
        self.n = img_px // PATCH
        self.mask = torch.from_numpy(circle_patch_mask(self.n)).to(self.device)
        self.vlad_k = vlad_k
        self.centroids = None  # (k, d) torch tensor, set by fit_vlad

    @torch.inference_mode()
    def patch_tokens(self, imgs):
        """imgs: (B, H, W, 3) uint8 at img_px. Returns (cls (B, d), patches (B, n*n, d)) L2-normalised per token."""
        x = (np.asarray(imgs, np.float32) / 255.0 - IMAGENET_MEAN) / IMAGENET_STD
        x = torch.from_numpy(x).permute(0, 3, 1, 2).to(self.device)
        out = self.model.forward_features(x)
        return out["x_norm_clstoken"].float(), F.normalize(out["x_norm_patchtokens"].float(), dim=-1)

    def heads(self, cls, patches):
        m = self.mask[None, :, None]
        gem = ((patches.clamp(min=1e-6) ** GEM_P) * m).sum(1) / m.sum(1)
        gem = gem ** (1 / GEM_P)
        res = {"cls": F.normalize(cls, dim=-1), "gem": F.normalize(gem, dim=-1)}
        if self.centroids is not None:
            res["vlad"] = self.vlad(patches)
        return {k: v.cpu().numpy() for k, v in res.items()}

    def vlad(self, patches):
        """Hard-assignment VLAD with intra-normalisation (AnyLoc recipe), masked to the inscribed circle."""
        b, n, d = patches.shape
        assign = (patches @ self.centroids.T).argmax(-1)  # cosine, centroids are unit vectors
        one = F.one_hot(assign, self.vlad_k).float() * self.mask[None, :, None]
        resid = one.transpose(1, 2) @ patches - one.sum(1)[..., None] * self.centroids[None]
        resid = F.normalize(resid, dim=-1)
        return F.normalize(resid.reshape(b, -1), dim=-1)

    def fit_vlad(self, patch_sample, iters=25, seed=0):
        """Spherical k-means on a (N, d) sample of patch tokens."""
        g = torch.Generator().manual_seed(seed)
        x = patch_sample.to(self.device)
        c = x[torch.randperm(len(x), generator=g)[: self.vlad_k].to(self.device)].clone()
        for _ in range(iters):
            a = (x @ c.T).argmax(-1)
            for j in range(self.vlad_k):
                sel = x[a == j]
                if len(sel):
                    c[j] = F.normalize(sel.mean(0), dim=-1)
        self.centroids = c

    def describe(self, imgs, batch=64):
        outs = []
        for i in range(0, len(imgs), batch):
            outs.append(self.heads(*self.patch_tokens(imgs[i:i + batch])))
        return {k: np.concatenate([o[k] for o in outs]) for k in outs[0]}


def ring_histogram(img_rgb):
    """Classic rotation-invariant descriptor: per concentric ring, Lab colour and gradient-magnitude histograms.

    Hellinger-normalised (sqrt then L2), so cosine similarity is the Bhattacharyya coefficient.
    """
    n = img_rgb.shape[0]
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mag = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))
    c = (n - 1) / 2
    yy, xx = np.mgrid[:n, :n]
    rad = np.hypot(xx - c, yy - c) / (n / 2)
    feats = []
    for i in range(RING_COUNT):
        sel = (rad >= i / RING_COUNT) & (rad < (i + 1) / RING_COUNT)
        for ch in range(3):
            feats.append(np.histogram(lab[..., ch][sel], RING_BINS, (0, 256))[0])
        feats.append(np.histogram(np.log1p(mag[sel]), RING_BINS, (0, 7))[0])
    v = np.sqrt(np.concatenate(feats).astype(np.float32))
    return v / (np.linalg.norm(v) + 1e-12)


def timed(fn, *a, **kw):
    t0 = time.perf_counter()
    r = fn(*a, **kw)
    return r, time.perf_counter() - t0
