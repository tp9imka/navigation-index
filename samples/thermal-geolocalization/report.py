"""Tables from out/<tag>.jsonl: per config x condition, plus an inlier-threshold sweep.

Frames whose GT position lies outside the reference map (Thermal-UAV has a few) are listed
separately: the right answer there is no fix, so they count only toward false fixes.

Usage: python report.py results_mps [results_cpu ...]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from geom import summarize

HERE = Path(__file__).resolve().parent
FALSE_FIX_M = 20.0
SWEEP = (8, 12, 16, 20, 25, 30)
SGM_MARGINS = (1.0, 1.1, 1.2, 1.3)


def covered(rows):
    """Frame names whose GT centre falls on non-empty map pixels."""
    import rasterio
    from rasterio.warp import transform
    man = json.loads((HERE / "data" / "manifest.json").read_text())
    out = set()
    for fl in {f["flight"] for f in man["frames"]}:
        with rasterio.open(HERE / "data" / "maps" / f"{fl}.tif") as src:
            band = src.read(1)
            for f in (f for f in man["frames"] if f["flight"] == fl):
                xs, ys = transform("EPSG:4326", src.crs, [f["lon"]], [f["lat"]])
                r, c = src.index(xs[0], ys[0])
                if 0 <= r < band.shape[0] and 0 <= c < band.shape[1] and band[r, c] > 0:
                    out.add(Path(f["path"]).name)
    return out


def cfg_of(r):
    return f"{r['features']}/{r['preproc']}"


def table(rows, inside):
    lines = ["| Config | Condition | Frames (on map) | Accepted | Correct | False fixes | Median / p90 err (correct) "
             "| Best fit within 20 m, ungated | Median t/frame |", "|---|---|---|---|---|---|---|---|---|"]
    groups = defaultdict(list)
    for r in rows:
        groups[(cfg_of(r), r["condition"])].append(r)
        groups[(cfg_of(r), "ALL")].append(r)
    for (cfg, cond), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1] != "ALL", kv[0][1])):
        on = [r for r in rs if r["frame"] in inside]
        acc = [r for r in rs if r.get("accepted")]
        s = summarize([r["err_m"] for r in acc], len(on), FALSE_FIX_M)
        raw_ok = sum(1 for r in on if r["err_m"] is not None and r["err_m"] <= FALSE_FIX_M)
        ts = sorted(r["t_total_s"] for r in rs if r["t_total_s"] == r["t_total_s"]) or [float("nan")]
        err = "-" if s["median_err_m"] is None else f"{s['median_err_m']:.1f} / {s['p90_err_m']:.1f} m"
        bold = "**" if cond == "ALL" else ""
        lines.append(f"| {bold}{cfg}{bold} | {bold}{cond}{bold} | {len(rs)} ({len(on)}) | {s['accepted']} | "
                     f"{s['correct']} | {s['false_fixes']} | {err} | {raw_ok} | {ts[len(ts) // 2]:.2f} s |")
    return lines


def sweep(rows, inside):
    lines = ["| Config | " + " | ".join(f">= {k} inliers" for k in SWEEP) + " |",
             "|---|" + "---|" * len(SWEEP)]
    by = defaultdict(list)
    for r in rows:
        if r["features"] != "sgm":
            by[cfg_of(r)].append(r)
    for cfg, rs in sorted(by.items()):
        cells = []
        for k in SWEEP:
            # every gate check except the inlier count
            acc = [r for r in rs if r["err_m"] is not None and r.get("inliers", 0) >= k and
                   all(w.startswith("inliers") for w in r["reasons"])]
            good = sum(1 for r in acc if r["err_m"] <= FALSE_FIX_M)
            cells.append(f"{good} ok / {len(acc) - good} false")
        lines.append(f"| {cfg} | " + " | ".join(cells) + " |")
    return lines


def sgm_table(rows, inside):
    lines = ["| Config | Condition | Frames on map | Top-1 within 20 m | " +
             " | ".join(f"margin >= {m}: ok / false" for m in SGM_MARGINS) + " |",
             "|---|---|---|---|" + "---|" * len(SGM_MARGINS)]
    groups = defaultdict(list)
    for r in rows:
        if r["features"] == "sgm" and r["frame"] in inside and r["err_m"] is not None:
            groups[(cfg_of(r), r["condition"])].append(r)
            groups[(cfg_of(r), "ALL")].append(r)
    for (cfg, cond), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1] != "ALL", kv[0][1])):
        ok = sum(1 for r in rs if r["err_m"] <= FALSE_FIX_M)
        cells = []
        for m in SGM_MARGINS:
            acc = [r for r in rs if r["margin"] >= m]
            g = sum(1 for r in acc if r["err_m"] <= FALSE_FIX_M)
            cells.append(f"{g} / {len(acc) - g}")
        lines.append(f"| {cfg} | {cond} | {len(rs)} | {ok} | " + " | ".join(cells) + " |")
    return lines


def main_tags(tags):
    for tag in tags:
        rows = [json.loads(line) for line in open(HERE / "out" / f"{tag}.jsonl")]
        inside = covered(rows)
        outside = sorted({r["frame"] for r in rows} - inside)
        lm = [r for r in rows if r["features"] != "sgm"]
        sg = [r for r in rows if r["features"] == "sgm"]
        md = [f"# {tag}", "", f"False fix = accepted with error > {FALSE_FIX_M} m. Frames outside the map: "
              f"{len(outside)} ({', '.join(o[-30:] for o in outside) or 'none'})", ""]
        if lm:
            md += ["## Local features + LightGlue", ""] + table(lm, inside)
            md += ["", "## Inlier threshold sweep (all other gate checks kept, post-hoc)", ""] + sweep(lm, inside)
        if sg:
            md += ["", "## SGM retrieval (no geometric check)", ""] + table(sg, inside)
            md += ["", "### SGM distinctiveness margin (2nd-best distance outside 40 m / best)", ""]
            md += sgm_table(sg, inside)
        (HERE / "out" / f"{tag}_summary.md").write_text("\n".join(md) + "\n")
        print("\n".join(md))


if __name__ == "__main__":
    main_tags(sys.argv[1:])
