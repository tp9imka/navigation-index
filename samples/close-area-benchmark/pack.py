"""Scenario packs (`close-area-pack/1`): "our room + our drone + the bar" in one JSON file, re-run
with the benchmark's own flight loop while tuning.

.venv/bin/python pack.py run packs/office_crazyflie.json --workers 14     # results/pack_office_crazyflie.*
.venv/bin/python pack.py run packs/hall_8x6.json --out results/pack_hall_8x6
.venv/bin/python pack.py check-matrix results/pack_office_crazyflie.json  # seed-0 rows vs results/matrix_0.json

Schema (README.md "Scenario packs" has the long form):

    {
      "schema": "close-area-pack/1",
      "name": "office_crazyflie",                      # [a-z0-9_-]+, default output stem results/pack_<name>
      "worlds": ["preset:office_0",                    # site/playground/presets/office_0.json
                 "family:office:1",                    # world_glass.make_any_world("office", seed 0, index 1)
                 "../../close-area-arena/rooms/hall_8x6.world.json",   # path, relative to the pack file
                 {"schema": "close-area-world/1", ...}],               # inline world
      "vehicle": "default" | {"radius_m", "v_max", "a_max", "tau"},     # presets.vehicle_kwargs
      "sensor": "crazyflie" | "depth_cam_87" | {"beams", "fov_deg", ...},   # presets.make_sensor
      "planners": ["astar_known", ...],                # bench.PLANNERS ids
      "seeds": 5 | {"n": 5, "jitter_m": 0.5},          # seed 0 exact A/B, k > 0 jittered (site/solver/sweep.js)
      "max_time_s": "auto" | 90,                       # auto = bench.max_time(world family)
      "criteria": {"reached_rate": ">= 0.9", "collisions": "== 0", "time_to_goal_p50_s": "<= 30"}
                  # count rule with its own minimum: "collisions": {"rule": "<= 1", "min_runs": 30};
                  # a top-level "min_runs": 30 in criteria applies to every count rule
    }

Criteria. Metrics: <outcome>_rate (reached, collision, stuck, timeout, error), <outcome>_count (also
collisions, timeouts, errors), time_to_goal_p<q>_s (quantile of time to B over all runs, a run that
did not reach B counts as +inf) and min_clearance_m (smallest over all flown runs). Operators >=, >,
<=, <, and == for counts.
- Rates: 95 % Wilson interval on the distinct runs (identical runs count once, as the Solver).
  ">=" / ">" passes only if the LOWER bound meets the threshold, "<=" / "<" only if the UPPER bound
  does: the bar must hold at the pessimistic end of the interval. It fails if even the optimistic
  bound misses it. Anything between is NOT PROVEN (more runs needed). Each rate verdict carries
  runs_needed(): the smallest n that passes if every run succeeds (None for "<= 0": never).
- Counts: k = runs with that outcome (every run, duplicates included). "<=", "<", "==" FAIL as soon as
  k is past the bar. Otherwise NOT PROVEN below min_runs distinct runs (default seeds x worlds), else
  the bar decides. A count PASS is "none happened in n runs", not a rate; the Wilson bound is printed
  next to it.
- Quantiles: distribution-free 95 % interval from order statistics (binomial ranks), same rule.
- min_clearance_m: the observed worst case, no interval; PASS or FAIL.
Planner verdict: PASS if every criterion passes, FAIL if any fails, else NOT PROVEN.
Exit code 0 if at least one planner passes every criterion, 1 otherwise, 2 on a bad pack.

The flight loop is bench.run_one's own code object, run with its world, vehicle, sensor and time
limit swapped in (see fly()). Scored on truth by the arena scorer. Synthetic only.
Vehicle radius: changes the vehicle, the collision stop and the scoring. The planners still inflate
by their own constants (astar_esdf RADIUS 0.15 m and the like); bench.py's factories take no radius.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import types
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PRESET_DIR = os.path.join(REPO, "site", "playground", "presets")
SCHEMA = "close-area-pack/1"
KEYS_REQUIRED = ("schema", "name", "worlds", "planners", "criteria")
KEYS_OPTIONAL = ("description", "vehicle", "sensor", "seeds", "max_time_s")
OUTCOMES = ("reached", "collision", "stuck", "timeout", "error")
Z95 = 1.96
# site/solver/sweep.js
JITTER_DEFAULT_M = 0.5
JITTER_MARGIN_M = 0.1
JITTER_DRAWS = 50
M32 = 0xFFFFFFFF
CLEAR_TOL_M = 2e-4             # check-matrix: world JSON rounding (0.1 mm) may move min clearance this much


# ------------------------------------------------------------ statistics (stdlib only)
def wilson(k: int, n: int, z: float = Z95) -> tuple:
    """(p, lo, hi), as site/solver/sweep.js wilson. n = 0 => (None, 0, 1)."""
    if not n:
        return None, 0.0, 1.0
    p, z2 = k / n, z * z
    den = 1 + z2 / n
    c = (p + z2 / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def _binom_cdf(k: int, n: int, q: float) -> float:
    return sum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(0, k + 1)) if k >= 0 else 0.0


def quantile_ci(xs: list, q: float, alpha: float = 0.05) -> tuple:
    """Nearest-rank quantile and a distribution-free (1 - alpha) interval [X_(j), X_(k)] with
    B ~ Bin(n, q): j largest with P(B <= j - 1) <= alpha/2, k smallest with P(B <= k - 1) >= 1 - alpha/2.
    Ranks outside 1..n give -inf / +inf. Returns (value, lo, hi); n = 0 => (None, -inf, inf)."""
    v = sorted(xs)
    n = len(v)
    if not n:
        return None, -math.inf, math.inf
    point = v[max(0, math.ceil(q * n) - 1)]
    j = 0
    while j + 1 <= n and _binom_cdf(j, n, q) <= alpha / 2:
        j += 1
    k = 1
    while k <= n and _binom_cdf(k - 1, n, q) < 1 - alpha / 2:
        k += 1
    lo = v[j - 1] if j >= 1 else -math.inf
    hi = v[k - 1] if k <= n else math.inf
    return point, lo, hi


def _sig(r: dict) -> str:
    f = lambda v: "-" if v is None else f"{v:.3f}"   # noqa: E731
    return "|".join([str(r.get("world")), r["outcome"], f(r.get("time_to_goal_s")), f(r.get("path_length_m"))])


def distinct(recs: list) -> list:
    """One record per distinct run (world, outcome, time to B and path length at 3 dp, as the Solver's
    runSignature). Errors are never collapsed."""
    seen, out = set(), []
    for i, r in enumerate(recs):
        key = f"error#{i}" if r["outcome"] == "error" else _sig(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


_OPS = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, "<": lambda a, b: a < b,
        "==": lambda a, b: a == b}
_CRIT = re.compile(r"^\s*(>=|<=|==|>|<)\s*(-?[0-9]+(?:\.[0-9]+)?)\s*$")
_QUANT = re.compile(r"^time_to_goal_p([0-9]{1,2})_s$")
# count metrics: <outcome>_count, plus plural names for the outcomes that have one
COUNT_ALIASES = {"collisions": "collision", "timeouts": "timeout", "errors": "error"}
RUNS_NEEDED_CAP = 100000       # runs_needed() gives None (never) past this


def _count_outcome(metric: str):
    if metric in COUNT_ALIASES:
        return COUNT_ALIASES[metric]
    if metric.endswith("_count") and metric[:-6] in OUTCOMES:
        return metric[:-6]
    return None


def _min_runs(v, where: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 100000:
        raise ValueError(f"{where}: min_runs must be a whole number in 1..100000")
    return v


def parse_criteria(criteria: dict) -> list:
    """List of {metric, op, threshold, kind, text[, outcome, min_runs]}. A criterion value is "<op> <number>",
    or for a count rule also {"rule": "<op> <n>", "min_runs": N}. A top-level "min_runs" key sets the
    minimum run count for every count rule that does not set its own (None = the caller's default)."""
    if not isinstance(criteria, dict) or not criteria:
        raise ValueError("criteria must be a non-empty object {metric: \"<op> <number>\"}")
    shared = _min_runs(criteria["min_runs"], "criteria") if "min_runs" in criteria else None
    out = []
    for metric, text in criteria.items():
        if metric == "min_runs":
            continue
        own = None
        if isinstance(text, dict):
            if _count_outcome(metric) is None:
                raise ValueError(f"criterion {metric}: the object form is only for count rules")
            if "rule" not in text or set(text) - {"rule", "min_runs"}:
                raise ValueError(f"criterion {metric}: object form is {{\"rule\": \"<op> <n>\", \"min_runs\": N}}")
            own = _min_runs(text["min_runs"], f"criterion {metric}") if "min_runs" in text else None
            text = text["rule"]
        m = _CRIT.match(str(text))
        if not m:
            raise ValueError(f"criterion {metric}: {text!r} is not '<op> <number>' with op in >=, >, <=, <"
                             " (== for count rules)")
        op, thr = m.group(1), float(m.group(2))
        extra = {}
        outcome = _count_outcome(metric)
        if outcome is not None:
            kind = "count"
            if thr < 0 or thr != int(thr):
                raise ValueError(f"criterion {metric}: count threshold {m.group(2)} is not a whole number >= 0")
            extra = {"outcome": outcome, "min_runs": own if own is not None else shared}
        elif op == "==":
            raise ValueError(f"criterion {metric}: == is only for count rules (collisions, <outcome>_count)")
        elif metric.endswith("_rate") and metric[:-5] in OUTCOMES:
            kind = "rate"
            if not 0 <= thr <= 1:
                raise ValueError(f"criterion {metric}: rate threshold {thr} is outside [0, 1]")
        elif _QUANT.match(metric) and 1 <= int(_QUANT.match(metric).group(1)) <= 99:
            kind = "quantile"
        elif metric == "min_clearance_m":
            kind = "min"
        else:
            raise ValueError(f"criterion {metric}: unknown metric (have <outcome>_rate, <outcome>_count, "
                             f"{', '.join(COUNT_ALIASES)}, time_to_goal_p<q>_s, min_clearance_m)")
        out.append({"metric": metric, "op": op, "threshold": thr, "kind": kind, "text": f"{op} {m.group(2)}",
                    **extra})
    return out


def runs_needed(op: str, thr: float, z: float = Z95):
    """Smallest n for which a rate bar passes when every run goes the bar's way (k = n for >= / >,
    k = 0 for <= / <), judged on the same Wilson bound as the verdict. None if no n up to
    RUNS_NEEDED_CAP does it (e.g. "<= 0": the upper bound z^2 / (n + z^2) is above 0 for every n)."""
    up = op in (">=", ">")

    def ok(n):
        _, lo, hi = wilson(n if up else 0, n, z)
        return _OPS[op](lo if up else hi, thr)
    # all-success lower bound is n / (n + z^2), all-clean upper bound z^2 / (n + z^2): start just below
    # the closed form and step, so the float comparison is the verdict's own
    z2 = z * z
    if up:
        guess = 1 if thr <= 0 else (None if thr >= 1 else z2 * thr / (1 - thr))
    else:
        guess = None if thr <= 0 else (1 if thr >= 1 else z2 * (1 - thr) / thr)
    if guess is None or guess > RUNS_NEEDED_CAP:
        return None
    n = max(1, int(guess) - 2)
    while n <= RUNS_NEEDED_CAP:
        if ok(n):
            return n
        n += 1
    return None


def _judge(op: str, thr: float, lo: float, hi: float) -> str:
    """PASS if the whole interval satisfies the bar, FAIL if none of it does, else NOT PROVEN."""
    if op in (">=", ">"):
        return "PASS" if _OPS[op](lo, thr) else ("FAIL" if not _OPS[op](hi, thr) else "NOT PROVEN")
    return "PASS" if _OPS[op](hi, thr) else ("FAIL" if not _OPS[op](lo, thr) else "NOT PROVEN")


def _judge_count(op: str, thr: float, k: int, n: int, min_runs: int) -> str:
    """Count rule. More runs can only add to k, so "<=", "<" and "==" FAIL as soon as k is past the bar,
    whatever n is. Otherwise fewer than min_runs distinct runs => NOT PROVEN, else the bar decides."""
    if (op in ("<=", "==") and k > thr) or (op == "<" and k >= thr):
        return "FAIL"
    if n < min_runs:
        return "NOT PROVEN"
    return "PASS" if _OPS[op](k, thr) else "FAIL"


def evaluate_one(recs: list, c: dict, min_runs_default=None) -> dict:
    d = distinct(recs)
    n = len(d)
    up = c["op"] in (">=", ">")
    if c["kind"] == "rate":
        outcome = c["metric"][:-5]
        k = sum(r["outcome"] == outcome for r in d)
        p, lo, hi = wilson(k, n)
        verdict = _judge(c["op"], c["threshold"], lo, hi) if n else "NOT PROVEN"
        need = runs_needed(c["op"], c["threshold"])
        gap = None
        if verdict == "NOT PROVEN":
            gap = ("unprovable" if need is None else
                   "sample_size" if n and _OPS[c["op"]](p, c["threshold"]) else "data")
        return {"verdict": verdict, "k": k, "n": n, "n_runs": len(recs), "value": p, "lo": lo, "hi": hi,
                "bound_used": "lower" if up else "upper", "runs_needed_all_success": need,
                "all_success": bool(n) and k == (n if up else 0), "gap": gap}
    if c["kind"] == "count":
        o = c["outcome"]
        k = sum(r["outcome"] == o for r in recs)            # every run counts, duplicates included
        kd = sum(r["outcome"] == o for r in d)
        min_runs = c.get("min_runs") or min_runs_default or len(recs)
        verdict = _judge_count(c["op"], c["threshold"], k, n, min_runs)
        p, lo, hi = wilson(kd, n)
        return {"verdict": verdict, "k": k, "n": n, "n_runs": len(recs), "min_runs": min_runs, "outcome": o,
                "value": p, "lo": lo, "hi": hi, "bound_used": "count",
                "gap": "sample_size" if verdict == "NOT PROVEN" else None}
    if c["kind"] == "quantile":
        q = int(_QUANT.match(c["metric"]).group(1)) / 100
        xs = [r["time_to_goal_s"] if r["outcome"] == "reached" and r.get("time_to_goal_s") is not None
              else math.inf for r in d]
        v, lo, hi = quantile_ci(xs, q)
        verdict = _judge(c["op"], c["threshold"], lo, hi) if n else "NOT PROVEN"
        gap = None
        if verdict == "NOT PROVEN":
            gap = "sample_size" if v is not None and _OPS[c["op"]](v, c["threshold"]) else "data"
        return {"verdict": verdict, "n": n, "n_runs": len(recs), "value": v, "lo": lo, "hi": hi,
                "bound_used": "lower" if up else "upper", "gap": gap}
    flown = [r["min_clearance_m"] for r in recs if r["outcome"] != "error" and r.get("min_clearance_m") is not None]
    if not flown:
        return {"verdict": "NOT PROVEN", "n": 0, "n_runs": len(recs), "value": None, "lo": None, "hi": None,
                "bound_used": "observed"}
    v = min(flown)
    return {"verdict": "PASS" if _OPS[c["op"]](v, c["threshold"]) else "FAIL", "n": len(flown), "n_runs": len(recs),
            "value": v, "lo": v, "hi": v, "bound_used": "observed"}


def size_hint(planner: str, e: dict, crit: list, n_worlds=None):
    """One line if the planner is NOT PROVEN only because of sample size: every NOT PROVEN criterion
    is met by its observed value (a count rule: below min_runs) and none is unprovable. Else None."""
    if e["verdict"] != "NOT PROVEN":
        return None
    open_ = [(c, e["criteria"][c["metric"]]) for c in crit if e["criteria"][c["metric"]]["verdict"] == "NOT PROVEN"]
    if any(r["gap"] != "sample_size" for _, r in open_):
        return None
    parts, need = [], 0
    for c, r in open_:
        if c["kind"] == "rate":
            n_req = r["runs_needed_all_success"]
            if r["all_success"]:
                parts.append(f"{c['metric']} {c['text']} needs {n_req} distinct runs if every run succeeds (has {r['n']})")
                need = max(need, n_req)
            else:
                parts.append(f"{c['metric']} {c['text']} needs more than {n_req} distinct runs, since "
                             f"{r['k']}/{r['n']} is not all-success, and the extra runs must hold the observed rate")
                need = max(need, n_req + 1)
        elif c["kind"] == "count":
            parts.append(f"{c['metric']} {c['text']} needs {r['min_runs']} distinct runs (has {r['n']})")
            need = max(need, r["min_runs"])
        else:
            parts.append(f"{c['metric']} {c['text']}: observed {_num(r['value'], 1)} meets the bar, the interval "
                         "is too wide (more runs)")
    seeds = f" => at least {math.ceil(need / n_worlds)} seeds x {n_worlds} worlds" if n_worlds and need else ""
    return f"{planner}: NOT PROVEN only on sample size. " + "; ".join(parts) + seeds + "."


def evaluate(records: list, criteria: dict, planners=None, min_runs=None, n_worlds=None) -> dict:
    """{planner: {"criteria": {metric: result}, "verdict": PASS | FAIL | NOT PROVEN}} plus "exit_code" and
    "hints". min_runs: default minimum run count of a count rule (pack: seeds x worlds; None = the
    planner's own run count). n_worlds turns a hint's run count into a seed count."""
    crit = parse_criteria(criteria)
    planners = list(planners) if planners else list(dict.fromkeys(r["planner"] for r in records))
    out, hints = {}, []
    for p in planners:
        mine = [r for r in records if r["planner"] == p]
        res = {c["metric"]: dict(evaluate_one(mine, c, min_runs), criterion=c["text"]) for c in crit}
        vs = [x["verdict"] for x in res.values()]
        verdict = "PASS" if all(v == "PASS" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT PROVEN")
        out[p] = {"criteria": res, "verdict": verdict, "n_runs": len(mine)}
        h = size_hint(p, out[p], crit, n_worlds)
        out[p]["size_hint"] = h
        if h:
            hints.append(h)
    return {"planners": out, "hints": hints, "min_runs_default": min_runs,
            "exit_code": 0 if any(v["verdict"] == "PASS" for v in out.values()) else 1}


# ------------------------------------------------------------ table
def _num(v, nd=2):
    if v is None:
        return "-"
    if v == math.inf:
        return "inf"
    if v == -math.inf:
        return "-inf"
    return f"{v:.{nd}f}"


def reason(r: dict, c: dict, nd: int = 2) -> str:
    """The bound that decided the verdict, e.g. "lower 0.80 < 0.9 <= upper 1.00"."""
    lo, hi, t = _num(r["lo"], nd), _num(r["hi"], nd), f"{c['threshold']:g}"
    if c["op"] in (">=", ">"):
        if r["verdict"] == "PASS":
            return f"lower {lo} {c['op']} {t}"
        if r["verdict"] == "FAIL":
            return f"upper {hi} misses {c['op']} {t}"
        return f"lower {lo} misses {c['op']} {t}, upper {hi} meets it"
    if r["verdict"] == "PASS":
        return f"upper {hi} {c['op']} {t}"
    if r["verdict"] == "FAIL":
        return f"lower {lo} misses {c['op']} {t}"
    return f"upper {hi} misses {c['op']} {t}, lower {lo} meets it"


def count_reason(r: dict, c: dict) -> str:
    t = f"{c['threshold']:g}"
    if r["verdict"] == "FAIL":
        return f"{r['k']} {c['op']} {t} is false"
    if r["verdict"] == "NOT PROVEN":
        return f"{r['n']} distinct runs < min_runs {r['min_runs']}"
    return f"{r['k']} {c['op']} {t} in {r['n']} >= {r['min_runs']} distinct runs"


def cell(r: dict, c: dict) -> str:
    if c["kind"] == "rate":
        need = r["runs_needed_all_success"]
        need_s = "never (no n proves it; use a count rule)" if need is None else str(need)
        return (f"{r['verdict']}: {r['k']}/{r['n']} = {_num(r['value'])}, CI [{_num(r['lo'])}, {_num(r['hi'])}]; "
                + reason(r, c) + f"; runs needed if every run succeeds: {need_s}")
    if c["kind"] == "count":
        runs = f"{r['n']} distinct runs" + (f" ({r['n_runs']} flown)" if r["n_runs"] != r["n"] else "")
        bound = (f"rate <= {_num(r['hi'])}" if c["op"] in ("<=", "<", "==") else f"rate >= {_num(r['lo'])}")
        return (f"{r['verdict']}: {r['k']} {r['outcome']} in {runs}; {count_reason(r, c)}; "
                f"{bound} (95 % Wilson bound, not a rate claim)")
    if c["kind"] == "quantile":
        return (f"{r['verdict']}: {_num(r['value'], 1)} s, CI [{_num(r['lo'], 1)}, {_num(r['hi'], 1)}], n={r['n']}; "
                + reason(r, c, 1))
    return f"{r['verdict']}: {_num(r['value'], 3)} m (worst of {r['n']}) vs {c['text']}"


def table(ev: dict, criteria: dict) -> str:
    crit = parse_criteria(criteria)

    def head_of(c):
        if c["kind"] != "count":
            return f"{c['metric']} {c['text']}"
        mins = {e["criteria"][c["metric"]]["min_runs"] for e in ev["planners"].values()}
        return f"{c['metric']} {c['text']} (min {', '.join(map(str, sorted(mins)))} runs)"
    head = "| planner | " + " | ".join(head_of(c) for c in crit) + " | verdict |"
    lines = [head, "|---" * (len(crit) + 2) + "|"]
    for p, e in ev["planners"].items():
        lines.append(f"| {p} | " + " | ".join(cell(e["criteria"][c["metric"]], c) for c in crit)
                     + f" | **{e['verdict']}** |")
    lines.append("")
    for p, e in ev["planners"].items():
        lines.append(f"- {p}: {e['verdict']} ({e['n_runs']} runs)")
    if ev.get("hints"):
        lines += ["", "Sample-size hints (the observed runs meet every open bar; only n is short):", ""]
        lines += [f"- {h}" for h in ev["hints"]]
    lines += ["", f"Exit code {ev['exit_code']}: " + ("at least one planner passes every criterion."
                                                      if ev["exit_code"] == 0 else "no planner passes every criterion.")]
    return "\n".join(lines)


# ------------------------------------------------------------ A/B jitter, port of site/solver/sweep.js
def mulberry32(seed: int):
    a = seed & M32

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & M32
        t = a
        t = ((t ^ (t >> 15)) * (t | 1)) & M32
        t = (t ^ ((t + (((t ^ (t >> 7)) * (t | 61)) & M32)) & M32)) & M32
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return rng


def clearance_at(doc: dict, x: float, y: float) -> float:
    x0, y0, x1, y1 = doc["bounds"]
    d = min(x - x0, x1 - x, y - y0, y1 - y)
    for o in doc.get("obstacles", []):
        if o["type"] == "cylinder":
            e = math.hypot(x - o["cx"], y - o["cy"]) - o["r"]
        else:
            if o["type"] == "box":
                cx, cy, hx, hy = o["cx"], o["cy"], o["hx"], o["hy"]
            else:
                h = (o.get("thickness") or 0.1) / 2
                cx, cy = (o["x0"] + o["x1"]) / 2, (o["y0"] + o["y1"]) / 2
                horiz = abs(o["y1"] - o["y0"]) < 1e-9
                hx = abs(o["x1"] - o["x0"]) / 2 if horiz else h
                hy = h if horiz else abs(o["y1"] - o["y0"]) / 2
            qx, qy = abs(x - cx) - hx, abs(y - cy) - hy
            e = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)
        d = min(d, e)
    return d


def _r4(v: float) -> float:
    return math.floor(v * 1e4 + 0.5) / 1e4      # JS Math.round


def jitter_point(doc, p, rng, R, min_clear, draws=JITTER_DRAWS):
    for i in range(1, draws + 1):
        r, th = R * math.sqrt(rng()), 2 * math.pi * rng()
        q = [_r4(p[0] + r * math.cos(th)), _r4(p[1] + r * math.sin(th))]
        if clearance_at(doc, q[0], q[1]) >= min_clear:
            return q, False
    return [p[0], p[1]], True


def seed_jitter(doc: dict, seed: int, R: float, radius: float) -> dict:
    """A and B for one seed; depends only on (world, seed, R, radius), so every planner gets the same.
    min clearance = vehicle radius + 0.1 m (the Solver reads the radius from the world, here the pack's)."""
    a = list(doc.get("a") or [0.0, 0.0])
    b = list(doc["b"])
    if not seed or not R:
        return {"a": a, "b": b, "exact": True, "a_kept": False, "b_kept": False}
    rng = mulberry32(((seed * 0x9E3779B1) & M32) ^ 0x5EED)
    mc = radius + JITTER_MARGIN_M
    ja, ka = jitter_point(doc, a, rng, R, mc)
    jb, kb = jitter_point(doc, b, rng, R, mc)
    return {"a": ja, "b": jb, "exact": False, "a_kept": ka, "b_kept": kb}


# ------------------------------------------------------------ pack loading
def _load_world(ref, base: str, radius: float) -> tuple:
    """(name, close-area-world/1 dict) for one entry of "worlds"."""
    if isinstance(ref, dict):
        return ref.get("name") or f"inline_{ref.get('family', 'custom')}", {k: v for k, v in ref.items() if k != "name"}
    if not isinstance(ref, str):
        raise ValueError(f"world {ref!r}: must be a dict, a path, 'preset:<name>' or 'family:<family>:<index>'")
    if ref.startswith("preset:"):
        name = ref[7:]
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise ValueError(f"world {ref!r}: bad preset name")
        path = os.path.join(PRESET_DIR, name + ".json")
        if not os.path.isfile(path):
            have = sorted(f[:-5] for f in os.listdir(PRESET_DIR) if f.endswith(".json") and f != "index.json")
            raise ValueError(f"world {ref!r}: no {os.path.relpath(path, REPO)} (have {', '.join(have)})")
        return name, json.load(open(path))
    if ref.startswith("family:"):
        parts = ref.split(":")
        import bench
        if len(parts) not in (3, 4) or parts[1] not in bench.world_glass.FAMILIES:
            raise ValueError(f"world {ref!r}: expected family:<family>:<index>[:<seed>], family in "
                             f"{', '.join(bench.world_glass.FAMILIES)}")
        idx, seed = int(parts[2]), int(parts[3]) if len(parts) == 4 else 0
        w = bench.world_glass.make_any_world(parts[1], seed, idx)          # same layout as the matrix
        return f"{parts[1]}_{idx}" + (f"_s{seed}" if seed else ""), bench.A("world_json").to_json(w)
    path = ref if os.path.isabs(ref) else os.path.normpath(os.path.join(base, ref))
    if not os.path.isfile(path):
        raise ValueError(f"world {ref!r}: file {path} not found")
    name = os.path.basename(path)
    for suf in (".world.json", ".json"):
        if name.endswith(suf):
            name = name[: -len(suf)]
            break
    return name, json.load(open(path))


def load_pack(path: str) -> dict:
    """Validate a pack file. Returns the resolved pack (worlds as dicts, specs filled in)."""
    import bench
    presets, wj = bench.presets, bench.A("world_json")
    d = json.load(open(path))
    bench.presets.check_keys(d, KEYS_REQUIRED, KEYS_OPTIONAL, "pack")
    if d["schema"] != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA!r}")
    if not re.fullmatch(r"[a-z0-9_-]+", str(d["name"])):
        raise ValueError("name must match [a-z0-9_-]+")
    vspec = d.get("vehicle", "default")
    vk = presets.vehicle_kwargs(vspec)
    sspec = d.get("sensor", "ideal")
    if isinstance(sspec, str):
        if sspec not in presets.SENSOR_PRESETS:
            raise ValueError(f"unknown sensor {sspec!r} (have {', '.join(presets.SENSOR_PRESETS)})")
        sensor_name = sspec
    else:
        presets.sensor_spec(sspec)
        sensor_name = "custom"
    planners = d["planners"]
    if not isinstance(planners, list) or not planners:
        raise ValueError("planners must be a non-empty list")
    bad = [p for p in planners if p not in bench.PLANNERS]
    if bad:
        raise ValueError(f"unknown planners {bad} (have {', '.join(bench.PLANNERS)})")
    missing = [p for p in planners if not bench.available(p)]
    if missing:
        raise ValueError(f"planners whose sample module did not load: {missing}")
    seeds = d.get("seeds", 5)
    if isinstance(seeds, int) and not isinstance(seeds, bool):
        n_seeds, jit = seeds, JITTER_DEFAULT_M
    elif isinstance(seeds, dict):
        presets.check_keys(seeds, ("n",), ("jitter_m",), "seeds")
        n_seeds, jit = seeds["n"], seeds.get("jitter_m", JITTER_DEFAULT_M)
    else:
        raise ValueError("seeds must be a whole number or {\"n\", \"jitter_m\"}")
    if not isinstance(n_seeds, int) or isinstance(n_seeds, bool) or not 1 <= n_seeds <= 200:
        raise ValueError("seeds n must be a whole number in 1..200")
    if isinstance(jit, bool) or not isinstance(jit, (int, float)) or not 0 <= jit <= 5:
        raise ValueError("jitter_m must be a number in [0, 5]")
    mt = d.get("max_time_s", "auto")
    if mt != "auto" and (isinstance(mt, bool) or not isinstance(mt, (int, float)) or not 1 <= mt <= 600):
        raise ValueError("max_time_s must be \"auto\" or a number of seconds in [1, 600]")
    parse_criteria(d["criteria"])
    if not isinstance(d["worlds"], list) or not d["worlds"]:
        raise ValueError("worlds must be a non-empty list")
    base = os.path.dirname(os.path.abspath(path))
    worlds, names = [], set()
    for ref in d["worlds"]:
        name, doc = _load_world(ref, base, vk["radius"])
        wj.from_json(doc)                                  # validates, raises ValueError
        while name in names:
            name += "_"
        names.add(name)
        fam = doc.get("family", "custom")
        worlds.append({"ref": ref if isinstance(ref, str) else "inline", "name": name, "family": fam,
                       "max_time_s": float(bench.max_time(fam)) if mt == "auto" else float(mt), "doc": doc})
    return {"schema": SCHEMA, "name": d["name"], "description": d.get("description"), "file": path,
            "vehicle": presets.vehicle_spec(vspec), "vehicle_ref": vspec, "vehicle_kwargs": vk,
            "sensor": presets.describe_sensor(sspec), "sensor_ref": sspec, "sensor_name": sensor_name,
            "planners": planners, "seeds": n_seeds, "jitter_m": float(jit), "max_time_s": mt,
            "criteria": d["criteria"], "worlds": worlds}


# ------------------------------------------------------------ one flight
def fly(planner: str, w, wname: str, sensor_ref, sensor_name: str, vk: dict, t_max: float, index: int, seed: int):
    """bench.run_one's code, run with this world, vehicle, sensor and limit in its globals.
    run_one reads run.DEFAULTS, world_glass.make_any_world / nearest_material, presets.make_sensor
    and max_time(family) from module globals; those four are swapped, nothing else."""
    import bench
    real = bench.presets
    g = dict(bench.__dict__)
    g["run"] = types.SimpleNamespace(DEFAULTS=dict(bench.run.DEFAULTS, vehicle=dict(vk)))
    g["world_glass"] = types.SimpleNamespace(make_any_world=lambda *a, **k: w,
                                             nearest_material=bench.world_glass.nearest_material)
    g["presets"] = types.SimpleNamespace(make_sensor=lambda _name, rng: real.make_sensor(sensor_ref, rng))
    g["max_time"] = lambda _family: t_max
    run_one = types.FunctionType(bench.run_one.__code__, g, "run_one", bench.run_one.__defaults__)
    return run_one(planner, wname, sensor_name, index, seed)


def _task(t):
    import bench
    wj, WC = bench.A("world_json"), bench.A("worlds_complex")
    base = {"planner": t["planner"], "world": t["world"], "world_index": t["index"], "seed": t["seed"],
            "a": t["a"], "b": t["b"], "ab_kept": t["ab_kept"], "max_time_s": t["t_max"]}
    try:
        w = wj.from_json(t["doc"])
        free = bool(WC.has_free_path(w, t["vk"]["radius"]))
        r = fly(t["planner"], w, t["world"], t["sensor_ref"], t["sensor_name"], t["vk"], t["t_max"],
                t["index"], t["seed"])
        keep = ("outcome", "time_to_goal_s", "path_length_m", "min_clearance_m", "duration_s", "wall_s",
                "planner_ms_mean", "hit_material", "intervention_frac")
        return dict(base, free_path=free, error=None, **{k: r.get(k) for k in keep})
    except Exception as e:                                  # counted as a failed run, never dropped
        return dict(base, free_path=None, outcome="error", time_to_goal_s=None, path_length_m=None,
                    min_clearance_m=None, duration_s=None, wall_s=None, error=f"{type(e).__name__}: {e}")


def build_tasks(pack: dict) -> list:
    tasks = []
    for i, wd in enumerate(pack["worlds"]):
        for s in range(pack["seeds"]):
            j = seed_jitter(wd["doc"], s, pack["jitter_m"], pack["vehicle_kwargs"]["radius"])
            doc = dict(wd["doc"], a=j["a"], b=j["b"])
            for p in pack["planners"]:
                tasks.append({"planner": p, "world": wd["name"], "index": i, "seed": s, "doc": doc,
                              "a": j["a"], "b": j["b"], "ab_kept": [j["a_kept"], j["b_kept"]],
                              "t_max": wd["max_time_s"], "vk": pack["vehicle_kwargs"],
                              "sensor_ref": pack["sensor_ref"], "sensor_name": pack["sensor_name"]})
    return tasks


def run_pack(path: str, workers: int, out: str | None, argv) -> int:
    import bench
    try:
        pack = load_pack(path)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"bad pack {path}: {e}", file=sys.stderr)
        return 2
    tasks = build_tasks(pack)
    tasks.sort(key=lambda t: bench.SLOW.get(t["planner"], 9))     # slow planners first
    t0 = time.perf_counter()
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            recs = list(ex.map(_task, tasks, chunksize=1))
    else:
        recs = [_task(t) for t in tasks]
    wall = round(time.perf_counter() - t0, 1)
    order = {p: k for k, p in enumerate(pack["planners"])}
    recs.sort(key=lambda r: (order[r["planner"]], r["world_index"], r["seed"]))
    n_worlds = len(pack["worlds"])
    ev = evaluate(recs, pack["criteria"], pack["planners"], min_runs=pack["seeds"] * n_worlds, n_worlds=n_worlds)
    stem = out or os.path.join("results", f"pack_{pack['name']}")
    stem = stem[:-5] if stem.endswith(".json") else stem
    stem = stem if os.path.isabs(stem) else os.path.join(HERE, stem)
    os.makedirs(os.path.dirname(stem), exist_ok=True)
    cmd = "python pack.py " + " ".join(argv)
    no_path = sorted({(r["world"], r["seed"]) for r in recs if r.get("free_path") is False})
    meta = {"command": cmd, "input": "synthetic", "note": "SYNTHETIC SIMULATION, 2.5D point mass, scored on truth, "
            "planner sees the true pose. Not a flight result.", "pack_file": os.path.relpath(path, HERE),
            "workers": workers, "wall_s": wall, "n_runs": len(recs), "env": bench.env(),
            "date": time.strftime("%Y-%m-%d"),
            "pack": {k: v for k, v in pack.items() if k not in ("worlds", "file")},
            "worlds": [{k: v for k, v in wd.items() if k != "doc"} for wd in pack["worlds"]],
            "no_free_path_at_radius": [list(x) for x in no_path],
            "planner_inflation_note": "planners inflate by their own constants (0.15 m class); the pack radius "
                                      "changes the vehicle, the collision stop and the scoring only"}
    with open(stem + ".json", "w") as fh:
        json.dump(_finite({**meta, "evaluation": ev, "records": recs}), fh, indent=1, allow_nan=False)
    md = render_md(meta, pack, ev, recs)
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    print(table(ev, pack["criteria"]))
    print(f"wall {wall} s for {len(recs)} runs on {workers} workers; wrote {os.path.relpath(stem, HERE)}.json, .md")
    return ev["exit_code"]


def _finite(x):
    """JSON-safe copy: +-inf => "inf" / "-inf" (a quantile bound past the last run), nan => None."""
    if isinstance(x, float) and not math.isfinite(x):
        return None if math.isnan(x) else ("inf" if x > 0 else "-inf")
    if isinstance(x, dict):
        return {k: _finite(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_finite(v) for v in x]
    return x


def render_md(meta, pack, ev, recs) -> str:
    v = pack["vehicle"]
    s = pack["sensor"]
    out = [f"# Scenario pack `{pack['name']}`", "",
           f"`{meta['command']}` from samples/close-area-benchmark, {meta['date']}. Input: synthetic (simulated "
           "world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. "
           f"{meta['n_runs']} runs, {meta['workers']} worker processes, wall {meta['wall_s']} s, Python "
           f"{meta['env']['python']}, numpy {meta['env']['numpy']}.", "",
           "Worlds: " + "; ".join(f"`{w['name']}` ({w['ref']}, family {w['family']}, limit {w['max_time_s']:g} s)"
                                  for w in meta["worlds"]) + ".",
           f"Vehicle: radius {v['radius_m']} m, v_max {v['v_max']} m/s, a_max {v['a_max']} m/s^2, tau {v['tau']} s. "
           f"Sensor `{s['name']}`: {s['beams']} beams, fov {s['fov_deg']:g} deg, {s['min_range_m']}-{s['max_range_m']} m, "
           f"noise {s['noise_sigma_m']} m, cone {s['cone_deg']:.3g} deg, dropout {s['dropout']}.",
           f"Seeds 0-{pack['seeds'] - 1}: seed 0 exact A/B, seeds > 0 move A and B up to {pack['jitter_m']:g} m "
           "(same points for every planner).", ""]
    if meta["no_free_path_at_radius"]:
        out += ["No free path at the pack radius (world, seed): "
                + ", ".join(f"{w} s{k}" for w, k in meta["no_free_path_at_radius"]), ""]
    out += ["Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. "
            "\"Runs needed if every run succeeds\" is the smallest n whose all-success Wilson bound meets the bar. "
            "Counts: every run of that outcome counts; PASS needs at least min_runs distinct runs "
            f"(default seeds x worlds = {ev.get('min_runs_default')}). A count PASS says \"none (or at most k) "
            "happened in n runs\"; it is not a rate claim, the Wilson bound next to it is what n runs support. "
            "Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.", "",
            table(ev, pack["criteria"]), "", "## Outcomes", "",
            "| planner | runs | reached | collision | stuck | timeout | error |", "|---|---|---|---|---|---|---|"]
    for p in pack["planners"]:
        mine = [r for r in recs if r["planner"] == p]
        out.append(f"| {p} | {len(mine)} | " + " | ".join(str(sum(r['outcome'] == o for r in mine)) for o in OUTCOMES)
                   + " |")
    errs = [r for r in recs if r["outcome"] == "error"]
    if errs:
        out += ["", "Errors: " + "; ".join(f"{r['planner']} {r['world']} s{r['seed']}: {r['error']}" for r in errs[:10])]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------ seed-0 rows vs the matrix
def check_matrix(path: str) -> int:
    """Seed-0 runs on family worlds (preset:<family>_<i> or family:<family>:<i>) with a matrix preset and
    the default vehicle must equal results/matrix_0.json run by run (outcome and min clearance)."""
    d = json.load(open(path))
    m = json.load(open(os.path.join(HERE, "results", "matrix_0.json")))
    pk = d["pack"]
    if pk["sensor_name"] not in m["presets"] or pk["vehicle_kwargs"] != {"tau": 0.15, "a_max": 3.0, "v_max": 2.0,
                                                                          "radius": 0.15}:
        print("not comparable: sensor not a matrix preset or vehicle not the default")
        return 1
    ref = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in m["runs"]}
    fam_idx = {}
    for w in d["worlds"]:
        mm = re.fullmatch(r"(?:preset:([a-z_]+)_([0-9]+)|family:([a-z_]+):([0-9]+))", str(w["ref"]))
        if mm:
            fam_idx[w["name"]] = (mm.group(1) or mm.group(3), int(mm.group(2) or mm.group(4)))
    import bench
    near = exact = tot = 0
    lines = ["| planner | world | matrix outcome, min clearance m | pack run (world JSON, 0.1 mm) | "
             "fly() on the unrounded layout |", "|---|---|---|---|---|"]
    for r in d["records"]:
        if r["seed"] != 0 or r["world"] not in fam_idx:
            continue
        fam, idx = fam_idx[r["world"]]
        o = ref.get((r["planner"], fam, pk["sensor_name"], idx))
        if o is None:
            continue
        tot += 1
        # 1. the pack run flew the world JSON (coordinates rounded to 0.1 mm): same outcome, clearance within 0.2 mm
        ok1 = o["outcome"] == r["outcome"] and abs(o["min_clearance_m"] - r["min_clearance_m"]) <= CLEAR_TOL_M
        # 2. the same code path on the unrounded generator layout must be identical
        w = bench.world_glass.make_any_world(fam, 0, idx)
        f = fly(r["planner"], w, fam, pk["sensor_ref"], pk["sensor_name"], pk["vehicle_kwargs"], r["max_time_s"], idx, 0)
        ok2 = (f["outcome"], f["min_clearance_m"]) == (o["outcome"], o["min_clearance_m"])
        near += ok1
        exact += ok2
        lines.append(f"| {r['planner']} | {fam} #{idx} | {o['outcome']}, {o['min_clearance_m']} | {r['outcome']}, "
                     f"{r['min_clearance_m']} {'ok' if ok1 else 'DIFFERENT'} | {f['outcome']}, {f['min_clearance_m']} "
                     f"{'identical' if ok2 else 'DIFFERENT'} |")
    summary = (f"Pack runs vs matrix: {near}/{tot} same outcome with min clearance within {CLEAR_TOL_M * 1000:g} mm "
               f"(the world JSON rounds coordinates to 0.1 mm). fly() on the unrounded layouts: {exact}/{tot} "
               "identical outcome and min clearance.")
    md = [f"`python pack.py check-matrix {os.path.relpath(path, HERE)}`. Input: synthetic. Seed-0 runs of the pack "
          "(no jitter) on family layouts, against results/matrix_0.json (preset "
          f"{pk['sensor_name']}, same layout index).", "", summary, ""] + lines
    out = path[:-5] + "_matrix_check.md"
    with open(out, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(lines))
    print(summary)
    print(f"wrote {os.path.relpath(out, HERE)}")
    return 0 if tot and near == tot and exact == tot else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a pack and judge it")
    r.add_argument("pack")
    r.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    r.add_argument("--out", default=None, help="output stem (default results/pack_<name>)")
    c = sub.add_parser("check-matrix", help="seed-0 rows of a pack result vs results/matrix_0.json")
    c.add_argument("result")
    a = ap.parse_args(argv)
    if a.cmd == "check-matrix":
        return check_matrix(a.result)
    return run_pack(a.pack, a.workers, a.out, argv)


if __name__ == "__main__":
    raise SystemExit(main())
