#!/usr/bin/env python3
"""Real visual geolocalization for the golden demo: render a nadir camera frame from the 2019
NAIP orthophoto at the SITL truth position, match it against the 2023 NAIP orthophoto with
samples/geoloc-license-clean (ALIKED + LightGlue + MAGSAC), return the fix or a failure.

Two uses:
    python vgeo_real.py table --out data/vgeo_table.json     # grid of real matches for replay
    LiveVgeo(...)                                             # in-loop, used by companion.py --vgeo live

Needs the geoloc-license-clean requirements (torch, lightglue, opencv, rasterio) and its
data (python ../geoloc-license-clean/download_data.py). The two NAIP epochs differ in
season, sun and GSD (2019-10 at 0.6 m vs 2023-05 at 0.3 m), so failures are real ones.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
GEOLOC = HERE.parent / "geoloc-license-clean"
sys.path.insert(0, str(GEOLOC))
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

from geoloc import Localizer, OrthoMap  # noqa: E402
from synth_frames import photometric  # noqa: E402
from navapp.geo import enu_to_geodetic, geodetic_to_enu  # noqa: E402

FRAME_W, FRAME_H = 640, 480
HFOV_DEG = 85.0
# Home 200 m south and 75 m west of the NAIP window centre (download_data.py CENTER_LON/LAT),
# so the survey and a 75 m westward drift stay inside the 2 km window with search margin.
HOME = (41.301800, -81.751397, 290.0)
AGL_M = 150.0
PRIOR_ERR_M = 20.0
SEARCH_RADIUS_M = 60.0
HEADING_NOISE_DEG = 3.0
FEATURES = "aliked"
GRID_STEP_M = 20.0
GRID_E = (-120.0, 200.0)
GRID_N = (-40.0, 440.0)


def frame_gsd(agl_m: float) -> float:
    return 2 * agl_m * math.tan(math.radians(HFOV_DEG / 2)) / FRAME_W


class Camera:
    """Gimbal-stabilised nadir camera over the 2019 orthophoto (the 'world')."""

    def __init__(self, world_tif: Path):
        self.world = OrthoMap.open(world_tif)

    def render(self, lat, lon, yaw_deg, agl_m, rng):
        gsd = frame_gsd(agl_m)
        c, r = self.world.world_to_px(*self.world.lonlat_to_world(lon, lat))
        s = gsd / self.world.gsd
        th = math.radians(yaw_deg)
        rot = np.array([[math.cos(th), math.sin(th)], [-math.sin(th), math.cos(th)]]) * s
        fc = np.array([(FRAME_W - 1) / 2, (FRAME_H - 1) / 2])
        corners = np.array([[0, 0], [FRAME_W - 1, 0], [FRAME_W - 1, FRAME_H - 1], [0, FRAME_H - 1]], float)
        src = (corners - fc) @ rot.T + np.array([c, r])
        Hm = cv2.getPerspectiveTransform(corners.astype(np.float32), src.astype(np.float32))
        frame = cv2.warpPerspective(self.world.rgb, Hm, (FRAME_W, FRAME_H),
                                    flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        return photometric(frame, rng), gsd


class Geolocator:
    def __init__(self, world_tif=GEOLOC / "data" / "naip_aukerman_2019.tif",
                 map_tif=GEOLOC / "data" / "naip_aukerman.tif", features=FEATURES):
        self.camera = Camera(world_tif)
        self.map = OrthoMap.open(map_tif)
        self.loc = Localizer(features)

    def fix(self, lat, lon, yaw_deg, agl_m, prior_latlon, rng):
        frame, gsd = self.camera.render(lat, lon, yaw_deg, agl_m, rng)
        heading = yaw_deg + rng.normal(0, HEADING_NOISE_DEG)
        r = self.loc.localize(frame, gsd, heading % 360, self.map, (prior_latlon[1], prior_latlon[0]),
                              SEARCH_RADIUS_M)
        out = {"inliers": r["inliers"], "matches": r["matches"], "t_s": r["t_total_s"], "lat": None, "lon": None}
        if r["fix"]:
            out["lon"], out["lat"] = r["fix"]
        return out


class LiveVgeo:
    """Background matcher: the companion submits (truth, prior); the worker returns fixes."""

    def __init__(self, seed: int):
        self.geo = Geolocator()
        self.rng = np.random.default_rng(seed)
        self.lock = threading.Lock()
        self.job = None
        self.results: list[dict] = []
        self.busy = False
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, job: dict) -> bool:
        with self.lock:
            if self.busy or self.job is not None:
                return False
            self.job = job
            return True

    def take(self) -> list[dict]:
        with self.lock:
            out, self.results = self.results, []
        return out

    def _worker(self):
        while True:
            with self.lock:
                job, self.job = self.job, None
                self.busy = job is not None
            if job is None:
                time.sleep(0.01)
                continue
            r = self.geo.fix(job["lat"], job["lon"], job["yaw_deg"], job["agl_m"], job["prior"], self.rng)
            with self.lock:
                self.results.append(job | r)
                self.busy = False


def build_table(out: Path, seed: int, step: float):
    geo = Geolocator()
    rng = np.random.default_rng(seed)
    lat0, lon0, _ = HOME
    nodes = []
    es = np.arange(GRID_E[0], GRID_E[1] + 1e-6, step)
    ns = np.arange(GRID_N[0], GRID_N[1] + 1e-6, step)
    t0 = time.time()
    for i, n in enumerate(ns):
        for j, e in enumerate(es):
            yaw = (0.0 if (i + j) % 2 == 0 else 180.0) + rng.uniform(-10, 10)
            lat, lon = enu_to_geodetic(e, n, lat0, lon0)
            a = rng.uniform(0, 2 * math.pi)
            prior = enu_to_geodetic(e + PRIOR_ERR_M * math.cos(a), n + PRIOR_ERR_M * math.sin(a), lat0, lon0)
            r = geo.fix(lat, lon, yaw, AGL_M, prior, rng)
            node = {"e": float(e), "n": float(n), "yaw": round(yaw, 1), "inliers": r["inliers"],
                    "t_s": r["t_s"], "de": None, "dn": None}
            if r["lat"] is not None:
                fe, fn = geodetic_to_enu(r["lat"], r["lon"], lat0, lon0)
                node["de"], node["dn"] = round(fe - e, 2), round(fn - n, 2)
            nodes.append(node)
        done = len(nodes)
        ok = sum(x["de"] is not None for x in nodes)
        print(f"row {i + 1}/{len(ns)}: {done} frames, {ok} fixes, {time.time() - t0:.0f} s", flush=True)
    table = {"schema": "golden-vgeo-table/1", "home": HOME, "agl_m": AGL_M, "hfov_deg": HFOV_DEG,
             "frame_px": [FRAME_W, FRAME_H], "step_m": step, "features": FEATURES,
             "world": "naip_aukerman_2019.tif (rendered)", "map": "naip_aukerman.tif (matched)",
             "prior_err_m": PRIOR_ERR_M, "search_radius_m": SEARCH_RADIUS_M, "seed": seed,
             "wall_s": round(time.time() - t0, 1), "nodes": nodes}
    out.write_text(json.dumps(table) + "\n")
    print(f"wrote {out}: {len(nodes)} nodes")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table")
    t.add_argument("--out", type=Path, default=HERE / "data" / "vgeo_table.json")
    t.add_argument("--seed", type=int, default=3)
    t.add_argument("--step", type=float, default=GRID_STEP_M)
    a = ap.parse_args(argv)
    if a.cmd == "table":
        build_table(a.out, a.seed, a.step)
    return 0


if __name__ == "__main__":
    sys.exit(main())
