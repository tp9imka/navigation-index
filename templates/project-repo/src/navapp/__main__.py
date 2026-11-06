"""python3 -m navapp --scenario spoof --out runs/spoof.jsonl [--cot-udp 127.0.0.1:6969]"""
from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

from .filter import DeadReckoningFilter
from .integrity import ChiSquareMonitor, NullMonitor
from .pipeline import run
from .publishers import CotPublisher, JsonlPublisher, MavlinkStatusPublisher, UdpSink
from .sim import SCENARIOS, Scenario, SyntheticSource


def _hostport(s: str) -> tuple[str, int]:
    host, port = s.rsplit(":", 1)
    return host, int(port)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="navapp")
    p.add_argument("--scenario", choices=SCENARIOS, default="spoof")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--out", type=Path, default=Path("runs/run.jsonl"))
    p.add_argument("--origin", default="59.0,10.0", help="lat,lon of the local ENU origin")
    p.add_argument("--cot-udp", type=_hostport, help="host:port for CoT (TAK input or multicast)")
    p.add_argument("--mavlink-udp", type=_hostport, help="host:port for STATUSTEXT (GCS)")
    p.add_argument("--no-integrity", action="store_true", help="baseline: fuse every fix")
    args = p.parse_args(argv)

    lat0, lon0 = (float(v) for v in args.origin.split(","))
    scenario = Scenario(kind=args.scenario, seed=args.seed)
    sinks = []
    publishers = []
    if args.cot_udp:
        sinks.append(UdpSink(*args.cot_udp))
        publishers.append(CotPublisher("navapp-1", lat0, lon0, sink=sinks[-1]))
    if args.mavlink_udp:
        sinks.append(UdpSink(*args.mavlink_udp))
        publishers.append(MavlinkStatusPublisher(sink=sinks[-1]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        log = JsonlPublisher(fh)
        meta = dataclasses.asdict(scenario) | {"attack_onset_s": scenario.onset(), "origin": [lat0, lon0],
                                               "source": "synthetic",
                                               "integrity": not args.no_integrity}
        log.write_meta(meta)
        monitor = NullMonitor() if args.no_integrity else ChiSquareMonitor()
        records = run(SyntheticSource(scenario), DeadReckoningFilter(), monitor, publishers, log)
    for s in sinks:
        s.close()
    print(f"{len(records)} epochs => {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
