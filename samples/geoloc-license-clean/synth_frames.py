"""Synthesize nadir-ish 'drone frames' from an orthophoto with known ground truth.

Each frame: random centre, yaw 0-360 deg, scale (frame GSD / source GSD), corner jitter
(a perspective warp, roughly a few degrees off-nadir), then gamma / contrast / colour cast /
blur / noise / JPEG. Truth is the world position of the frame centre under the generating
homography.
"""
import math

import cv2
import numpy as np

FRAME_W, FRAME_H = 640, 480


def make_frame(src_rgb, src_gsd, rng, scale_range=(1.0, 2.0), jitter_frac=0.06, margin_px=900):
    h, w = src_rgb.shape[:2]
    cx = rng.uniform(margin_px, w - margin_px)
    cy = rng.uniform(margin_px, h - margin_px)
    yaw = rng.uniform(0, 360)
    s = rng.uniform(*scale_range)
    th = math.radians(yaw)
    # frame pixel offset (u, v) from centre => source pixel: rotate by -yaw (camera yawed clockwise)
    rot = np.array([[math.cos(th), math.sin(th)], [-math.sin(th), math.cos(th)]]) * s
    fc = np.array([(FRAME_W - 1) / 2, (FRAME_H - 1) / 2])
    fcorners = np.array([[0, 0], [FRAME_W - 1, 0], [FRAME_W - 1, FRAME_H - 1], [0, FRAME_H - 1]], float)
    jitter = rng.uniform(-jitter_frac, jitter_frac, (4, 2)) * np.array([FRAME_W, FRAME_H]) * s
    scorners = (fcorners - fc) @ rot.T + np.array([cx, cy]) + jitter
    H = cv2.getPerspectiveTransform(fcorners.astype(np.float32), scorners.astype(np.float32))
    frame = cv2.warpPerspective(src_rgb, H, (FRAME_W, FRAME_H), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP,
                                borderMode=cv2.BORDER_REFLECT)
    p = H @ np.array([fc[0], fc[1], 1.0])
    truth_px = (p[0] / p[2], p[1] / p[2])
    frame = photometric(frame, rng)
    return frame, {"truth_px": truth_px, "yaw_deg": yaw, "scale": s, "frame_gsd": s * src_gsd}


def photometric(img, rng):
    f = img.astype(np.float32) / 255.0
    f = f ** rng.uniform(0.7, 1.4)
    f = (f - 0.5) * rng.uniform(0.7, 1.3) + 0.5 + rng.uniform(-0.08, 0.08)
    f = f * rng.uniform(0.9, 1.1, 3)
    f = np.clip(f, 0, 1)
    out = (f * 255).astype(np.uint8)
    k = int(rng.choice([0, 3, 5]))
    if k:
        out = cv2.GaussianBlur(out, (k, k), 0)
    out = np.clip(out.astype(np.int16) + rng.normal(0, 4, out.shape).astype(np.int16), 0, 255).astype(np.uint8)
    ok, enc = cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, int(rng.integers(60, 90))])
    return cv2.imdecode(enc, cv2.IMREAD_UNCHANGED)
