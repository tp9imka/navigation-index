"""Score alerts against injected episodes (stdlib)."""
from collections import Counter, defaultdict

OFFSET_BUCKETS_M = (500.0, 2_000.0, 10_000.0)
OBSERVABLE_MIN_FIXES = 10
OBSERVABLE_MAX_LEAD_GAP_S = 300.0
END_GRACE_S = 300.0   # the jump back when spoofing stops is still caused by the episode


def _bucket(m):
    lo = 0.0
    for hi in OFFSET_BUCKETS_M:
        if m < hi:
            return f"{lo / 1000:g}-{hi / 1000:g} km"
        lo = hi
    return f">={lo / 1000:g} km"


def score(alerts, episodes):
    by_mmsi = defaultdict(list)
    for a in alerts:
        by_mmsi[a.mmsi].append(a)
    rows, tp_alerts = [], set()
    for ep in episodes:
        hits = []
        for a in by_mmsi.get(ep.mmsi, []):
            if any(ep.start <= f.t <= ep.end + END_GRACE_S for f in a.flags):
                tp_alerts.add(id(a))
            hits += [f for f in a.flags if ep.start <= f.t <= ep.end]
        first = min(hits, key=lambda f: f.t) if hits else None
        rows.append({"ep": ep, "detected": bool(hits),
                     "ttd_s": first.t - ep.start if first else None,
                     "first_kind": first.kind if first else None,
                     "kinds": Counter(f.kind for f in hits)})
    injected = {ep.mmsi for ep in episodes}
    fp_injected = sum(1 for m in injected for a in by_mmsi.get(m, []) if id(a) not in tp_alerts)
    return rows, {"alerts": len(alerts), "tp_alerts": len(tp_alerts),
                  "fp_alerts_all": len(alerts) - len(tp_alerts), "fp_alerts_on_injected": fp_injected}


def observable(ep):
    """Episode the receiver network could see: enough fixes and no coverage hole at onset."""
    return ep.n_in >= OBSERVABLE_MIN_FIXES and ep.lead_gap_s <= OBSERVABLE_MAX_LEAD_GAP_S


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def summarize(rows, totals):
    lines = []
    groups = defaultdict(list)
    for r in rows:
        groups[r["ep"].kind].append(r)
        if r["ep"].kind == "offset":
            groups["offset " + _bucket(r["ep"].param)].append(r)
    groups["ALL"] = rows
    groups["ALL observable"] = [r for r in rows if observable(r["ep"])]
    lines.append(f"{'episode kind':<22}{'n':>5}{'recall':>8}{'TTD med s':>11}{'TTD p90 s':>11}  first detector")
    for k in sorted(groups, key=lambda k: (k.startswith("ALL"), k)):
        rs = groups[k]
        if not rs:
            continue
        det = [r for r in rs if r["detected"]]
        ttd = [r["ttd_s"] for r in det]
        fk = Counter(r["first_kind"] for r in det).most_common(3)
        med, p90 = _pct(ttd, 0.5), _pct(ttd, 0.9)
        lines.append(f"{k:<22}{len(rs):>5}{len(det) / len(rs):>8.2f}"
                     f"{med if med is not None else float('nan'):>11.0f}{p90 if p90 is not None else float('nan'):>11.0f}  "
                     + ", ".join(f"{a} {b}" for a, b in fk))
    n_inj_alerts = totals["tp_alerts"] + totals["fp_alerts_on_injected"]
    lines.append("")
    lines.append(f"alerts total {totals['alerts']}, overlapping an injected episode {totals['tp_alerts']}")
    lines.append(f"precision over all alerts (real-data alerts count as FP): "
                 f"{totals['tp_alerts'] / max(1, totals['alerts']):.2f}")
    lines.append(f"precision on injected vessels only: {totals['tp_alerts'] / max(1, n_inj_alerts):.2f} "
                 f"({totals['fp_alerts_on_injected']} alerts outside episodes)")
    return "\n".join(lines)
