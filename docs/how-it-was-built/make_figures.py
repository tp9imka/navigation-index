#!/usr/bin/env python3
"""Derive every simulation number and figure of docs/how-it-was-built.md from committed files.

    python3 docs/how-it-was-built/make_figures.py        # from the repo root, stdlib only, ~2 s

Reads (never writes) samples/close-area-benchmark/results/matrix_0.json, the kill-test result
files in samples/close-area-safety-filter/results/, and the relocalization and Hybrid A* result
files. Writes:

    docs/how-it-was-built/figures/numbers.json         every number the page quotes
    docs/how-it-was-built/figures/benchmark_heatmap.svg
    docs/how-it-was-built/figures/kill_test_intervals.svg

and prints numbers.json to stdout. The output carries no wall-clock timestamp, so a rerun on the
same commit gives the same bytes. All simulation inputs are synthetic (2.5D point-mass arena).
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FIG = HERE / "figures"

MATRIX = ROOT / "samples/close-area-benchmark/results/matrix_0.json"
KILL = ROOT / "samples/close-area-safety-filter/results"
KILL_FILES = {  # seed 0 = part d (tuning seed), seeds 1-2 = part e (held out)
    0: KILL / "kill_d_unsensed_on_0.json",
    1: KILL / "kill_e_unsensed_on_1.json",
    2: KILL / "kill_e_unsensed_on_2.json",
}
KILL_FAMILY_FILES = {
    "u_trap": KILL / "kill_e_u_trap_unsensed_on_1.json",
    "narrow_gap": KILL / "kill_e_narrow_gap_unsensed_on_1.json",
}
KILL_TABLES_MD = KILL / "kill_e_tables.md"
RELOC_SPARSE = ROOT / "samples/close-area-relocalize/results/sparse_random_0.json"
RELOC_SUBMAP = ROOT / "samples/close-area-relocalize/results/submap_seed2.json"
RELOC_SUBMAP_X = ROOT / "samples/close-area-relocalize/results/submap_seed2_extras.json"
HYBRID = ROOT / "samples/close-area-planner-hybrid-astar/results/bench_0.json"

ARMS = ("F2", "F3", "F4@eps_m=0.2", "F5")
CASES = ("none", "jump", "bias", "dropout", "uwb_nlos", "both")
Z = 1.959964  # same constant as kill_e_tables.py


def rel(p):
    return str(Path(p).relative_to(ROOT))


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1))


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- benchmark

FAM_SHORT = {"random": "random", "u_trap": "u_trap", "narrow_gap": "narrow", "office": "office",
             "warehouse": "wareh.", "forest": "forest", "maze": "maze", "glass_office": "glass"}


def benchmark():
    d = json.loads(MATRIX.read_text())
    planners = list(d["planners"])
    fams = list(d["families"])
    presets = list(d["presets"])
    cells = {}
    for r in d["runs"]:
        c = cells.setdefault((r["preset"], r["planner"], r["family"]), [0, 0, 0])
        c[0] += 1
        c[1] += int(bool(r["reached"]))
        c[2] += int(bool(r["collision"]))
    reached = {p: {pl: {f: round(100 * cells[(p, pl, f)][1] / cells[(p, pl, f)][0], 1) for f in fams}
                   for pl in planners} for p in presets}
    # check against the summary block the bench wrote
    mism = [(p, pl, f) for p in presets for pl in planners for f in fams
            if abs(d["summary"][p][pl][f]["reached_pct"] - reached[p][pl][f]) > 0.05]
    per_cell = sorted({c[0] for c in cells.values()})
    full = {p: [pl for pl in planners if all(reached[p][pl][f] == 100.0 for f in fams)
                and all(cells[(p, pl, f)][2] == 0 for f in fams)] for p in presets}
    walls = [d["wall_s"]] + [a["wall_s"] for a in d.get("additions", [])]
    nrun_add = [a["n_runs"] for a in d.get("additions", [])]
    au = {p: {f: reached[p]["astar_unknown"][f] for f in fams} for p in presets}
    return d, planners, fams, presets, reached, {
        "source": rel(MATRIX),
        "input": d["input"],
        "planners": len(planners),
        "families": len(fams),
        "presets": presets,
        "runs": len(d["runs"]),
        "layouts_per_cell": per_cell,
        "seed": d["seed"],
        "reached_matches_summary_block": not mism,
        "planners_100_reached_0_collision_every_family": full,
        "astar_unknown_reached_pct": au,
        "wall_s_runs": walls,
        "wall_s_total": round(sum(walls), 1),
        "runs_in_additions": nrun_add,
        "reached_pct": reached,
    }


# ---------------------------------------------------------------- kill test

def load_cells(path):
    d = json.loads(Path(path).read_text())
    cells = {}
    for r in d["runs"]:
        if r["arm"] in ARMS:
            c = cells.setdefault((r["arm"], r["case"]), [0, 0, 0])
            c[0] += 1
            c[1] += int(bool(r["collision"]))
            c[2] += int(bool(r["reached"]))
    return d, cells


def add(into, cells):
    for k, v in cells.items():
        into[k] = [a + b for a, b in zip(into.get(k, [0, 0, 0]), v)]


def cell_out(c):
    n, k, rc = c
    lo, hi = wilson(k, n)
    return {"runs": n, "collisions": k, "collision_pct": round(100 * k / n, 1),
            "ci95": [lo, hi], "reached_pct": round(100 * rc / n)}


def kill_test():
    comb, held, walls, inputs = {}, {}, [], set()
    for seed, p in KILL_FILES.items():
        d, cells = load_cells(p)
        assert d["seed"] == seed and d["family"] == "random", p
        inputs.add(d["input"])
        add(comb, cells)
        if seed != 0:
            add(held, cells)
        walls.append(d["wall_s"])
    fam = {}
    for name, p in KILL_FAMILY_FILES.items():
        d, cells = load_cells(p)
        inputs.add(d["input"])
        walls.append(d["wall_s"])
        fam[name] = {f"{a}|{c}": cell_out(v) for (a, c), v in cells.items()}
    combined = {f"{a}|{c}": cell_out(v) for (a, c), v in comb.items()}
    heldout = {f"{a}|{c}": cell_out(v) for (a, c), v in held.items()}
    # cross-check: the strings kill_e_tables.py printed must contain ours
    md = KILL_TABLES_MD.read_text()
    checks = []
    for key in ("F4@eps_m=0.2|jump", "F5|jump"):
        for label, src in (("seeds 0-2", combined), ("held out 1-2", heldout)):
            c = src[key]
            s = f"{c['collisions']}/{c['runs']} = {c['collision_pct']:.1f} [{c['ci95'][0]:.1f}, {c['ci95'][1]:.1f}]"
            checks.append({"cell": f"{key} {label}", "string": s, "found_in_kill_e_tables_md": s in md})
    ratio = {}
    for a in ARMS[1:]:
        ratio[a] = {c: round(comb[(a, c)][2] / comb[("F2", c)][2], 2) for c in CASES[:4]}
    over = [k for k, v in combined.items() if k.startswith("F5|") and v["collision_pct"] > 1.0]
    return comb, {
        "source": [rel(p) for p in KILL_FILES.values()],
        "families_source": [rel(p) for p in KILL_FAMILY_FILES.values()],
        "input": sorted(inputs),
        "planner": "astar_esdf known_map=True",
        "threshold_collision_pct": 1.0,
        "random_seeds_0_2": combined,
        "random_heldout_seeds_1_2": heldout,
        "families_seed_1": fam,
        "reach_ratio_vs_F2_seeds_0_2": ratio,
        "F5_cells_over_threshold_seeds_0_2": over,
        "wall_s_runs": walls,
        "wall_s_total": round(sum(walls), 1),
        "cross_check": checks,
    }


# ---------------------------------------------------------------- relocalization, Hybrid A*

def reloc():
    d = json.loads(RELOC_SPARSE.read_text())
    sp = {}
    for pre in ("ideal", "crazyflie"):
        for f in ("dropout", "jump"):
            s = d["results"][pre][f]["spin_ig"]["summary"]
            sp[f"{pre}|{f}"] = {"reached_pct": s["reached_pct"], "collision_pct": s["collision_pct"],
                                "wrong_commits": s["wrong_commits"]}
    x = json.loads(RELOC_SUBMAP_X.read_text())
    sub = {}
    for fam in ("random", "office"):
        for f in ("dropout", "jump"):
            s = x["results"][fam]["crazyflie"][f]["submap_fwd_ig"]["summary"]
            sub[f"{fam}|{f}"] = {"reached_pct": s["reached_pct"], "ci95": s["reached_ci95"],
                                 "collision_pct": s["collision_pct"], "wrong_commits": s["wrong_commits"]}
    m = json.loads(RELOC_SUBMAP.read_text())
    mcl = {}
    for fam in ("random", "office"):
        for f in ("dropout", "jump"):
            s = m["results"][fam]["crazyflie"][f]["mcl"]["summary"]
            mcl[f"{fam}|{f}"] = {"reached_pct": s["reached_pct"], "collision_pct": s["collision_pct"],
                                 "wrong_commits": s["wrong_commits"]}
    reached = [v["reached_pct"] for v in sub.values()]
    wrong = [v["wrong_commits"] for v in sub.values()]
    return {
        "input": sorted({d["input"], x["input"], m["input"]}),
        "bar": "reached >= 90 % and 0 wrong commits (the acceptance bar set before the test)",
        "spin_ig_seed0_random_100_layouts": {"source": rel(RELOC_SPARSE), "cells": sp},
        "submap_fwd_ig_seed2_crazyflie_100_layouts": {"source": rel(RELOC_SUBMAP_X), "cells": sub,
                                                      "reached_range": [min(reached), max(reached)],
                                                      "wrong_commits_range": [min(wrong), max(wrong)]},
        "mcl_seed2_crazyflie_100_layouts": {"source": rel(RELOC_SUBMAP), "cells": mcl},
    }


def hybrid():
    d = json.loads(HYBRID.read_text())
    t = d["totals"]
    keep = {k: {"runs": v["n"], "reached_pct": v["reached_pct"], "collision_pct": v["collision_pct"]}
            for k, v in t.items() if "|ideal|" in k}
    return {"source": rel(HYBRID), "input": d["input"], "seed": d["seed"],
            "layouts_per_family": d["layouts"], "families": len(d["families"]),
            "ideal_totals": keep}


# ---------------------------------------------------------------- SVG

def svg_doc(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="11">\n<title>{escape(title)}</title>\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n' + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, size=11, anchor="start", fill="#222", weight="normal", rotate=None):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
            f'font-weight="{weight}"{tr}>{escape(str(s))}</text>')


def blue(v):
    """0 % => near white, 100 % => dark blue."""
    t = max(0.0, min(1.0, v / 100))
    lo, hi = (247, 251, 255), (8, 69, 148)
    return "#%02x%02x%02x" % tuple(round(a + (b - a) * t) for a, b in zip(lo, hi))


def heatmap_svg(planners, fams, presets, reached, meta):
    cw, ch, left, top, gap = 42, 18, 170, 78, 24
    pw = cw * len(fams)
    w = left + len(presets) * pw + (len(presets) - 1) * gap + 20
    h = top + ch * len(planners) + 48
    b = [text(10, 20, "Benchmark: reached B, % of 20 layouts per cell (seed 0, synthetic 2.5D arena)", 13, weight="bold"),
         text(10, 38, f"{meta['planners']} planners x {meta['families']} families x {len(presets)} sensor presets = "
                      f"{meta['runs']} flights. Source: samples/close-area-benchmark/results/matrix_0.json", 11, fill="#555")]
    for i, p in enumerate(presets):
        x0 = left + i * (pw + gap)
        label = {"ideal": "ideal: 72 rays, 360 deg, 6 m", "crazyflie": "crazyflie: 4 cones of 27 deg, 3 m"}.get(p, p)
        b.append(text(x0 + pw / 2, 58, label, 11, "middle", weight="bold"))
        for j, f in enumerate(fams):
            b.append(text(x0 + j * cw + cw / 2, top - 6, FAM_SHORT.get(f, f), 10, "middle", fill="#444"))
        for r, pl in enumerate(planners):
            y = top + r * ch
            for j, f in enumerate(fams):
                v = reached[p][pl][f]
                b.append(f'<rect x="{x0 + j * cw}" y="{y}" width="{cw - 1}" height="{ch - 1}" fill="{blue(v)}"/>')
                b.append(text(x0 + j * cw + cw / 2, y + 12.5, f"{v:.0f}", 10, "middle",
                              fill="#fff" if v >= 55 else "#222"))
    for r, pl in enumerate(planners):
        b.append(text(left - 6, top + r * ch + 12.5, pl, 10, "end"))
    b.append(text(10, h - 14, "Planner sees the true pose; prior-map rows read no scan, so they are an upper bound. "
                              "One run = 5 percentage points.", 10, fill="#555"))
    return svg_doc(w, h, b, "Benchmark heatmap")


def intervals_svg(comb):
    rows = [(c, a) for c in CASES for a in ARMS if (a, c) in comb]
    left, top, rh, xmax, pxp = 190, 70, 17, 18.0, 32
    plot_w = xmax * pxp
    w = int(left + plot_w + 60)
    h = top + rh * len(rows) + 60
    colors = {"F2": "#7f7f7f", "F3": "#9467bd", "F4@eps_m=0.2": "#1f77b4", "F5": "#d62728"}
    b = [text(10, 20, "Kill test: collision % with 95 % Wilson interval, random family, seeds 0-2 (300 runs per cell)", 13, weight="bold"),
         text(10, 38, "A* known map, unsensed obstacles on, synthetic. Dashed line: the 1 % bar. "
                      "F5 = ours (PL margin + hover); F4 = fixed 0.2 m bound.", 11, fill="#555")]
    X = lambda v: left + v * pxp
    for t in range(0, int(xmax) + 1, 2):
        b.append(f'<line x1="{X(t):.1f}" y1="{top - 6}" x2="{X(t):.1f}" y2="{top + rh * len(rows)}" stroke="#eee"/>')
        b.append(text(X(t), top + rh * len(rows) + 16, f"{t}", 10, "middle", fill="#444"))
    b.append(text(X(xmax / 2), top + rh * len(rows) + 34, "collision % of runs", 11, "middle"))
    b.append(f'<line x1="{X(1):.1f}" y1="{top - 10}" x2="{X(1):.1f}" y2="{top + rh * len(rows)}" '
             f'stroke="#000" stroke-dasharray="4 3"/>')
    b.append(text(X(1) + 4, top - 12, "1 % bar", 10))
    prev = None
    for i, (c, a) in enumerate(rows):
        y = top + i * rh + rh / 2
        if c != prev:
            if prev is not None:
                b.append(f'<line x1="10" y1="{top + i * rh}" x2="{w - 10}" y2="{top + i * rh}" stroke="#ccc"/>')
            b.append(text(12, y + 4, c, 11, weight="bold"))
            prev = c
        n, k, _ = comb[(a, c)]
        lo, hi = wilson(k, n)
        p = 100 * k / n
        col = colors[a]
        b.append(text(left - 8, y + 4, "F4 0.2 m" if a.startswith("F4") else a, 10, "end", fill=col))
        b.append(f'<line x1="{X(lo):.1f}" y1="{y:.1f}" x2="{X(hi):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2"/>')
        b.append(f'<circle cx="{X(p):.1f}" cy="{y:.1f}" r="3.5" fill="{col}"/>')
        b.append(text(X(hi) + 6, y + 4, f"{k}/{n} = {p:.1f} [{lo}, {hi}]", 9, fill="#444"))
    return svg_doc(w, h, b, "Kill test intervals")


# ---------------------------------------------------------------- main

def main():
    FIG.mkdir(exist_ok=True)
    _, planners, fams, presets, reached, bench = benchmark()
    comb, kill = kill_test()
    numbers = {
        "generated_by": "python3 docs/how-it-was-built/make_figures.py",
        "head": git("rev-parse", "--short", "HEAD").strip(),
        "inputs_sha256_16": {rel(p): sha256(p) for p in
                             [MATRIX, *KILL_FILES.values(), *KILL_FAMILY_FILES.values(),
                              KILL_TABLES_MD, RELOC_SPARSE, RELOC_SUBMAP, RELOC_SUBMAP_X, HYBRID]},
        "benchmark": bench,
        "kill_test": kill,
        "relocalize_4_beams": reloc(),
        "hybrid_astar": hybrid(),
        "cost": {
            "benchmark_wall_s": bench["wall_s_total"],
            "kill_test_seeds_0_2_and_families_wall_s": kill["wall_s_total"],
            "agent_jobs_tokens_or_credits": "not measured",
            "human_hours": "not measured",
        },
    }
    (FIG / "benchmark_heatmap.svg").write_text(heatmap_svg(planners, fams, presets, reached, bench))
    (FIG / "kill_test_intervals.svg").write_text(intervals_svg(comb))
    out = json.dumps(numbers, indent=1, sort_keys=False) + "\n"
    (FIG / "numbers.json").write_text(out)
    print(out, end="")


if __name__ == "__main__":
    main()
