"""Jammer geolocation from DF bearings => CoT for TAK.

  python3 locate.py                                  # synthetic, stdlib least squares
  python3 locate.py --method all                     # + Stone Soup PF and UKF (needs stonesoup)
  python3 locate.py --jsonl bearings.jsonl           # recorded "Kraken Pro Local" JSON lines
  python3 locate.py --kraken-csv http://KRAKEN_IP:8081/DOA_value.html --polls 60
  python3 locate.py --send-udp 239.2.3.1:6969        # also push CoT to Mesh SA
"""
import argparse
import math

import kraken
import scenario
import tak_out
from triangulate import ellipse, locate

DEFAULT_SIGMA_DEG = 5.0


def report(name, fix, truth):
    smaj, smin, ang = ellipse(fix["cov"])
    line = (f"{name:<6} lat={fix['lat']:.6f} lon={fix['lon']:.6f}  95% ellipse "
            f"{smaj:.0f} x {smin:.0f} m @ {ang:.0f} deg  used {fix['n_used']}/{fix['n_total']}")
    if truth:
        te, tn, _ = fix["frame"].to_enu(*truth)
        err = math.hypot(fix["enu"][0] - te, fix["enu"][1] - tn)
        line += f"  error {err:.0f} m"
    print(line)
    return smaj, smin, ang


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--jsonl")
    src.add_argument("--kraken-csv")
    ap.add_argument("--polls", type=int, default=30)
    ap.add_argument("--method", choices=["ls", "pf", "ukf", "all"], default="ls")
    ap.add_argument("--sigma", type=float, default=DEFAULT_SIGMA_DEG, help="bearing 1-sigma, deg")
    ap.add_argument("--window", type=float, help="use only the first N seconds of bearings")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--send-udp", help="host:port")
    a = ap.parse_args()

    truth, station_sigma, sigma = None, None, a.sigma
    if a.jsonl:
        bearings = kraken.read_jsonl(a.jsonl)
    elif a.kraken_csv:
        bearings = list(kraken.poll_csv(a.kraken_csv, max_polls=a.polls))
    else:
        recs, n_out = scenario.generate()
        bearings = [kraken.from_kraken_json(r) for r in recs]
        truth = (scenario.JAMMER_LAT, scenario.JAMMER_LON)
        sigma = scenario.FIXED_SIGMA_DEG
        station_sigma = {scenario.VEHICLE_ID: scenario.MOVING_SIGMA_DEG}
        print(f"synthetic: {len(bearings)} bearings from "
              f"{len({b.station_id for b in bearings})} stations, {n_out} injected outliers")

    if a.window:
        t0 = min(b.t for b in bearings)
        bearings = [b for b in bearings if b.t - t0 < a.window]
        print(f"window {a.window:.0f} s: {len(bearings)} bearings")

    fixes = {"ls": lambda: locate(bearings, sigma, station_sigma)}
    if a.method in ("pf", "ukf", "all"):
        import locate_stonesoup as ss
        fixes["pf"] = lambda: ss.locate_pf(bearings, sigma, station_sigma)
        fixes["ukf"] = lambda: ss.locate_ukf(bearings, sigma, station_sigma)
    chosen = ["ls", "pf", "ukf"] if a.method == "all" else [a.method]

    best = None
    for name in chosen:
        fix = fixes[name]()
        ell = report(name, fix, truth)
        best = best or (name, fix, ell)

    name, fix, ell = best
    remarks = (f"GNSS interference source estimate ({name}, {fix['n_used']}/{fix['n_total']} "
               f"bearings). 95% ellipse {ell[0]:.0f} x {ell[1]:.0f} m.")
    events = tak_out.events_from_fix("jammer-est-1", fix["lat"], fix["lon"], ell, remarks)
    for p in tak_out.write_events(events, a.out_dir, "jammer-est-1"):
        print("wrote", p)
    if a.send_udp:
        host, port = a.send_udp.rsplit(":", 1)
        tak_out.send_udp(events, host, int(port))
        print(f"sent {len(events)} CoT events to udp {a.send_udp}")


if __name__ == "__main__":
    main()
