"""Build tile databases over the 49 km2 NAIP area and measure retrieval recall, latency and index size.

Synthetic queries (known truth) come from synth_frames.make_frame of ../geoloc-license-clean, cut from
NAIP of several years and matched against a DB built from one year. Real queries are CC0 eBee frames
with EXIF GPS as truth.
"""
import argparse
import json
import math
import pathlib
import statistics
import sys
import time

import cv2
import numpy as np
from PIL import Image
from rasterio.warp import transform as warp_transform

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "geoloc-license-clean"))
from geoloc import OrthoMap  # noqa: E402
from synth_frames import make_frame  # noqa: E402

from geo import angle_diff_deg, recall_at, tile_centres  # noqa: E402
from vpr import Dinov2Describer, TileIndex, query_crop, render_tile, ring_histogram, rotate_square  # noqa: E402

DATA = HERE / "data"
OUT = HERE / "out"
OUT_PX = 224
YAWS = [0, 45, 90, 135, 180, 225, 270, 315]
TOP_K = 10
HEADING_PRIOR_NOISE_DEG = 5.0
GSD_NOISE = 0.05
# heading error is scored only where top-1 is the right place; elsewhere it is meaningless
HEADING_EVAL_RADIUS_M = 100
VLAD_SAMPLE_TILES = 1500
# synthetic frame GSD range per DB tile size, chosen so the 640x480 frame's short side covers the tile
SYNTH_GSD = {250: (0.55, 0.8), 100: (0.22, 0.3)}
SYNTH_MARGIN_M = 450
# Sony DSC-WX220 (eBee payload): sensor width 6.17 mm from the spec sheet, focal 4.45 mm from EXIF
SENSOR_WIDTH_MM = 6.17
REAL_WORK_WIDTH = 1224


def load_map(year):
    return OrthoMap.open(DATA / f"naip_{year}.tif")


def map_origin(ortho):
    return ortho.transform.c, ortho.transform.f


def build_db(desc, ortho, year, tile_m, stride_m, yaws, cache=True):
    """Render every tile at every yaw, describe it, cache to out/. Returns dict of arrays."""
    f = OUT / f"db_{year}_{tile_m}m_s{stride_m}_y{len(yaws)}_{desc.tag}.npz"
    if cache and f.exists():
        return dict(np.load(f))
    t0 = time.perf_counter()
    h, w = ortho.rgb.shape[:2]
    centres = np.array(tile_centres(w * ortho.gsd, h * ortho.gsd, tile_m, stride_m))
    work_gsd = tile_m / OUT_PX
    if work_gsd > ortho.gsd * 1.05:
        k = ortho.gsd / work_gsd
        src = cv2.resize(ortho.rgb, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        src_gsd = ortho.gsd * ortho.rgb.shape[1] / src.shape[1]
    else:
        src, src_gsd = ortho.rgb, ortho.gsd
    centres_px = centres / src_gsd - 0.5
    e0, n0 = map_origin(ortho)
    meta = np.stack([e0 + centres[:, 0], n0 - centres[:, 1]], 1)

    def tiles(yaw, sel):
        return np.stack([render_tile(src, src_gsd, centres_px[i], tile_m, OUT_PX, yaw) for i in sel])

    if desc.centroids is None:
        rng = np.random.default_rng(0)
        sel = rng.choice(len(centres), min(VLAD_SAMPLE_TILES, len(centres)), replace=False)
        sample = []
        for i in range(0, len(sel), 64):
            sample.append(desc.patch_tokens(tiles(0, sel[i:i + 64]))[1].reshape(-1, desc.model.embed_dim).cpu())
        import torch
        allp = torch.cat(sample)
        desc.fit_vlad(allp[torch.randperm(len(allp), generator=torch.Generator().manual_seed(0))[:200000]])
    out = {"meta": meta, "centroids": desc.centroids.cpu().numpy()}
    batch = 64
    for yaw in yaws:
        gem, cls, vlad, ring = [], [], [], []
        for i in range(0, len(centres), batch):
            imgs = tiles(yaw, range(i, min(i + batch, len(centres))))
            d = desc.describe(imgs, batch)
            gem.append(d["gem"])
            cls.append(d["cls"])
            if yaw == 0:
                vlad.append(d["vlad"].astype(np.float16))
                ring.append(np.stack([ring_histogram(t) for t in imgs]))
        out[f"gem_{yaw}"] = np.concatenate(gem)
        out[f"cls_{yaw}"] = np.concatenate(cls)
        if yaw == 0:
            out["vlad_0"] = np.concatenate(vlad)
            out["ring_0"] = np.concatenate(ring)
        print(f"  db {year} {tile_m} m yaw {yaw}: {len(centres)} tiles, {time.perf_counter() - t0:.0f} s", flush=True)
    out["build_s"] = np.array(time.perf_counter() - t0)
    if cache:
        OUT.mkdir(exist_ok=True)
        np.savez(f, **out)
    return out


def make_indexes(db, yaws):
    meta = db["meta"]
    n = len(meta)
    idx = {}
    for head in ("gem", "cls"):
        idx[f"{head}/0"] = TileIndex(db[f"{head}_0"], np.c_[meta, np.zeros(n)])
        if len(yaws) > 1:
            idx[f"{head}/aug"] = TileIndex(np.concatenate([db[f"{head}_{y}"] for y in yaws]),
                                           np.concatenate([np.c_[meta, np.full(n, y)] for y in yaws]))
            m = np.mean([db[f"{head}_{y}"] for y in yaws], 0)
            idx[f"{head}/inv"] = TileIndex(m / np.linalg.norm(m, axis=1, keepdims=True), np.c_[meta, np.zeros(n)])
    idx["vlad/0"] = TileIndex(db["vlad_0"].astype(np.float32), np.c_[meta, np.zeros(n)])
    idx["ring/0"] = TileIndex(db["ring_0"], np.c_[meta, np.zeros(n)])
    return idx


def strategies(idx):
    """(name, index key, which query rows). Query rows: 0..7 = crop rotated by YAWS, 8 = heading-prior north-up."""
    s = []
    for head in ("gem", "cls", "vlad"):
        s += [(f"{head}/north-up-prior", f"{head}/0", "prior"), (f"{head}/none", f"{head}/0", "plain"),
              (f"{head}/query-tta8", f"{head}/0", "tta")]
        if f"{head}/aug" in idx:
            s += [(f"{head}/db-aug8", f"{head}/aug", "plain"), (f"{head}/invariant8", f"{head}/inv", "mean")]
    s.append(("ring/invariant (classic)", "ring/0", "ring"))
    return s


def describe_query(desc, crop, prior_yaw):
    imgs = np.stack([rotate_square(crop, a) for a in YAWS] + [rotate_square(crop, prior_yaw)])
    t0 = time.perf_counter()
    d1 = desc.describe(imgs[:1])
    t1 = time.perf_counter()
    d = desc.describe(imgs)
    t8 = time.perf_counter()
    d["ring"] = ring_histogram(crop)[None]
    return d, {"fwd1_ms": (t1 - t0) * 1e3, "fwd9_ms": (t8 - t1) * 1e3}


def query_rows(d, head, mode):
    if mode == "ring":
        return d["ring"]
    x = d[head]
    if mode == "plain":
        return x[:1]
    if mode == "prior":
        return x[8:9]
    if mode == "tta":
        return x[:8]
    m = x[:8].mean(0, keepdims=True)
    return m / np.linalg.norm(m)


def eval_queries(desc, idx, queries, yaw_known=True):
    """queries: list of dict(crop, truth_en, yaw). Returns per-strategy summary and per-query rows."""
    res = {name: {"d": [], "hdg_err": [], "search_ms": []} for name, _, _ in strategies(idx)}
    fwd = []
    for q in queries:
        d, t = describe_query(desc, q["crop"], q.get("prior_yaw", 0.0))
        fwd.append(t)
        for name, key, mode in strategies(idx):
            if mode == "prior" and not yaw_known:
                continue
            head = key.split("/")[0]
            t0 = time.perf_counter()
            ids, sims, var = idx[key].search_places(query_rows(d, head, mode), TOP_K)
            res[name]["search_ms"].append((time.perf_counter() - t0) * 1e3)
            m = idx[key].meta[ids]
            res[name]["d"].append(np.hypot(m[:, 0] - q["truth_en"][0], m[:, 1] - q["truth_en"][1]).tolist())
            if q.get("yaw") is not None and (mode == "tta" or key.endswith("/aug")):
                est = YAWS[var[0]] if mode == "tta" else m[0, 2]
                res[name]["hdg_err"].append((angle_diff_deg(est, q["yaw"]), res[name]["d"][-1][0] <= HEADING_EVAL_RADIUS_M))
            res[name].setdefault("top", []).append([[float(m[i, 0]), float(m[i, 1]), float(m[i, 2]) if mode != "tta"
                                                     else float(YAWS[var[i]])] for i in range(len(ids))])
    summ = {}
    for name, r in res.items():
        if not r["d"]:
            continue
        summ[name] = recall_at(r["d"]) | {
            "median_top1_err_m": round(statistics.median(x[0] for x in r["d"]), 1),
            "search_ms_median": round(statistics.median(r["search_ms"]), 2),
            "index_mb": round(idx[[k for n, k, _ in strategies(idx) if n == name][0]].nbytes / 2 ** 20, 1)}
        e = [x for x, ok in r["hdg_err"] if ok]
        if e:
            summ[name] |= {"heading_err_median_deg": round(statistics.median(e), 1),
                           "heading_within_30deg": round(sum(x <= 30 for x in e) / len(e), 3),
                           "heading_n": len(e)}
    lat = {"fwd1_ms_median": round(statistics.median(t["fwd1_ms"] for t in fwd), 1),
           "fwd9_ms_median": round(statistics.median(t["fwd9_ms"] for t in fwd), 1)}
    return summ, lat, res


def synth_queries(src, ortho_db, tile_m, n, seed):
    rng = np.random.default_rng(seed)
    lo, hi = SYNTH_GSD[tile_m]
    qs = []
    for _ in range(n):
        frame, gt = make_frame(src.rgb, src.gsd, rng, scale_range=(lo / src.gsd, hi / src.gsd),
                               margin_px=int(SYNTH_MARGIN_M / src.gsd))
        e, nn = src.px_to_world(gt["truth_px"][0] + 0.5, gt["truth_px"][1] + 0.5)
        gsd_est = gt["frame_gsd"] * (1 + rng.normal(0, GSD_NOISE))
        crop, _ = query_crop(frame, gsd_est, tile_m, OUT_PX)
        qs.append({"crop": crop, "frame": frame, "frame_gsd_est": gsd_est, "truth_en": (e, nn), "yaw": gt["yaw_deg"],
                   "prior_yaw": gt["yaw_deg"] + rng.normal(0, HEADING_PRIOR_NOISE_DEG), "scale": gt["scale"]})
    return qs


def exif(path):
    ex = Image.open(path).getexif()
    g = ex.get_ifd(0x8825)
    dms = lambda v: float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
    lat = dms(g[2]) * (1 if g[1] == "N" else -1)
    lon = dms(g[4]) * (1 if g[3] == "E" else -1)
    return lat, lon, float(g[6]), float(ex.get_ifd(0x8769)[0x920A])


def real_queries(agl_mode, tile_m, crs):
    """eBee frames. agl_mode: 'msl' treats EXIF altitude as MSL, 'ellipsoid' as WGS84 ellipsoidal height."""
    elev = json.loads((DATA / "uav" / "ground_elev.json").read_text())["frames"]
    qs = []
    for p in sorted((DATA / "uav").glob("*.JPG")):
        lat, lon, alt, focal = exif(p)
        agl = alt - elev[p.name]["ground_m"] + (GEOID_UNDULATION_M if agl_mode == "ellipsoid" else 0.0)
        img = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)
        native_w = img.shape[1]
        ds = REAL_WORK_WIDTH / native_w
        img = cv2.resize(img, None, fx=ds, fy=ds, interpolation=cv2.INTER_AREA)
        gsd = agl * SENSOR_WIDTH_MM / (focal * native_w) / ds
        crop, ground = query_crop(img, gsd, tile_m, OUT_PX)
        xs, ys = warp_transform("EPSG:4326", crs, [lon], [lat])
        qs.append({"crop": crop, "frame": img, "frame_gsd_est": gsd, "truth_en": (xs[0], ys[0]), "yaw": None,
                   "name": p.name, "agl_m": round(agl, 1), "crop_ground_m": round(ground, 1), "lonlat": (lon, lat)})
    return qs


# EGM96/EGM2008 geoid height near Medina, Ohio is about -34 m (not computed here; standard tables)
GEOID_UNDULATION_M = 34.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="dinov2_vits14")
    ap.add_argument("--db-year", default="2023")
    ap.add_argument("--synth-years", nargs="*", default=["2023", "2021", "2019", "2017", "2015"])
    ap.add_argument("--tiles", nargs="*", type=int, default=[250, 100])
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--real-db-years", nargs="*", default=["2023", "2021", "2019", "2017", "2015"])
    ap.add_argument("--real-tiles", nargs="*", type=int, default=[100, 70])
    ap.add_argument("--real-yaws", type=int, default=1, help="8 to also test db-aug8 / invariant8 on real frames")
    ap.add_argument("--skip-synth", action="store_true")
    ap.add_argument("--skip-real", action="store_true")
    ap.add_argument("--out", default="vpr_results.json")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    desc = Dinov2Describer(a.arch, OUT_PX)
    desc.tag = a.arch.replace("dinov2_", "")
    strides = {250: 50, 100: 50, 70: 35}
    report = {"env": {"arch": a.arch, "device": desc.device, "out_px": OUT_PX, "n_synth": a.n, "seed": a.seed},
              "synthetic": {}, "real": {}}
    rpath = OUT / a.out
    if rpath.exists():
        report = json.loads(rpath.read_text()) | {"env": report["env"]}

    def save():
        rpath.write_text(json.dumps(report, indent=1, default=float))

    if not a.skip_synth:
        ortho = load_map(a.db_year)
        for tile_m in a.tiles:
            desc.centroids = None
            db = build_db(desc, ortho, a.db_year, tile_m, strides[tile_m], YAWS)
            import torch
            desc.centroids = torch.from_numpy(db["centroids"]).to(desc.device)
            idx = make_indexes(db, YAWS)
            info = {"tiles": len(db["meta"]), "stride_m": strides[tile_m], "build_s": float(db["build_s"])}
            for sy in a.synth_years:
                src = ortho if sy == a.db_year else load_map(sy)
                qs = synth_queries(src, ortho, tile_m, a.n, a.seed)
                summ, lat, _ = eval_queries(desc, idx, qs)
                key = f"db{a.db_year}/{tile_m}m/src{sy}"
                report["synthetic"][key] = {"db": info, "latency": lat, "strategies": summ}
                print(key, json.dumps(lat), flush=True)
                for name, s in summ.items():
                    print(f"   {name:28s} R@1<=50 {s['R@1<=50m']:.2f} R@10<=50 {s['R@10<=50m']:.2f} "
                          f"R@1<=250 {s['R@1<=250m']:.2f} R@10<=250 {s['R@10<=250m']:.2f} "
                          f"hdg {s.get('heading_err_median_deg', '-')}", flush=True)
                save()
                del src
    if not a.skip_real:
        for year in a.real_db_years:
            ortho = load_map(year)
            for tile_m in a.real_tiles:
                desc.centroids = None
                yaws = YAWS if a.real_yaws == len(YAWS) else [0]
                db = build_db(desc, ortho, year, tile_m, strides[tile_m], yaws)
                import torch
                desc.centroids = torch.from_numpy(db["centroids"]).to(desc.device)
                idx = make_indexes(db, yaws)
                for agl_mode in ("msl", "ellipsoid"):
                    qs = real_queries(agl_mode, tile_m, ortho.crs)
                    summ, lat, rows = eval_queries(desc, idx, qs, yaw_known=False)
                    key = f"db{year}/{tile_m}m/agl-{agl_mode}" + ("/y8" if len(yaws) > 1 else "")
                    report["real"][key] = {"db": {"tiles": len(db["meta"]), "stride_m": strides[tile_m]},
                                           "latency": lat, "strategies": summ,
                                           "agl_m": [q["agl_m"] for q in qs],
                                           "crop_ground_m": [q["crop_ground_m"] for q in qs]}
                    print(key, flush=True)
                    for name, s in summ.items():
                        print(f"   {name:28s} R@1<=50 {s['R@1<=50m']:.2f} R@10<=50 {s['R@10<=50m']:.2f} "
                              f"R@1<=250 {s['R@1<=250m']:.2f} R@10<=250 {s['R@10<=250m']:.2f} "
                              f"top1 {s['median_top1_err_m']}", flush=True)
                    save()
    save()


if __name__ == "__main__":
    main()
