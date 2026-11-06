"""Real MILUV two-way-ranging error vs the synthetic UWB model of samples/swarm-coop-localization."""
import math
import statistics

import adapter  # noqa: F401  (puts the sim sample on sys.path)
import miluv_io as io
from sim import Config, generate

GROUND_Z = 0.3            # m, mocap z below which a drone counts as on the ground
TAIL_THRESHOLDS = (0.3, 0.5, 1.0, 2.0, 5.0)


def quantile(sorted_v, q):
    if not sorted_v:
        return float("nan")
    k = (len(sorted_v) - 1) * q
    lo = int(math.floor(k))
    hi = min(lo + 1, len(sorted_v) - 1)
    return sorted_v[lo] + (sorted_v[hi] - sorted_v[lo]) * (k - lo)


def describe(errs):
    v = sorted(errs)
    n = len(v)
    med = quantile(v, 0.5)
    mad = quantile(sorted(abs(x - med) for x in v), 0.5)
    d = {"n": n, "mean": statistics.fmean(v), "sd": statistics.pstdev(v), "robust_sd": 1.4826 * mad,
         "p1": quantile(v, 0.01), "p5": quantile(v, 0.05), "median": med, "p95": quantile(v, 0.95),
         "p99": quantile(v, 0.99), "min": v[0], "max": v[-1]}
    for th in TAIL_THRESHOLDS:
        d[f"gt{th}"] = sum(1 for x in v if x > th) / n
    d["lt-0.3"] = sum(1 for x in v if x < -0.3) / n
    return d


def real_errors(exp, data_dir=io.DATA_DIR):
    """Errors (range - mocap truth) split by link type and flight phase."""
    tracks = {r: io.load_track(exp, r, data_dir) for r in io.ROBOTS}
    out = {}
    for m in io.load_ranges(exp, data_dir):
        robots = [io.TAG_ROBOT[x] for x in (m.frm, m.to) if not io.is_anchor(x)]
        if len(robots) == 2 and robots[0] == robots[1]:
            kind = "intra"
        else:
            kind = "inter" if len(robots) == 2 else "anchor"
        zs = [tracks[r].at(m.t) for r in robots]
        if any(z is None for z in zs):
            continue
        phase = "air" if all(p[2] > GROUND_Z for p in zs) else "ground"
        out.setdefault((kind, phase, "cal"), []).append(m.r - m.gt)
        out.setdefault((kind, phase, "raw"), []).append(m.r_raw - m.gt)
    return out


def sim_errors(seed=1):
    """Errors of the sim's own UWB draws (sim.generate, default Config): range - true distance."""
    cfg = Config(seed=seed)
    _, epochs = generate(cfg)
    return [m.r - math.dist(ep.truth[m.i], ep.truth[m.j]) for ep in epochs for m in ep.ranges]


ROW_FMT = "{:34s}{:>7d}{:>8.3f}{:>7.3f}{:>8.3f}{:>8.3f}{:>8.3f}{:>8.3f}{:>8.3f}{:>7.1f}{:>7.1f}{:>7.1f}{:>7.2f}{:>7.2f}"
HDR = (f"{'source':34s}{'n':>7s}{'mean':>8s}{'sd':>7s}{'rob sd':>8s}{'p1':>8s}{'median':>8s}{'p99':>8s}{'max':>8s}"
       f"{'>0.3%':>7s}{'>0.5%':>7s}{'>1m%':>7s}{'>2m%':>7s}{'>5m%':>7s}")


def row(name, d):
    return ROW_FMT.format(name, d["n"], d["mean"], d["sd"], d["robust_sd"], d["p1"], d["median"], d["p99"], d["max"],
                          100 * d["gt0.3"], 100 * d["gt0.5"], 100 * d["gt1.0"], 100 * d["gt2.0"], 100 * d["gt5.0"])
