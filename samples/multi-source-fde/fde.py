"""ARAIM-style fault detection and exclusion over a bank of subset filters. Stdlib only.

The bank holds one filter per subset of the absolute sources (dead reckoning drives all of them).
Per epoch it is a dict {frozenset(sources): (east, north, pos_cov_2x2)}. The decision logic here
never touches the filters, so detection-only and FDE variants replay the same bank.

Admitted set A, monitored fault hypotheses E (subsets of A up to max_faults sources):
  detection   any |x_A - x_{A\\E}| > T_E,  T_E = K_fa * sigma(P_{A\\E} - P_A) (+ registration bias)
  exclusion   candidates E of the smallest size whose remaining set A\\E passes its own detection
              test; exactly one => exclude it; two or more => ambiguous, declare unavailable;
              none => no consistent subset, declare unavailable
  PL          max(K_ff sigma_A, max_E T_E + K_md(E) sigma_{A\\E}) (+ bias), K_md from the prior of E
  readmission A + {s} passes its own detection test for PROBATION epochs after HOLD
"""
import itertools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "altpnt-integrity"))
import altpnt_integrity as v1  # noqa: E402  (stdlib)
import altpnt_v2 as v2  # noqa: E402  (stdlib)
import stanford  # noqa: E402

K_FF = v1.q_inv(v1.IR_FF / 2)
HOLD_EPOCHS = int(v1.EXCLUSION_HOLD / v1.EPOCH)
PROBATION_EPOCHS = int(v1.PROBATION_TIME / v1.EPOCH)
LOOKBACK_EPOCHS = int(v1.LOOKBACK / v1.EPOCH)


def _lmax2(a):
    tr = a[0][0] + a[1][1]
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return tr / 2.0 + math.sqrt(max(tr * tr / 4.0 - det, 0.0))


def hypotheses(admitted, max_faults):
    a = sorted(admitted)
    return [frozenset(c) for n in range(1, min(max_faults, len(a)) + 1) for c in itertools.combinations(a, n)]


def prior(e, priors):
    return math.prod(priors[s] for s in e)


class Ss:
    """Solution-separation statistics of admitted set A on one bank epoch."""

    def __init__(self, bank_k, admitted, max_faults, priors, vgeo_bias=0.0):
        self.a = frozenset(admitted)
        self.hyps = hypotheses(self.a, max_faults)
        n = max(len(self.hyps), 1)
        self.k_fa = v1.q_inv(v1.P_FA / (2 * n))
        x0, y0, p0 = bank_k[self.a]
        self.sig0 = math.sqrt(_lmax2(p0))
        self.bias = vgeo_bias if "vgeo" in self.a else 0.0
        self.vgeo_bias = vgeo_bias
        self.rows = {}
        for e in self.hyps:
            x, y, p = bank_k[self.a - e]
            pd = [[p[i][j] - p0[i][j] for j in range(2)] for i in range(2)]
            sig_d = max(math.sqrt(max(_lmax2(pd), 0.0)), v1.SIGMA_D_FLOOR)
            d = math.hypot(x - x0, y - y0)
            thr = self.k_fa * sig_d + self.bias
            k_md = v1.q_inv(min(0.5, v2.IR_FAULT / (n * prior(e, priors))))
            b_e = vgeo_bias if "vgeo" in (self.a - e) else 0.0
            self.rows[e] = (d, thr, thr + k_md * math.sqrt(_lmax2(p)) + b_e)

    def tripped(self):
        return {e: d / thr for e, (d, thr, _) in self.rows.items() if d > thr}

    def hpl(self):
        return max([K_FF * self.sig0 + self.bias] + [r[2] for r in self.rows.values()])


class SubsetFde:
    """mode: 'detect' (alert while the test trips, never exclude) or 'fde' (exclude by subset)."""

    def __init__(self, sources, priors, max_faults=1, mode="fde", vgeo_bias=0.0, readmit=True):
        self.sources = tuple(sources)
        self.priors, self.max_faults, self.mode = priors, max_faults, mode
        self.vgeo_bias, self.readmit = vgeo_bias, readmit
        self.admitted = frozenset(sources)
        self.excluded = {}          # source => {"k": epoch excluded, "passes": consecutive passes}

    def _ss(self, bank_k, a):
        return Ss(bank_k, a, self.max_faults, self.priors, self.vgeo_bias)

    def _try_exclude(self, bank_k):
        """Smallest exclusion whose remaining set is self-consistent. Returns (E, n_consistent)."""
        for size in range(1, min(self.max_faults, len(self.admitted)) + 1):
            ok = [e for e in hypotheses(self.admitted, size) if len(e) == size
                  and not self._ss(bank_k, self.admitted - e).tripped()]
            if ok:
                return (ok[0] if len(ok) == 1 else None), len(ok)
        return None, 0

    def _readmit(self, k, bank_k, events):
        for s, ex in list(self.excluded.items()):
            if k - ex["k"] < HOLD_EPOCHS:
                continue
            # the whole readmitted set must pass, not only the {s} branch: filters that carried
            # the faulty source may still be off, and they become fault branches after readmission
            ex["passes"] = 0 if self._ss(bank_k, self.admitted | {s}).tripped() else ex["passes"] + 1
            if ex["passes"] >= PROBATION_EPOCHS:
                del self.excluded[s]
                self.admitted = self.admitted | {s}
                events.append(f"readmit:{s}")

    def step(self, k, bank_k):
        events = []
        if self.readmit and self.mode == "fde":
            self._readmit(k, bank_k, events)
        alert = False
        if self.admitted:
            ss = self._ss(bank_k, self.admitted)
            if ss.tripped():
                events.append("detect")
                if self.mode == "fde":
                    e, n_ok = self._try_exclude(bank_k)
                    if e is not None:
                        for s in sorted(e):
                            self.excluded[s] = {"k": k, "passes": 0}
                        self.admitted = self.admitted - e
                        events.append("exclude:" + "+".join(sorted(e)))
                    else:
                        alert = True
                        events.append("alert:ambiguous" if n_ok > 1 else "alert:no-consistent-subset")
                else:
                    alert = True
                    events.append("alert:detected")
        if self.admitted:
            ss = self._ss(bank_k, self.admitted)
            if ss.tripped() and not alert:
                alert = True
                events.append("alert:post-exclusion")
            hpl = ss.hpl()
        else:
            hpl = K_FF * math.sqrt(_lmax2(bank_k[frozenset()][2]))
        x, y, _ = bank_k[self.admitted]
        return {"k": k, "est": (x, y), "hpl": hpl, "alert": alert, "admitted": "+".join(sorted(self.admitted)),
                "events": events}


def run(bank, truth, sources, priors, max_faults=1, mode="fde", vgeo_bias=0.0, readmit=True):
    """bank: list of (k, bank_k); truth: {k: (east, north)}. Returns per-epoch rows with hpe."""
    m = SubsetFde(sources, priors, max_faults, mode, vgeo_bias, readmit)
    rows = []
    for k, bank_k in bank:
        r = m.step(k, bank_k)
        r["hpe"] = math.hypot(r["est"][0] - truth[k][0], r["est"][1] - truth[k][1])
        rows.append(r)
    return rows


def faulty_at(windows, src, k):
    a, b = windows.get(src, (None, None))
    return a is not None and a <= k < b


def evaluate(rows, windows, als=(25.0, 50.0, 100.0)):
    """windows: {source: (first faulty frame, end exclusive)}; empty for a fault-free run.

    exclusion of s at k is wrong unless s was faulty somewhere in [k - LOOKBACK, k]."""
    onset = min((a for a, _ in windows.values()), default=None)
    faulty = set(windows)
    det = [r["k"] for r in rows if r["events"] and any(e == "detect" for e in r["events"])]
    det_after = [k for k in det if onset is not None and k >= onset]
    excl = [(r["k"], e.split(":", 1)[1].split("+")) for r in rows for e in r["events"] if e.startswith("exclude:")]
    right, wrong = set(), set()
    for k, srcs in excl:
        for s in srcs:
            if any(faulty_at(windows, s, j) for j in range(k - LOOKBACK_EPOCHS, k + 1)):
                right.add(s)
            else:
                wrong.add(s)
    if wrong:
        outcome = "wrong_exclusion"
    elif faulty and right >= faulty:
        outcome = "correct_exclusion"
    elif right:
        outcome = "partial_exclusion"
    elif faulty and det_after:
        outcome = "detected_not_excluded"
    elif faulty:
        outcome = "missed"
    else:
        outcome = "false_detection" if det else "quiet"
    out = {"outcome": outcome, "exclusions": [(k, "+".join(s)) for k, s in excl],
           "wrong_excluded": sorted(wrong), "right_excluded": sorted(right),
           "detected_at": det_after[0] if det_after else None,
           "latency": (det_after[0] - onset) if det_after else None,
           "false_detections_before_onset": len([k for k in det if onset is None or k < onset]),
           "alert_epochs": sum(r["alert"] for r in rows),
           "hpe_max": round(max(r["hpe"] for r in rows), 1),
           "hpl_median": round(sorted(r["hpl"] for r in rows)[len(rows) // 2], 1), "per_al": {}}
    post = [r for r in rows if onset is not None and r["k"] >= onset]
    for al in als:
        regs = [stanford.classify(r["hpe"], r["hpl"] if (r["hpl"] < al and not r["alert"]) else max(r["hpl"], al), al)
                for r in rows]
        avail = [r["hpl"] < al and not r["alert"] for r in rows]
        pa = [r["hpl"] < al and not r["alert"] for r in post]
        out["per_al"][f"{al:g}"] = {
            "avail_pct": round(100 * sum(avail) / len(rows), 1),
            "avail_post_onset_pct": round(100 * sum(pa) / len(pa), 1) if pa else None,
            "HMI": regs.count("HMI"), "MI": regs.count("MI")}
    return out
