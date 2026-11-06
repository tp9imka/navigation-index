"""Chain: VPR top-k over the 49 km2 DB => geoloc-license-clean fine matching => fix with inlier gate.

Compared against the fine matcher alone with a known position prior (truth + 100 m, radius 150 m,
heading truth + N(0, 5 deg)), the protocol of ../geoloc-license-clean.
"""
import argparse
import json
import math
import statistics
import time

import numpy as np
import torch

import run_vpr as R
from geo import angle_diff_deg, haversine_m
from geoloc import MIN_INLIERS, Localizer
from vpr import Dinov2Describer

TOP_K = 5
CANDIDATE_RADIUS_M = 100.0
HEADING_OFFSETS_DEG = (-20, 0, 20)
PRIOR_OFFSET_M = 100.0
PRIOR_RADIUS_M = 150.0
WRONG_FIX_M = 50.0
REAL_SWEEP_STEP_DEG = 15


def lonlat_of(ortho, e, n):
    return ortho.world_to_lonlat(e, n)


def vpr_candidates(desc, idx, db, q, strategy):
    """Top-k (east, north, heading or None). 'invariant8+hdg': rank by the rotation-invariant descriptor,
    then take each candidate's heading from its best-matching rotated DB tile (no extra search)."""
    head, kind = strategy.split("/")
    base = kind.split("+")[0]
    key = {"db-aug8": f"{head}/aug", "query-tta8": f"{head}/0", "invariant8": f"{head}/inv"}[base]
    mode = {"db-aug8": "plain", "query-tta8": "tta", "invariant8": "mean"}[base]
    t0 = time.perf_counter()
    d, _ = R.describe_query(desc, q["crop"], 0.0)
    ids, _, var = idx[key].search_places(R.query_rows(d, head, mode), TOP_K)
    m = idx[key].meta[ids]
    n = len(db["meta"])
    if kind == "invariant8+hdg":
        q0 = d[head][0]
        hdg = [float(R.YAWS[int(np.argmax([db[f"{head}_{y}"][i % n] @ q0 for y in R.YAWS]))]) for i in ids]
    elif mode == "tta":
        hdg = [float(R.YAWS[v]) for v in var]
    elif base == "db-aug8":
        hdg = [float(x) for x in m[:, 2]]
    else:
        hdg = [None] * len(ids)
    return [(m[i, 0], m[i, 1], hdg[i]) for i in range(len(ids))], time.perf_counter() - t0


def fine(loc, q, ortho, prior_lonlat, headings, radius, gsds):
    best, t, tries = None, 0.0, 0
    for g in gsds:
        for h in headings:
            r = loc.localize(q["frame"], g, h % 360, ortho, prior_lonlat, radius)
            t += r["t_total_s"]
            tries += 1
            if best is None or r["inliers"] > best["inliers"]:
                best = r | {"heading": round(h % 360, 1), "gsd": g}
    return best, t, tries


def err_m(q, fix, ortho):
    lon, lat = q.get("lonlat") or ortho.world_to_lonlat(*q["truth_en"])
    return haversine_m(lat, lon, fix[1], fix[0])


def chain_one(loc, desc, idx, db, q, ortho, strategy, gsds):
    cands, t_vpr = vpr_candidates(desc, idx, db, q, strategy)
    t_fine, tries, out = 0.0, 0, None
    for rank, (e, n, hdg) in enumerate(cands):
        headings = [hdg + o for o in HEADING_OFFSETS_DEG] if hdg is not None else \
            [float(h) for h in range(0, 360, REAL_SWEEP_STEP_DEG)]
        best, t, k = fine(loc, q, ortho, lonlat_of(ortho, e, n), headings, CANDIDATE_RADIUS_M, gsds)
        t_fine += t
        tries += k
        if best["fix"]:
            out = best | {"rank": rank}
            break
    cand_d = [math.hypot(e - q["truth_en"][0], n - q["truth_en"][1]) for e, n, _ in cands]
    row = {"t_vpr_s": round(t_vpr, 3), "t_fine_s": round(t_fine, 2), "tries": tries,
           "best_cand_m": round(min(cand_d), 1), "top1_cand_m": round(cand_d[0], 1)}
    hd = [angle_diff_deg(h, q["yaw"]) for _, _, h in cands[:1] if h is not None and q.get("yaw") is not None]
    if hd:
        row["top1_heading_err_deg"] = round(hd[0], 1)
    if out:
        row |= {"fix": True, "rank": out["rank"], "inliers": out["inliers"], "err_m": round(err_m(q, out["fix"], ortho), 2)}
    else:
        row |= {"fix": False}
    return row


def prior_one(loc, q, ortho, rng, headings, gsds):
    e, n = q["truth_en"]
    a = rng.uniform(0, 2 * math.pi)
    prior = lonlat_of(ortho, e + PRIOR_OFFSET_M * math.cos(a), n + PRIOR_OFFSET_M * math.sin(a))
    best, t, k = fine(loc, q, ortho, prior, headings, PRIOR_RADIUS_M, gsds)
    row = {"t_fine_s": round(t, 2), "tries": k, "fix": bool(best["fix"]), "inliers": best["inliers"]}
    if best["fix"]:
        row["err_m"] = round(err_m(q, best["fix"], ortho), 2)
    return row


def summarize(rows):
    fixes = [r for r in rows if r["fix"]]
    errs = sorted(r["err_m"] for r in fixes)
    s = {"n": len(rows), "fixes": len(fixes), "wrong_fixes_gt50m": sum(e > WRONG_FIX_M for e in errs),
         "within_5m": sum(e <= 5 for e in errs), "within_20m": sum(e <= 20 for e in errs),
         "median_err_m": round(statistics.median(errs), 2) if errs else None,
         "median_t_s": round(statistics.median(r["t_fine_s"] + r.get("t_vpr_s", 0) for r in rows), 2),
         "median_tries": statistics.median(r["tries"] for r in rows)}
    if "best_cand_m" in rows[0]:
        s["vpr_top5_within_100m"] = sum(r["best_cand_m"] <= 100.0 for r in rows)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="aliked")
    ap.add_argument("--strategy", default="gem/db-aug8")
    ap.add_argument("--db-year", default="2023")
    ap.add_argument("--synth-years", nargs="*", default=["2019", "2023"])
    ap.add_argument("--tile", type=int, default=250)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--real", action="store_true", help="eBee frames instead of synthetic")
    ap.add_argument("--agl-mode", default="ellipsoid", help="AGL hypothesis used for the VPR crop")
    ap.add_argument("--fine-year", default=None, help="map vintage for fine matching (default: the DB year)")
    ap.add_argument("--real-yaws", type=int, default=8)
    ap.add_argument("--skip-prior", action="store_true")
    ap.add_argument("--cand-radius-m", type=float, default=CANDIDATE_RADIUS_M)
    ap.add_argument("--out", default="chain_results.json")
    a = ap.parse_args()
    torch.set_num_threads(8)
    globals()["CANDIDATE_RADIUS_M"] = a.cand_radius_m
    desc = Dinov2Describer("dinov2_vits14", R.OUT_PX)
    desc.tag = "vits14"
    ortho = R.load_map(a.db_year)
    yaws = R.YAWS if (not a.real or a.real_yaws == len(R.YAWS)) else [0]
    stride = {250: 50, 100: 50, 70: 35}[a.tile]
    db = R.build_db(desc, ortho, a.db_year, a.tile, stride, yaws)
    desc.centroids = torch.from_numpy(db["centroids"]).to(desc.device)
    idx = R.make_indexes(db, yaws)
    loc = Localizer(a.features)
    fine_map = ortho if a.fine_year in (None, a.db_year) else R.load_map(a.fine_year)
    path = R.OUT / a.out
    report = json.loads(path.read_text()) if path.exists() else {}
    if a.real:
        qs = R.real_queries(a.agl_mode, a.tile, ortho.crs)
        other = R.real_queries("msl" if a.agl_mode == "ellipsoid" else "ellipsoid", a.tile, ortho.crs)
        for q, o in zip(qs, other):
            q["gsds"] = [q["frame_gsd_est"], o["frame_gsd_est"]]  # AGL is ambiguous: try both hypotheses
        sets = {f"real-agl-{a.agl_mode}": qs}
    else:
        sets = {f"src{y}": R.synth_queries(R.load_map(y) if y != a.db_year else ortho, ortho, a.tile, a.n, a.seed)
                for y in a.synth_years}
    for label, qs in sets.items():
        key = f"{a.strategy}/{a.features}/db{a.db_year}/fine{a.fine_year or a.db_year}/{a.tile}m/{label}" + (f"/r{a.cand_radius_m:g}" if a.cand_radius_m != 100.0 else "")
        rng = np.random.default_rng(a.seed)
        chain_rows, prior_rows = [], []
        for i, q in enumerate(qs):
            gsds = q.get("gsds", [q["frame_gsd_est"]])
            cr = chain_one(loc, desc, idx, db, q, fine_map, a.strategy, gsds)
            chain_rows.append(cr | {"case": q.get("name", i)})
            if not a.skip_prior:
                headings = ([q["prior_yaw"]] if q.get("yaw") is not None
                            else [float(h) for h in range(0, 360, REAL_SWEEP_STEP_DEG)])
                prior_rows.append(prior_one(loc, q, fine_map, rng, headings, gsds) | {"case": q.get("name", i)})
            print(key, i, json.dumps(chain_rows[-1]), json.dumps(prior_rows[-1]) if prior_rows else "", flush=True)
        report[key] = {"chain": {"summary": summarize(chain_rows), "rows": chain_rows}}
        if prior_rows:
            report[key]["known_prior"] = {"summary": summarize(prior_rows), "rows": prior_rows}
        print(key, "CHAIN", json.dumps(report[key]["chain"]["summary"]), flush=True)
        if prior_rows:
            print(key, "PRIOR", json.dumps(report[key]["known_prior"]["summary"]), flush=True)
        path.write_text(json.dumps(report, indent=1, default=float))


if __name__ == "__main__":
    main()
