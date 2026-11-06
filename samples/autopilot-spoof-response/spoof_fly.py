#!/usr/bin/env python3
"""One shadow-mode flight (no external monitor acts) with a GNSS spoof, for EKF2 or EKF3 fault
handling experiments. Reuses the golden-demo companions unchanged; adds a step spoof, EKF
parameter overrides set before arming, and faster estimator-status streams.

    # PX4 (inside the client container that shares the PX4 SIH network namespace, see spoof_sweep.py)
    python spoof_fly.py --autopilot px4 --spoof coherent --rate 3 --set EKF2_GPS_P_GATE=3 --log x.jsonl
    # ArduPilot (host, SITL on a TCP port)
    python spoof_fly.py --autopilot ardupilot --connect tcp:127.0.0.1:15820 --spoof step --step 100 --log y.jsonl
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent

STATUS_HZ = 5            # ESTIMATOR_STATUS / EKF_STATUS_REPORT; golden-demo uses 2
PX4_ODOMETRY_HZ = 10     # PX4 ODOMETRY carries EKF2's summed reset counter
INT_PARAMS = {"EKF2_GPS_MODE", "EKF2_GPS_CTRL", "EKF2_GPS_CHECK"}


class StepSpoof:
    """Position jumps by `step_m` at onset and stays there; velocity untouched."""

    def __init__(self, onset_s: float, step_m: float, bearing_deg: float, base):
        self.onset, self.step, self.rate, self.kind = onset_s, step_m, 0.0, "step"
        self.u = base.u

    def offset_m(self, t):
        return 0.0 if t is None or t < self.onset else self.step

    def offset_en(self, t):
        d = self.offset_m(t)
        return d * self.u[0], d * self.u[1]

    def vel_en(self, t):
        return 0.0, 0.0


def parse_sets(items: list[str]) -> dict:
    out = {}
    for s in items:
        k, v = s.split("=", 1)
        out[k] = int(v) if k in INT_PARAMS else float(v)
    return out


def build(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--autopilot", choices=["px4", "ardupilot"], required=True)
    ap.add_argument("--connect")
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--spoof", choices=["position", "coherent", "step", "none"], default="coherent")
    ap.add_argument("--rate", type=float, default=1.0, help="drag rate, m/s")
    ap.add_argument("--step", type=float, default=50.0, help="step offset, m (--spoof step)")
    ap.add_argument("--onset", type=float, default=25.0)
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", help="EKF parameter override")
    ap.add_argument("--config", default="default", help="label stored in the log")
    a = ap.parse_args(argv)
    for d in ("golden-demo", "golden-demo-px4"):
        if str(SAMPLES / d) not in sys.path:
            sys.path.insert(0, str(SAMPLES / d))
    base_spoof = "position" if a.spoof == "step" else a.spoof
    common = ["--mode", "baseline", "--log", str(a.log), "--seed", str(a.seed), "--spoof", base_spoof,
              "--rate", str(a.rate), "--onset", str(a.onset), "--quiet"]
    if a.autopilot == "px4":
        import companion_px4 as P
        P.STREAMS_HZ["ESTIMATOR_STATUS"] = STATUS_HZ
        P.STREAMS_HZ["ODOMETRY"] = PX4_ODOMETRY_HZ
        P.LOGGED.add("ODOMETRY")
        ca = P.parse(common + ["--connect", a.connect or "udpin:0.0.0.0:14540"])
        base = P.PX4Companion
    else:
        import companion as G
        G.STREAMS_HZ["EKF_STATUS_REPORT"] = STATUS_HZ
        ca = G.parse(common + ["--connect", a.connect or "tcp:127.0.0.1:15820", "--gps", "inject",
                               "--vgeo", "replay", "--detector", "ss+vel", "--alt", "150", "--vio-to-ap",
                               "--extnav", "reference"])
        base = G.Companion
    return a, ca, base


def make_companion(a, ca, base):
    sets = parse_sets(a.set)

    class Flight(base):
        def __init__(self, ca_):
            super().__init__(ca_)
            if a.spoof == "step":
                self.spoof = StepSpoof(a.onset, a.step, ca_.bearing, self.spoof)
            self.record({"type": "EXPERIMENT", "autopilot": a.autopilot, "config": a.config, "params": sets,
                         "spoof": a.spoof, "rate_mps": a.rate if a.spoof in ("position", "coherent") else None,
                         "step_m": a.step if a.spoof == "step" else None, "onset_s": a.onset, "seed": a.seed})

        def apply_sets(self):
            for k, v in sets.items():
                if a.autopilot == "px4":
                    self.param_set(k, v)
                else:
                    self.m.param_set_send(k, float(v))

        def setup_params(self):            # PX4 only
            super().setup_params()
            self.apply_sets()

        def request_streams(self):
            super().request_streams()
            if a.autopilot == "ardupilot":
                self.apply_sets()

    return Flight(ca)


def main(argv=None) -> int:
    a, ca, base = build(argv)
    a.log.parent.mkdir(parents=True, exist_ok=True)
    make_companion(a, ca, base).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
