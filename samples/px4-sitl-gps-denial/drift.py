#!/usr/bin/env python3
"""Position drift during a GPS outage, from a CSV of estimate vs truth. Stdlib only.

CSV columns: t, phase, est_lat, est_lon, true_lat, true_lon. Truth may be empty;
then error reads "not measured" rather than a made-up number.

  python3 drift.py flight_log.csv
  python3 drift.py --synthetic        # built-in dead-reckoning example
"""
import argparse
import csv
import io
import math
import sys

EARTH_RADIUS_M = 6_378_137.0  # WGS84 semi-major axis
DRIFT_ALERT_M = 5.0
DENIED_PHASE = "gps-denied"
PHASE_ORDER = ("pre-denial", DENIED_PHASE, "recovery")


def latlon_to_ne(lat, lon, lat0, lon0):
    """Local north/east metres from (lat0, lon0); equirectangular, fine for a few km."""
    north = math.radians(lat - lat0) * EARTH_RADIUS_M
    east = math.radians(lon - lon0) * EARTH_RADIUS_M * math.cos(math.radians(lat0))
    return north, east


def ne_to_latlon(north, east, lat0, lon0):
    lat = lat0 + math.degrees(north / EARTH_RADIUS_M)
    lon = lon0 + math.degrees(east / (EARTH_RADIUS_M * math.cos(math.radians(lat0))))
    return lat, lon


def horizontal_error_m(est_lat, est_lon, true_lat, true_lon):
    n, e = latlon_to_ne(est_lat, est_lon, true_lat, true_lon)
    return math.hypot(n, e)


def _float_or_none(s):
    return float(s) if s not in ("", None) else None


def load_rows(f):
    rows = []
    for r in csv.DictReader(f):
        rows.append({
            "t": float(r["t"]),
            "phase": r["phase"],
            "est": (_float_or_none(r["est_lat"]), _float_or_none(r["est_lon"])),
            "true": (_float_or_none(r["true_lat"]), _float_or_none(r["true_lon"])),
        })
    return rows


def summarize(rows, alert_m=DRIFT_ALERT_M):
    """Per-phase sample count, mean and max error, plus seconds from the first denied
    sample until error first exceeds alert_m. None means not measurable from the data."""
    out = {}
    denial_start = next((r["t"] for r in rows if r["phase"] == DENIED_PHASE), None)
    time_to_alert = None
    for r in rows:
        phase = out.setdefault(r["phase"], {"samples": 0, "errors": []})
        phase["samples"] += 1
        if None in r["est"] or None in r["true"]:
            continue
        err = horizontal_error_m(*r["est"], *r["true"])
        phase["errors"].append(err)
        if (time_to_alert is None and denial_start is not None and r["t"] >= denial_start
                and err > alert_m):
            time_to_alert = r["t"] - denial_start
    for phase in out.values():
        errs = phase.pop("errors")
        phase["measured"] = len(errs)
        phase["mean_m"] = sum(errs) / len(errs) if errs else None
        phase["max_m"] = max(errs) if errs else None
    return out, time_to_alert


def synthetic_csv(speed_m_s=5.0, rate_hz=5, pre_s=10.0, denied_s=20.0, recovery_s=10.0,
                  vel_bias_m_s=(0.15, -0.10), accel_bias_m_s2=(0.02, 0.01), recovery_tau_s=2.0):
    """Straight east-bound flight; during denial the estimate dead-reckons with a velocity
    and acceleration bias, after GPS returns the error decays with time constant tau."""
    lat0, lon0 = 47.397742, 8.545594
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["t", "phase", "est_lat", "est_lon", "true_lat", "true_lon"])
    err_at_restore = (0.0, 0.0)
    total = pre_s + denied_s + recovery_s
    for i in range(int(total * rate_hz) + 1):
        t = i / rate_hz
        true_n, true_e = 0.0, speed_m_s * t
        if t < pre_s:
            phase, dn, de = "pre-denial", 0.0, 0.0
        elif t < pre_s + denied_s:
            tau = t - pre_s
            phase = DENIED_PHASE
            dn = vel_bias_m_s[0] * tau + 0.5 * accel_bias_m_s2[0] * tau ** 2
            de = vel_bias_m_s[1] * tau + 0.5 * accel_bias_m_s2[1] * tau ** 2
            err_at_restore = (dn, de)
        else:
            decay = math.exp(-(t - pre_s - denied_s) / recovery_tau_s)
            phase, dn, de = "recovery", err_at_restore[0] * decay, err_at_restore[1] * decay
        tl = ne_to_latlon(true_n, true_e, lat0, lon0)
        el = ne_to_latlon(true_n + dn, true_e + de, lat0, lon0)
        w.writerow([f"{t:.2f}", phase, f"{el[0]:.9f}", f"{el[1]:.9f}", f"{tl[0]:.9f}", f"{tl[1]:.9f}"])
    return buf.getvalue()


def report(summary, time_to_alert, alert_m=DRIFT_ALERT_M):
    lines = []
    ordered = [p for p in PHASE_ORDER if p in summary] + [p for p in summary if p not in PHASE_ORDER]
    for name in ordered:
        s = summary[name]
        if s["measured"] == 0:
            lines.append(f"{name:<11} samples={s['samples']:<4} error: not measured (no truth)")
        else:
            lines.append(f"{name:<11} samples={s['samples']:<4} mean={s['mean_m']:.2f} m  "
                         f"max={s['max_m']:.2f} m")
    tta = "not reached" if time_to_alert is None else f"{time_to_alert:.1f} s"
    lines.append(f"time from GPS loss to >{alert_m:.0f} m error: {tta}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv", nargs="?")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--alert-m", type=float, default=DRIFT_ALERT_M)
    args = p.parse_args(argv)
    if args.synthetic:
        rows = load_rows(io.StringIO(synthetic_csv()))
    elif args.csv:
        with open(args.csv, newline="") as f:
            rows = load_rows(f)
    else:
        p.error("give a CSV path or --synthetic")
    print(report(*summarize(rows, args.alert_m), alert_m=args.alert_m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
