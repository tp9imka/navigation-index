"""Adapter: GNSS-SDR epochs (extract_epochs.py JSON lines) => gnss-interference-monitor scorer.

Stdlib only; imports ../gnss-interference-monitor/scorer.py. Mapping:
  cn0           <= RINEX S1C per SV (GNSS-SDR tracking C/N0 estimate)
  clk_bias_ns   <= pvt.mat user_clk_offset (clk_drift_ns_s left None: the scorer differences the bias)
  lat, lon      <= pvt.mat latitude / longitude
  vel_e, vel_n  <= pvt.mat ECEF velocity rotated to east/north (Doppler-based SPP velocity)
  hdop          <= pvt.mat hdop (scales the learned position/velocity noise)
  ref_vel_*     <= --ref-vel only: an independent velocity reference. "0,0" models a platform that
                   knows it is static (IMU at rest / parked vehicle). Without it the scorer falls
                   back to a constant-velocity prior learned on clean epochs.
  agc_cnt       <= with --power-proxy only: per-second mean IQ power of the input FILE (mix_iq.py
                   log). It is not a receiver AGC count; it rises where an AGC would fall, and
                   the scorer only tests the size of the relative change.
  fix_ok=False  for every second after the first fix with no GNSS-SDR PVT, up to the end of the
                power log (the receiver kept running; it produced no solution). GNSS-SDR writes no
                RINEX epoch without a PVT, so those epochs carry cn0=None (not reported), not "0 SVs".
  jam_ind, spoof_det_state, jamming_state: no GNSS-SDR equivalent, left None.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gnss-interference-monitor"))
from scorer import Epoch, InterferenceScorer, haversine_m  # noqa: E402


def load_power(path):
    with open(path) as f:
        return {int(r["t_s"]): float(r["power_lsb2"]) for r in csv.DictReader(f)}


def load_rtklib_pos(path, t0="2022/01/01 00:00:00"):
    """rnx2rtkp -t output (GPST yyyy/mm/dd hh:mm:ss.sss lat lon h ...) => {t_s: (lat, lon)}."""
    out = {}
    for line in open(path):
        if line.startswith("%") or not line.strip():
            continue
        f = line.split()
        if f[0] != t0.split()[0]:
            continue
        hh, mm, ss = f[1].split(":")
        out[round(int(hh) * 3600 + int(mm) * 60 + float(ss))] = (float(f[2]), float(f[3]))
    return out


def longest_run(ts, pred):
    """Longest run of consecutive epochs (by list order) satisfying pred => (length, start_t, end_t)."""
    best, cur, start = (0, None, None), 0, None
    for t, ok in ((t, pred(t)) for t in ts):
        if ok:
            start = t if cur == 0 else start
            cur += 1
            if cur > best[0]:
                best = (cur, start, t)
        else:
            cur = 0
    return best


def metrics(rows, attack_t):
    pre = [r for r in rows if attack_t is None or r["t"] < attack_t]
    post = [r for r in rows if attack_t is not None and r["t"] >= attack_t]
    m = {"epochs": len(rows), "fix_epochs": sum(r["fix"] for r in rows),
         "alert_epochs": sum(r["verdict"] != "clean" for r in rows),
         "false_alert_epochs": sum(r["verdict"] != "clean" for r in pre),
         "false_alarm_epochs": sum(r["alarm"] for r in pre),
         "attack_t": attack_t}
    if post:
        first = next((r["t"] for r in post if r["verdict"] != "clean"), None)
        m["first_alert_t"] = first
        m["time_to_detect_s"] = None if first is None else first - attack_t
        by_det = {}
        for r in post:
            for d in r["detectors"]:
                by_det.setdefault(d, r["t"])
        m["first_by_detector"] = by_det
        ts = [r["t"] for r in post]
        verd = {r["t"]: r for r in post}
        n, a, b = longest_run(ts, lambda t: verd[t]["verdict"] == "clean")
        m["silent_instant"] = {"epochs": n, "from_t": a, "to_t": b}
        n, a, b = longest_run(ts, lambda t: not verd[t]["alarm"])
        m["silent_latched"] = {"epochs": n, "from_t": a, "to_t": b}
        after = [t for t in ts if first is not None and t > first]
        m["silent_latched_after_first_alert"] = longest_run(after, lambda t: not verd[t]["alarm"])[0]
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("epochs")
    ap.add_argument("--power-proxy", help="mix_iq.py power CSV used as agc_cnt and as the scenario timeline")
    ap.add_argument("--truth", default="30.286502,120.032669", help="true lat,lon for error column")
    ap.add_argument("--max-speed", type=float, default=50.0,
                    help="m/s; single-epoch SPP noise alone implies up to ~15 m/s here")
    ap.add_argument("--ref-vel", help="east,north m/s of an independent velocity reference, e.g. 0,0")
    ap.add_argument("--attack-t", type=float, help="attack onset (s) for time-to-detect / false-alarm split")
    ap.add_argument("--all", action="store_true", help="print every epoch, not only changes")
    ap.add_argument("--rtklib-pos", help="rnx2rtkp .pos of the same run, for a cross-check line")
    ap.add_argument("--json-out")
    a = ap.parse_args()
    tlat, tlon = map(float, a.truth.split(","))
    ref = tuple(map(float, a.ref_vel.split(","))) if a.ref_vel else (None, None)
    power = load_power(a.power_proxy) if a.power_proxy else {}
    pvt = {int(e["t"]): e for e in map(json.loads, open(a.epochs))}
    if not pvt:
        print("no PVT epochs at all")
    t_first = min(pvt) if pvt else 0
    t_end = max(list(power) + list(pvt)) if (power or pvt) else -1
    sc = InterferenceScorer(max_speed_mps=a.max_speed)
    rows, prev_key, prev_alarm = [], None, False
    print(f"{'t':>5} {'nSV':>3} {'meanCN0':>7} {'sdCN0':>5} {'herr_m':>9} {'clk_ns':>9} "
          f"{'jam':>4} {'spoof':>5} {'alarm':>5} verdict / reasons")
    for t in range(t_first, t_end + 1):
        e = pvt.get(t)
        if e is None:
            ep = Epoch(t=float(t), cn0=None, fix_ok=False, agc_cnt=power.get(t),
                       ref_vel_e=ref[0], ref_vel_n=ref[1])
            c = []
        else:
            ep = Epoch(t=e["t"], cn0=e["cn0"], clk_bias_ns=e["clk_bias_ns"], clk_drift_ns_s=None,
                       lat=e["lat"], lon=e["lon"], agc_cnt=power.get(t), fix_ok=True,
                       vel_e=e.get("vel_e"), vel_n=e.get("vel_n"), ref_vel_e=ref[0], ref_vel_n=ref[1],
                       hdop=e.get("hdop"))
            c = list(e["cn0"].values())
        res = sc.assess(ep)
        mean = sum(c) / len(c) if c else float("nan")
        sd = (sum((x - mean) ** 2 for x in c) / len(c)) ** 0.5 if c else float("nan")
        herr = haversine_m(tlat, tlon, e["lat"], e["lon"]) if e else float("nan")
        al = res.alarm
        row = {"t": float(t), "fix": e is not None, "n_sv": len(c), "mean_cn0": round(mean, 1),
               "sd_cn0": round(sd, 1), "herr_m": round(herr, 1),
               "clk_bias_ns": round(e["clk_bias_ns"], 1) if e else None,
               "jam_score": res.jam_score, "spoof_score": res.spoof_score,
               "verdict": res.verdict,
               "detectors": [x.detector for x in res.alerts],
               "explain": [{"detector": x.detector, "family": x.family, "message": x.message,
                            "value": round(x.value, 2),
                            "threshold": round(x.threshold, 2), "unit": x.unit, **x.evidence}
                           for x in res.alerts],
               "alarm": al.active, "alarm_since_t": al.since_t}
        rows.append(row)
        key = (res.verdict, len(c), round(herr, -2) if e else None, al.active)
        if a.all or key != prev_key or res.reasons:
            clk = f"{e['clk_bias_ns']:9.1f}" if e else f"{'-':>9}"
            print(f"{t:5d} {len(c):3d} {mean:7.1f} {sd:5.1f} {herr:9.1f} {clk} "
                  f"{res.jam_score:4.2f} {res.spoof_score:5.2f} {'ON' if al.active else '-':>5} {res.verdict}"
                  + (" / " + "; ".join(res.reasons) if res.reasons else ""))
        if al.active and not prev_alarm:
            print(f"      ALARM raised t={al.since_t:.0f}: {', '.join(al.families)}")
        if prev_alarm and not al.active:
            print(f"      ALARM cleared t={al.cleared_t:.0f}: {al.clear_reason}")
        prev_key, prev_alarm = key, al.active
    if a.rtklib_pos and os.path.exists(a.rtklib_pos):
        rk = load_rtklib_pos(a.rtklib_pos)
        both = [(r["herr_m"], haversine_m(tlat, tlon, *rk[r["t"]])) for r in rows if r["fix"] and r["t"] in rk]
        if both:
            gs, rt = zip(*both)
            print(f"RTKLIB rnx2rtkp SPP on GNSS-SDR RINEX: {len(both)} common epochs, horizontal error "
                  f"vs truth median {sorted(rt)[len(rt) // 2]:.1f} m (GNSS-SDR PVT {sorted(gs)[len(gs) // 2]:.1f} m), "
                  f"last epoch {rt[-1]:.1f} m (GNSS-SDR {gs[-1]:.1f} m)")
    m = metrics(rows, a.attack_t)
    print(f"epochs {m['epochs']} ({m['fix_epochs']} with fix), alert epochs {m['alert_epochs']}, "
          f"false alerts before attack {m['false_alert_epochs']} (latched {m['false_alarm_epochs']})")
    if "first_alert_t" in m:
        print(f"attack t={a.attack_t:.0f}: first alert t={m['first_alert_t']}, "
              f"first per detector {m['first_by_detector']}")
        print(f"longest silent run after attack: instantaneous {m['silent_instant']['epochs']} epochs "
              f"({m['silent_instant']['from_t']}-{m['silent_instant']['to_t']}), latched alarm "
              f"{m['silent_latched']['epochs']} epochs; after the first alert {m['silent_latched_after_first_alert']}")
    if a.json_out:
        with open(a.json_out, "w") as f:  # one epoch per line keeps the file small and diffable
            f.write('{"metrics": ' + json.dumps(m) + ',\n "epochs": [\n')
            f.write(",\n".join(json.dumps(r) for r in rows) + "\n]}\n")


if __name__ == "__main__":
    main()
