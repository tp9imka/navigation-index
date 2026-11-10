"""Floor plan or whiteboard photo => close-area-world/1 JSON (axis-aligned boxes).

python world_from_image.py rooms/sketch_hall.png --ref 40 40 440 40 8.0 --origin-px 40 340 \\
    --a-m 0.8 0.8 --b-m 7.2 1.0 -o rooms/sketch_hall.world.json --preview results/room_sketch_hall.png

Pipeline: grey => dark pixels (grey < --threshold, or Otsu) => 0.1 m occupancy (a cell is occupied
when at least --fill of its pixels are dark) => drop blobs under --min-cells => greedy rectangle
cover => one box per rectangle. Bounds = bounding box of the occupied cells (--crop occupied,
default; the drawn outer walls then sit on the bounds) or the whole image (--crop image).

Scale (one of): --m-per-px S, or --ref X1 Y1 X2 Y2 D: two points in pixel coords (column, row)
and their real distance D in metres, for example two corners of a wall you measured.
Frame: origin at the image's lower-left corner, or at --origin-px COL ROW (for example the room's
lower-left corner, so metres match a tape measure); +x right, +y up (image rows grow down).
A and B: --a-px COL ROW or --a-m X Y (same for B).

PGM (P2/P5) and PBM (P1/P4) are read with the stdlib. PNG / JPG need Pillow:
uv pip install --python .venv -r requirements-image.txt
Limits: no perspective correction (photograph the plan straight on), no rotated boxes, round
pillars become stair-step boxes, any dark mark (text, arrows, a shadow) becomes an obstacle.
"""
from __future__ import annotations

import argparse
import math
import os

import numpy as np

try:
    from . import world as W, world_json as WJ, world_from_room as WR
except ImportError:
    import world as W
    import world_json as WJ
    import world_from_room as WR

RES = W.RES


# ---------------------------------------------------------------- image input

def _pnm_tokens(data: bytes, n: int, pos: int = 0):
    """First n whitespace-separated header tokens, skipping # comments. Returns (tokens, end)."""
    toks = []
    while len(toks) < n:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b"#":
            while data[pos:pos + 1] not in (b"\n", b"\r", b""):
                pos += 1
            continue
        s = pos
        while pos < len(data) and not data[pos:pos + 1].isspace():
            pos += 1
        toks.append(data[s:pos])
    return toks, pos


def read_pnm(path: str) -> np.ndarray:
    """PGM / PBM => grey float array (rows, cols), 0 black .. 255 white."""
    data = open(path, "rb").read()
    magic = data[:2]
    if magic in (b"P1", b"P4"):
        (_, w, h), pos = _pnm_tokens(data, 3)
        w, h = int(w), int(h)
        if magic == b"P1":
            body = "".join(ln.split("#")[0] for ln in data[pos:].decode("ascii").splitlines())
            bits = [ch for ch in body if ch in "01"]
            a = np.array(bits[:w * h], dtype=np.uint8).reshape(h, w)
        else:
            row = (w + 7) // 8
            raw = np.frombuffer(data[pos + 1:pos + 1 + row * h], np.uint8).reshape(h, row)
            a = np.unpackbits(raw, axis=1)[:, :w]
        return np.where(a == 1, 0.0, 255.0)                       # PBM: 1 = black
    if magic in (b"P2", b"P5"):
        (_, w, h, mx), pos = _pnm_tokens(data, 4)
        w, h, mx = int(w), int(h), int(mx)
        if magic == b"P2":
            vals = np.array(data[pos:].split()[:w * h], dtype=float)
        else:
            dt = np.dtype(">u2") if mx > 255 else np.dtype(np.uint8)
            vals = np.frombuffer(data[pos + 1:pos + 1 + w * h * dt.itemsize], dt).astype(float)
        return vals.reshape(h, w) * (255.0 / mx)
    raise ValueError(f"{path}: not a PGM/PBM file (magic {magic!r})")


def read_grey(path: str) -> np.ndarray:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".pgm", ".pbm", ".pnm"):
        return read_pnm(path)
    try:
        from PIL import Image
    except ImportError as e:
        raise SystemExit(f"{path}: PNG/JPG needs Pillow: uv pip install --python .venv -r requirements-image.txt ({e})")
    with Image.open(path) as im:
        return np.asarray(im.convert("L"), dtype=float)


def otsu(grey: np.ndarray) -> float:
    hist = np.bincount(np.clip(grey, 0, 255).astype(int).ravel(), minlength=256).astype(float)
    p = hist / hist.sum()
    w0 = np.cumsum(p)
    mu = np.cumsum(p * np.arange(256))
    with np.errstate(divide="ignore", invalid="ignore"):
        between = (mu[-1] * w0 - mu) ** 2 / (w0 * (1 - w0))
    return float(np.nanargmax(between)) + 0.5


# ---------------------------------------------------------------- occupancy and cover

def occupancy(dark: np.ndarray, m_per_px: float, fill: float) -> np.ndarray:
    """dark[row, col] => occ[ix, iy] at RES, origin at the image's lower-left corner."""
    h, w = dark.shape
    nx = int(math.ceil(w * m_per_px / RES - 1e-9))
    ny = int(math.ceil(h * m_per_px / RES - 1e-9))
    cols = np.arange(w)
    ys_rows = np.arange(h)
    ix = np.minimum(((cols + 0.5) * m_per_px / RES).astype(int), nx - 1)
    iy = np.minimum(((h - ys_rows - 0.5) * m_per_px / RES).astype(int), ny - 1)
    IX, IY = np.meshgrid(ix, iy)                        # shape (h, w)
    tot = np.zeros((nx, ny))
    drk = np.zeros((nx, ny))
    np.add.at(tot, (IX.ravel(), IY.ravel()), 1.0)
    np.add.at(drk, (IX.ravel(), IY.ravel()), dark.ravel().astype(float))
    occ = np.zeros((nx, ny), bool)
    has = tot > 0
    occ[has] = drk[has] / tot[has] >= fill
    if not has.all():                                   # pixels bigger than a cell: nearest pixel
        gx, gy = np.nonzero(~has)
        c = np.clip(((gx + 0.5) * RES / m_per_px).astype(int), 0, w - 1)
        r = np.clip(h - 1 - ((gy + 0.5) * RES / m_per_px).astype(int), 0, h - 1)
        occ[gx, gy] = dark[r, c]
    return occ


def drop_specks(occ: np.ndarray, min_cells: int) -> tuple[np.ndarray, int]:
    if min_cells <= 1:
        return occ, 0
    from scipy.ndimage import label
    lab, n = label(occ, structure=np.ones((3, 3)))
    sizes = np.bincount(lab.ravel())
    small = np.nonzero(sizes < min_cells)[0]
    small = small[small > 0]
    return occ & ~np.isin(lab, small), int(len(small))


def greedy_rectangles(occ: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Cover every occupied cell with axis-aligned rectangles (ix0, iy0, ix1, iy1), inclusive.
    At the first uncovered cell (scan order) grow x-then-y and y-then-x over occupied cells
    (overlap with earlier rectangles allowed) and keep the larger one."""
    nx, ny = occ.shape
    covered = np.zeros_like(occ)
    rects = []

    def grow(i, j, x_first):
        if x_first:
            i1 = i
            while i1 + 1 < nx and occ[i1 + 1, j]:
                i1 += 1
            j1 = j
            while j1 + 1 < ny and occ[i:i1 + 1, j1 + 1].all():
                j1 += 1
        else:
            j1 = j
            while j1 + 1 < ny and occ[i, j1 + 1]:
                j1 += 1
            i1 = i
            while i1 + 1 < nx and occ[i1 + 1, j:j1 + 1].all():
                i1 += 1
        return i1, j1

    for j in range(ny):
        for i in range(nx):
            if occ[i, j] and not covered[i, j]:
                cands = [grow(i, j, True), grow(i, j, False)]
                # prefer the one that covers more not-yet-covered cells
                best = max(cands, key=lambda c: int((~covered[i:c[0] + 1, j:c[1] + 1]).sum()))
                i1, j1 = best
                covered[i:i1 + 1, j:j1 + 1] = True
                rects.append((i, j, i1, j1))
    return rects


# ---------------------------------------------------------------- CLI

def image_to_world(grey, m_per_px, a, b, threshold, fill=0.3, min_cells=3, crop="occupied", origin=(0.0, 0.0)):
    """a, b in metres in the image frame shifted by origin (metres of the new origin in the image frame)."""
    thr = otsu(grey) if threshold == "otsu" else float(threshold)
    dark = grey < thr
    occ = occupancy(dark, m_per_px, fill)
    occ, n_specks = drop_specks(occ, min_cells)
    rects = greedy_rectangles(occ)
    nx, ny = occ.shape
    if crop == "occupied" and rects:
        xs, ys = np.nonzero(occ)
        bounds = [xs.min() * RES, ys.min() * RES, (xs.max() + 1) * RES, (ys.max() + 1) * RES]
    else:
        bounds = [0.0, 0.0, nx * RES, ny * RES]
    ox, oy = origin
    bounds = [bounds[0] - ox, bounds[1] - oy, bounds[2] - ox, bounds[3] - oy]
    obs = []
    for i0, j0, i1, j1 in rects:
        obs.append({"type": "box", "cx": WR._r((i0 + i1 + 1) * RES / 2 - ox), "cy": WR._r((j0 + j1 + 1) * RES / 2 - oy),
                    "hx": WR._r((i1 - i0 + 1) * RES / 2), "hy": WR._r((j1 - j0 + 1) * RES / 2),
                    "material": "matte", "tag": "drawn"})
    doc = {"schema": WJ.SCHEMA, "frame": "local ENU m, origin at A", "family": "custom", "seed": 0, "index": 0,
           "bounds": [WR._r(v) for v in bounds], "a": [WR._r(a[0]), WR._r(a[1])],
           "b": [WR._r(b[0]), WR._r(b[1])], "z": 1.0, "radius": W.RADIUS, "obstacles": obs}
    stats = {"threshold": round(thr, 1), "dark_px_pct": round(100 * float(dark.mean()), 2),
             "grid": [nx, ny], "occupied_cells": int(occ.sum()), "specks_dropped": n_specks,
             "boxes": len(rects)}
    return doc, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    sc = ap.add_mutually_exclusive_group(required=True)
    sc.add_argument("--m-per-px", type=float)
    sc.add_argument("--ref", type=float, nargs=5, metavar=("X1", "Y1", "X2", "Y2", "D"),
                    help="two pixel points (col row) and their real distance in metres")
    ga = ap.add_mutually_exclusive_group(required=True)
    ga.add_argument("--a-px", type=float, nargs=2, metavar=("COL", "ROW"))
    ga.add_argument("--a-m", type=float, nargs=2, metavar=("X", "Y"))
    gb = ap.add_mutually_exclusive_group(required=True)
    gb.add_argument("--b-px", type=float, nargs=2, metavar=("COL", "ROW"))
    gb.add_argument("--b-m", type=float, nargs=2, metavar=("X", "Y"))
    ap.add_argument("--origin-px", type=float, nargs=2, metavar=("COL", "ROW"),
                    help="pixel corner that becomes (0, 0) m (default: image lower-left corner)")
    ap.add_argument("--threshold", default="128", help="grey level below which a pixel is dark, or 'otsu' (default 128)")
    ap.add_argument("--fill", type=float, default=0.3, help="dark fraction that makes a 0.1 m cell occupied (default 0.3)")
    ap.add_argument("--min-cells", type=int, default=3, help="drop dark blobs smaller than this many cells (default 3)")
    ap.add_argument("--crop", choices=("occupied", "image"), default="occupied")
    ap.add_argument("--name", help="name for results/room_<name>.json (default: image file stem)")
    ap.add_argument("-o", "--out", help="world JSON (default: <image>.world.json)")
    ap.add_argument("--fly", action="store_true", help="fly astar_esdf known map, write results/room_<name>.json")
    ap.add_argument("--preview", help="PNG of map + flown path (implies --fly)")
    a = ap.parse_args(argv)

    grey = read_grey(a.image)
    h, w = grey.shape
    if a.ref:
        x1, y1, x2, y2, d = a.ref
        lpx = math.hypot(x2 - x1, y2 - y1)
        if lpx <= 0 or d <= 0:
            raise SystemExit("--ref needs two different points and D > 0")
        mpp = d / lpx
        # +-1 px on each clicked point => up to sqrt(2) px on the length
        scale = {"m_per_px": round(mpp, 6), "ref_px": round(lpx, 2), "ref_m": d,
                 "scale_err_pct_1px": round(100 * math.sqrt(2) / lpx, 2)}
        print(f"scale {mpp:.5f} m/px from {lpx:.1f} px = {d} m; +-1 px per point => +-{scale['scale_err_pct_1px']:.2f} % scale")
    else:
        mpp = a.m_per_px
        if not (mpp and mpp > 0):
            raise SystemExit("--m-per-px must be > 0")
        scale = {"m_per_px": mpp}
        print(f"scale {mpp:.5f} m/px (given)")
    org = (a.origin_px[0] * mpp, (h - a.origin_px[1]) * mpp) if a.origin_px else (0.0, 0.0)
    to_m = lambda col, row: ((col + 0.5) * mpp - org[0], (h - row - 0.5) * mpp - org[1])
    pa = to_m(*a.a_px) if a.a_px else tuple(a.a_m)
    pb = to_m(*a.b_px) if a.b_px else tuple(a.b_m)
    thr = a.threshold if a.threshold == "otsu" else float(a.threshold)
    doc, st = image_to_world(grey, mpp, pa, pb, thr, a.fill, a.min_cells, a.crop, org)
    print(f"image {w} x {h} px = {w * mpp:.2f} x {h * mpp:.2f} m; threshold {st['threshold']}, "
          f"{st['dark_px_pct']} % dark px; grid {st['grid'][0]} x {st['grid'][1]} cells, "
          f"{st['occupied_cells']} occupied, {st['specks_dropped']} specks dropped => {st['boxes']} boxes")
    name = a.name or os.path.splitext(os.path.basename(a.image))[0]
    out = a.out or os.path.splitext(a.image)[0] + ".world.json"
    extra = {"image": {"file": os.path.basename(a.image), "px": [w, h], **scale, **st,
                       "fill": a.fill, "min_cells": a.min_cells}}
    return WR.finish(doc, out, name, a.fly, a.preview, extra)


if __name__ == "__main__":
    raise SystemExit(main())
