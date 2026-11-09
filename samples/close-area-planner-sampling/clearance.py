"""Read results/sweep_0.json and count planned paths whose exact clearance (world.sdf along the
path) is below the 0.15 m vehicle radius, split by inflation level. Writes results/sweep_0_clearance.md.

python clearance.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RADIUS = 0.15


def main() -> int:
    d = json.load(open(os.path.join(HERE, "results", "sweep_0.json")))
    lines = ["`python clearance.py` over results/sweep_0.json (synthetic, planning only). "
             "Level 0.25 = planned at ESDF > 0.25 m; level 0.15 = the RADIUS-only fallback.\n",
             "| planner | budget | inflation level m | ok plans | exact clearance < 0.15 m | % | min exact clearance m |",
             "|---|---|---|---|---|---|---|"]
    keys = sorted({(r["planner"], r["budget"] or 0) for r in d["rows"]})
    for name, b in keys:
        for fb, lvl in ((0, 0.25), (1, 0.15)):
            sel = [r for r in d["rows"] if r["ok"] and r["planner"] == name and (r["budget"] or 0) == b
                   and r["fallback"] == fb]
            if not sel:
                continue
            low = sum(r["truth_clear_m"] < RADIUS for r in sel)
            lines.append(f"| {name} | {b or '-'} | {lvl} | {len(sel)} | {low} | {100.0 * low / len(sel):.1f} | "
                         f"{min(r['truth_clear_m'] for r in sel):.3f} |")
    out = os.path.join(HERE, "results", "sweep_0_clearance.md")
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
