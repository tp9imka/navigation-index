"""GPSJam-style area interference map from readsb aircraft.json snapshots. Stdlib only.

Aircraft broadcast their own GNSS quality in ADS-B (NACp, NIC). When many aircraft
in one area report degraded accuracy at once, the likely cause is ground-level
interference, not the avionics. This bins aircraft into lat/lon cells and applies
the GPSJam percentage formula. GPSJam uses H3 hexagons and 24 h windows; square
cells keep this stdlib-only.

Usage: python3 adsb_area_map.py SNAPSHOT.json [SNAPSHOT.json ...] [--cell-deg 1.0]
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict

NACP_GOOD_MIN = 8  # NACp 8 => EPU < 92.6 m. GPSJam's FAQ names NACp but not its cut-off.
CELL_DEG = 1.0
MAX_POS_AGE_S = 30.0
YELLOW_PCT = 2.0
RED_PCT = 10.0
MIN_AIRCRAFT = 3


def cell_of(lat, lon, cell_deg):
    return (math.floor(lat / cell_deg) * cell_deg, math.floor(lon / cell_deg) * cell_deg)


def is_bad(ac: dict) -> bool:
    if "gpsOkBefore" in ac:  # readsb's own "GPS was fine until..." marker
        return True
    nacp = ac.get("nac_p")
    return nacp is not None and nacp < NACP_GOOD_MIN


def aircraft_cells(snapshots, cell_deg=CELL_DEG):
    """{cell: {hex: bad?}} - an aircraft counts as bad in a cell if any of its reports there was."""
    cells: dict[tuple, dict[str, bool]] = defaultdict(dict)
    for snap in snapshots:
        for ac in snap.get("aircraft", []):
            lat, lon = ac.get("lat"), ac.get("lon")
            if lat is None or lon is None or ac.get("seen_pos", 0.0) > MAX_POS_AGE_S:
                continue
            if "nac_p" not in ac and "gpsOkBefore" not in ac:
                continue  # no quality field (e.g. MLAT/TIS-B): can't classify, don't count as good
            key = cell_of(lat, lon, cell_deg)
            cells[key][ac["hex"]] = cells[key].get(ac["hex"], False) or is_bad(ac)
    return cells


def percent_bad(n_good: int, n_bad: int) -> float:
    total = n_good + n_bad
    return max(0.0, 100.0 * (n_bad - 1) / total) if total else 0.0


def level(pct: float, total: int) -> str:
    if total < MIN_AIRCRAFT:
        return "no-data"
    return "red" if pct > RED_PCT else "yellow" if pct >= YELLOW_PCT else "green"


def summarize(cells):
    rows = []
    for (lat, lon), acs in sorted(cells.items()):
        n_bad = sum(acs.values())
        n_good = len(acs) - n_bad
        pct = percent_bad(n_good, n_bad)
        rows.append((lat, lon, n_good, n_bad, pct, level(pct, len(acs))))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshots", nargs="+")
    ap.add_argument("--cell-deg", type=float, default=CELL_DEG)
    args = ap.parse_args()
    snaps = []
    for path in args.snapshots:
        with open(path) as fh:
            snaps.append(json.load(fh))
    print(f"{'lat':>7}{'lon':>8}{'good':>6}{'bad':>5}{'%bad':>7}  level")
    for lat, lon, good, bad, pct, lvl in summarize(aircraft_cells(snaps, args.cell_deg)):
        print(f"{lat:>7.1f}{lon:>8.1f}{good:>6}{bad:>5}{pct:>7.1f}  {lvl}")


if __name__ == "__main__":
    main()
