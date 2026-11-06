#!/usr/bin/env python3
"""Small PNGs for the README from data/ (needs matplotlib).

    python spoof_plot.py      # data/timeline_*.json + data/sweep_summary.json => plots/*.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "plots"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#e87ba4"]
DPI = 110


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def timeline_panel(ax, tl, title):
    style(ax)
    flags = tl["flag_t"]
    for t in flags:
        ax.axvspan(t - 0.1, t + 0.1, color="#eda100", alpha=0.18, linewidth=0)
    ax.plot(tl["t"], tl["spoof_m"], color=MUTED, linewidth=1.5, linestyle="--", label="spoof offset (GNSS - truth)")
    ax.plot(tl["t"], tl["ekf_err_east_m"], color=SERIES[0], linewidth=2, label="EKF - truth, east")
    ax.set_xlim(-5, max(tl["t"]))
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.set_ylabel("m", fontsize=8, color=MUTED)


def timelines():
    files = {"px4": DATA / "timeline_px4-default-position-3.json",
             "ardupilot": DATA / "timeline_ardupilot-default-position-3.json"}
    if not all(p.exists() for p in files.values()):
        return
    fig, axes = plt.subplots(2, 1, figsize=(7, 4.6), sharex=True, facecolor=SURFACE)
    timeline_panel(axes[0], json.loads(files["px4"].read_text()), "PX4 v1.17 EKF2, defaults: position-only drag 3 m/s")
    timeline_panel(axes[1], json.loads(files["ardupilot"].read_text()), "ArduCopter 4.6.3 EKF3, defaults: same drag")
    axes[1].set_xlabel("s after spoof onset (shaded: autopilot GNSS glitch flag set)", fontsize=8, color=MUTED)
    axes[0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "reset_sawtooth.png", dpi=DPI, facecolor=SURFACE)


def sweep():
    p = DATA / "sweep_summary.json"
    if not p.exists():
        return
    rows = [r for r in json.loads(p.read_text()) if r["spoof"] == "coherent"]
    fig, ax = plt.subplots(figsize=(7, 3.6), facecolor=SURFACE)
    style(ax)
    keys = sorted({(r["autopilot"], r["config"]) for r in rows})
    for i, k in enumerate(keys):
        pts = sorted((r["rate_mps"], r["capture_ratio_end"], r["outcome"] != "mission_complete")
                     for r in rows if (r["autopilot"], r["config"]) == k)
        c = SERIES[i % len(SERIES)]
        x = [p[0] * (1 + 0.04 * (i - 2)) for p in pts]          # small dodge so markers do not overlap
        ax.plot(x, [p[1] for p in pts], color=c, linewidth=1.2, alpha=0.6)
        ax.scatter(x, [p[1] for p in pts], s=36, color=[SURFACE if p[2] else c for p in pts], edgecolors=c,
                   linewidths=1.6, zorder=3, label=f"{'PX4' if k[0] == 'px4' else 'ArduPilot'} {k[1]}")
    ax.set_xscale("log")
    ax.set_xticks([0.1, 0.5, 1, 2, 3, 5])
    ax.set_xticklabels(["0.1", "0.5", "1", "2", "3", "5"])
    ax.set_ylim(0, 1.3)
    ax.set_xlabel("coherent drag rate, m/s (log)", fontsize=8, color=MUTED)
    ax.set_ylabel("EKF east error / spoof offset", fontsize=8, color=MUTED)
    ax.set_title("Share of a coherent spoof each EKF believed at the end (hollow = flight ended in a LAND failsafe)",
                 fontsize=8.5, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="lower left", ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "sweep_coherent.png", dpi=DPI, facecolor=SURFACE)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    timelines()
    sweep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
