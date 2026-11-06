"""Pool injection_results.json over seeds into the README tables (stdlib).

  python3 summarize_results.py example_output/injection_results_2026-11-03.json
"""
import json
import sys
from collections import defaultdict

from evaluate import OBSERVABLE_MAX_LEAD_GAP_S, OBSERVABLE_MIN_FIXES

DETECTORS = ["jump", "sog_mismatch", "cog_mismatch", "turn", "loiter_underway", "cluster", "on_land"]


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float("nan")


def offset_bucket(m):
    return "0.2-0.5 km" if m < 500 else "0.5-2 km" if m < 2000 else "2-10 km" if m < 10000 else "10-40 km"


def table(path):
    runs = json.load(open(path))
    eps = [e for r in runs for e in r["episodes"]]
    groups = defaultdict(list)
    for e in eps:
        groups[e["kind"]].append(e)
        if e["kind"] == "offset":
            groups["offset " + offset_bucket(e["param"])].append(e)
        if e["kind"] == "drift":
            groups[f"drift {int(e['param'])}-{int(e['param']) + 1} m/s"].append(e)
    groups["ALL"] = eps
    print(f"## {path} ({len(runs)} seeds)")
    print("| episodes | n | recall | recall (observable) | TTD median s | TTD p90 s | "
          + " | ".join(DETECTORS) + " |")
    print("|" + "---|" * (6 + len(DETECTORS)))
    for k in sorted(groups):
        g = groups[k]
        obs = [e for e in g if e["n_in"] >= OBSERVABLE_MIN_FIXES and e["lead_gap_s"] <= OBSERVABLE_MAX_LEAD_GAP_S]
        ttd = [e["ttd_s"] for e in g if e["detected"]]
        rec = sum(e["detected"] for e in g) / len(g)
        rec_obs = sum(e["detected"] for e in obs) / max(1, len(obs))
        share = " | ".join(f"{sum(d in e['kinds'] for e in g) / len(g):.2f}" for d in DETECTORS)
        print(f"| {k} | {len(g)} | {rec:.2f} | {rec_obs:.2f} (n={len(obs)}) | {pct(ttd, .5):.0f} | "
              f"{pct(ttd, .9):.0f} | {share} |")
    for r in runs:
        t = r["totals"]
        print(f"seed {r['seed']}: alerts {t['alerts']}, on episodes {t['tp_alerts']}, "
              f"on injected vessels outside episodes {t['fp_alerts_on_injected']}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        table(p)
