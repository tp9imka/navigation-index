"""Remote ID => tracker => Cursor-on-Target (UAS track + operator point).

  python3 rid_to_cot.py --sim --offline                         # stdlib only, prints CoT + flags
  python3 rid_to_cot.py --pcap odid_wifi_bcn_sample.pcap --offline
  python3 rid_to_cot.py --sim --cot-url tcp://127.0.0.1:18087   # via PyTAK to a TAK input
"""
import argparse
import asyncio
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mavlink-to-tak-cot"))

import cot  # noqa: E402  (samples/mavlink-to-tak-cot/cot.py)
import capture  # noqa: E402
import sim  # noqa: E402
from tracker import STALE_AFTER_S, Tracker  # noqa: E402

UNKNOWN_HAE = cot.UNKNOWN_ERROR_M
MIN_EMIT_INTERVAL_S = 1.0
FLUSH_WAIT_S = 1.0
# Affiliation stays "u" (unknown): a Remote ID broadcast says nothing about intent.
UAS_COT_TYPES = {"aeroplane": "a-u-A-M-F-Q", "hybrid_lift": "a-u-A-M-F-Q",
                 "helicopter_or_multirotor": "a-u-A-M-H-Q", "gyroplane": "a-u-A-M-H-Q"}
UAS_COT_DEFAULT = "a-u-A"
OPERATOR_COT_TYPE = "a-u-G"


def _with_remarks(event: bytes, text: str) -> bytes:
    if not text:
        return event
    root = ET.fromstring(event)
    ET.SubElement(root.find("detail"), "remarks").text = text
    return ET.tostring(root, encoding="utf-8")


def _remarks(tr):
    i = tr.info
    parts = [f"RID {tr.uas_id or 'no-id'} via {tr.mac}"]
    if i.get("operator_id"):
        parts.append(f"operator {i['operator_id']}")
    if i.get("self_id"):
        parts.append(f"self-id '{i['self_id']}'")
    if i.get("status"):
        parts.append(f"status {i['status']}")
    for name, f in sorted(tr.flags.items()):
        parts.append(f"FLAG {name}: {f['detail']}")
    return "; ".join(parts)


def events_for_track(tr, now: datetime):
    """CoT events for one track: the UAS itself and, when known, its operator."""
    i, out = tr.info, []
    short = (tr.uas_id or tr.key).split(":", 1)[-1]
    if i.get("lat") is not None:
        hae = i["alt_geo_m"] if i.get("alt_geo_m") is not None else UNKNOWN_HAE  # F3411 geodetic alt is WGS84 HAE
        ev = cot.build_event(
            uid=f"rid-{short}", lat=i["lat"], lon=i["lon"], hae=hae,
            course=i.get("course_deg"), speed=i.get("speed_h_ms"),
            callsign=f"RID {short}", ce=i.get("h_acc_m") or cot.UNKNOWN_ERROR_M,
            le=i.get("v_acc_m") or cot.UNKNOWN_ERROR_M, now=now, stale_s=STALE_AFTER_S,
            cot_type=UAS_COT_TYPES.get(i.get("ua_type"), UAS_COT_DEFAULT))
        out.append(_with_remarks(ev, _remarks(tr)))
    if i.get("operator_lat") is not None:
        hae = i["operator_alt_geo_m"] if i.get("operator_alt_geo_m") is not None else UNKNOWN_HAE
        ev = cot.build_event(
            uid=f"rid-op-{short}", lat=i["operator_lat"], lon=i["operator_lon"], hae=hae,
            callsign=f"OP {i.get('operator_id') or short}", now=now, stale_s=STALE_AFTER_S,
            cot_type=OPERATOR_COT_TYPE)
        out.append(_with_remarks(ev, f"operator of {short} ({i.get('operator_location_type')} location)"))
    return out


def load_source(args):
    if args.sim:
        return sim.scenario(duration_s=args.duration)
    return [(r["t"], r["mac"] or r["transport"], r["payload"]) for r in capture.extract(args.pcap)]


def run(records, emit, use_wall_clock=False):
    """Feed records through the tracker; call emit(event_bytes) at most 1 Hz per track."""
    tracker, last_emit = Tracker(), {}
    for t, mac, payload in records:
        tr = tracker.ingest(t, mac, payload)
        if tr is None or t - last_emit.get(tr.key, -1e18) < MIN_EMIT_INTERVAL_S:
            continue
        last_emit[tr.key] = t
        now = datetime.now(timezone.utc) if use_wall_clock else datetime.fromtimestamp(t, timezone.utc)
        for ev in events_for_track(tr, now):
            emit(ev)
    return tracker


def report(tracker, t0, end_t):
    live, stale = tracker.sweep(end_t)
    print(f"# tracks at end: {len(live)} live, {len(stale)} stale")
    for tr in sorted(live + stale, key=lambda x: x.key):
        print(f"#  {tr.key:36s} msgs={tr.msg_count:3d} fixes={len(tr.history):3d} "
              f"{'STALE' if tr in stale else 'live '} flags={sorted(tr.flags) or '-'}")
    print("# anomaly events (first occurrence per track):")
    for t, key, name, detail in tracker.events:
        print(f"#  t+{t - t0:6.1f}s {key}: {name} - {detail}")


class ReplayDone(Exception):
    pass


async def send_via_pytak(records, cot_url, realtime_speed):
    import pytak
    from configparser import ConfigParser

    class Replay(pytak.QueueWorker):
        async def run(self):
            prev = None
            queue = []
            for rec in records:
                if realtime_speed and prev is not None:
                    await asyncio.sleep(max(0.0, (rec[0] - prev) / realtime_speed))
                prev = rec[0]
                self.tracker_feed(rec, queue)
                while queue:
                    await self.put_queue(queue.pop(0))
            await asyncio.sleep(FLUSH_WAIT_S)  # let PyTAK's TX worker drain the queue
            raise ReplayDone()

        def tracker_feed(self, rec, queue):
            t, mac, payload = rec
            tr = self.tracker.ingest(t, mac, payload)
            if tr is None or t - self.last_emit.get(tr.key, -1e18) < MIN_EMIT_INTERVAL_S:
                return
            self.last_emit[tr.key] = t
            queue.extend(events_for_track(tr, datetime.now(timezone.utc)))

    config = ConfigParser()
    config["ridcot"] = {"COT_URL": cot_url}
    config = config["ridcot"]
    clitool = pytak.CLITool(config)
    await clitool.setup()
    worker = Replay(clitool.tx_queue, config)
    worker.tracker, worker.last_emit = Tracker(), {}
    clitool.add_tasks({worker})
    try:
        await clitool.run()
    except ReplayDone:
        pass
    return worker.tracker


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--sim", action="store_true", help="synthetic scenario from sim.py")
    src.add_argument("--pcap", help="pcap/pcapng with Wi-Fi beacon/NAN or BLE Remote ID")
    ap.add_argument("--duration", type=float, default=30)
    ap.add_argument("--offline", action="store_true", help="print CoT to stdout instead of sending")
    ap.add_argument("--quiet", action="store_true", help="with --offline: summary only")
    ap.add_argument("--cot-url", default="tcp://127.0.0.1:18087")
    ap.add_argument("--speed", type=float, default=10.0, help="replay speed-up for --cot-url (0 = no waits)")
    args = ap.parse_args()
    records = load_source(args)
    if not records:
        print("no Remote ID payloads found")
        return 1
    t0 = records[0][0]
    if args.offline:
        n = [0]

        def emit(ev):
            n[0] += 1
            if not args.quiet:
                print(ev.decode())
        tracker = run(records, emit)
        print(f"# {len(records)} payloads => {n[0]} CoT events")
    else:
        tracker = asyncio.run(send_via_pytak(records, args.cot_url, args.speed))
    report(tracker, t0, records[-1][0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
