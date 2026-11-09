"""H3: selective identification in a one-axis drag measurement model.

a = -k * (v_ground - wind) + bias = -k*v_ground + c.
Only k and the composite c = k*wind+bias are identifiable from these data.
The code NEVER claims to estimate wind and bias separately.
"""
import math
import random

POLICIES = ("fixed", "calibrate_once", "always", "selective", "no_excitation_gate", "no_reference_gate")
SCENARIOS = ("nominal", "no_excitation", "reference_outage", "parameter_change", "nonlinear_drag", "unobserved_change")


def fit_window(window, minimum_variance=0.0):
    if len(window) < 8:
        return None
    velocities, accelerations = zip(*window)
    mean_v = sum(velocities) / len(window)
    mean_a = sum(accelerations) / len(window)
    excitation = sum((v - mean_v) ** 2 for v in velocities) / len(window)
    if excitation < max(1e-8, minimum_variance):
        return None
    slope = sum((v - mean_v) * (a - mean_a) for v, a in window) / (len(window) * excitation)
    k = -slope
    c = mean_a + k * mean_v
    if not 0.05 <= k <= 2.0:
        return None
    return k, c


def run(seed, scenario, policy, gate=0.3, trace=False):
    rng = random.Random(seed)
    phase = rng.uniform(0, 2 * math.pi)
    accel_noise = [rng.gauss(0, 0.06) for _ in range(240)]
    ref_noise = [rng.gauss(0, 0.04) for _ in range(240)]
    k_est, c_est = 0.35, 0.0
    window = []
    errors = []
    history = []
    updates = 0
    pos_error = 0.0
    for t in range(240):
        # Alternating calibration and weak-excitation cruise windows.
        excited = t < 60 or 100 <= t < 150
        if scenario == "no_excitation":
            excited = False
        velocity = 5 + (2 * math.sin(0.22 * t + phase) if excited else 0.03 * math.sin(0.2 * t))
        k_true = 0.55 if scenario != "parameter_change" or t < 100 else 0.8
        if scenario == "unobserved_change" and t >= 180:
            k_true = 0.8
        # Wind/bias composite changes during low-excitation cruise; cannot
        # attribute a changing intercept to wind vs bias with this sensor set.
        c_true = 0.8 + (0.25 * math.sin(0.09 * t) if not excited else 0)
        a = -k_true * velocity + c_true + accel_noise[t]
        if scenario == "nonlinear_drag":
            a -= 0.025 * velocity * abs(velocity)
        # Reference absent during final evaluation and sometimes calibration.
        reference_available = t < 160 and not (scenario == "reference_outage" and 35 <= t < 140)
        reference = velocity + ref_noise[t] if reference_available else None
        predicted_velocity = (c_est - a) / k_est
        # Baselines show the failure caused by training on one's own prediction.
        used_velocity = reference if reference is not None else predicted_velocity
        if policy == "calibrate_once":
            # Strong conventional baseline: calibrate from the initial reference
            # window, freeze afterwards. No availability/ground-truth oracle.
            if t < 60 and reference is not None:
                window.append((reference, a))
            if t == 59:
                fitted = fit_window(window)
                if fitted:
                    k_est, c_est = fitted
                    updates += 1
        elif policy != "fixed":
            trust_reference = policy in ("selective", "no_excitation_gate")
            if reference is None and trust_reference:
                window.clear()  # no stale pre-outage identification window
            else:
                window.append((used_velocity, a))
                window = window[-24:]
                threshold = gate if policy in ("selective", "no_reference_gate") else 0
                fitted = fit_window(window, threshold)
                if fitted:
                    k_est, c_est = fitted
                    updates += 1
        estimate = (c_est - a) / k_est
        # Score only the 80-second held-out reference-free tail. Updates never
        # see truth; the evaluator does. The plant keeps evolving during it.
        if t >= 160:
            errors.append(estimate - velocity)
            pos_error += estimate - velocity
        history.append({"t": t, "reference_available": reference_available, "velocity": velocity,
                        "estimate": estimate, "k": k_est, "c": c_est})
    result = {"velocity_rmse": math.sqrt(sum(e * e for e in errors) / len(errors)),
              "position_error": abs(pos_error), "updates": updates,
              "k_error": abs(k_est - k_true)}
    if trace:
        result["trace"] = history
    return result
