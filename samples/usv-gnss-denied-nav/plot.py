"""Optional figure from an exported scenario (needs matplotlib):

  python3 plot.py out/spoof-coastal example_output/spoof-coastal.png
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import chart as chartmod  # noqa: E402

TRACKS = [("truth.jsonl", "truth", "k", 1.2), ("ins.jsonl", "DR only", "#9e9e9e", 1.0),
          ("fused-gnss_dr.jsonl", "GNSS + DR, no monitor", "#2e7d32", 1.0),
          ("fused-single.jsonl", "single filter, gates only", "#ef6c00", 1.0),
          ("fused-monitor.jsonl", "fused + monitor", "#0277bd", 1.6)]


def load(path):
    pos, ev = [], []
    for line in Path(path).read_text().splitlines()[1:]:
        r = json.loads(line)
        (ev if "event" in r else pos).append(r)
    return pos, ev


def main(d, out):
    d = Path(d)
    frame = chartmod.default_frame()
    data = chartmod.load_chart_data()
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 7.5), gridspec_kw={"width_ratios": [1, 1.25]})
    for line in data["coast"] + [s["line"] for s in data["structures"]]:
        xy = [frame.to_xy(lat, lon) for lon, lat in line]
        ax.plot([p[0] / 1000 for p in xy], [p[1] / 1000 for p in xy], color="#555", lw=0.5)
    truth = {r["t"]: frame.to_xy(r["lat"], r["lon"]) for r in load(d / "truth.jsonl")[0]}
    for fname, label, color, lw in TRACKS:
        pos, ev = load(d / fname)
        xy = [frame.to_xy(r["lat"], r["lon"]) for r in pos]
        ax.plot([p[0] / 1000 for p in xy], [p[1] / 1000 for p in xy], color=color, lw=lw, label=label)
        if fname != "truth.jsonl":
            err = [(r["t"], math.hypot(p[0] - truth[r["t"]][0], p[1] - truth[r["t"]][1]))
                   for r, p in zip(pos, xy) if r["t"] in truth]
            ax2.plot([e[0] for e in err], [max(e[1], 0.1) for e in err], color=color, lw=lw, label=label)
        for e in ev:
            if e["event"] in ("attack_onset", "spoof_suspected", "alarm_raised"):
                ax2.axvline(e["t"], color=color if e["event"] != "attack_onset" else "r", ls="--", lw=0.8)
    rad, _ = load(d / "radar.jsonl")
    rxy = [frame.to_xy(r["lat"], r["lon"]) for r in rad]
    ax.scatter([p[0] / 1000 for p in rxy], [p[1] / 1000 for p in rxy], s=2, color="#8e24aa", label="radar-chart fixes")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-11, 10)
    ax.set_aspect("equal")
    ax.set_xlabel("east of 55.62N 12.70E, km")
    ax.set_ylabel("north, km")
    ax.legend(fontsize=7, loc="lower left")
    ax2.set_yscale("log")
    ax2.set_xlabel("time, s (dashed red: attack onset, dashed blue: monitor alarm)")
    ax2.set_ylabel("horizontal error, m")
    ax2.grid(True, which="both", lw=0.3)
    ax2.legend(fontsize=7)
    fig.suptitle(json.loads((d / "manifest.json").read_text())["title"])
    fig.tight_layout()
    fig.savefig(out, dpi=90)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
