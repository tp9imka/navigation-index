"""Score RTKLIB .pos solutions (ECEF output, rnx2rtkp -e) against an NGS CORS coordinate. Stdlib only.

Usage:
  python3 compare_pos.py --truth data/p730_20.coord.txt --epoch 2024.27 out/spp.pos out/rtk.pos
  python3 compare_pos.py --truth data/p731_20.coord.txt --epoch 2024.27 --print-xyz   # base for -r
"""

from __future__ import annotations

import argparse
import math
import re

WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
Q_LABELS = {1: "fix", 2: "float", 3: "sbas", 4: "dgps", 5: "single", 6: "ppp"}
NUM = r"(-?\d+\.\d+)"


def parse_ngs_coord(path):
    """ITRF2020 ARP position + velocity from an NGS '<site>_20.coord.txt' sheet."""
    with open(path) as fh:
        text = fh.read()
    block = text.split("ITRF2020 POSITION", 1)[1]
    ref_epoch = float(re.search(r"EPOCH\s+(\d+\.\d+)", block).group(1))
    pos = [float(re.search(rf"\b{ax} =\s+{NUM} m", block).group(1)) for ax in "XYZ"]
    vel = [float(re.search(rf"\bV{ax} =\s+{NUM} m/yr", block).group(1)) for ax in "XYZ"]
    return pos, vel, ref_epoch


def truth_at(path, epoch):
    pos, vel, ref = parse_ngs_coord(path)
    return [p + v * (epoch - ref) for p, v in zip(pos, vel)]


def ecef_to_geodetic(x, y, z):
    e2 = WGS84_F * (2 - WGS84_F)
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(6):
        n = WGS84_A / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        h = p / math.cos(lat) - n
        lat = math.atan2(z, p * (1 - e2 * n / (n + h)))
    return lat, lon, h


def ecef_delta_to_enu(d, lat, lon):
    sl, cl, sp, cp = math.sin(lon), math.cos(lon), math.sin(lat), math.cos(lat)
    e = -sl * d[0] + cl * d[1]
    n = -sp * cl * d[0] - sp * sl * d[1] + cp * d[2]
    u = cp * cl * d[0] + cp * sl * d[1] + sp * d[2]
    return e, n, u


def read_pos(path):
    """[(x, y, z, q, ns)] from an rnx2rtkp -e solution file (2 time tokens, then x y z Q ns)."""
    rows = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("%") or not line.strip():
                continue
            tok = line.split()
            rows.append((float(tok[2]), float(tok[3]), float(tok[4]), int(tok[5]), int(tok[6])))
    return rows


def percentile(sorted_vals, pct):
    return sorted_vals[min(len(sorted_vals) - 1, int(pct / 100 * len(sorted_vals)))]


def score(rows, truth):
    lat, lon, _ = ecef_to_geodetic(*truth)
    enu = [ecef_delta_to_enu([r[0] - truth[0], r[1] - truth[1], r[2] - truth[2]], lat, lon)
           for r in rows]
    rms = [math.sqrt(sum(v[i] ** 2 for v in enu) / len(enu)) for i in range(3)]
    horiz = sorted(math.hypot(e, n) for e, n, _ in enu)
    q_counts = {}
    for r in rows:
        q_counts[r[3]] = q_counts.get(r[3], 0) + 1
    return rms, percentile(horiz, 95), q_counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", required=True, help="NGS <site>_20.coord.txt")
    ap.add_argument("--epoch", type=float, required=True, help="decimal year of the data")
    ap.add_argument("--print-xyz", action="store_true", help="print propagated ECEF and exit")
    ap.add_argument("pos", nargs="*")
    args = ap.parse_args()
    truth = truth_at(args.truth, args.epoch)
    if args.print_xyz:
        print(" ".join(f"{v:.4f}" for v in truth))
        return
    print(f"{'file':<22}{'epochs':>7}{'E rms':>8}{'N rms':>8}{'U rms':>8}{'H 95%':>8}  solution types")
    for path in args.pos:
        rows = read_pos(path)
        if not rows:
            print(f"{path:<22}  no solutions")
            continue
        (e, n, u), h95, q = score(rows, truth)
        types = ", ".join(f"{Q_LABELS.get(k, k)} {100 * v / len(rows):.0f}%" for k, v in sorted(q.items()))
        print(f"{path:<22}{len(rows):>7}{e:>8.3f}{n:>8.3f}{u:>8.3f}{h95:>8.3f}  {types}")


if __name__ == "__main__":
    main()
