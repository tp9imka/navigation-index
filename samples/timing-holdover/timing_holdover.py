"""GNSS-disciplined oscillator: holdover error per oscillator grade, and a slow
time-walk spoof caught by an internal steering monitor and a second time source.

Stdlib only. Run `python3 timing_holdover.py --help`.
"""
import argparse
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, field

SECONDS_PER_DAY = 86400.0
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY
SECONDS_PER_MONTH = SECONDS_PER_YEAR / 12.0


@dataclass(frozen=True)
class Grade:
    name: str
    adev_1s: float          # Allan deviation at tau = 1 s, modelled as white FM
    aging_per_s: float      # linear frequency drift, 1/s
    temp_spec: float        # fractional frequency change over the full temperature range
    source: str


# TCXO, OCXO, Rb: J. R. Vig, "Introduction to Quartz Frequency Standards", table 1
# (accuracy/aging/temperature/stability comparison). CSAC: Microchip SA65 datasheet
# DS00003478F (9/25): ADEV 3e-10 at 1 s, typical aging <9e-10/month, +/-3e-10 over temp.
GRADES = [
    Grade("TCXO", 1e-9, 5e-7 / SECONDS_PER_YEAR, 5e-7, "Vig table 1"),
    Grade("CSAC", 3e-10, 9e-10 / SECONDS_PER_MONTH, 3e-10, "Microchip SA65 DS00003478F"),
    Grade("OCXO", 1e-12, 5e-9 / SECONDS_PER_YEAR, 1e-9, "Vig table 1"),
    Grade("Rb", 3e-12, 2e-10 / SECONDS_PER_YEAR, 3e-10, "Vig table 1"),
]
GRADE_BY_NAME = {g.name: g for g in GRADES}

LOOP_DAMPING = 0.707
LOOP_TC_MIN_S = 30.0
LOOP_TC_MAX_S = 2000.0
ACQ_TC_S = 30.0            # fast-lock time constant used first, as many GPSDO firmwares do
ACQ_S = 1800.0
U_AVG_WINDOW_S = 600       # averaging window for the steering value
MONITOR_PERIOD_S = 60      # detectors evaluate once per minute
STEER_LOOKBACK_S = 1800    # internal monitor compares steering now vs this long ago
INTERNAL_K = 6.0           # internal monitor threshold, multiples of training RMS
INTERNAL_CONSEC = 3
CROSS_K = 6.0              # cross-source threshold, multiples of training std
CROSS_CONSEC = 2


@dataclass
class Config:
    sigma_pps: float = 20e-9      # GNSS 1PPS noise, 1 sigma (assumption, see README)
    sigma_net: float = 100e-9     # second time source (network PTP) noise, 1 sigma (assumption)
    net_bias: float = 300e-9      # constant path asymmetry of the second source (assumption)
    cross_margin: float = 100e-9  # extra allowance on the cross-source threshold (assumption)
    temp_fraction: float = 0.0    # fraction of temp_spec swung by a 24 h sinusoid
    holdover_dt: float = 10.0


def loop_time_constant(grade, sigma_pps, temp_fraction=0.0):
    """Crossover of white-PM GNSS noise (sqrt(3)*sigma/tau) and white-FM oscillator
    noise (adev_1s/sqrt(tau)), clamped to a practical range.

    A type-2 loop lags a frequency ramp by ramp * tc^2, so with a temperature term the
    time constant is also capped where that lag equals sigma_pps."""
    tc = (math.sqrt(3.0) * sigma_pps / grade.adev_1s) ** 2
    ramp = temp_fraction * grade.temp_spec * 2.0 * math.pi / SECONDS_PER_DAY
    if ramp > 0.0:
        tc = min(tc, math.sqrt(sigma_pps / ramp))
    return min(max(tc, LOOP_TC_MIN_S), LOOP_TC_MAX_S)


def oadev(phase, tau0, m):
    """Overlapping Allan deviation of phase samples (seconds) at tau = m * tau0."""
    n = len(phase)
    if n < 2 * m + 1:
        raise ValueError("not enough samples")
    acc = 0.0
    for i in range(n - 2 * m):
        d = phase[i + 2 * m] - 2.0 * phase[i + m] + phase[i]
        acc += d * d
    tau = m * tau0
    return math.sqrt(acc / (2.0 * tau * tau * (n - 2 * m)))


def free_run_phase(grade, seconds, dt, seed, temp_fraction=0.0):
    """Phase (local minus true time) of an undisciplined oscillator starting at zero offset."""
    rng = random.Random(seed)
    sig = grade.adev_1s * math.sqrt(dt)
    amp = temp_fraction * grade.temp_spec
    w = 2.0 * math.pi / SECONDS_PER_DAY
    x, t, out = 0.0, 0.0, [0.0]
    for _ in range(int(seconds / dt)):
        tm = t + 0.5 * dt
        y = grade.aging_per_s * tm + amp * math.sin(w * tm)
        x += y * dt + rng.gauss(0.0, sig)
        t += dt
        out.append(x)
    return out


@dataclass
class RunResult:
    grade: str
    te_at: dict = field(default_factory=dict)       # holdover: seconds into outage => TE (s)
    y_err_at_holdover: float = 0.0                   # frequency error at holdover start
    alarm_internal_s: float = None                   # seconds after spoof start (or after training if no spoof)
    alarm_cross_s: float = None
    te_end: float = 0.0
    te_locked_rms: float = 0.0


def run(grade, cfg, seed, *, settle_s, train_s=0.0, end_s, outage_at=None,
        checkpoints=(), spoof_at=None, spoof_rate=0.0, mitigate=False, monitor=True):
    """One simulation. Phase x is local clock minus true time (s).

    Discipline: type-2 PLL on the GNSS 1PPS phase error, frequency steering u.
    Holdover: u frozen. Detectors run after settle_s, train until settle_s + train_s.
    """
    rng = random.Random(seed)
    tc = loop_time_constant(grade, cfg.sigma_pps, cfg.temp_fraction)
    gains = [(2.0 * LOOP_DAMPING / c, 1.0 / (c * c)) for c in (ACQ_TC_S, tc)]
    amp = cfg.temp_fraction * grade.temp_spec
    w = 2.0 * math.pi / SECONDS_PER_DAY
    tphase = rng.uniform(0.0, 2.0 * math.pi)
    y0 = grade.aging_per_s * SECONDS_PER_YEAR * rng.choice((-1.0, 1.0))
    sig1 = grade.adev_1s

    res = RunResult(grade.name)
    x, f, u = 0.0, 0.0, 0.0
    t = 0.0
    u_hist = []                 # per-second u, for window averages
    u_avg_by_min = {}           # minute index => 600 s mean of u
    d_acc, d_n = 0.0, 0
    d_means_train, steer_train = [], []
    base_d = thr_d = thr_s = None
    consec_s = consec_d = 0
    holdover = False
    u_hold = 0.0
    hold_start = None
    locked_sq, locked_n = 0.0, 0
    cps = sorted(checkpoints)
    cp_i = 0

    def true_y(tm):
        return y0 + grade.aging_per_s * tm + amp * math.sin(w * tm + tphase)

    def enter_holdover(t_now, u_value):
        nonlocal holdover, u_hold, hold_start
        holdover, u_hold, hold_start = True, u_value, t_now
        res.y_err_at_holdover = true_y(t_now) + u_value

    while t < end_s - 1e-9:
        if outage_at is not None and not holdover and t >= outage_at:
            enter_holdover(t, statistics.fmean(u_hist[-U_AVG_WINDOW_S:]))
        dt = cfg.holdover_dt if (holdover and outage_at is not None) else 1.0
        if not holdover:
            spoof = spoof_rate * (t - spoof_at) if (spoof_at is not None and t > spoof_at) else 0.0
            z = x - spoof + rng.gauss(0.0, cfg.sigma_pps)
            kp, ki = gains[0] if t < ACQ_S else gains[1]
            f -= ki * z
            u = f - kp * z
            u_hist.append(u)
            if t >= settle_s:
                z_net = x + cfg.net_bias + rng.gauss(0.0, cfg.sigma_net)
                d_acc += z - z_net
                d_n += 1
                if spoof_at is None or t < spoof_at:
                    locked_sq += x * x
                    locked_n += 1
        tm = t + 0.5 * dt
        x += (true_y(tm) + (u_hold if holdover else u)) * dt + rng.gauss(0.0, sig1 * math.sqrt(dt))
        t += dt

        if holdover and outage_at is not None:
            while cp_i < len(cps) and t - hold_start >= cps[cp_i] - 1e-9:
                res.te_at[cps[cp_i]] = x
                cp_i += 1

        if not monitor or holdover or t < settle_s or int(round(t)) % MONITOR_PERIOD_S:
            continue
        minute = int(round(t)) // MONITOR_PERIOD_S
        u_avg_by_min[minute] = statistics.fmean(u_hist[-U_AVG_WINDOW_S:])
        d_mean = d_acc / d_n if d_n else 0.0
        d_acc, d_n = 0.0, 0
        back = u_avg_by_min.get(minute - STEER_LOOKBACK_S // MONITOR_PERIOD_S)
        steer = None if back is None else u_avg_by_min[minute] - back
        training = t <= settle_s + train_s
        if training:
            d_means_train.append(d_mean)
            if steer is not None:
                steer_train.append(steer)
            continue
        if base_d is None:
            base_d = statistics.fmean(d_means_train)
            thr_d = CROSS_K * statistics.pstdev(d_means_train) + cfg.cross_margin
            thr_s = (INTERNAL_K * math.sqrt(statistics.fmean(s * s for s in steer_train))
                     if steer_train else math.inf)
        ref = spoof_at if spoof_at is not None else settle_s + train_s
        consec_d = consec_d + 1 if abs(d_mean - base_d) > thr_d else 0
        consec_s = consec_s + 1 if (steer is not None and abs(steer) > thr_s) else 0
        if consec_d >= CROSS_CONSEC and res.alarm_cross_s is None:
            res.alarm_cross_s = t - ref
        if consec_s >= INTERNAL_CONSEC and res.alarm_internal_s is None:
            res.alarm_internal_s = t - ref
        if mitigate and (res.alarm_cross_s is not None or res.alarm_internal_s is not None):
            safe = u_avg_by_min.get(minute - STEER_LOOKBACK_S // MONITOR_PERIOD_S, u_avg_by_min[minute])
            enter_holdover(t, safe)

    res.te_end = x
    res.te_locked_rms = math.sqrt(locked_sq / locked_n) if locked_n else 0.0
    return res


def pct(values, q):
    v = sorted(values)
    k = (len(v) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def analytic_te(grade, t, y_err=0.0, temp_fraction=0.0):
    """|y_err|*t + D*t^2/2 + adev_1s*sqrt(t) (+ worst-case temperature term amp*t)."""
    temp = temp_fraction * grade.temp_spec * t
    return abs(y_err) * t + 0.5 * grade.aging_per_s * t * t + grade.adev_1s * math.sqrt(t) + temp


HOLDOVER_CHECKPOINTS = (60, 600, 3600, 4 * 3600, 24 * 3600)


def holdover_study(cfg, runs, settle_s=6 * 3600, seed=1):
    out = {}
    for g in GRADES:
        te = {c: [] for c in HOLDOVER_CHECKPOINTS}
        yerr, locked = [], []
        for k in range(runs):
            r = run(g, cfg, seed * 1000 + k, settle_s=settle_s - 3600, end_s=settle_s + HOLDOVER_CHECKPOINTS[-1],
                    outage_at=settle_s, checkpoints=HOLDOVER_CHECKPOINTS, monitor=False)
            for c in HOLDOVER_CHECKPOINTS:
                te[c].append(abs(r.te_at[c]))
            yerr.append(abs(r.y_err_at_holdover))
            locked.append(r.te_locked_rms)
        med_y = statistics.median(yerr)
        out[g.name] = {
            "loop_tc_s": loop_time_constant(g, cfg.sigma_pps, cfg.temp_fraction),
            "locked_te_rms_ns": statistics.median(locked) * 1e9,
            "y_err_at_holdover_median": med_y,
            "te_median_us": {c: statistics.median(te[c]) * 1e6 for c in HOLDOVER_CHECKPOINTS},
            "te_p95_us": {c: pct(te[c], 0.95) * 1e6 for c in HOLDOVER_CHECKPOINTS},
            "analytic_floor_us": {c: analytic_te(g, c) * 1e6 for c in HOLDOVER_CHECKPOINTS},
            "analytic_with_yerr_us": {c: analytic_te(g, c, med_y, cfg.temp_fraction) * 1e6
                                      for c in HOLDOVER_CHECKPOINTS},
        }
    return out


SPOOF_SETTLE_S = 2 * 3600
SPOOF_TRAIN_S = 2 * 3600
SPOOF_DURATION_S = 2 * 3600


def spoof_study(cfg, rates, control_runs, seed=1):
    start = SPOOF_SETTLE_S + SPOOF_TRAIN_S
    end = start + SPOOF_DURATION_S
    out = {}
    for g in GRADES:
        rows = []
        for rate_ns in rates:
            kw = dict(settle_s=SPOOF_SETTLE_S, train_s=SPOOF_TRAIN_S, end_s=end,
                      spoof_at=start, spoof_rate=rate_ns * 1e-9)
            followed = run(g, cfg, seed, mitigate=False, **kw)
            guarded = run(g, cfg, seed, mitigate=True, **kw)
            rows.append({
                "rate_ns_per_s": rate_ns,
                "alarm_internal_s": followed.alarm_internal_s,
                "alarm_cross_s": followed.alarm_cross_s,
                "te_end_unguarded_us": abs(followed.te_end) * 1e6,
                "te_end_guarded_us": abs(guarded.te_end) * 1e6,
            })
        fa_int = fa_cross = 0
        for k in range(control_runs):
            c = run(g, cfg, seed * 7919 + k, settle_s=SPOOF_SETTLE_S, train_s=SPOOF_TRAIN_S, end_s=end)
            fa_int += c.alarm_internal_s is not None
            fa_cross += c.alarm_cross_s is not None
        out[g.name] = {"rows": rows, "control_runs": control_runs,
                       "false_alarm_internal": fa_int, "false_alarm_cross": fa_cross}
    return out


def fmt_s(v):
    return "-" if v is None else f"{v:.0f}"


def fmt_us(v):
    if v >= 1000:
        return f"{v / 1000:.2f} ms"
    if v >= 1:
        return f"{v:.2f} us"
    return f"{v * 1000:.1f} ns"


def print_holdover(title, res):
    labels = ["1 min", "10 min", "1 h", "4 h", "24 h"]
    print(f"\n{title}")
    print(f"{'grade':<6} {'loop tc':>8} {'locked rms':>11} {'y_err@HO':>9} | "
          + " | ".join(f"{l:>17}" for l in labels))
    for name, r in res.items():
        cells = [f"{fmt_us(r['te_median_us'][c]):>8}/{fmt_us(r['te_p95_us'][c]):>8}" for c in HOLDOVER_CHECKPOINTS]
        print(f"{name:<6} {r['loop_tc_s']:>7.0f}s {r['locked_te_rms_ns']:>8.1f} ns {r['y_err_at_holdover_median']:>9.1e} | "
              + " | ".join(cells))
    print("cells: median / 95th percentile |time error| after the GNSS outage starts")
    print("analytic |y_err|*t + D*t^2/2 + adev1*sqrt(t) (+ temp) with the median y_err:")
    for name, r in res.items():
        print(f"  {name:<6} " + "  ".join(f"{l}={fmt_us(r['analytic_with_yerr_us'][c])}"
                                        for l, c in zip(labels, HOLDOVER_CHECKPOINTS)))


def print_spoof(res, cfg):
    print(f"\nSlow time-walk spoof: settle {SPOOF_SETTLE_S // 3600} h, detector training {SPOOF_TRAIN_S // 3600} h, "
          f"walk for {SPOOF_DURATION_S // 3600} h; temp_fraction={cfg.temp_fraction}")
    print(f"second source: sigma {cfg.sigma_net * 1e9:.0f} ns, unknown bias {cfg.net_bias * 1e9:.0f} ns")
    print(f"{'grade':<6} {'walk ns/s':>9} {'internal alarm s':>17} {'cross alarm s':>14} "
          f"{'TE end, follows':>16} {'TE end, guarded':>16}")
    for name, r in res.items():
        for row in r["rows"]:
            print(f"{name:<6} {row['rate_ns_per_s']:>9g} {fmt_s(row['alarm_internal_s']):>17} "
                  f"{fmt_s(row['alarm_cross_s']):>14} {fmt_us(row['te_end_unguarded_us']):>16} "
                  f"{fmt_us(row['te_end_guarded_us']):>16}")
        print(f"{name:<6} no-spoof control: false alarms internal {r['false_alarm_internal']}/{r['control_runs']}, "
              f"cross {r['false_alarm_cross']}/{r['control_runs']}")
    print("alarm times are seconds after the walk starts; '-' = no alarm in the window")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=int, default=20, help="Monte Carlo runs per grade for holdover")
    p.add_argument("--rates", type=float, nargs="+", default=[0.5, 2.0, 10.0], help="spoof walk rates, ns/s")
    p.add_argument("--control-runs", type=int, default=5)
    p.add_argument("--temp-fraction", type=float, default=0.1,
                   help="fraction of the temperature spec swung daily, for the second holdover table and the spoof study")
    p.add_argument("--sigma-pps", type=float, default=20.0, help="GNSS 1PPS noise, ns")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--json", help="write all results to this JSON file")
    a = p.parse_args(argv)

    base = Config(sigma_pps=a.sigma_pps * 1e-9)
    warm = Config(sigma_pps=a.sigma_pps * 1e-9, temp_fraction=a.temp_fraction)
    print("grades: " + ", ".join(f"{g.name} adev(1s)={g.adev_1s:g} aging={g.aging_per_s * SECONDS_PER_YEAR:.2g}/yr "
                                 f"temp={g.temp_spec:g} [{g.source}]" for g in GRADES))
    h0 = holdover_study(base, a.runs, seed=a.seed)
    print_holdover(f"Holdover after 6 h of GNSS discipline, {a.runs} runs, no temperature term", h0)
    h1 = holdover_study(warm, a.runs, seed=a.seed)
    print_holdover(f"Holdover, temperature term {a.temp_fraction} of spec over a 24 h cycle", h1)
    sp = spoof_study(warm, a.rates, a.control_runs, seed=a.seed)
    print_spoof(sp, warm)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"holdover_no_temp": h0, "holdover_temp": h1, "spoof": sp}, f, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
