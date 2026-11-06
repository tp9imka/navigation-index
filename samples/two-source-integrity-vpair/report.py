"""SVG of protection level vs error per frame, and navdash/1 export for templates/demo-dashboard."""
import math
from pathlib import Path

import numpy as np

import nav_core as nc

SERIES = [("visual_only", "#ef6c00", "VO + visual fixes"), ("both", "#1e88e5", "VO + visual fixes + TRN (LiDAR heightmap)"),
          ("misreg", "#8e24aa", "both, visual map misregistration from frame 100 (0 => 40 m ramp, held)")]
AL_LINES = (25, 50, 100)
YMAX_M = 3000.0


def write_svg(path, rows_by, ctx, w=780, h=400, pad=56):
    k0, k1 = ctx["start"] + 1, len(ctx["en"]) - 1
    yl = lambda v: h - pad - math.log10(min(max(v, 1.0), YMAX_M)) / math.log10(YMAX_M) * (h - 2 * pad)
    xl = lambda k: pad + (k - k0) / (k1 - k0) * (w - 2 * pad)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 24 * len(SERIES) + 24}" font-family="sans-serif" font-size="11">',
         '<rect width="100%" height="100%" fill="white"/>']
    for v in (1, 10, 100, 1000):
        p.append(f'<line x1="{pad}" x2="{w - pad}" y1="{yl(v):.1f}" y2="{yl(v):.1f}" stroke="#eee"/>'
                 f'<text x="{pad - 6}" y="{yl(v) + 4:.1f}" text-anchor="end">{v} m</text>')
    for al in AL_LINES:
        p.append(f'<line x1="{pad}" x2="{w - pad}" y1="{yl(al):.1f}" y2="{yl(al):.1f}" stroke="#c62828" stroke-dasharray="4 3"/>'
                 f'<text x="{w - pad + 4}" y="{yl(al) + 4:.1f}" fill="#c62828">AL {al}</text>')
    for k in range(20, k1 + 1, 20):
        p.append(f'<text x="{xl(k):.1f}" y="{h - pad + 16}" text-anchor="middle">{k}</text>')
    p.append(f'<text x="{w / 2}" y="{h - 14}" text-anchor="middle">frame (about 45 m each; GNSS lost at frame {ctx["start"]})</text>')
    p.append(f'<text x="{pad}" y="{pad - 16}">solid: protection level (solution separation), dotted: true horizontal error; log scale</text>')
    for i, (key, col, lab) in enumerate(SERIES):
        rows = rows_by.get(key)
        if not rows:
            continue
        pl = " ".join(f"{xl(r['k']):.1f},{yl(r['hpl']):.1f}" for r in rows)
        pe = " ".join(f"{xl(r['k']):.1f},{yl(r['hpe']):.1f}" for r in rows)
        p.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.8" points="{pl}"/>')
        p.append(f'<polyline fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="2 2" points="{pe}"/>')
        y = h + 8 + 24 * i
        p.append(f'<rect x="{pad}" y="{y}" width="16" height="4" fill="{col}"/><text x="{pad + 22}" y="{y + 6}">{lab}</text>')
    p.append("</svg>")
    Path(path).write_text("\n".join(p))


def export_navdash(nd, ctx, rows_by, trnfx):
    nd = Path(nd)
    nd.mkdir(parents=True, exist_ok=True)
    poses, en, start = ctx["poses"], ctx["en"], ctx["start"]
    lat0, lon0 = poses["lat0"], poses["lon0"]
    ll = lambda q: nc.common.enu_to_ll(lat0, lon0, float(q[0]), float(q[1]))
    wn = nc.common.write_navdash
    wn(str(nd / "truth.jsonl"), "truth", "truth", "VPAIR query poses (GNSS/INS)",
       [{"t": float(k), "lat": ll(q)[0], "lon": ll(q)[1]} for k, q in enumerate(en)])
    wn(str(nd / "vo_only.jsonl"), "vo-only", "ins", "Nadir VO only, yaw +2 deg",
       [{"t": float(k), "lat": ll(q)[0], "lon": ll(q)[1], "sources": ["nadir-vo"]} for k, q in enumerate(ctx["vo_pos"])],
       color="#ffb74d")
    vis = ctx["vis"][8]
    wn(str(nd / "fixes_visual.jsonl"), "fixes-visual", "altpnt", "Visual fixes (real imagery, map stride 8)",
       [{"t": float(k), "lat": ll(q)[0], "lon": ll(q)[1], "sources": ["dinov2+lightglue"]} for k, q in sorted(vis.items())],
       color="#69f0ae")
    wn(str(nd / "fixes_trn.jsonl"), "fixes-trn", "altpnt", "TRN fixes (simulated LiDAR heightmap over the real NRW DSM)",
       [{"t": float(k), "lat": ll(q)[0], "lon": ll(q)[1], "r95_m": round(2.45 * q[2], 1), "sources": ["trn-heightmap"]}
        for k, q in sorted(trnfx.items())], color="#ce93d8")

    def fused(name, key, label, color, primary=False):
        rows = rows_by[key]
        ev = [{"t": float(start), "event": "gnss_lost", "text": "end of GNSS window"}]
        for r in rows:
            for e in r["events"]:
                if e.startswith(("alert:", "exclude:", "blame:", "readmit:")):
                    ev.append({"t": float(r["k"]), "event": "fix_excluded" if not e.startswith("readmit") else "fix_readmitted",
                               "text": e.replace("magnav", "trn").replace("vgeo", "visual")})
        out = [{"t": float(k), "lat": ll(en[k])[0], "lon": ll(en[k])[1], "health": "trusted", "sources": ["gnss"]}
               for k in range(start + 1)]
        for r in rows:
            la, lo = ll(r["est"])
            avail = r["hpl"] < 50.0 and not r["alert"]
            src = ["nadir-vo"] + (["visual-fix"] if r["vis_in"] else []) + (["trn"] if r["trn_in"] else [])
            out.append({"t": float(r["k"]), "lat": la, "lon": lo, "pl_m": round(r["hpl"], 2),
                        "health": "excluded" if r["excluded"] else ("trusted" if avail else "unavailable"),
                        "alarm": not avail, "sources": src})
        wn(str(nd / f"{name}.jsonl"), name, "fused", label, out, color=color, primary=primary,
           extra={"alert_limit_m": 50.0, "pl_method": "altpnt-integrity v2 Monitor2: solution separation over "
                  "visual fixes and TRN, k_md from per-source fault priors, not certified",
                  "run_meta": {"time": "frame index, 1 s per frame (VPAIR has no timestamps)"}}, events=ev)

    fused("fused_two_source", "both", "VO + visual fixes + TRN, solution separation", "#4fc3f7", primary=True)
    fused("fused_visual_only", "visual_only", "VO + visual fixes only, solution separation", "#ff8a65")
    fused("fused_misreg_fault", "misreg", "two-source, visual map misregistration from frame 100 (ramp to 40 m, then held)", "#ba68c8")
    nc.common.write_manifest(str(nd / "manifest.json"), "VPAIR: visual fixes + TRN, two-source integrity",
                             ["truth.jsonl", "vo_only.jsonl", "fixes_visual.jsonl", "fixes_trn.jsonl",
                              "fused_two_source.jsonl", "fused_visual_only.jsonl", "fused_misreg_fault.jsonl"])
