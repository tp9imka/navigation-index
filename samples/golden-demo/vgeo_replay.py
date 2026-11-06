"""Replay of real visual-geoloc matches (stdlib only, used by companion.py --vgeo replay).

vgeo_real.py table renders a nadir frame from the 2019 NAIP orthophoto at every node of a
grid around home and matches it against the 2023 NAIP orthophoto; each node keeps its real
residual (fix minus truth) or its failure. At run time the fix for a truth position is drawn
from one of the four surrounding nodes, chosen at random with bilinear weights, so the error
field keeps its spatial structure (failure zones, map-registration bias) without per-frame
matching.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HOME_TOLERANCE_M = 50.0


def load(path: Path) -> dict:
    t = json.loads(Path(path).read_text())
    t["_idx"] = {(round(n["e"], 3), round(n["n"], 3)): n for n in t["nodes"]}
    t["_e0"] = min(n["e"] for n in t["nodes"])
    t["_n0"] = min(n["n"] for n in t["nodes"])
    return t


def home_offset_en(table: dict, origin) -> tuple[float, float]:
    """East/north of the EKF origin relative to the table's home."""
    lat0, lon0 = table["home"][0], table["home"][1]
    r = 6371008.8
    e = math.radians(origin[1] - lon0) * r * math.cos(math.radians(lat0))
    n = math.radians(origin[0] - lat0) * r
    if math.hypot(e, n) > HOME_TOLERANCE_M:
        raise SystemExit(f"EKF origin is {math.hypot(e, n):.0f} m from the vgeo table home {table['home'][:2]}: "
                         "start SITL with SITL_HOME at the table home (run.sh does with VGEO=replay)")
    return e, n


def lookup(table: dict, origin, e: float, n: float, rng):
    """Truth (e, n) in the origin frame => (fix_e, fix_n) or None, plus info for the log."""
    oe, on = home_offset_en(table, origin)
    te, tn = e + oe, n + on
    step = table["step_m"]
    fi, fj = (te - table["_e0"]) / step, (tn - table["_n0"]) / step
    i0, j0 = math.floor(fi), math.floor(fj)
    ai, aj = fi - i0, fj - j0
    cands = [((i0, j0), (1 - ai) * (1 - aj)), ((i0 + 1, j0), ai * (1 - aj)),
             ((i0, j0 + 1), (1 - ai) * aj), ((i0 + 1, j0 + 1), ai * aj)]
    r, acc, pick = rng.random(), 0.0, cands[-1][0]
    for ij, w in cands:
        acc += w
        if r <= acc:
            pick = ij
            break
    key = (round(table["_e0"] + pick[0] * step, 3), round(table["_n0"] + pick[1] * step, 3))
    node = table["_idx"].get(key)
    if node is None:
        return None, {"reason": "outside table", "node": key}
    info = {"node": [node["e"], node["n"]], "inliers": node["inliers"]}
    if node["de"] is None:
        return None, info | {"reason": "no fix (real matcher failure at this node)"}
    return (e + node["de"], n + node["dn"]), info | {"residual": [node["de"], node["dn"]]}
