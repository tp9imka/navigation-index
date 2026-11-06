"""Fusion and scoring over the cached front end (results/frontend.json). numpy + the altpnt v2 filter.

For each heading-bias variant (0 and 2 deg added to the recorded yaw) and map density:
  VO only | VO + single-frame fixes | VO + multi-frame voting, each fused by the altpnt-integrity v2
  EKF (heading and scale error states) with no gate ('none') or with chi-square gate +
  solution-separation FDE + protection level ('full').

    python run_fusion.py --data <dir with vpair_sample/>     # writes results/e2e_result.json, CSV, SVG, navdash
"""
import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

import nav_core as nc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "altpnt-integrity"))
import altpnt_integrity as v1  # noqa: E402
import altpnt_v2 as v2  # noqa: E402
import stanford  # noqa: E402

YAW_BIASES_DEG = (0.0, 2.0)
FIX_PERIODS = (1, 5)
VOTE_EPOCHS = 5            # look back this many fix epochs
VOTE_MIN_SUPPORT = 3       # distinct fix epochs (including the current one) that must agree
VOTE_RADIUS_M = 30.0
ACCEL_SIGMA = 3.0          # m/s^2 white acceleration: no IMU in VPAIR, constant-velocity model
VGEO_R_FLOOR_M = 5.382     # geoloc overbound sigma from ../altpnt-integrity/calibration.json
ALERT_LIMIT_M = v1.ALERT_LIMIT
IMU_ZERO = [(0.0, 0.0)] * v1.IMU_PER_EPOCH
# per-frame match gates: strict = geoloc-license-clean's 25 inliers + homography scale check
GATES = {"strict": {"min_inliers": None, "check_scale": True}, "loose": {"min_inliers": 8, "check_scale": False}}
MODES = ("none", "gate", "full")
PRIMARY = (2.0, 8, 1, "loose", "vote", "gate")   # bias, stride, period, match gate, fix mode, integrity mode


class EkfNoImu(v2.Ekf2):
    """altpnt v2 EKF driven by VO velocity only: velocity random walk sized for an aircraft."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        q = ACCEL_SIGMA ** 2
        for i in range(2):
            self.Q[i][i] += q * v1.EPOCH ** 3 / 3
            self.Q[i][2 + i] += q * v1.EPOCH ** 2 / 2
            self.Q[2 + i][i] += q * v1.EPOCH ** 2 / 2
            self.Q[2 + i][2 + i] += q * v1.EPOCH


def vo_steps(fe, att, bias_deg):
    v = fe["vo"]
    d = np.array(v["d_raw_px"])
    C, P, h = np.array(v["C"]), np.array(v["P"]), v["hagl_m"]
    dtan = np.diff(np.tan(att[:, :2]), axis=0)
    b = math.radians(bias_deg)
    return np.array([nc.r_yaw(att[k, 2] + b) @ (C @ d[k] + h * (P @ dtan[k])) for k in range(len(d))])


def calibrate_tiles(fe, poses):
    """Fit tile pixel*depth => E/N on the GNSS window pairs (query k vs renders k +-1, +-2)."""
    v, tiles = fe["vo"], fe["tiles"]
    P, h = np.array(v["P"]), v["hagl_m"]
    c = np.array(tiles["centre_px"])
    X, Y = [], []
    for key, m in fe["matches"].items():
        k, j = map(int, key.split(":"))
        if k >= nc.CALIB_FRAMES or j >= tiles["n_renders"] or abs(j - k) > 2 or j == k or not good(fe, m):
            continue
        X.append(m["depth"] * (np.array(m["p_tile"]) - c))
        Y.append(poses["en"][k] - np.array(tiles["en"][j]) - nc.nadir_offset(poses["att"][k], 0.0, h, P))
    X, Y = np.array(X), np.array(Y)
    T = nc.fit_tile_scale(X, Y)
    res = Y - X @ T.T
    return T, {"pairs": len(X), "focal_px": round(float(1 / math.sqrt(abs(np.linalg.det(T)))), 1),
               "rotation_deg": round(math.degrees(math.atan2(T[1, 0], T[0, 0])), 2),
               "det_sign": int(np.sign(np.linalg.det(T))),
               "residual_rms_m": round(float(np.sqrt(np.mean(np.sum(res ** 2, 1)))), 2),
               "residual_per_axis_std_m": [round(float(x), 2) for x in res.std(0)]}


def good(fe, m, gate="strict"):
    g = GATES[gate]
    lo, hi = fe["h_scale_range"] if g["check_scale"] else (0.0, math.inf)
    return m["p_tile"] is not None and m["inliers"] >= (g["min_inliers"] or fe["min_inliers"]) and lo <= m["h_scale"] <= hi


def candidates(fe, poses, T, stride, bias_deg, gate="strict"):
    v, tiles = fe["vo"], fe["tiles"]
    P, h = np.array(v["P"]), v["hagl_m"]
    c = np.array(tiles["centre_px"])
    ten = np.array(tiles["en"])
    out = {}
    for q in fe["queries"]:
        k = q["k"]
        nadir = nc.nadir_offset(poses["att"][k], math.radians(bias_deg), h, P)
        lst = []
        for rank, (j, sim) in enumerate(q["top"][str(stride)]):
            m = fe["matches"][f"{k}:{j}"]
            pos = nc.fix_position(ten[j], T, m["depth"], m["p_tile"], c, nadir) if good(fe, m, gate) else None
            lst.append({"tile": j, "rank": rank, "sim": sim, "inliers": m["inliers"], "pos": pos,
                        "distractor": j >= tiles["n_renders"],
                        "err": None if pos is None else float(np.linalg.norm(pos - poses["en"][k]))})
        out[k] = lst
    return out


def fixes(cands, vo_pos, period, mode, start, n):
    out = {}
    for k in range(start + 1, n):
        if (k - start) % period:
            continue
        if mode == "single":
            c = nc.single_frame_fix(cands[k])
            out[k] = None if c is None else c["pos"]
        else:
            sub = {s: cands[s] for s in range(start + 1, k + 1) if (s - start) % period == 0}
            r = nc.vote(sub, vo_pos, k, period * (VOTE_EPOCHS - 1), VOTE_RADIUS_M, VOTE_MIN_SUPPORT)
            out[k] = None if r is None else r[0]
    return out


def run_filter(steps, fx, poses, cfg, mode, start):
    """altpnt v2 Monitor2 over the real flight. Returns per-frame rows."""
    en = poses["en"]
    n = len(en)
    x0 = [en[start][0], en[start][1], *(en[start] - en[start - 1]) / nc.FRAME_DT, 0, 0, 0, 0]
    P0 = v2.mat.zeros(8, 8)
    for i, s in enumerate([3, 3, 1.0, 1.0, 0.05, 0.05, cfg.s_sigma, cfg.psi_sigma]):
        P0[i][i] = s * s
    mon = v2.Monitor2(EkfNoImu(x0, P0, cfg), v1.monitored_sources(SC) if mode == "full" else (), mode != "none", cfg)
    rows = []
    for k in range(start + 1, n):
        z = fx.get(k)
        ep = {"t": float(k), "imu": IMU_ZERO, "vio": (tuple(steps[k - 1] / nc.FRAME_DT), cfg.vio_r),
              "gnss": None, "gnss_state": "denied", "vgeo": None if z is None else tuple(z), "magnav": None}
        err = None if z is None else float(np.linalg.norm(np.asarray(z) - en[k]))
        ep["vgeo_state"] = "none" if z is None else ("false" if err > nc.FALSE_FIX_M else "ok")
        was_excluded = "vgeo" in mon.excluded
        t0 = time.perf_counter()
        hpl, events = mon.step(ep)
        dt = time.perf_counter() - t0
        x = mon.main.x
        hpe = math.hypot(x[0] - en[k][0], x[1] - en[k][1])
        avail = hpl < ALERT_LIMIT_M and not mon.ambiguous
        accepted = z is not None and not was_excluded and "gate:vgeo" not in events and "exclude:vgeo" not in events
        rows.append({"k": k, "est": (x[0], x[1]), "hpe": hpe, "hpl": hpl, "available": avail,
                     "region": stanford.classify(hpe, hpl if avail else max(hpl, ALERT_LIMIT_M), ALERT_LIMIT_M),
                     "fix_err": err, "accepted": accepted, "events": events, "psi_deg": math.degrees(x[7]),
                     "scale": x[6], "excluded": "vgeo" in mon.excluded, "t_s": dt})
    return rows


class _Sc:
    magnav = False


SC = _Sc()


def summarize_filter(rows, poses, dist, start):
    en = poses["en"]
    est = np.vstack([en[:start + 1], np.array([r["est"] for r in rows])])
    prof, err = nc.error_profile(est, en, dist, start)
    offered = [r for r in rows if r["fix_err"] is not None]
    acc = [r for r in offered if r["accepted"]]
    tally = stanford.tally(rows)
    return {**prof,
            "fixes_offered": len(offered),
            "fixes_offered_false": sum(r["fix_err"] > nc.FALSE_FIX_M for r in offered),
            "fixes_accepted": len(acc),
            "fixes_accepted_false": sum(r["fix_err"] > nc.FALSE_FIX_M for r in acc),
            "accepted_fix_err_median_m": round(float(np.median([r["fix_err"] for r in acc])), 1) if acc else None,
            "exclusions": sum(any(e.startswith("exclude:") for e in r["events"]) for r in rows),
            "integrity_available_pct": round(100 * sum(r["available"] for r in rows) / len(rows), 1),
            "hpl_median_m": round(float(np.median([r["hpl"] for r in rows])), 1),
            "stanford": tally,
            "heading_err_est_deg_final": round(rows[-1]["psi_deg"], 2),
            "filter_step_ms_median": round(1000 * float(np.median([r["t_s"] for r in rows])), 2)}, err


def candidate_stats(cands, start, n):
    ks = range(start + 1, n)
    gated = [c for k in ks for c in cands[k] if c["pos"] is not None]
    top1_ok = sum(1 for k in ks if cands[k][0]["err"] is not None and cands[k][0]["err"] <= nc.FALSE_FIX_M)
    single = [nc.single_frame_fix(cands[k]) for k in ks]
    return {"frames": len(ks), "gated_candidates": len(gated),
            "gated_candidates_false": sum(c["err"] > nc.FALSE_FIX_M for c in gated),
            "gated_false_from_distractors": sum(c["err"] > nc.FALSE_FIX_M and c["distractor"] for c in gated),
            "frames_with_any_gated_candidate": sum(s is not None for s in single),
            "frames_with_a_correct_candidate": sum(any(c["err"] is not None and c["err"] <= nc.FALSE_FIX_M for c in cands[k]) for k in ks),
            "top1_retrieval_gives_correct_fix": top1_ok,
            "single_frame_fix_err_median_m": round(float(np.median([s["err"] for s in single if s])), 1) if any(single) else None}


def fix_stats(fx, en):
    att = [k for k in fx]
    got = [k for k in fx if fx[k] is not None]
    errs = [float(np.linalg.norm(np.asarray(fx[k]) - en[k])) for k in got]
    return {"attempts": len(att), "produced": len(got), "availability_pct": round(100 * len(got) / max(len(att), 1), 1),
            "false": sum(e > nc.FALSE_FIX_M for e in errs),
            "err_median_m": round(float(np.median(errs)), 1) if errs else None,
            "err_p95_m": round(float(np.percentile(errs, 95)), 1) if errs else None,
            "err_max_m": round(float(max(errs)), 1) if errs else None}


def filter_cfg(vgeo_r):
    c = v2.calibrated_values(source="nadir-vo-vpair")
    cal = v2.load_cal()["relative"]["models"]["nadir-vo-vpair"]["fit_whole_run"]
    return v2.FilterCfg("altpnt v2 L3v, VO R at this flight's speed, fix R from the GNSS window",
                        psi_sigma=c["psi_sigma"], s_sigma=c["s_sigma"],
                        vio_r=cal["white_frac_of_speed"] * cal["mean_speed_mps"], vgeo_r=vgeo_r,
                        vgeo_bias=c["vgeo_bias"], priors=c["priors"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory containing vpair_sample/ (poses only are read)")
    ap.add_argument("--frontend", default=str(HERE / "results" / "frontend.json"))
    ap.add_argument("--frontend-biased", default=str(HERE / "results" / "frontend_yaw2.json"),
                    help="front end rerun with the heading error in the north-up rotation; used for that bias if present")
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    fe = json.loads(Path(a.frontend).read_text())
    fe_b = json.loads(Path(a.frontend_biased).read_text()) if Path(a.frontend_biased).exists() else None
    poses = nc.load_poses(Path(a.data) / "vpair_sample")
    en, n, start = poses["en"], len(poses["en"]), nc.CALIB_FRAMES
    dist = nc.distance_along(en)
    T, tcal = calibrate_tiles(fe, poses)
    vgeo_r = max(VGEO_R_FLOOR_M, max(tcal["residual_per_axis_std_m"]))
    cfg = filter_cfg(vgeo_r)
    res = {"dataset": fe["dataset"], "path_after_calibration_m": round(float(dist[-1] - dist[start]), 1),
           "calibration_frames": start, "tile_calibration": tcal,
           "filter": {k: (round(v, 5) if isinstance(v, float) else v) for k, v in vars(cfg).items()} | {"accel_sigma": ACCEL_SIGMA},
           "alert_limit_m": ALERT_LIMIT_M, "false_fix_m": nc.FALSE_FIX_M,
           "vote": {"epochs": VOTE_EPOCHS, "min_support": VOTE_MIN_SUPPORT, "radius_m": VOTE_RADIUS_M},
           "runs": []}
    errs = {}
    res["frontend_per_bias"] = {}
    for bias in YAW_BIASES_DEG:
        fb = fe_b if bias and fe_b and fe_b.get("yaw_bias_deg") == bias else fe
        res["frontend_per_bias"][f"{bias:g}"] = Path(a.frontend_biased if fb is fe_b else a.frontend).name
        steps = vo_steps(fe, poses["att"], bias)
        vo_pos = np.vstack([en[:start + 1], en[start] + np.cumsum(steps[start:], axis=0)])
        prof, err = nc.error_profile(vo_pos, en, dist, start)
        res["runs"].append({"yaw_bias_deg": bias, "config": "vo_only", **prof})
        errs[(bias, "vo_only")] = err
        rows = run_filter(steps, {}, poses, cfg, "none", start)
        s, err = summarize_filter(rows, poses, dist, start)
        res["runs"].append({"yaw_bias_deg": bias, "config": "vo_only_filtered", **s})
        for stride in fe["strides"]:
            for gate in GATES:
                cands = candidates(fb, poses, T, stride, bias, gate)
                cs = candidate_stats(cands, start, n)
                for period in FIX_PERIODS:
                    for fmode in ("single", "vote"):
                        fx = fixes(cands, vo_pos, period, fmode, start, n)
                        fs = fix_stats(fx, en)
                        for mode in MODES:
                            rows = run_filter(steps, fx, poses, cfg, mode, start)
                            s, err = summarize_filter(rows, poses, dist, start)
                            errs[(bias, f"{fmode}_{mode}_{gate}_s{stride}_p{period}")] = err
                            res["runs"].append({"yaw_bias_deg": bias, "config": f"{fmode}_fix", "integrity": mode,
                                                "match_gate": gate, "map_stride": stride, "fix_period": period,
                                                "fix_frontend": fs, "candidates": cs, **s})
                            if (bias, stride, period, gate, fmode, mode) == PRIMARY:
                                primary_rows, primary_fx = rows, fx
    t = fe["timing"]
    per_frame = {"vo_pair_s": fe["vo"]["time"]["median_s"], "query_prep_aliked_s": t["prep_query_s"]["median_s"],
                 "dinov2_describe_s": t["describe_query_s"]["median_s"], "search_s": t["search_s"]["median_s"],
                 "lightglue_topk_s": {s: v["median_s"] for s, v in t["match_topk_s"].items()},
                 "filter_step_s": round(float(np.median([r["t_s"] for r in primary_rows])), 5)}
    per_frame["total_s_stride1"] = round(per_frame["vo_pair_s"] + per_frame["query_prep_aliked_s"] + per_frame["dinov2_describe_s"]
                                         + per_frame["search_s"] + per_frame["lightglue_topk_s"]["1"] + per_frame["filter_step_s"], 3)
    res["runtime_per_frame_median"] = per_frame | {"device": fe["device"], "host": t["host"], "top_k": fe["top_k"],
                                                   "frontend_wall_s": t["wall_total_s"], "map_descriptors_s": t["map_descriptors_s"]}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "e2e_result.json").write_text(json.dumps(res, indent=1, default=float))
    write_error_csv(out / "error_vs_distance.csv", errs, dist, start)
    write_svg(out / "error_vs_distance.svg", errs, dist, start)
    export_navdash(out / "navdash", poses, errs, primary_rows, primary_fx, fe, T)
    print_table(res)


def write_error_csv(path, errs, dist, start):
    keys = list(errs)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "distance_m"] + [f"{c}_bias{b:g}" for b, c in keys])
        for k in range(start, len(dist)):
            w.writerow([k, round(float(dist[k] - dist[start]), 1)] + [round(float(errs[x][k]), 2) for x in keys])


SVG_SERIES = [((0.0, "vo_only"), "#ffb74d", "VO only, recorded yaw"),
              ((2.0, "vo_only"), "#e65100", "VO only, yaw +2 deg"),
              ((2.0, "single_none_loose_s8_p1"), "#ef5350", "single-frame fixes, loose match gate, no filter gate (clipped)"),
              ((2.0, "single_gate_loose_s8_p1"), "#ab47bc", "single-frame fixes, loose match gate, chi-square gate"),
              ((2.0, "vote_none_loose_s8_p1"), "#26a69a", "voted fixes, loose match gate, no filter gate"),
              ((2.0, "single_none_strict_s1_p1"), "#1e88e5", "single-frame fixes, strict gate, dense map")]
SVG_YMAX_M = 10000.0


def write_svg(path, errs, dist, start, w=760, h=380, pad=50):
    d = dist[start:] - dist[start]
    series = [(errs[k][start:], col, lab) for k, col, lab in SVG_SERIES if k in errs]
    ymax = min(SVG_YMAX_M, max(10.0, max(float(e.max()) for e, _, _ in series)))
    yl = lambda v: h - pad - (math.log10(min(max(v, 1.0), ymax)) / math.log10(ymax)) * (h - 2 * pad)
    xl = lambda v: pad + v / d[-1] * (w - 2 * pad)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 20 * len(series)}" font-family="sans-serif" font-size="11">',
             f'<rect width="100%" height="100%" fill="white"/>']
    for v in (1, 10, 100, 1000):
        if v <= ymax:
            parts.append(f'<line x1="{pad}" x2="{w - pad}" y1="{yl(v):.1f}" y2="{yl(v):.1f}" stroke="#ddd"/>'
                         f'<text x="{pad - 6}" y="{yl(v) + 4:.1f}" text-anchor="end">{v} m</text>')
    for km in range(0, int(d[-1] / 1000) + 1):
        parts.append(f'<text x="{xl(km * 1000):.1f}" y="{h - pad + 16}" text-anchor="middle">{km} km</text>')
    parts.append(f'<text x="{w / 2}" y="{h - 10}" text-anchor="middle">distance flown since GNSS loss (VPAIR sample, real imagery); map stride 8 unless noted</text>')
    parts.append(f'<text x="{pad}" y="{pad - 14}">horizontal error, log scale, clipped at {ymax:.0f} m</text>')
    for i, (e, col, lab) in enumerate(series):
        pts = " ".join(f"{xl(x):.1f},{yl(y):.1f}" for x, y in zip(d, e))
        parts.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.6" points="{pts}"/>')
        parts.append(f'<rect x="{pad}" y="{h + 6 + 20 * i}" width="14" height="4" fill="{col}"/>'
                     f'<text x="{pad + 20}" y="{h + 12 + 20 * i}">{lab}</text>')
    parts.append("</svg>")
    Path(path).write_text("\n".join(parts))


def export_navdash(nd, poses, errs, rows, fx, fe, T):
    nd.mkdir(parents=True, exist_ok=True)
    lat0, lon0, en, start = poses["lat0"], poses["lon0"], poses["en"], nc.CALIB_FRAMES
    ll = lambda p: nc.common.enu_to_ll(lat0, lon0, float(p[0]), float(p[1]))
    nc.common.write_navdash(str(nd / "truth.jsonl"), "truth", "truth", "VPAIR query poses (GNSS/INS)",
                            [{"t": float(k), "lat": ll(p)[0], "lon": ll(p)[1]} for k, p in enumerate(en)])
    steps = vo_steps(fe, poses["att"], 2.0)
    vo = np.vstack([en[:start + 1], en[start] + np.cumsum(steps[start:], axis=0)])
    nc.common.write_navdash(str(nd / "vo_only.jsonl"), "vo-only", "ins", "Nadir VO only, yaw +2 deg",
                            [{"t": float(k), "lat": ll(p)[0], "lon": ll(p)[1], "sources": ["nadir-vo"]} for k, p in enumerate(vo)],
                            color="#ffb74d")
    ev = [{"t": float(start), "event": "gnss_lost", "text": "end of GNSS window: VO + visual fixes from here"}]
    for r in rows:
        if any(e.startswith("exclude:vgeo") for e in r["events"]):
            ev.append({"t": float(r["k"]), "event": "fix_excluded", "text": "solution separation excluded visual fixes"})
        if any(e.startswith("readmit:vgeo") for e in r["events"]):
            ev.append({"t": float(r["k"]), "event": "fix_readmitted", "text": "visual fixes passed probation"})
        if "gate:vgeo" in r["events"]:
            ev.append({"t": float(r["k"]), "event": "fix_excluded", "text": f"chi-square gate rejected a visual fix ({r['fix_err']:.0f} m off truth)"})
    out = [{"t": float(k), "lat": ll(en[k])[0], "lon": ll(en[k])[1], "health": "trusted", "sources": ["gnss"]} for k in range(start + 1)]
    for r in rows:
        la, lo = ll(r["est"])
        out.append({"t": float(r["k"]), "lat": la, "lon": lo, "pl_m": round(r["hpl"], 2),
                    "health": "excluded" if r["excluded"] else ("trusted" if r["available"] else "unavailable"),
                    "alarm": not r["available"], "sources": ["nadir-vo"] + (["visual-fix"] if r["accepted"] else [])})
    nc.common.write_navdash(str(nd / "fused_vote_integrity.jsonl"), "fused-vote", "fused",
                            "VO + voted fixes + chi-square gate (yaw +2 deg, map stride 8, loose match gate)", out, color="#4fc3f7", primary=True,
                            extra={"alert_limit_m": ALERT_LIMIT_M,
                                   "pl_method": "altpnt-integrity v2 Monitor2 in gate mode: fault-free HPL only (k_ff sigma + fix bias), no fault hypotheses, not certified",
                                   "run_meta": {"time": "frame index, 1 s per frame (VPAIR has no timestamps)"}},
                            events=ev)
    nc.common.write_navdash(str(nd / "fixes_voted.jsonl"), "fixes-voted", "altpnt", "Voted visual fixes",
                            [{"t": float(k), "lat": ll(p)[0], "lon": ll(p)[1], "sources": ["dinov2+lightglue"]}
                             for k, p in sorted(fx.items()) if p is not None], color="#69f0ae")
    nc.common.write_manifest(str(nd / "manifest.json"), "VPAIR: nadir VO + DINOv2 top-5 + LightGlue fixes + voting + gate",
                             ["truth.jsonl", "vo_only.jsonl", "fused_vote_integrity.jsonl", "fixes_voted.jsonl"])


def print_table(res):
    print(f"{'bias':>5} {'config':12}{'gate':7}{'integ':6}{'stride':>7}{'per':>4}{'final':>8}{'rms':>8}{'max':>8}"
          f"{'fixes':>7}{'false':>6}{'acc':>5}{'accF':>5}{'avail%':>7}{'HMI':>5}")
    for r in res["runs"]:
        f = r.get("fix_frontend", {})
        print(f"{r['yaw_bias_deg']:>5g} {r['config']:12}{r.get('match_gate', '-'):7}{r.get('integrity', '-'):6}{r.get('map_stride', '-'):>7}{r.get('fix_period', '-'):>4}"
              f"{r['final_m']:>8}{r['rms_m']:>8}{r['max_m']:>8}{f.get('produced', '-'):>7}{f.get('false', '-'):>6}"
              f"{r.get('fixes_accepted', '-'):>5}{r.get('fixes_accepted_false', '-'):>5}{r.get('integrity_available_pct', '-'):>7}"
              f"{r.get('stanford', {}).get('HMI', '-'):>5}")


if __name__ == "__main__":
    main()
