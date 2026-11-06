"""Adapter: GNSS-SDR epochs (extract_epochs.py JSON lines) => gnss-interference-monitor scorer.

Stdlib only; imports ../gnss-interference-monitor/scorer.py unchanged. Mapping:
  cn0           <= RINEX S1C per SV (GNSS-SDR tracking C/N0 estimate)
  clk_bias_ns   <= pvt.mat user_clk_offset (clk_drift_ns_s left None: the clock is near-ideal here)
  lat, lon      <= pvt.mat latitude / longitude
  agc_cnt       <= with --power-proxy only: per-second mean IQ power of the input FILE (mix_iq.py
                   log). It is not a receiver AGC count; it rises where an AGC would fall, and
                   the scorer only tests the size of the relative change.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("epochs")
    ap.add_argument("--power-proxy", help="mix_iq.py power CSV used as agc_cnt")
    ap.add_argument("--truth", default="30.286502,120.032669", help="true lat,lon for error column")
    ap.add_argument("--max-speed", type=float, default=50.0,
                    help="m/s; single-epoch SPP noise alone implies up to ~15 m/s here")
    ap.add_argument("--all", action="store_true", help="print every epoch, not only changes")
    ap.add_argument("--rtklib-pos", help="rnx2rtkp .pos of the same run, for a cross-check line")
    ap.add_argument("--json-out")
    a = ap.parse_args()
    tlat, tlon = map(float, a.truth.split(","))
    power = load_power(a.power_proxy) if a.power_proxy else {}
    sc = InterferenceScorer(max_speed_mps=a.max_speed)
    rows, prev_line = [], None
    print(f"{'t':>5} {'nSV':>3} {'meanCN0':>7} {'sdCN0':>5} {'herr_m':>9} {'clk_ns':>9} "
          f"{'jam':>4} {'spoof':>5} verdict / reasons")
    for line in open(a.epochs):
        e = json.loads(line)
        ep = Epoch(t=e["t"], cn0=e["cn0"], clk_bias_ns=e["clk_bias_ns"], clk_drift_ns_s=None,
                   lat=e["lat"], lon=e["lon"], agc_cnt=power.get(int(e["t"])))
        res = sc.assess(ep)
        c = list(e["cn0"].values())
        mean = sum(c) / len(c) if c else float("nan")
        sd = (sum((x - mean) ** 2 for x in c) / len(c)) ** 0.5 if c else float("nan")
        herr = haversine_m(tlat, tlon, e["lat"], e["lon"])
        row = {"t": e["t"], "n_sv": len(c), "mean_cn0": round(mean, 1), "sd_cn0": round(sd, 1),
               "herr_m": round(herr, 1), "clk_bias_ns": round(e["clk_bias_ns"], 1),
               "jam_score": res.jam_score, "spoof_score": res.spoof_score,
               "verdict": res.verdict, "reasons": res.reasons}
        rows.append(row)
        key = (res.verdict, len(c), round(herr, -2))
        if a.all or key != prev_line or res.reasons:
            print(f"{e['t']:5.0f} {len(c):3d} {mean:7.1f} {sd:5.1f} {herr:9.1f} {e['clk_bias_ns']:9.1f} "
                  f"{res.jam_score:4.2f} {res.spoof_score:5.2f} {res.verdict}"
                  + (" / " + "; ".join(res.reasons) if res.reasons else ""))
        prev_line = key
    if a.rtklib_pos and os.path.exists(a.rtklib_pos):
        rk = load_rtklib_pos(a.rtklib_pos)
        both = [(r["herr_m"], haversine_m(tlat, tlon, *rk[r["t"]])) for r in rows if r["t"] in rk]
        if both:
            gs, rt = zip(*both)
            print(f"RTKLIB rnx2rtkp SPP on GNSS-SDR RINEX: {len(both)} common epochs, horizontal error "
                  f"vs truth median {sorted(rt)[len(rt) // 2]:.1f} m (GNSS-SDR PVT {sorted(gs)[len(gs) // 2]:.1f} m), "
                  f"last epoch {rt[-1]:.1f} m (GNSS-SDR {gs[-1]:.1f} m)")
    alerts = [r for r in rows if r["verdict"] != "clean"]
    first = alerts[0]["t"] if alerts else None
    print(f"epochs {len(rows)}, alert epochs {len(alerts)}, first alert t={first}")
    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump({"epochs": rows, "first_alert_t": first, "alert_epochs": len(alerts)}, f, indent=1)


if __name__ == "__main__":
    main()
