"""Fetch the terrain under the VPAIR sample flight (east of Bonn, NRW).

- Geobasis NRW DOM1: 1 m airborne-LiDAR surface model, 1 x 1 km GeoTIFF tiles in ETRS89 / UTM 32N,
  licence Datenlizenz Deutschland - Zero - 2.0. Only tiles within CORRIDOR_M of the flown track,
  via ../terrain-heightmap-pf/fetch_lidar.tile (same URL scheme, same checks). ~2.5 MB per tile.
- Copernicus GLO-30 DSM (30 m, public COG, no login), reprojected onto the same grid (terrain.glo30_on_grid).

    python fetch_terrain.py --data <dir with vpair_sample/>      # writes data/nrw_tiles/*.tif, data/glo30_*.npy
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "terrain-heightmap-pf"))
import fetch_lidar  # noqa: E402

import terrain  # noqa: E402

NRW_YEAR = 2021            # the tiles around Bonn / Siebengebirge in the opengeodata.nrw.de index
CORRIDOR_M = 1500.0


def corridor_tiles(track_utm, margin_m=CORRIDOR_M):
    """1 km tile indices (east_km, north_km) whose square lies within margin_m of any track point."""
    e, n = track_utm[:, 0], track_utm[:, 1]
    out = set()
    for ek in range(int((e.min() - margin_m) // 1000), int((e.max() + margin_m) // 1000) + 1):
        for nk in range(int((n.min() - margin_m) // 1000), int((n.max() + margin_m) // 1000) + 1):
            dx = np.maximum(0, np.maximum(ek * 1000 - e, e - (ek + 1) * 1000))
            dy = np.maximum(0, np.maximum(nk * 1000 - n, n - (nk + 1) * 1000))
            if np.min(np.hypot(dx, dy)) <= margin_m:
                out.add((ek, nk))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory containing vpair_sample/")
    ap.add_argument("--out", default=os.path.join(HERE, "data"))
    a = ap.parse_args()
    track = terrain.track_utm(os.path.join(a.data, "vpair_sample"))
    cache = os.path.join(a.out, "nrw_tiles")
    os.makedirs(cache, exist_ok=True)
    got, missing = 0, []
    for ek, nk in corridor_tiles(track):
        try:
            fetch_lidar.tile("dom1", ek, nk, NRW_YEAR, cache)
            got += 1
        except Exception as exc:  # tiles south of N 5608 km are in Rhineland-Palatinate, not NRW
            missing.append((ek, nk, type(exc).__name__))
    print(f"NRW DOM1: {got} tiles in {cache}; not available: {missing}")
    dsm, origin = terrain.load_dsm(cache)
    g = terrain.glo30_on_grid(origin, dsm.shape, cache=a.out)
    print(f"DSM mosaic {dsm.shape[1] / 1000:.0f} x {dsm.shape[0] / 1000:.0f} km from UTM {origin}, "
          f"{np.nanmin(dsm):.0f}..{np.nanmax(dsm):.0f} m, {100 * np.isnan(dsm).mean():.0f} % no data; "
          f"GLO-30 {g.shape} cells, {np.nanmin(g):.0f}..{np.nanmax(g):.0f} m")


if __name__ == "__main__":
    main()
