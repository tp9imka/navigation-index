"""Scoring: error at along-track distance checkpoints, robust summaries, divergence. Stdlib only."""
import bisect
import math

CHECKPOINTS_M = (5_000.0, 10_000.0, 20_000.0)
DIVERGED_M = 500.0   # error at the last checkpoint above this counts as a lost track


def error_at_distances(s, e_true, n_true, e_est, n_est, checkpoints=CHECKPOINTS_M):
    """Horizontal error at the first epoch whose truth along-track distance reaches each checkpoint.

    s must be non-decreasing. A checkpoint beyond the end of the flight yields NaN.
    """
    s = [float(x) for x in s]
    out = []
    for d in checkpoints:
        k = bisect.bisect_left(s, d)
        if k < len(s):
            out.append(math.hypot(float(e_est[k]) - float(e_true[k]), float(n_est[k]) - float(n_true[k])))
        else:
            out.append(float("nan"))
    return out


def percentile(values, q):
    """Linear interpolation between closest ranks (numpy's default method)."""
    v = sorted(values)
    if not v:
        return float("nan")
    pos = (len(v) - 1) * q / 100.0
    lo = math.floor(pos)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def summarize(values):
    v = [float(x) for x in values if math.isfinite(float(x))]
    if not v:
        return {"n": 0, "median": float("nan"), "p95": float("nan")}
    return {"n": len(v), "median": percentile(v, 50), "p95": percentile(v, 95)}


def divergence_rate(final_errors, threshold=DIVERGED_M):
    v = [float(x) for x in final_errors if math.isfinite(float(x))]
    return sum(x > threshold for x in v) / len(v) if v else float("nan")
