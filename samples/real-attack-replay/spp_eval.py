"""Horizontal position error during labelled attack windows: RTKLIB SPP (.pos from run_rtklib_spp.sh)
next to the receiver's own NMEA fix, against a stationary reference. Stdlib only.

  python3 spp_eval.py --labels labels.json --file 2024-09-12/Test_1/ublox_...ubx --pos X.spp.pos [--ubx X.ubx]

Truth: for a file marked static, the median SPP (and, separately, median NMEA) position more than
REF_MARGIN_S from every window; for a window with 'stationary' and 'ref' spans, the median over 'ref' and the error
over 'stationary'. Both are self-referenced (no surveyed antenna position), good to a few metres.
"""

from __future__ import annotations

import argparse
import calendar
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay import REF_MARGIN_S, utc  # noqa: E402
from scorer import haversine_m  # noqa: E402
from ubx_nmea_epochs import to_epochs  # noqa: E402

GPS_EPOCH = calendar.timegm((1980, 1, 6, 0, 0, 0))
GPS_UTC_LEAP_S = 18  # valid 2017-2024 and still in force
WEEK_S = 604800
BIG_ERR_M = 100.0  # an SPP epoch this far off counts as captured / corrupted, not noise


def read_pos(path: Path):
    out = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("%"):
            continue
        f = line.split()
        t = GPS_EPOCH + int(f[0]) * WEEK_S + float(f[1]) - GPS_UTC_LEAP_S
        out.append((t, float(f[2]), float(f[3]), int(f[6])))  # t, lat, lon, ns
    return out


def stats(errs, n_expected):
    if not errs:
        return {"n": 0, "availability": 0.0}
    errs = sorted(errs)
    return {"n": len(errs), "availability": round(len(errs) / max(n_expected, 1), 3),
            "median_m": round(statistics.median(errs), 1), "p95_m": round(errs[int(0.95 * (len(errs) - 1))], 1),
            "max_m": round(errs[-1], 1), "frac_gt_100m": round(sum(e > BIG_ERR_M for e in errs) / len(errs), 3)}


def evaluate(spec: dict, spp: list, nmea: list | None):
    day = spec["day"]
    wins = [(utc(day, w["start"]), utc(day, w["end"])) for w in spec["windows"]]

    def outside(t):
        return not any(s - REF_MARGIN_S <= t <= e + REF_MARGIN_S for s, e in wins)

    rows = []
    for w, (s, e) in zip(spec["windows"], wins):
        if spec.get("static"):
            span, ref_sel = (s, e), outside
        elif "stationary" in w:
            span = (utc(day, w["stationary"][0]), utc(day, w["stationary"][1]))
            r0, r1 = utc(day, w["ref"][0]), utc(day, w["ref"][1])
            ref_sel = lambda t, r0=r0, r1=r1: r0 <= t <= r1  # noqa: E731
        else:
            continue
        row = {"test": w["test"], "span_utc": [w.get("stationary", [w["start"], w["end"]])[0],
                                               w.get("stationary", [w["start"], w["end"]])[1]]}
        for name, pts in (("spp", spp), ("nmea", nmea)):
            if pts is None:
                continue
            ref_pts = [p for p in pts if ref_sel(p[0])]
            if len(ref_pts) < 10:
                row[name] = {"n": 0, "note": "too few reference epochs"}
                continue
            ref = (statistics.median(p[1] for p in ref_pts), statistics.median(p[2] for p in ref_pts))
            errs = [haversine_m(ref[0], ref[1], p[1], p[2]) for p in pts if span[0] <= p[0] <= span[1]]
            base = [haversine_m(ref[0], ref[1], p[1], p[2]) for p in ref_pts]
            row[name] = {**stats(errs, span[1] - span[0] + 1), "ref_spread_p95_m": stats(base, len(base))["p95_m"]}
        rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, default=HERE / "labels.json")
    ap.add_argument("--file", required=True, help="the 'path' of a labels.json entry")
    ap.add_argument("--pos", required=True, type=Path)
    ap.add_argument("--ubx", type=Path, help="same recording, for the receiver's own NMEA fix")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    spec = next(f for f in json.loads(args.labels.read_text())["files"] if f["path"] == args.file)
    spp = [(t, la, lo) for t, la, lo, _ in read_pos(args.pos)]
    nmea = None
    if args.ubx:
        nmea = [(ep.t, ep.lat, ep.lon) for ep, _ in to_epochs(args.ubx.read_bytes(), spec["day"], spec.get("period_s", 1.0))
                if ep.has_fix]
    rows = evaluate(spec, spp, nmea)
    print(f"{'test':<8} {'span (UTC)':<12} | {'avail':>5} {'median m':>9} {'>100 m':>7} {'max km':>8} | NMEA fix: "
          f"{'avail':>5} {'median m':>9} {'max m':>8}   (left: RTKLIB SPP)")
    for r in rows:
        sp, nm = r.get("spp", {}), r.get("nmea", {})
        left = (f"{100 * sp['availability']:>4.0f}% {sp['median_m']:>9} {100 * sp['frac_gt_100m']:>6.0f}% "
                f"{sp['max_m'] / 1000:>8.1f}") if sp.get("n") else f"{'-':>32}"
        right = (f"{100 * nm['availability']:>4.0f}% {nm['median_m']:>9} {nm['max_m']:>8}") if nm.get("n") else "-"
        print(f"{r['test']:<8} {r['span_utc'][0][:5]}-{r['span_utc'][1][:5]}  | {left} |           {right}")
    if args.out:
        args.out.write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
