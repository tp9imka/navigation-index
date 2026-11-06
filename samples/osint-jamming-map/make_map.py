"""Merge both methods into one dashboard zones file + manifest, and draw a PNG map.

Usage: python make_map.py   (after s1_rfi.py and adsb_hexmap.py)
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Polygon  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "out"
LAND_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
ADSB_COLORS = {"red": "#d32f2f", "yellow": "#fbc02d", "green": "#43a047", "no-data": "#9e9e9e"}
S1_CAND = "#8e24aa"
ESA_COLOR = "#00acc1"
RECUR_COLOR = "#e65100"
LABELS = {"Kaliningrad": (20.51, 54.71), "Klaipeda": (21.14, 55.70), "Gdansk": (18.65, 54.35),
          "Vilnius": (25.28, 54.69), "Riga": (24.11, 56.95)}


def land(cache: Path):
    f = cache / "ne_50m_admin_0_countries.geojson"
    if not f.exists():
        cache.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(LAND_URL, timeout=120) as r:
            f.write_bytes(r.read())
    return json.loads(f.read_text())


def rings(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


def merge_zones(adsb, s1, adsb_sum, s1_sum):
    """Dashboard zones: t is seconds since the ADS-B window start; the S1 cells are active at the overpass."""
    t0 = adsb_sum["t0_unix"]
    t_pass = dt.datetime.fromisoformat(s1_sum["overpass_utc"].replace("Z", "+00:00")).timestamp() - t0
    feats = [f for f in adsb["features"] if f["properties"]["level"] in ("red", "yellow")]
    for f in s1["features"]:
        if f["properties"]["kind"] == "c-band-rfi":
            p = dict(f["properties"], t_start=round(t_pass - 30, 1), t_end=round(t_pass + 30, 1))
            feats.append({**f, "properties": p})
    return {"type": "FeatureCollection", "features": feats}, t_pass


def draw(adsb, s1, adsb_sum, s1_sum, png: Path):
    countries = land(HERE / "cache" / "ne")
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.2), sharey=True)
    W, S, E, N = adsb_sum["bbox"]
    for ax in axes:
        ax.set_facecolor("#dfe9f2")
        for c in countries["features"]:
            for r in rings(c["geometry"]):
                ax.add_patch(Polygon(r, closed=True, fc="#f4f1ea", ec="#8d8d8d", lw=0.5, zorder=1))
        for name, (x, y) in LABELS.items():
            if W <= x <= E and S <= y <= N:
                ax.plot(x, y, "k.", ms=4, zorder=6)
                ax.annotate(name, (x, y), xytext=(3, 3), textcoords="offset points", fontsize=8, zorder=6)
        ax.set_xlim(W, E)
        ax.set_ylim(S, N)
        ax.set_aspect(1 / 0.58)  # ~cos(55 deg)
        ax.set_xlabel("lon")
    axes[0].set_ylabel("lat")

    ax = axes[0]
    for f in adsb["features"]:
        p = f["properties"]
        ax.add_patch(Polygon(f["geometry"]["coordinates"][0], closed=True, fc=ADSB_COLORS[p["level"]],
                             alpha=0.55, ec="white", lw=0.4, zorder=3))
    ax.set_title(f"ADS-B NACp degradation, H3 res {adsb_sum['hex_res']}\n"
                 f"{adsb_sum['date']} {adsb_sum['window_utc'][0]}-{adsb_sum['window_utc'][1]} UTC, "
                 f"{adsb_sum['n_aircraft_bad']}/{adsb_sum['n_aircraft_classified']} aircraft NACp<8", fontsize=10)
    ax.legend(handles=[Patch(fc=c, alpha=0.55, label=k) for k, c in ADSB_COLORS.items()],
              loc="lower right", fontsize=8, title="GPSJam level", title_fontsize=8)

    ax = axes[1]
    n_esa = 0
    for f in s1["features"]:
        p = f["properties"]
        xy = f["geometry"]["coordinates"][0]
        if p["kind"] == "s1-footprint":
            ax.add_patch(Polygon(xy, closed=True, fill=False, ec="k", ls="--", lw=1, zorder=4))
        elif p["method"] == "esa-rfi-annotation":
            n_esa += 1
            ax.add_patch(Polygon(xy, closed=True, fc=ESA_COLOR, alpha=0.35, ec=ESA_COLOR, lw=1, zorder=4))
        elif p["method"] == "esa-rfi-recurrence":
            recurrent = p["kind"] == "c-band-rfi"
            ax.add_patch(Polygon(xy, closed=True, fill=False, ec=RECUR_COLOR, lw=2.2 if recurrent else 0.8,
                                 ls="-" if recurrent else ":", zorder=5))
            if recurrent:
                cx = sum(c[0] for c in xy[:4]) / 4
                cy = sum(c[1] for c in xy[:4]) / 4
                ax.annotate(f"{p['n_dates']}/{p['n_stack']} dates", (cx, cy), fontsize=8, color=RECUR_COLOR,
                            ha="center", va="center", zorder=6, weight="bold")
        else:
            cand = p["kind"] == "c-band-rfi"
            ax.add_patch(Polygon(xy, closed=True, fc=S1_CAND if cand else "#b0bec5",
                                 alpha=0.75 if cand else 0.25, ec="white", lw=0.3, zorder=3))
    ax.set_title(f"Sentinel-1 C-band RFI, {s1_sum['target'][:3]} {s1_sum['overpass_utc'][:16]} UTC, "
                 f"orbit {s1_sum['relative_orbit']} {s1_sum['orbit_state']}\n"
                 f"{s1_sum['n_hex_candidates']}/{s1_sum['n_hex_scored']} hexes: VH z>3 share highest of "
                 f"{s1_sum['n_scenes']}-scene stack; {n_esa} ESA rfiDetected strips", fontsize=10)
    ax.legend(handles=[Patch(fc=S1_CAND, alpha=0.75, label="temporal-z candidate hex"),
                       Patch(fc="#b0bec5", alpha=0.25, label="scored, not candidate"),
                       Patch(fc=ESA_COLOR, alpha=0.35, label="ESA rfiDetected this pass (approx. strip)"),
                       Patch(fill=False, ec=RECUR_COLOR, lw=2, label="ESA rfiDetected on >=3 stack dates"),
                       Patch(fill=False, ec=RECUR_COLOR, ls=":", label="ESA rfiDetected on 1-2 stack dates"),
                       Patch(fill=False, ec="k", ls="--", label="S1 frame")], loc="lower right", fontsize=8)
    fig.text(0.01, 0.01, "Data: ADS-B Exchange free sample (readsb-hist); Copernicus Sentinel-1 via Microsoft Planetary "
             "Computer; Copernicus DEM GLO-30; Natural Earth. C-band RFI is a proxy, not a GNSS (L-band) measurement.",
             fontsize=7, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(png, dpi=110)


def main():
    adsb = json.loads((OUT / "adsb_cells.geojson").read_text())
    s1 = json.loads((OUT / "s1_cells.geojson").read_text())
    adsb_sum = json.loads((OUT / "adsb_summary.json").read_text())
    s1_sum = json.loads((OUT / "s1_summary.json").read_text())
    zones, t_pass = merge_zones(adsb, s1, adsb_sum, s1_sum)
    (OUT / "zones.geojson").write_text(json.dumps(zones))
    with open(OUT / "s1-overpass.jsonl", "w") as fh:
        fh.write(json.dumps({"header": {"schema": "navdash/1", "track": "s1-overpass", "role": "altpnt",
                                        "label": "Sentinel-1 overpass (event only)"}}) + "\n")
        fh.write(json.dumps({"t": round(t_pass, 1), "event": "s1_overpass",
                             "text": f"{s1_sum['target'][:3]} orbit {s1_sum['relative_orbit']}: "
                                     f"{s1_sum['n_hex_candidates']} temporal-z candidate hexes"}) + "\n")
    manifest = {"title": f"OSINT interference map {adsb_sum['date']} (ADS-B NACp + Sentinel-1 RFI)",
                "tracks": ["adsb-good.jsonl", "adsb-bad.jsonl", "s1-overpass.jsonl"], "zones": "zones.geojson"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    draw(adsb, s1, adsb_sum, s1_sum, OUT / "map.png")
    print(f"zones {len(zones['features'])}, S1 overpass at t={t_pass:.0f} s of the ADS-B window")


if __name__ == "__main__":
    main()
