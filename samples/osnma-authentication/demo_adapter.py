"""Feed recorded OSNMAlib scenario results through AuthAwareScorer. Stdlib only.

Receiver telemetry is synthetic and clean on purpose (static receiver, steady C/N0 on the Galileo SVs
OSNMAlib saw, steady clock), so every alarm below comes from the OSNMA input alone.

Usage: python3 demo_adapter.py [fixtures/osnma_results_20min.json]
"""

import json
import sys
from pathlib import Path

from osnma_adapter import first_alarm, from_timeline, run_timeline
from scorer import Epoch

LAT0, LON0 = 52.0, 13.0
CN0_SPREAD_DBHZ = (47.0, 44.0, 41.0, 38.0, 45.0, 39.0, 42.0)  # open-sky spread, so cn0_uniform stays quiet
CLOCK_DRIFT_NS_S = 50.0


def epoch_fn_for(statuses):
    svs = sorted(set().union(*(s.tracked_svs for s in statuses))) if statuses else []

    def make(t):
        cn0 = {f"E{sv:02d}": CN0_SPREAD_DBHZ[i % len(CN0_SPREAD_DBHZ)] for i, sv in enumerate(svs)}
        return Epoch(t=t, cn0=cn0, clk_bias_ns=CLOCK_DRIFT_NS_S * t, clk_drift_ns_s=CLOCK_DRIFT_NS_S, lat=LAT0, lon=LON0, vel_e=0.0, vel_n=0.0,
                     ref_vel_e=0.0, ref_vel_n=0.0)
    return make


def summarize(result: dict) -> dict:
    statuses = from_timeline(result)
    runs = run_timeline(statuses, epoch_fn_for(statuses))
    alarm = first_alarm(runs)
    states = [r.osnma_state for r in runs]
    return {
        "scenario": result["scenario"],
        "first_alarm_s": None if alarm is None else alarm.t,
        "detectors": sorted({a.detector for r in runs for a in r.alerts}),
        "alarm_epochs": sum(1 for r in runs if r.alarm.active),
        "not_measured_epochs": states.count("not-measured"),
        "final_state": states[-1] if states else "not-measured",
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = Path(argv[0]) if argv else Path(__file__).parent / "fixtures" / "osnma_results_20min.json"
    print("| scenario | first spoofing alarm [s] | detectors | alarm epochs | not-measured epochs | final OSNMA state |")
    print("|---|---|---|---|---|---|")
    for result in json.loads(path.read_text()):
        s = summarize(result)
        first = "none" if s["first_alarm_s"] is None else f"{s['first_alarm_s']:.0f}"
        print(f"| {s['scenario']} | {first} | {', '.join(s['detectors']) or '-'} | {s['alarm_epochs']} | "
              f"{s['not_measured_epochs']} | {s['final_state']} |")


if __name__ == "__main__":
    main()
