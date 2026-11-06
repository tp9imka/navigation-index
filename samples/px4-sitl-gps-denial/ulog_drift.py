#!/usr/bin/env python3
"""Turn a PX4 SITL .ulg into the drift.py CSV: EKF2 vehicle_global_position vs
vehicle_global_position_groundtruth (SITL logs ground truth by default).

Requires `pip install pyulog`. Denial window is given in seconds since log start
(read it off the flight_log.csv phases or the "GPS OFF" console line).

  python3 ulog_drift.py log.ulg --deny-from 42 --deny-to 57 > ulog_drift.csv
  python3 drift.py ulog_drift.csv
"""
import argparse
import bisect
import csv
import sys

from pyulog import ULog

EST_TOPIC = "vehicle_global_position"
TRUTH_TOPIC = "vehicle_global_position_groundtruth"
US_PER_S = 1e6


def phase_at(t, deny_from, deny_to):
    if t < deny_from:
        return "pre-denial"
    return "gps-denied" if t < deny_to else "recovery"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ulg")
    p.add_argument("--deny-from", type=float, required=True)
    p.add_argument("--deny-to", type=float, required=True)
    args = p.parse_args()

    ulog = ULog(args.ulg, [EST_TOPIC, TRUTH_TOPIC])
    est = ulog.get_dataset(EST_TOPIC).data
    truth = ulog.get_dataset(TRUTH_TOPIC).data
    t_start = ulog.start_timestamp
    truth_ts = list(truth["timestamp"])

    w = csv.writer(sys.stdout)
    w.writerow(["t", "phase", "est_lat", "est_lon", "true_lat", "true_lon"])
    for i, ts in enumerate(est["timestamp"]):
        j = min(bisect.bisect_left(truth_ts, ts), len(truth_ts) - 1)
        t = (ts - t_start) / US_PER_S
        w.writerow([f"{t:.3f}", phase_at(t, args.deny_from, args.deny_to),
                    est["lat"][i], est["lon"][i], truth["lat"][j], truth["lon"][j]])


if __name__ == "__main__":
    main()
