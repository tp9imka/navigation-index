"""Draw rooms/sketch_hall.png: a hand-drawn-looking plan of the same hall as hall_8x6.json.

.venv/bin/python rooms/make_sketch.py        # needs Pillow (requirements-image.txt), seeded

Scale 50 px/m, outer wall corners at pixels (40, 40) and (440, 340), so --ref 40 40 440 40 8.0.
Pencil strokes wobble by about 1-2 px; A and B labels and smudges are light (grey > 128) so the
default threshold ignores them. Synthetic input: a drawing made by this script, not a photo.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PX, X0, Y0 = 50, 40, 340          # px per metre, pixel of plan origin (lower-left corner)
rng = np.random.default_rng(77)


def p(x, y):
    return X0 + x * PX, Y0 - y * PX


def wobbly(d, pts, width, ink):
    """Polyline through pts (metres) with low-frequency wobble, slight overshoot at the ends."""
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        (ca, ra), (cb, rb) = p(xa, ya), p(xb, yb)
        L = max(abs(cb - ca), abs(rb - ra))
        n = max(2, int(L / 6))
        over = rng.uniform(1, 4)
        t = np.linspace(-over / max(L, 1), 1 + over / max(L, 1), n)
        nx, ny = (-(rb - ra), cb - ca) / np.hypot(cb - ca, rb - ra)
        wob = np.convolve(rng.normal(0, 1.2, n + 6), np.ones(7) / 7, "valid")[:n] * 1.6
        cs = ca + (cb - ca) * t + nx * wob
        rs = ra + (rb - ra) * t + ny * wob
        line = list(zip(cs.tolist(), rs.tolist()))
        d.line(line, fill=ink, width=width, joint="curve")


def rough_box(d, cx, cy, sx, sy, ink):
    x0, y0, x1, y1 = cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2
    (c0, r1), (c1, r0) = p(x0, y0), p(x1, y1)
    j = lambda: rng.uniform(-1.5, 1.5)
    d.polygon([(c0 + j(), r0 + j()), (c1 + j(), r0 + j()), (c1 + j(), r1 + j()), (c0 + j(), r1 + j())], fill=ink)
    wobbly(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], 3, ink)


def main():
    W, H = 480, 380
    yy, xx = np.mgrid[0:H, 0:W]
    paper = 236 - 10 * (xx / W) - 6 * (yy / H) + rng.normal(0, 2.0, (H, W))   # uneven light + grain
    img = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(img)
    for _ in range(6):                                                         # light smudges
        c, r = rng.uniform(20, W - 20), rng.uniform(20, H - 20)
        rr = rng.uniform(6, 18)
        d.ellipse([c - rr, r - rr * 0.6, c + rr, r + rr * 0.6], fill=(200, 198, 192))
    ink = (48, 46, 52)
    wobbly(d, [(0, 0), (8, 0), (8, 6), (0, 6), (0, 0)], 6, ink)               # outer walls
    wobbly(d, [(5, 0), (5, 3.6)], 6, ink)                                      # partition, door 3.6-4.5
    wobbly(d, [(5, 4.5), (5, 6)], 6, ink)
    for cx, cy in ((2.6, 2.0), (2.6, 4.0)):                                    # pillars r 0.2
        c, r = p(cx, cy)
        rr = 0.2 * PX + rng.uniform(-0.5, 0.5)
        d.ellipse([c - rr, r - rr, c + rr, r + rr], fill=ink)
    for cx, cy, sx, sy in ((1.4, 3.0, 1.6, 0.8), (3.9, 1.2, 0.8, 1.6), (6.5, 2.4, 1.2, 0.8), (6.6, 5.7, 2.0, 0.4)):
        rough_box(d, cx, cy, sx, sy, ink)
    blue = (120, 170, 240)                                                     # light: ignored at 128
    for (x, y), t in (((0.8, 0.8), "A"), ((7.2, 1.0), "B")):
        c, r = p(x, y)
        d.ellipse([c - 7, r - 7, c + 7, r + 7], outline=blue, width=2)
        d.text((c + 9, r - 14), t, fill=blue)
    d.text((300, 352), "hall 8 x 6 m, door 0.9", fill=(150, 150, 160))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    out = os.path.join(HERE, "sketch_hall.png")
    img.quantize(colors=48, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
    print(f"wrote {out}: {W} x {H} px, {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
