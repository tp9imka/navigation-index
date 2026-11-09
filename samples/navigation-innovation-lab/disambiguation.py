"""H1: closed-loop, synthetic descriptor-level active localization.

No imagery, autopilot or six-DoF dynamics. Policies see the candidate map and
observations, never the hidden true candidate or future observation noise.
"""
import math
import random

POLICIES = ("passive", "texture", "information", "efficient", "no_unknown")
SCENARIOS = ("nominal", "indistinguishable", "missing_truth", "map_shift")
SIGMA = 0.25
ACTIONS = ((1.0, 0.0), (0.6, 0.8), (0.6, -0.8), (0.0, 1.0), (0.0, -1.0))


def descriptor(h, x, y, phase, indistinguishable=False):
    common = 0.5 * math.sin(0.35 * x + phase)
    if indistinguishable:
        return common
    # Repeated forward corridor, lateral distinctive structure, and a landmark
    # after x=10. Constructed mechanism test, not a learned image descriptor.
    separation = math.sin(0.55 * y) + max(0.0, x - 10.0) * 0.25
    return common + (h - 1) * separation


def safe_actions(x, y):
    # Intersection of allowed regions for ALL three location hypotheses.
    # One candidate has a narrow initial corridor. No true-pose safety oracle.
    return [a for a in ACTIONS if x + a[0] <= 18 and abs(y + a[1]) <= 3
            and not (x + a[0] < 3 and abs(y + a[1]) > 1)]


def posterior(prior, means, z, use_unknown=True):
    likelihood = [math.exp(-0.5 * ((z - m) / SIGMA) ** 2)
                  / (SIGMA * math.sqrt(2 * math.pi)) for m in means]
    # Heavy-tailed unknown model: avoids a finite-support all-zero likelihood.
    likelihood.append(1 / (math.pi * 4 * (1 + (z / 4) ** 2)) if use_unknown else 0)
    weights = [p * l for p, l in zip(prior, likelihood)]
    total = sum(weights)
    return [w / total for w in weights] if total > 1e-300 else [0, 0, 0, 1]


def entropy(p):
    return -sum(v * math.log(v) for v in p if v > 0)


def information_gain(prior, means):
    # Deterministic three-point quadrature of known-mode observation outcomes.
    # The unknown mode is a rejection mechanism, not an informative map model.
    mass = sum(prior[:3])
    if mass < 1e-12:
        return 0.0
    p = [v / mass for v in prior[:3]] + [0]
    expected = 0.0
    for i, mean in enumerate(means):
        for offset, weight in ((-math.sqrt(3), 1 / 6), (0, 2 / 3), (math.sqrt(3), 1 / 6)):
            expected += p[i] * weight * entropy(posterior(p, means, mean + offset * SIGMA, False))
    return max(0.0, entropy(p) - expected)


def choose_action(policy, prior, x, y, phase, indistinguishable, cost_weight=0.12):
    actions = safe_actions(x, y)
    if not actions:
        return None
    if policy == "passive":
        return max(actions, key=lambda a: a[0])
    if policy == "texture":
        return max(actions, key=lambda a: (5 - abs(y + a[1]), a[0]))
    def score(a):
        means = [descriptor(h, x + a[0], y + a[1], phase, indistinguishable) for h in range(3)]
        gain = information_gain(prior, means)
        # Raw expected-information baseline gets exactly the same action set.
        if policy == "information":
            return gain
        return gain - cost_weight * (1 - a[0])
    return max(actions, key=score)


def run(seed, scenario, policy, cost_weight=0.12, trace=False):
    rng = random.Random(seed)
    truth = rng.randrange(3)
    phase = rng.uniform(-math.pi, math.pi)
    # Precomputed exogenous observation errors shared by all policies per seed.
    noise = [rng.gauss(0, SIGMA) for _ in range(24)]
    prior = [0.95 / 3] * 3 + [0.05]
    if policy == "no_unknown":
        prior = [1 / 3] * 3 + [0]
    x = y = distance = 0.0
    accepted = None
    history = []
    for step in range(24):
        a = choose_action(policy, prior, x, y, phase, scenario == "indistinguishable", cost_weight)
        if a is None:
            break
        x, y = x + a[0], y + a[1]
        distance += math.hypot(*a)
        means = [descriptor(h, x, y, phase, scenario == "indistinguishable") for h in range(3)]
        z = means[truth] + noise[step]
        if scenario == "missing_truth":
            z += 5.0
        elif scenario == "map_shift":
            z += 0.65 * math.sin(x * 0.2 + 0.7)
        prior = posterior(prior, means, z, policy != "no_unknown")
        history.append({"step": step + 1, "x": x, "y": y, "belief": prior[:], "observation": z})
        if max(prior[:3]) > 0.98:
            accepted = max(range(3), key=prior.__getitem__)
            break
        if prior[3] > 0.98:
            break
    correct = accepted is not None and accepted == truth and scenario != "missing_truth"
    result = {"success": int(correct), "false_accept": int(accepted is not None and not correct),
              "abstain": int(accepted is None), "steps": len(history), "distance": distance,
              "forward_progress": x}
    if trace:
        result["trace"] = history
    return result
