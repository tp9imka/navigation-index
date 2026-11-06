"""Two independent absolute sources on the real VPAIR flight: visual fixes + terrain-relative navigation.

VO and visual fixes are the cached real-imagery front end of ../e2e-visual-nav-vpair (results/frontend*.json,
re-scored by import, no GPU). TRN sensors are simulated from the real NRW 1 m DSM / GLO-30 at the real
VPAIR poses (trn.py). Fusion and integrity: ../altpnt-integrity v2 (Ekf2 + Monitor2: chi-square gate,
solution-separation FDE, protection level), TRN in its 'magnav' slot with R from the TRN's own sigma.

    python run_two_source.py --data <dir with vpair_sample/>     # writes results/two_source_result.json, navdash, SVG
"""
import argparse
import copy
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import terrain  # noqa: E402  (puts ../e2e-visual-nav-vpair on the path)
import trn  # noqa: E402

import nav_core as nc  # noqa: E402
import run_fusion as rf  # noqa: E402
import nav2  # noqa: E402  (terrain-heightmap-pf, via trn)

v1, v2, stanford = rf.v1, rf.v2, rf.stanford

YAW_BIAS_DEG = 2.0                # AHRS heading error, as the e2e headline (front end rerun with it)
VIS_STRIDES = (8, 1)              # map tile spacing 360 m (headline) and 45 m
VIS_GATE = "strict"
ALS = (25.0, 50.0, 100.0)
SEEDS = 10                        # TRN sensor noise / PF draws; visual fixes are deterministic
TRN_VARIANTS = ("lidar5", "glo30", "radalt")
# GLO-30 config: the 300 m-swath sensor binned to 30 m; 21-cell local map as ../terrain-heightmap-pf run_lidar 30 m
GLO30_MAPCFG = trn.MapCfg(res=30.0, patch_cells=21, obs_res_m=30.0, update_every_frames=4, search_min_m=150.0,
                          search_max_m=1000.0, world_err_sigma=0.0, jitter_min_m=3.0)
# faults (frame indices; frames are ~45 m apart, GNSS lost at frame 10)
# map misregistration: offset ramps 0 => 40 m over RAMP frames, then holds until the window ends
MISREG = {"persistent": {"frames": (100, 199), "offset_m": 40.0, "dir_deg": 45.0, "ramp_frames": 40},
          "transient": {"frames": (100, 140), "offset_m": 40.0, "dir_deg": 45.0, "ramp_frames": 40}}
AMBIG_FRAMES = (60, 100)
PRIMARY = ("lidar5", 8)
THIRD = "glo30"                   # three-source demo: GLO-30 TRN in the 'gnss' slot next to the LiDAR TRN
SOURCES = ("vgeo", "magnav", "gnss")   # altpnt slot names: visual fixes, TRN, second TRN (three-source runs)
ORDERS = {"vis_first": ("vgeo", "magnav"), "trn_first": ("magnav", "vgeo")}


def load(data):
    poses = nc.load_poses(Path(data) / "vpair_sample")
    fe = json.loads((rf.HERE / "results" / "frontend.json").read_text())
    fe_b = json.loads((rf.HERE / "results" / "frontend_yaw2.json").read_text())
    assert fe_b.get("yaw_bias_deg") == YAW_BIAS_DEG
    en, start = poses["en"], nc.CALIB_FRAMES
    T, _ = rf.calibrate_tiles(fe, poses)
    steps = rf.vo_steps(fe, poses["att"], YAW_BIAS_DEG)
    vo_pos = np.vstack([en[:start + 1], en[start] + np.cumsum(steps[start:], axis=0)])
    vis = {}
    for s in VIS_STRIDES:
        cands = rf.candidates(fe_b, poses, T, s, YAW_BIAS_DEG, VIS_GATE)
        vis[s] = {k: p for k, p in rf.fixes(cands, vo_pos, 1, "single", start, len(en)).items() if p is not None}
    _, tcal = rf.calibrate_tiles(fe, poses)
    cfg = rf.filter_cfg(max(rf.VGEO_R_FLOOR_M, max(tcal["residual_per_axis_std_m"])))
    cfg.trn_from_spread, cfg.trn_infl = True, 1.0
    cfg3 = copy.copy(cfg)
    cfg3.priors = dict(cfg.priors, gnss=cfg.priors["magnav"])

    track = terrain.track_utm(Path(data) / "vpair_sample")
    dsm, origin = terrain.load_dsm(HERE / "data" / "nrw_tiles")
    fr = terrain.Frames(poses["lat0"], poses["lon0"], origin)
    truth_g, msl = track[:, :2] - origin, track[:, 2]
    g_vo = fr.en_to_grid(en[:-1] + steps) - fr.en_to_grid(en[:-1])   # VO steps expressed on the UTM grid
    dsm1, nodata = terrain.fill_nearest(dsm)
    ref5 = terrain.block_mean(dsm1, 5)
    t0 = time.perf_counter()
    beam = trn.bfb_navs.beam_map(ref5, 5.0, float(msl.mean()), trn.AltCfg().beam_full_deg)
    beam_s = time.perf_counter() - t0
    glo, _ = terrain.fill_nearest(terrain.glo30_on_grid(origin, dsm.shape, cache=HERE / "data"))
    w30 = terrain.block_mean(dsm1, 30)
    h, w = min(glo.shape[0], w30.shape[0]), min(glo.shape[1], w30.shape[1])
    agl = msl - nc_bilinear(dsm1, truth_g)
    return {"poses": poses, "en": en, "start": start, "steps": steps, "vo_pos": vo_pos, "vis": vis, "cfg": cfg, "cfg3": cfg3,
            "fr": fr, "truth_g": truth_g, "msl": msl, "g_vo": g_vo, "dsm1": dsm1, "ref5": ref5, "beam": beam,
            "glo": glo[:h, :w], "w30": w30[:h, :w], "origin": origin,
            "info": {"utm_origin": origin.tolist(), "dsm_nodata_pct": round(100 * float(nodata.mean()), 1),
                     "dsm_tiles": len(list((HERE / "data" / "nrw_tiles").glob("dom1_*.tif"))),
                     "ground_dsm_on_track_m": [round(float(nc_bilinear(dsm1, truth_g).min()), 1),
                                               round(float(nc_bilinear(dsm1, truth_g).max()), 1)],
                     "agl_m": [round(float(agl.min()), 1), round(float(np.median(agl)), 1), round(float(agl.max()), 1)],
                     "msl_m": [round(float(msl.min()), 1), round(float(msl.max()), 1)],
                     "grid_rotation_deg": round(fr.rotation_deg(en), 3), "beam_map_s": round(beam_s, 1),
                     "glo30_minus_dsm30_on_track_m": glo_vs_dsm(glo[:h, :w], w30[:h, :w], truth_g)}}


def nc_bilinear(grid, pts, res=1.0):
    return trn.core.bilinear(grid, pts[:, 0], pts[:, 1], res)


def glo_vs_dsm(glo, w30, truth_g):
    d = nc_bilinear(glo, truth_g, 30.0) - nc_bilinear(w30, truth_g, 30.0)
    return {"mean": round(float(np.mean(d)), 1), "std": round(float(np.std(d)), 1)}


def trn_fixes(ctx, variant, seed, fault_frames=()):
    """TRN fixes {frame: (E, N, sigma)} in the e2e local EN frame, plus diagnostics."""
    tg, g_vo, start = ctx["truth_g"], ctx["g_vo"], ctx["start"]
    t0 = time.perf_counter()
    if variant == "radalt":
        c = trn.AltCfg()
        rng = np.random.default_rng(seed)
        alt = trn.simulate_altimeter(ctx["dsm1"], tg, ctx["msl"], c, rng)
        fx, diag = trn.run_tercom(ctx["beam"], 5.0, alt, g_vo, start, tg[start], c, fault_frames)
        extra = {"alt_dropped": alt["dropped"], "alt_outliers": alt["outliers"],
                 "beam_minus_nadir_range_median_m": round(float(np.median(alt["range_true"] - alt["agl_true_nadir"])), 1)}
    else:
        v = nav2.V2()
        hdg = math.radians(-YAW_BIAS_DEG)     # VO yaw +2 deg (clockwise) = -2 deg in the sim's CCW convention
        if variant == "lidar5":
            fx, diag, _ = trn.run_heightmap_pf(ctx["ref5"], ctx["ref5"], tg, g_vo, hdg, start, trn.MapCfg(), v, seed,
                                               fault_frames)
        else:
            fx, diag, _ = trn.run_heightmap_pf(ctx["glo"], ctx["w30"], tg, g_vo, hdg, start, GLO30_MAPCFG, v, seed,
                                               fault_frames)
        extra = {"bias_est_final_deg": round(diag[-1]["bias_est_deg"], 2) if diag else None}
    wall = time.perf_counter() - t0
    if not fx:
        return {}, {"attempts": len(diag), "fixes": 0, "wall_s": round(wall, 2), **extra}
    ks = sorted(fx)
    en = ctx["fr"].grid_to_en(np.array([fx[k][:2] for k in ks]))
    out = {k: (float(p[0]), float(p[1]), fx[k][2]) for k, p in zip(ks, en)}
    err = np.array([math.hypot(out[k][0] - ctx["en"][k][0], out[k][1] - ctx["en"][k][1]) for k in ks])
    sig = np.array([out[k][2] for k in ks])
    nominal = np.array([not any(d["k"] == k and d["faulted"] for d in diag) for k in ks])
    return out, {"attempts": len(diag), "fixes": len(ks), "wall_s": round(wall, 2),
                 "err_median_m": round(float(np.median(err[nominal])), 1) if nominal.any() else None,
                 "err_p95_m": round(float(np.percentile(err[nominal], 95)), 1) if nominal.any() else None,
                 "err_max_m": round(float(err[nominal].max()), 1) if nominal.any() else None,
                 "sigma_median_m": round(float(np.median(sig)), 1),
                 "z_gt3": int(np.sum(err[nominal] / sig[nominal] > 3 * math.sqrt(2))),
                 "faulted_fixes": int((~nominal).sum()),
                 "fault_offset_m": [round(float(e), 1) for e in err[~nominal]], **extra}


def misreg_fixes(vis, m):
    a, b = m["frames"]
    u = np.array([math.sin(math.radians(m["dir_deg"])), math.cos(math.radians(m["dir_deg"]))])
    out = dict(vis)
    for k in vis:
        if a <= k < b:
            out[k] = np.asarray(vis[k]) + min(1.0, (k - a + 1) / m["ramp_frames"]) * m["offset_m"] * u
    return out


class EkfThird(rf.EkfNoImu):
    """Carries a second TRN in altpnt's (otherwise unused) 'gnss' slot, with R from that TRN's own sigma."""

    def _meas(self, src, ep):
        if src == "gnss":
            return ep["gnss"], [self.x[0], self.x[1]], v1.H_POS, ep["gnss_sigma"]
        return super()._meas(src, ep)


def run_filter(ctx, vis, trnfx, mode, monitored, third=None):
    """altpnt v2 Monitor2 over the flight with any subset of the absolute sources.
    third: optional second TRN {frame: (E, N, sigma)}, monitored as 'gnss'."""
    en, start, steps = ctx["en"], ctx["start"], ctx["steps"]
    cfg = ctx["cfg3"] if third is not None else ctx["cfg"]
    third = third or {}
    x0 = [en[start][0], en[start][1], *(en[start] - en[start - 1]) / nc.FRAME_DT, 0, 0, 0, 0]
    P0 = v2.mat.zeros(8, 8)
    for i, s in enumerate([3, 3, 1.0, 1.0, 0.05, 0.05, cfg.s_sigma, cfg.psi_sigma]):
        P0[i][i] = s * s
    ekf = (EkfThird if third else rf.EkfNoImu)(x0, P0, cfg)
    mon = v2.Monitor2(ekf, monitored if mode == "full" else (), mode != "none", cfg)
    rows = []
    for k in range(start + 1, len(en)):
        z, t, g = vis.get(k), trnfx.get(k), third.get(k)
        ep = {"t": float(k), "imu": rf.IMU_ZERO, "vio": (tuple(steps[k - 1] / nc.FRAME_DT), cfg.vio_r),
              "gnss": None if g is None else g[:2], "gnss_sigma": None if g is None else g[2],
              "gnss_state": "denied", "vgeo": None if z is None else tuple(z),
              "magnav": None if t is None else t[:2], "trn_spread": None if t is None else t[2] * math.sqrt(2)}
        hpl, events = mon.step(ep)
        x = mon.main.x
        hpe = math.hypot(x[0] - en[k][0], x[1] - en[k][1])
        rows.append({"k": k, "t": float(k), "est": (x[0], x[1]), "hpe": hpe, "hpl": hpl, "alert": mon.ambiguous,
                     "excluded": "+".join(sorted(mon.excluded)), "events": events,
                     "vis_in": z is not None, "trn_in": t is not None})
    return rows


def score(rows, al):
    rs = v2.relimit([dict(r, region=None, available=None) for r in rows], al)
    tally = stanford.tally(rs)
    return {"avail_pct": round(100 * sum(r["available"] for r in rs) / len(rs), 1), "HMI": tally["HMI"],
            "MI": tally["MI"], "unavail_MI": tally["unavail_MI"]}


def summary(rows):
    hpe = np.array([r["hpe"] for r in rows])
    ev = [(r["k"], e) for r in rows for e in r["events"]]
    return {"hpe_rms_m": round(float(np.sqrt(np.mean(hpe ** 2))), 1), "hpe_max_m": round(float(hpe.max()), 1),
            "hpe_final_m": round(float(hpe[-1]), 1), "hpl_median_m": round(float(np.median([r["hpl"] for r in rows])), 1),
            "per_al": {f"{al:g}": score(rows, al) for al in ALS},
            "detections": [(k, e) for k, e in ev if e.startswith(("alert:", "exclude:"))],
            "attributions": [(k, e) for k, e in ev if e.startswith(("blame:", "readmit:"))],
            "gate_rejects": {s: sum(e == f"gate:{s}" for _, e in ev) for s in SOURCES}}


def configs(vis, trnfx):
    return {"vo_only": ({}, {}, "none", ()), "visual_only": (vis, {}, "full", ("vgeo",)),
            "trn_only": ({}, trnfx, "full", ("magnav",)), "both": (vis, trnfx, "full", ("vgeo", "magnav")),
            "both_gate_only": (vis, trnfx, "gate", ())}


def aggregate(runs):
    """Pool epochs over seeds: availability and HMI/MI summed, HPE RMS pooled, PL median of medians."""
    out = {"seeds": len(runs), "hpe_rms_m": round(float(np.sqrt(np.mean([r["hpe_rms_m"] ** 2 for r in runs]))), 1),
           "hpe_max_m": max(r["hpe_max_m"] for r in runs),
           "hpl_median_m": round(float(np.median([r["hpl_median_m"] for r in runs])), 1),
           "detections_total": sum(len(r["detections"]) for r in runs),
           "gate_rejects_total": {s: sum(r["gate_rejects"][s] for r in runs) for s in SOURCES}, "per_al": {}}
    for al in runs[0]["per_al"]:
        p = [r["per_al"][al] for r in runs]
        out["per_al"][al] = {"avail_pct": round(float(np.mean([x["avail_pct"] for x in p])), 1),
                             **{k: sum(x[k] for x in p) for k in ("HMI", "MI", "unavail_MI")}}
    return out


def fault_report(rows, src, onset):
    det = [(k, e) for r in rows for k, e in [(r["k"], x) for x in r["events"]] if e.startswith(("alert:", "exclude:"))]
    att = [(r["k"], x) for r in rows for x in r["events"] if x.startswith(("blame:", "readmit:", "exclude:"))]
    first = next(((k, e) for k, e in det if k >= onset), None)
    blamed = [(k, e.split(":", 1)[1]) for k, e in att if e.startswith(("blame:", "exclude:")) and k >= onset]
    readm = [(k, e.split(":", 1)[1]) for k, e in att if e.startswith("readmit:")]
    return {"injected": None, "detected_at": first[0] if first else None, "detection": first[1] if first else None,
            "latency_frames": (first[0] - onset) if first else None, "blamed_or_excluded": blamed,
            "readmitted": readm, "first_attribution": blamed[0] if blamed else None,
            "correct_blame": bool(blamed) and blamed[0][1] == src,
            **summary(rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="directory containing vpair_sample/")
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    wall0 = time.perf_counter()
    ctx = load(a.data)
    en, start = ctx["en"], ctx["start"]
    dist = nc.distance_along(en)
    res = {"dataset": "VPAIR sample (Zenodo 6473989), 199 nadir frames", "yaw_bias_deg": YAW_BIAS_DEG,
           "path_after_gnss_loss_m": round(float(dist[-1] - dist[start]), 1), "frames_scored": len(en) - start - 1,
           "terrain": ctx["info"], "als_m": ALS, "seeds": a.seeds, "misreg_fault": MISREG,
           "ambiguity_fault_frames": AMBIG_FRAMES, "filter": {k: (round(v, 5) if isinstance(v, float) else v)
                                                                for k, v in vars(ctx["cfg"]).items()},
           "visual_fixes": {}, "trn_fixes": {}, "nominal": {}, "faults": {}}
    for s, vis in ctx["vis"].items():
        errs = [float(np.linalg.norm(np.asarray(p) - en[k])) for k, p in vis.items()]
        res["visual_fixes"][f"stride{s}"] = {"fixes": len(vis), "of_frames": len(en) - start - 1,
                                              "err_median_m": round(float(np.median(errs)), 1),
                                              "err_max_m": round(float(max(errs)), 1)}
    trn_cache = {}
    for var in TRN_VARIANTS:
        res["trn_fixes"][var] = []
        for seed in range(a.seeds):
            fx, d = trn_fixes(ctx, var, seed)
            trn_cache[(var, seed)] = fx
            res["trn_fixes"][var].append(d)
        print(f"TRN {var}: " + ", ".join(f"{d['fixes']}/{d['attempts']} fixes med {d.get('err_median_m')} m" for d in res["trn_fixes"][var][:3]), flush=True)
    primary_rows = None
    for s, vis in ctx["vis"].items():
        for var in TRN_VARIANTS:
            per = {}
            for seed in range(a.seeds):
                for name, (vf, tf, mode, mon) in configs(vis, trn_cache[(var, seed)]).items():
                    if name in ("vo_only", "visual_only") and seed > 0:
                        continue
                    rows = run_filter(ctx, vf, tf, mode, mon)
                    per.setdefault(name, []).append(summary(rows))
                    if (var, s) == PRIMARY and seed == 0 and name in ("both", "visual_only"):
                        primary_rows = primary_rows or {}
                        primary_rows[name] = rows
            res["nominal"][f"stride{s}_{var}"] = {name: aggregate(v) for name, v in per.items()}
            print(f"stride {s} {var}: " + "; ".join(f"{n} avail50 {x['per_al']['50']['avail_pct']}% HMI {x['per_al']['50']['HMI']}"
                                                   for n, x in res["nominal"][f"stride{s}_{var}"].items()), flush=True)
    # three sources (visual + LiDAR TRN + GLO-30 TRN), nominal, headline visual config
    s = PRIMARY[1]
    per = [summary(run_filter(ctx, ctx["vis"][s], trn_cache[(PRIMARY[0], seed)], "full", ("vgeo", "magnav", "gnss"),
                              third=trn_cache[(THIRD, seed)])) for seed in range(a.seeds)]
    res["nominal"][f"stride{s}_three_source"] = {"three": aggregate(per)}
    # fault injection, headline visual config; monitored order swapped as a control on attribution
    vis_bad = {name: misreg_fixes(ctx["vis"][s], m) for name, m in MISREG.items()}
    amb = set(range(*AMBIG_FRAMES))
    for var in TRN_VARIANTS:
        out_v = {}
        for seed in range(a.seeds):
            tf = trn_cache[(var, seed)]
            tfb, d = trn_fixes(ctx, var, seed, amb)
            for oname, order in ORDERS.items():
                for name, m in MISREG.items():
                    r = run_filter(ctx, vis_bad[name], tf, "full", order)
                    out_v.setdefault(f"misreg_{name}_{oname}", []).append(fault_report(r, "vgeo", m["frames"][0]))
                r = run_filter(ctx, ctx["vis"][s], tfb, "full", order)
                out_v.setdefault(f"trn_ambiguity_{oname}", []).append(
                    fault_report(r, "magnav", AMBIG_FRAMES[0]) | {"trn_fault_offsets_m": d.get("fault_offset_m", []),
                                                               "injected": len(d.get("fault_offset_m", []))})
            if var == PRIMARY[0]:
                third = trn_cache[(THIRD, seed)]
                r = run_filter(ctx, vis_bad["persistent"], tf, "full", ("vgeo", "magnav", "gnss"), third=third)
                out_v.setdefault("misreg_persistent_three", []).append(fault_report(r, "vgeo", MISREG["persistent"]["frames"][0]))
                r3 = run_filter(ctx, ctx["vis"][s], tfb, "full", ("vgeo", "magnav", "gnss"), third=third)
                out_v.setdefault("trn_ambiguity_three", []).append(
                    fault_report(r3, "magnav", AMBIG_FRAMES[0]) | {"trn_fault_offsets_m": d.get("fault_offset_m", []),
                                                                   "injected": len(d.get("fault_offset_m", []))})
                if seed == 0:
                    primary_rows["misreg"] = run_filter(ctx, vis_bad["persistent"], tf, "full", ORDERS["vis_first"])
                    primary_rows["misreg_three"] = r
                    primary_rows["misreg_visual_only"] = run_filter(ctx, vis_bad["persistent"], {}, "full", ("vgeo",))
                    primary_rows["misreg_gate_only"] = run_filter(ctx, vis_bad["persistent"], tf, "gate", ())
                    primary_rows["ambig"] = run_filter(ctx, ctx["vis"][s], tfb, "full", ORDERS["vis_first"])
                    primary_rows["ambig_three"] = r3
                    primary_rows["ambig_trn_only"] = run_filter(ctx, {}, tfb, "full", ("magnav",))
        res["faults"][var] = out_v
        for n, v in out_v.items():
            print(f"faults {var} {n}: detected {sum(f['detected_at'] is not None for f in v)}/{len(v)}, "
                  f"first attribution correct {sum(f['correct_blame'] for f in v)}, "
                  f"HMI@50 {sum(f['per_al']['50']['HMI'] for f in v)}", flush=True)
    res["single_fault_runs"] = {k: summary(v) for k, v in primary_rows.items()}
    res["wall_s"] = round(time.perf_counter() - wall0, 1)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "two_source_result.json").write_text(json.dumps(res, indent=1, default=float))
    import report
    report.write_svg(out / "pl_vs_frame.svg", primary_rows, ctx)
    report.export_navdash(out / "navdash", ctx, primary_rows, trn_cache[(PRIMARY[0], 0)])
    print(f"wrote {out}, {res['wall_s']} s")


if __name__ == "__main__":
    main()
