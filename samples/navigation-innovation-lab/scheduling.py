"""H2: asynchronous fixes on a synthetic route with localization tolerances.

Position error is estimator error, NOT physical cross-track motion. A violation
means an error tolerance was exceeded, not a collision. No real-time claims.
"""
import math
import random

POLICIES = ("periodic", "threshold", "opportunity", "predictive", "predictive_speed", "no_latency")
SCENARIOS = ("nominal", "slow_compute", "unexpected_blackout", "biased_odometry")
DT = 0.5
LENGTH = 120.0
Q = 0.12
R = 0.16
BUDGET = 10


def tolerance(x):
    return 1.8 if 42 <= x <= 58 or 92 <= x <= 105 else 6.0


def match_probability(x):
    return 0.12 if 48 <= x <= 80 else 0.95


def fuse_delayed(error, variance, captured_error, captured_variance, noise):
    gain = captured_variance / (captured_variance + R)
    # Correct the captured state and propagate its correction to the present.
    return error - gain * (captured_error + noise), max(1e-9, variance - gain * captured_variance)


def predicted_risk(x, variance, speed, steps=16):
    # Simple risk proxy; not a calibrated protection level or probability bound.
    return max(2 * math.sqrt(variance + Q * DT * j)
               / tolerance(min(LENGTH, x + speed * DT * j)) for j in range(1, steps + 1))


def decision(policy, x, variance, age, busy, remaining, latency, setting):
    speed = 2.5
    if policy == "predictive_speed" and predicted_risk(x, variance, speed) > 1:
        speed = 1.25
    if busy or remaining <= 0:
        return False, speed
    if policy == "periodic":
        return age >= setting, speed
    if policy == "threshold":
        return math.sqrt(variance) >= setting, speed
    if policy == "opportunity":
        closing = match_probability(x) > 0.8 and match_probability(x + speed * (latency + 4)) < 0.3
        return (age >= setting or closing) and match_probability(x) > 0.3, speed
    delay = 0 if policy == "no_latency" else latency
    # Evaluate uncertainty when a result could arrive, plus the following route.
    x_arrival = min(LENGTH, x + speed * delay)
    risk = predicted_risk(x_arrival, variance + Q * delay, speed)
    # Capture before entering predicted poor imagery rather than after it.
    opportunity_closing = match_probability(x) > 0.8 and match_probability(x + speed * (delay + 4)) < 0.3
    return (risk > setting or opportunity_closing) and match_probability(x) > 0.3, speed


def run(seed, scenario, policy, setting=1.0, trace=False):
    rng = random.Random(seed)
    # Time-indexed disturbances; policies cannot advance the generator by asking
    # for more fixes. Arrival noise/outcomes are capture-time indexed too.
    process = [rng.gauss(0, math.sqrt(Q * DT)) for _ in range(240)]
    measurement = [rng.gauss(0, math.sqrt(R)) for _ in range(240)]
    outcomes = [rng.random() for _ in range(240)]
    jitter = [rng.random() for _ in range(240)]
    latency_hint = 4.0 if scenario == "slow_compute" else 2.0
    x = error = 0.0
    variance = 0.16
    age = 1000.0
    pending = None
    used = delivered = violations = 0
    errors = []
    history = []
    for k in range(240):
        now = k * DT
        if pending is not None and now >= pending["arrival"]:
            if pending["valid"]:
                error, variance = fuse_delayed(error, variance, pending["error"], pending["variance"], pending["noise"])
                delivered += 1
            pending = None
        request, speed = decision(policy, x, variance, age, pending is not None,
                                  BUDGET - used, latency_hint, setting)
        if request:
            probability = match_probability(x)
            if scenario == "unexpected_blackout" and 20 < x < 95:
                probability = 0.0  # hidden mismatch, not given to the policy
            latency = latency_hint + 2 * jitter[k]
            pending = {"arrival": now + latency, "error": error, "variance": variance,
                       "noise": measurement[k], "valid": outcomes[k] < probability}
            used += 1
            age = 0
        x = min(LENGTH, x + speed * DT)
        error += process[k] + (0.09 * DT if scenario == "biased_odometry" else 0)
        variance += Q * DT
        age += DT
        errors.append(error)
        violations += abs(error) > tolerance(x)
        history.append({"t": now + DT, "x": x, "error": error, "sigma": math.sqrt(variance),
                        "tolerance": tolerance(x), "requested": request, "speed": speed})
        if x >= LENGTH:
            break
    result = {"success": int(x >= LENGTH and violations == 0),
              "violation_fraction": violations / len(errors),
              "rmse": math.sqrt(sum(e * e for e in errors) / len(errors)),
              "requests": used, "delivered": delivered, "duration": len(errors) * DT}
    if trace:
        result["trace"] = history
    return result
