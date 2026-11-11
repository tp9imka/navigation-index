"""depth_cam_87 rows (matrix_depth_0.json) next to the ideal and crazyflie rows of
matrix_0.json on the same layouts (indices 0-5, seed 0). Writes matrix_depth_0.compare.md.
Reads JSON only, flies nothing. Run from samples/close-area-benchmark:
  python3 results/matrix_depth_0.compare.py
Input: synthetic (both files are simulated arena runs)."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "matrix_depth_0.json")))
M = json.load(open(os.path.join(HERE, "matrix_0.json")))
PL, FAM, NL = list(D["planners"]), D["families"], D["layouts"]
Z = 1.959964


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return (max(0.0, c - h) * 100, min(1.0, c + h) * 100)


def rows(src, preset):
    return [r for r in src["runs"] if r["preset"] == preset and r["index"] < NL and r["planner"] in PL]


SETS = {"depth_cam_87": rows(D, "depth_cam_87"), "ideal": rows(M, "ideal"), "crazyflie": rows(M, "crazyflie")}


def cell(rs, p, f):
    s = [r for r in rs if r["planner"] == p and (f is None or r["family"] == f)]
    return len(s), sum(r["outcome"] == "reached" for r in s), sum(bool(r["collision"]) for r in s)


def pct(k, n):
    return f"{100 * k / n:.0f}"


out = [f"`python3 results/matrix_depth_0.compare.py`. Input: synthetic. depth_cam_87 rows from "
       f"matrix_depth_0.json; ideal and crazyflie rows from matrix_0.json restricted to the same layouts "
       f"(index 0-{NL - 1}, seed {D['seed']}), so every cell is paired on identical worlds. "
       f"n = {NL} per cell, {NL * len(FAM)} per pooled row. Intervals: 95 % Wilson.", ""]
for name, rs in SETS.items():
    out += [f"## Preset `{name}` (layouts 0-{NL - 1})", "", f"Cell = reached % / collision %, n = {NL}.", "",
            "| planner | " + " | ".join(FAM) + " | pooled reached % [95 % CI] | pooled collision % [95 % CI] |",
            "|---" * (len(FAM) + 3) + "|"]
    for p in PL:
        cells = []
        for f in FAM:
            n, k, c = cell(rs, p, f)
            cells.append(f"{pct(k, n)} / {pct(c, n)}" if n else "-")
        n, k, c = cell(rs, p, None)
        lo, hi = wilson(k, n)
        clo, chi = wilson(c, n)
        out.append(f"| {p} | " + " | ".join(cells)
                   + f" | {pct(k, n)} [{lo:.0f}, {hi:.0f}] ({k}/{n}) | {pct(c, n)} [{clo:.0f}, {chi:.0f}] ({c}/{n}) |")
    out.append("")
    best = []
    for f in FAM:
        sc = {p: cell(rs, p, f) for p in PL}
        key = {p: (-v[1], v[2]) for p, v in sc.items()}
        top = min(key.values())
        ties = [p for p in PL if key[p] == top]
        n, k, c = sc[ties[0]]
        best.append(f"{f} => {'/'.join(ties)} ({pct(k, n)} / {pct(c, n)})")
    out += ["Best per family (highest reached, then lowest collision; ties listed): " + "; ".join(best) + ".", ""]

# outcome mix and glass hits on depth
dr = SETS["depth_cam_87"]
out += ["## depth_cam_87 outcome mix and collision material", "",
        "| planner | reached | collision | stuck | timeout | hits on glass | hits on other |", "|---|---|---|---|---|---|---|"]
for p in PL:
    s = [r for r in dr if r["planner"] == p]
    oc = {o: sum(r["outcome"] == o for r in s) for o in ("reached", "collision", "stuck", "timeout")}
    g = sum(r.get("hit_material") == "glass" for r in s)
    o = sum(bool(r["collision"]) and r.get("hit_material") != "glass" for r in s)
    out.append(f"| {p} | {oc['reached']} | {oc['collision']} | {oc['stuck']} | {oc['timeout']} | {g} | {o} |")
out.append("")

# paired outcome agreement depth vs others
out += ["## Same outcome as depth_cam_87, run by run (layouts 0-%d)" % (NL - 1), "",
        "| planner | vs ideal | vs crazyflie |", "|---|---|---|"]
for p in PL:
    dk = {(r["family"], r["index"]): r["outcome"] for r in dr if r["planner"] == p}
    res = []
    for other in ("ideal", "crazyflie"):
        ok = {(r["family"], r["index"]): r["outcome"] for r in SETS[other] if r["planner"] == p}
        res.append(f"{sum(dk[x] == ok.get(x) for x in dk)}/{len(dk)}")
    out.append(f"| {p} | {res[0]} | {res[1]} |")
out.append("")

# prior-map planners: ideal vs crazyflie in matrix_0 (all 20 layouts), the reason they were not re-run
PRIOR = ("astar_known", "informed_rrt_star", "astar_mpc", "thetastar_known", "lazy_thetastar_known")
out += ["## Prior-map rows of matrix_0.json: ideal vs crazyflie, run by run (all layouts)", "",
        "Same outcome and same min clearance on both presets. These planners never read the scan, so they "
        "were not re-run on depth_cam_87; their depth column equals ideal.", "",
        "| planner | identical runs |", "|---|---|"]
for p in PRIOR:
    key = lambda r: (r["family"], r["index"])          # noqa: E731
    a = {key(r): (r["outcome"], r["min_clearance_m"]) for r in M["runs"] if r["planner"] == p and r["preset"] == "ideal"}
    b = {key(r): (r["outcome"], r["min_clearance_m"]) for r in M["runs"] if r["planner"] == p and r["preset"] == "crazyflie"}
    out.append(f"| {p} | {sum(a[x] == b.get(x) for x in a)}/{len(a)} |")
out.append("")

with open(os.path.join(HERE, "matrix_depth_0.compare.md"), "w") as fh:
    fh.write("\n".join(out))
print("\n".join(out))
