"""Real-data mode: PTP over mobile networks, Kalnins, Zenodo 14230741 (CC BY 4.0).

1. Characterise the real links: PPS-vs-PPS truth (Timebeat over 5G SA / NSA), PTPd's own
   view (offset from master, one-way delay, per-direction delays over 4G / 5G NSA / 5G SA),
   and Delay_Req transit from the UPF packet capture.
2. Replay the PPS truth error as the time-transfer error of both microwave links into
   comms-relay in scenario (a) and compare with the synthetic links.
3. Run scenario (b)'s no-spoof control with a real series on one monitored link.

Fetch the data first: python3 fetch_data.py. Stdlib only.
"""
import argparse
import json
import math
import re
import statistics
import struct
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # also under python3 -I, which drops the script directory
import timing_network as tn  # noqa: E402

DATASET = HERE / "data" / "mobile-ptp" / "Clock Synchronization Accuracy over Mobile Networks"
MS = 1e-3
NS, US, HOUR = tn.NS, tn.US, tn.HOUR
BUDGETS = (1 * US, 1.5 * US, 1 * MS)
DRIFT_PLAUSIBLE_PPB = 100_000          # 100 ppm: beyond any crystal; the servo is chasing delay noise
SAME_CLOCK_WINDOW_S = 1.0              # Delay_Req originTimestamp this close to capture => slave fills t3
MOVING_MEAN_S = 60
PTPD_SETTLE_S = 300                    # PTPd rows this long after a log starts are acquisition, dropped
PCAP_TAIL_FRACTION = 0.5               # one UPF-capture slave slews in from 320 ms over the first ~440 s

# label => (path under the dataset, what the scope compared)
PPS_FILES = {
    "5G SA, UE is GM, idle": (
        "Clock offset (Pulse-per-second offset) over private 5G SA mobile network/User Equipment serves as "
        "Grandmaster clock/TIMEBEAT_PPS clock offset without random traffic calculated from Oscilloscope "
        "(CH2-CH1)_03.07.2024.txt", "slave vs GM"),
    "5G SA, UE is GM, 50 Mb/s iperf3": (
        "Clock offset (Pulse-per-second offset) over private 5G SA mobile network/User Equipment serves as "
        "Grandmaster clock/TIMEBEAT_PPS clock offset with random traffic calculated from Oscilloscope "
        "(CH2-CH1)_03.07.2024.txt", "slave vs GM"),
    "5G SA, UPF is GM": (
        "Clock offset (Pulse-per-second offset) over private 5G SA mobile network/UPF entity inside 5G core as "
        "Grandmaster clock/TIMEBEAT_PPS clock offset when UPF Grandmaster calculated from Oscilloscope "
        "(CH2-CH1)_04.07.2024.txt", "slave vs slave"),
    "5G NSA public, two UEs": (
        "Clock offset (Pulse-per-second offset) over BITE 5G NSA mobile network/TIMEBEAT_PPS clock offset "
        "calculated from Oscilloscope (CH2-CH1)_06.06.2024.txt", "slave vs GM"),
}
PTPD_DIRS = {
    "4G public": "Clock offset (calculated) over BITE 4G mobile network",
    "5G NSA public": "Clock offset (calculated) over BITE 5G NSA mobile network",
    "5G SA private": "Clock offset (calculated) over private 5G SA mobile network",
}
UPF_PCAP = ("Clock offset (Pulse-per-second offset) over private 5G SA mobile network/UPF entity inside 5G core as "
            "Grandmaster clock/Network traffic inside UPF entity when UPF is Grandmaster_04.07.2024.pcapng")

# ---------------------------------------------------------------- parsers


def parse_pps(lines):
    """Oscilloscope CH2 - CH1 per second, seconds. Two layouts in the dataset:
    'index,value|null' and 'ISO time,index,value'. Returns [(index, value or None)]."""
    out = []
    for line in lines:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < 2 or not parts[-2].lstrip("-").isdigit():
            continue
        try:
            v = None if parts[-1].lower() == "null" else float(parts[-1])
        except ValueError:
            continue
        out.append((int(parts[-2]), v))
    return out


_PTPD_ROW = re.compile(r"(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+, )")


def parse_ptpd(text):
    """PTPd2 statistics log rows in the slave state. Some rows in the dataset are glued to the
    next one without a newline, so split on the timestamp, not on lines. Seconds throughout;
    drift in ppb. The all-zero first row after (re)entering slave state is dropped."""
    rows, seen = [], set()
    for chunk in _PTPD_ROW.split(text):
        f = [x.strip() for x in chunk.strip().split(",")]
        if len(f) < 17 or f[1] != "slv":
            continue
        try:
            t = datetime.strptime(f[0], "%Y-%m-%d %H:%M:%S.%f").timestamp()
            owd, ofm, s2m, m2s, drift = (float(f[i]) for i in (3, 4, 5, 6, 7))
        except ValueError:
            continue
        if t in seen or (owd == 0.0 and ofm == 0.0 and s2m == 0.0 and m2s == 0.0):
            continue
        seen.add(t)
        rows.append({"t": t, "owd": owd, "ofm": ofm, "s2m": s2m, "m2s": m2s, "drift_ppb": drift})
    return rows


def parse_pcapng_ptp(buf):
    """PTP event/general messages (UDP 319/320) from a pcapng with raw-IP or Ethernet links.
    Returns [(capture s, src, dst, message type, sequence id, 10-byte timestamp field s)]."""
    out, off, le, linktypes, tsres = [], 0, "<", [], []
    while off + 12 <= len(buf):
        btype = struct.unpack_from("<I", buf, off)[0]
        if btype == 0x0A0D0D0A:
            le = "<" if struct.unpack_from("<I", buf, off + 8)[0] == 0x1A2B3C4D else ">"
        blen = struct.unpack_from(le + "I", buf, off + 4)[0]
        if blen < 12:
            break
        if btype == 1:
            linktypes.append(struct.unpack_from(le + "H", buf, off + 8)[0])
            res, o = 6, off + 16
            while o + 4 <= off + blen - 4:
                code, ln = struct.unpack_from(le + "HH", buf, o)
                if code == 0:
                    break
                if code == 9:
                    r = buf[o + 4]
                    res = r if r < 128 else None
                o += 4 + (ln + 3) // 4 * 4
            tsres.append(res)
        elif btype == 6:
            iid, th, tl, caplen = struct.unpack_from(le + "IIII", buf, off + 8)
            d = buf[off + 28:off + 28 + caplen]
            lt = linktypes[iid] if iid < len(linktypes) else None
            ip = 14 if lt == 1 else 0 if lt in (12, 101, 228) else None
            if ip is not None and len(d) > ip + 20 and d[ip] >> 4 == 4 and d[ip + 9] == 17:
                ihl = (d[ip] & 15) * 4
                sport, dport = struct.unpack_from(">HH", d, ip + ihl)
                p = d[ip + ihl + 8:]
                if dport in (319, 320) and len(p) >= 44:
                    sh, sl, sns = struct.unpack_from(">HII", p, 34)
                    cap = ((th << 32) | tl) * 10.0 ** -(tsres[iid] or 6)
                    out.append((cap, ".".join(map(str, d[ip + 12:ip + 16])), ".".join(map(str, d[ip + 16:ip + 20])),
                                p[0] & 15, struct.unpack_from(">H", p, 30)[0], ((sh << 32) | sl) + sns * 1e-9))
        off += blen
    return out


# ---------------------------------------------------------------- statistics

def pct(v, q):
    s = sorted(v)
    return s[min(len(s) - 1, max(0, round(q * (len(s) - 1))))]


def describe(v):
    a = [abs(x) for x in v]
    return {"n": len(v), "mean": statistics.fmean(v), "median": statistics.median(v),
            "std": statistics.pstdev(v), "p5": pct(v, 0.05), "p95": pct(v, 0.95),
            "abs_median": statistics.median(a), "abs_p95": pct(a, 0.95), "abs_max": max(a),
            "under": {b: sum(x <= b for x in a) / len(a) for b in BUDGETS}}


def slope(v):
    n = len(v)
    xm, ym = (n - 1) / 2.0, statistics.fmean(v)
    return sum((i - xm) * (y - ym) for i, y in enumerate(v)) / sum((i - xm) ** 2 for i in range(n))


def filled(pairs):
    """1 Hz series with missed pulses held at the previous value (first valid value backwards)."""
    vals = [v for _, v in pairs]
    first = next(v for v in vals if v is not None)
    out, last = [], first
    for v in vals:
        last = last if v is None else v
        out.append(last)
    return out


def mirrored(series):
    """Forward then backward, so looping a 900 s record has no jump at the wrap."""
    return series + series[::-1]


def pps_summary(pairs, compared):
    v = [x for _, x in pairs if x is not None]
    d = describe(v)
    diffs = [b - a for (_, a), (_, b) in zip(pairs, pairs[1:]) if a is not None and b is not None]
    s = filled(pairs)
    w = MOVING_MEAN_S
    mm = [statistics.fmean(s[i:i + w]) for i in range(0, len(s) - w + 1, w)]
    d.update({"compared": compared, "missing": sum(x is None for _, x in pairs),
              "jitter_1s": statistics.pstdev(diffs) / math.sqrt(2.0),
              "wander_60s_std": statistics.pstdev(mm), "trend_ns_per_s": slope(s) / NS,
              "implied_asym": -2.0 * d["mean"] if compared == "slave vs GM" else None})
    return d


def ptpd_summary(rows):
    owd = [r["owd"] for r in rows]
    ofm = [r["ofm"] for r in rows]
    dt = [b["t"] - a["t"] for a, b in zip(rows, rows[1:])]
    owd_steps = [b["owd"] - a["owd"] for a, b in zip(rows, rows[1:]) if b["owd"] != a["owd"]]
    return {"rows": len(rows), "median_interval_s": statistics.median(dt) if dt else None,
            "owd": describe(owd), "owd_step_std": statistics.pstdev(owd_steps) if len(owd_steps) > 1 else None,
            "m2s_p5_p95": (pct([r["m2s"] for r in rows], 0.05), pct([r["m2s"] for r in rows], 0.95)),
            "s2m_p5_p95": (pct([r["s2m"] for r in rows], 0.05), pct([r["s2m"] for r in rows], 0.95)),
            "offset_from_master": describe(ofm),
            "drift_implausible": sum(abs(r["drift_ppb"]) > DRIFT_PLAUSIBLE_PPB for r in rows) / len(rows)}


def settled(rows, settle_s=PTPD_SETTLE_S):
    return [r for r in rows if r["t"] >= rows[0]["t"] + settle_s] if rows else rows


def delay_req_transit(msgs, tail=PCAP_TAIL_FRACTION):
    """Delay_Req (type 1) seen at the GM-side capture: capture time minus the slave's
    originTimestamp, for slaves whose originTimestamp tracks real time. Equals uplink transit
    plus the slave's own time error (both unknown separately)."""
    by_src = {}
    for cap, src, _, mtype, _, ots in msgs:
        if mtype == 1:
            by_src.setdefault(src, []).append(cap - ots)
    out = {}
    for src, v in by_src.items():
        v = v[int(len(v) * (1.0 - tail)):]
        if statistics.median(abs(x) for x in v) < SAME_CLOCK_WINDOW_S:
            d = describe(v)
            d["above_floor_p95"] = pct([x - min(v) for x in v], 0.95)
            out[src] = d
        else:
            out[src] = {"n": len(v), "unusable": "originTimestamp not tied to the slave clock"}
    return out


# ---------------------------------------------------------------- replay into the sample

def relay_links():
    return [k for k, l in enumerate(tn.LINKS) if "comms-relay" in (l.a, l.b) and l.kind == "microwave"]


def replay_regional(series, cfg, seeds, outage_s, calibrate):
    """Scenario (a) with both microwave links into comms-relay replaced by the real series
    (second link offset by half a loop). Returns per-run comms-relay and worst-sensor stats."""
    ks = relay_links()
    rep = {}
    if series is not None:
        loop = mirrored(series)
        rep = {ks[0]: (loop, 0), ks[1]: (loop, len(series) // 2)}
    c = tn.Config(**{**cfg.__dict__, "calibrate": calibrate})
    runs = []
    for s in seeds:
        scn = tn.Scenario(end_s=tn.SETTLE_S + outage_s, mode="peers", ref_t=tn.SETTLE_S,
                          loss={n: (tn.SETTLE_S, math.inf) for n in tn.JAMMED_REGION},
                          calib=(tn.SETTLE_S - HOUR, tn.SETTLE_S), link_replay=rep,
                          checkpoints=(HOUR, 4 * HOUR, 24 * HOUR))
        r = tn.run(scn, c, s)
        runs.append({"relay_max": r.max_te["comms-relay"],
                     "relay_te": {cp: abs(v) for cp, v in r.te_at["comms-relay"].items()},
                     "relay_exceed": r.exceed_at["comms-relay"],
                     "sensors_max": max(r.max_te[n] for n in ("sensor-north", "sensor-south"))})
    return runs


def spliced(train, after, phase=0):
    """1 Hz series for scenario (b): `train` (mirrored loop) until the walk starts, then `after`."""
    start = int(tn.SPOOF_SETTLE_S + tn.SPOOF_TRAIN_S)
    a, b = mirrored(train), mirrored(after)
    return ([a[(i + phase) % len(a)] for i in range(start)]
            + [b[(i + phase) % len(b)] for i in range(int(tn.SPOOF_WALK_S) + 1)])


def replay_spoof(train, after, cfg, seeds, rate=0.0, both=False):
    """Scenario (b) with a real series on base-station <=> comms-relay (and, with `both`, on
    c2-post <=> comms-relay too, half a record out of phase); `train` until the walk starts,
    `after` from then on. No spoof (false-alarm control) or a push on comms-relay (detection).
    train=None runs the synthetic links."""
    ks = relay_links() if both else relay_links()[:1]
    c = tn.Config(**{**cfg.__dict__, "dt": 1.0})
    alarms, det, thr = [], [], []
    for s in seeds:
        scn = tn.spoof_scenario("comms-relay", rate, guard=False)
        if train is not None:
            scn.link_replay = {k: (spliced(train, after, j * len(train) // 2), 0) for j, k in enumerate(ks)}
        r = tn.run(scn, c, s)
        alarms += r.alarms
        det.append(next((a for a, n in r.alarms if n == "comms-relay"), None))
        thr.append(r.thresholds.get("comms-relay"))
    return {"runs": len(seeds), "hours": len(seeds) * tn.SPOOF_WALK_S / HOUR, "alarms": len(alarms),
            "nodes": sorted({n for _, n in alarms}), "first_s": min((a for a, _ in alarms), default=None),
            "relay_detect_s": det, "relay_threshold_median": statistics.median(thr)}


# ---------------------------------------------------------------- printing

def f(v):
    return "-" if v is None else tn.fmt(v)


def print_pps(res):
    print("\n1. PPS truth (oscilloscope CH2 - CH1, 1 Hz, 900 s each; Timebeat v2.1.4, software timestamps)")
    print(f"  {'series':<32} {'compared':<14} {'mean':>9} {'std':>9} {'|TE| med':>9} {'|TE| p95':>9} "
          f"{'|TE| max':>9} {'1s jitter':>9} {'60s wander':>10} {'trend':>10} {'<1.5us':>7} {'<1ms':>6} {'missing':>7}")
    for k, d in res.items():
        print(f"  {k:<32} {d['compared']:<14} {f(d['mean']):>9} {f(d['std']):>9} {f(d['abs_median']):>9} "
              f"{f(d['abs_p95']):>9} {f(d['abs_max']):>9} {f(d['jitter_1s']):>9} {f(d['wander_60s_std']):>10} "
              f"{d['trend_ns_per_s']:>6.0f}ns/s {d['under'][1.5 * US]:>7.1%} {d['under'][1 * MS]:>6.0%} "
              f"{d['missing']:>7}")
    print("  implied static asymmetry (GM=>slave minus slave=>GM) = -2 x mean, slave-vs-GM series only:")
    for k, d in res.items():
        if d["implied_asym"] is not None:
            print(f"    {k:<32} {f(d['implied_asym'])}")


def print_ptpd(res):
    print(f"\n1b. PTPd's own view (statistics log, slave state, first {PTPD_SETTLE_S} s of each log dropped; "
          "not simultaneous with the PPS runs)")
    print(f"  {'network':<14} {'rows':>5} {'interval':>8} {'OWD med':>9} {'OWD p5-p95':>21} {'OWD step sd':>11} "
          f"{'m2s p5-p95':>21} {'s2m p5-p95':>21} {'|offset| med':>12} {'|offset| p95':>12} {'drift>100ppm':>12}")
    for k, d in res.items():
        o, m = d["owd"], d["offset_from_master"]
        print(f"  {k:<14} {d['rows']:>5} {d['median_interval_s']:>7.1f}s {f(o['median']):>9} "
              f"{f(o['p5']):>9} - {f(o['p95']):>9} {f(d['owd_step_std']):>11} "
              f"{f(d['m2s_p5_p95'][0]):>9} - {f(d['m2s_p5_p95'][1]):>9} {f(d['s2m_p5_p95'][0]):>9} - "
              f"{f(d['s2m_p5_p95'][1]):>9} {f(m['abs_median']):>12} {f(m['abs_p95']):>12} {d['drift_implausible']:>12.0%}")


def print_pcap(res):
    print(f"\n1c. UPF capture (UPF is GM, 1 Delay_Req/s per slave, last {PCAP_TAIL_FRACTION:.0%} of the capture): "
          "capture time - Delay_Req originTimestamp")
    for src, d in res.items():
        if "unusable" in d:
            print(f"  slave {src}: {d['n']} Delay_Req, {d['unusable']}")
        else:
            print(f"  slave {src}: {d['n']} Delay_Req, median {f(d['median'])}, p5-p95 {f(d['p5'])} - {f(d['p95'])}, "
                  f"p95 above the minimum {f(d['above_floor_p95'])} (uplink transit + slave time error)")


def summarise_runs(runs, outage_s):
    rm = [r["relay_max"] for r in runs]
    te = {cp: statistics.median(r["relay_te"][cp] for r in runs) for cp in runs[0]["relay_te"]}
    ex = {b: statistics.median(outage_s if r["relay_exceed"][b] is None else r["relay_exceed"][b] for r in runs)
          for b in tn.BUDGETS[:2]}
    return {"relay_max_median": statistics.median(rm), "relay_te_median": te, "relay_under_s": ex,
            "sensors_max_median": statistics.median(r["sensors_max"] for r in runs)}


def print_replay(res, outage_s):
    print(f"\n2. Replay into scenario (a): both microwave links into comms-relay carry the real error, "
          f"{outage_s / HOUR:.0f} h outage, median of runs")
    print(f"  {'link error':<34} {'cal':<4} {'relay |TE| 1 h':>14} {'4 h':>9} {'24 h':>9} {'relay max':>10} "
          f"{'sensors max':>11} {'relay <1 us':>11} {'<1.5 us':>9}")
    for (label, cal), d in res.items():
        te = d["relay_te_median"]
        under = [tn.fmt_dur(d["relay_under_s"][b]) if d["relay_under_s"][b] < outage_s else f"whole {outage_s / HOUR:.0f} h"
                 for b in tn.BUDGETS[:2]]
        print(f"  {label:<34} {'yes' if cal else 'no':<4} {f(te.get(HOUR)):>14} {f(te.get(4 * HOUR)):>9} "
              f"{f(te.get(24 * HOUR)):>9} {f(d['relay_max_median']):>10} {f(d['sensors_max_median']):>11} "
              f"{under[0]:>11} {under[1]:>9}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", default=str(DATASET))
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--outage-h", type=float, default=24.0)
    p.add_argument("--control-runs", type=int, default=5)
    p.add_argument("--json", help="write all results to this JSON file")
    a = p.parse_args(argv)
    root = Path(a.data)
    if not root.is_dir():
        print(f"no dataset at {root}; run: python3 fetch_data.py", file=sys.stderr)
        return 2
    out = {"pps": {}, "ptpd": {}}
    series = {}
    for label, (rel, compared) in PPS_FILES.items():
        pairs = parse_pps((root / rel).read_text().splitlines())
        out["pps"][label] = pps_summary(pairs, compared)
        series[label] = filled(pairs)
    print_pps(out["pps"])
    for label, d in PTPD_DIRS.items():
        rows = []
        for log in sorted((root / d).glob("*.log")):
            rows += settled(parse_ptpd(log.read_text(errors="replace")))
        out["ptpd"][label] = ptpd_summary(rows)
    print_ptpd(out["ptpd"])
    out["pcap"] = delay_req_transit(parse_pcapng_ptp((root / UPF_PCAP).read_bytes()))
    print_pcap(out["pcap"])

    cfg = tn.Config()
    seeds = list(range(1, a.seeds + 1))
    outage = a.outage_h * HOUR
    rep = {("synthetic microwave (sample)", False): summarise_runs(replay_regional(None, cfg, seeds, outage, False), outage),
           ("synthetic microwave (sample)", True): summarise_runs(replay_regional(None, cfg, seeds, outage, True), outage)}
    for label in PPS_FILES:
        if PPS_FILES[label][1] != "slave vs GM":
            continue
        for cal in (False, True):
            rep[(label, cal)] = summarise_runs(replay_regional(series[label], cfg, seeds, outage, cal), outage)
    print_replay(rep, outage)
    out["replay"] = {f"{k[0]} | calibrated={k[1]}": v for k, v in rep.items()}

    idle, load = series["5G SA, UE is GM, idle"], series["5G SA, UE is GM, 50 Mb/s iperf3"]
    ctl = list(range(100, 100 + a.control_runs))
    cases = {"synthetic links, 50 ns/s push": (None, None, 50 * NS, seeds, False),
             "1 link, idle, no spoof": (idle, idle, 0.0, ctl, False),
             "1 link, idle => load after training, no spoof": (idle, load, 0.0, ctl, False),
             "1 link, idle, 50 ns/s push": (idle, idle, 50 * NS, seeds, False),
             "2 links, idle, no spoof": (idle, idle, 0.0, ctl, True),
             "2 links, idle => load after training, no spoof": (idle, load, 0.0, ctl, True),
             "2 links, idle, 50 ns/s push": (idle, idle, 50 * NS, seeds, True)}
    out["spoof"] = {}
    print("\n3. Scenario (b), '5G SA, UE is GM' replayed on base-station <=> comms-relay (1 link) or on both "
          "microwave links into comms-relay (2 links); unguarded, dt 1 s, 2 h walk")
    for label, (train, after, rate, sds, both) in cases.items():
        r = replay_spoof(train, after, cfg, sds, rate, both)
        out["spoof"][label] = r
        det = "" if not rate else ", relay detected after " + ", ".join(
            "never" if d is None else f"{d:.0f} s" for d in r["relay_detect_s"])
        print(f"  {label:<48} relay threshold {f(r['relay_threshold_median']):>9}, {r['alarms']} alarms in {r['runs']} runs ({r['hours']:.0f} h)"
              + (f" on {', '.join(r['nodes'])}" if r["alarms"] else "") + det)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
