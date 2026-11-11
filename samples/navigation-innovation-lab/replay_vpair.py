#!/usr/bin/env python3
"""H2 follow-up: causal request scheduling on cached real VPAIR observations.

One previously processed flight; artificial frame delays and covariance model.
No GPU rerun, physical-time latency claim, or changed-flight counterfactual.
"""
import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "e2e-visual-nav-vpair" / "results"
R_EARTH = 6378137.0
POLICIES = ("vo_only", "periodic", "threshold", "predictive")


def solve(matrix, rhs):
    """Small pivoted linear solve; fail instead of inventing a singular fit."""
    a = [list(row) + [value] for row, value in zip(matrix, rhs)]
    n = len(rhs)
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-12:
            raise ValueError("singular calibration")
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [v / scale for v in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x - scale * y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


def read_track(path, origin=None):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows = [r for r in rows if "t" in r]
    if len({r["t"] for r in rows}) != len(rows):
        raise ValueError("duplicate frame index")
    if any(b["t"] <= a["t"] for a, b in zip(rows, rows[1:])):
        raise ValueError("non-monotonic frame index")
    lat0, lon0 = origin or (rows[0]["lat"], rows[0]["lon"])
    points = {int(r["t"]): (math.radians(r["lon"] - lon0) * R_EARTH * math.cos(math.radians(lat0)),
                            math.radians(r["lat"] - lat0) * R_EARTH) for r in rows}
    return points, (lat0, lon0)


def strict(match):
    return match.get("p_tile") is not None and match["inliers"] >= 25 and 0.67 <= match["h_scale"] <= 1.5


def features(frontend, match):
    c = frontend["tiles"]["centre_px"]
    # Scale features to kilometres to condition the small normal equations.
    return [match["depth"] * (match["p_tile"][i] - c[i]) / 1000 for i in range(2)] + [1.0]


def calibrate(frontend, calibration_truth):
    """Only known-reference frames 0..9 may influence the pixel-to-map fit."""
    if any(k >= 10 for k in calibration_truth):
        raise ValueError("calibration must not receive evaluation truth")
    inputs, outputs = [], []
    tiles = frontend["tiles"]
    for key, match in frontend["matches"].items():
        k, j = map(int, key.split(":"))
        if k not in calibration_truth or j >= tiles["n_renders"] or abs(j - k) > 2 or j == k or not strict(match):
            continue
        inputs.append(features(frontend, match))
        outputs.append([calibration_truth[k][axis] - tiles["en"][j][axis] for axis in range(2)])
    gram = [[sum(x[i] * x[j] for x in inputs) for j in range(3)] for i in range(3)]
    coefficients = [solve(gram, [sum(x[i] * y[axis] for x, y in zip(inputs, outputs))
                                for i in range(3)]) for axis in range(2)]
    return coefficients, len(inputs)


def cached_fix(frontend, coefficients, frame, stride):
    """Read matching outcomes only after the policy requests this frame."""
    query = frontend["queries"][frame]
    candidates = query["top"][str(stride)]
    matches = [(j, frontend["matches"][f"{frame}:{j}"]) for j, _ in candidates]
    cost = sum(m["t_s"] for _, m in matches)
    cost += frontend["timing"]["prep_query_s"]["median_s"] + frontend["timing"]["describe_query_s"]["median_s"]
    for j, match in matches:  # retrieval rank, never truth error or inlier oracle
        if strict(match):
            x = features(frontend, match)
            p = tuple(frontend["tiles"]["en"][j][axis] + sum(a * b for a, b in zip(coefficients[axis], x))
                      for axis in range(2))
            return p, cost
    return None, cost


def request(policy, variance, age, latency, successes, completed, q):
    if policy == "vo_only":
        return False
    if policy == "periodic":
        return age >= 5
    if policy == "threshold":
        return 3 * math.sqrt(variance) >= 25
    # Beta(1,1) success-rate estimate uses COMPLETED past jobs only.
    probability = (successes + 1) / (completed + 2)
    return 3 * math.sqrt(variance + q * (latency + 1 / probability)) >= 25


def replay(frontend, coefficients, vo, policy, stride, delay_frames, q, budget=40):
    # Truth is deliberately absent from this function's signature.
    variance = 4.0
    offset = [0.0, 0.0]
    pending = None
    age = 1000
    sent = completed = matches = accepted = rejected = 0
    historical_compute = 0.0
    trace = []
    for k in sorted(i for i in vo if i >= 10):
        variance += q if k > 10 else 0
        # A zero-delay request is delivered in the capture frame; other jobs at
        # their specified frame. At most one outstanding request.
        def deliver(job):
            nonlocal variance, offset, completed, matches, accepted, rejected
            completed += 1
            if job["fix"] is None:
                return
            matches += 1
            residual = [job["fix"][i] - job["predicted"][i] for i in range(2)]
            measurement_variance = 25.0
            if sum(v * v for v in residual) / (job["variance"] + measurement_variance) > 13.816:
                rejected += 1
                return
            gain = job["variance"] / (job["variance"] + measurement_variance)
            offset = [offset[i] + gain * residual[i] for i in range(2)]
            variance = max(1e-9, variance - gain * job["variance"])
            accepted += 1
        if pending and pending["arrival"] <= k:
            deliver(pending)
            pending = None
        sent_now = False
        if pending is None and sent < budget and request(policy, variance, age, delay_frames, matches, completed, q):
            fix, cost = cached_fix(frontend, coefficients, k, stride)
            pending = {"arrival": k + delay_frames, "fix": fix, "variance": variance,
                       "predicted": [vo[k][i] + offset[i] for i in range(2)]}
            sent += 1
            historical_compute += cost
            age = 0
            sent_now = True
            if delay_frames == 0:
                deliver(pending)
                pending = None
        trace.append({"frame": k, "estimate": [vo[k][i] + offset[i] for i in range(2)],
                      "sigma_proxy": math.sqrt(variance), "request": sent_now, "accepted_total": accepted})
        age += 1
    return {"requests": sent, "completed": completed, "matches": matches, "accepted": accepted,
            "rejected": rejected, "historical_frontend_seconds": historical_compute, "trace": trace}


def score(trace, truth):
    errors = [math.dist(r["estimate"], truth[r["frame"]]) for r in trace]
    return {"rmse_m": math.sqrt(sum(e * e for e in errors) / len(errors)),
            "max_error_m": max(errors), "within_50m_fraction": sum(e <= 50 for e in errors) / len(errors)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=ROOT / "replay-results")
    args = parser.parse_args()
    paths = [args.source / "frontend_yaw2.json", args.source / "navdash/vo_only.jsonl", args.source / "navdash/truth.jsonl"]
    if not paths[2].exists():
        raise SystemExit(f"{paths[2]} missing: run ../e2e-visual-nav-vpair/fetch_truth.py first")
    frontend = json.loads(paths[0].read_text())
    truth, origin = read_track(paths[2])
    vo, _ = read_track(paths[1], origin)
    if sorted(vo) != sorted(truth) or sorted(vo) != list(range(len(frontend["queries"]))):
        raise ValueError("VO/truth/cache frame alignment mismatch")
    coefficients, n = calibrate(frontend, {k: v for k, v in truth.items() if k < 10})
    rows, traces = [], {}
    for stride in (1, 8):
        for q in (4.0, 16.0):
            for delay in (0, 2, 5):
                for policy in POLICIES:
                    result = replay(frontend, coefficients, vo, policy, stride, delay, q)
                    trace = result.pop("trace")
                    traces[f"s{stride}/q{q}/d{delay}/{policy}"] = trace
                    rows.append({"stride": stride, "q_m2_per_frame": q, "delay_frames": delay,
                                 "policy": policy, **result, **score(trace, truth)})
    receipt = {"input_type": "recorded real-flight derived observations plus artificial timing/covariance",
               "python": sys.version.split()[0], "platform": platform.platform(),
               "source_sha256": {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
               "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "calibration_frames": list(range(10)), "calibration_pairs": n, "coefficients": coefficients,
               "evaluation_frames": list(range(10, len(vo))), "request_budget": 40, "rows": rows,
               "limitations": ["One previously studied flight; not independent validation or parameter tuning/test separation.",
                   "Frame indices are not sensor timestamps; delays in frames are artificial.",
                   "VO includes an injected 2-degree heading error and calibration on this flight.",
                   "Map renders and evaluation truth share a reference; error independence is not established.",
                   "Affine image/map calibration omits changing attitude correction; not the sibling's full estimator.",
                   "Cached matching is not rerun; historical runtime sums do not establish current hardware savings.",
                   "Fixed recorded path cannot test speed or active-motion changes. Covariance is an uncalibrated proxy."]}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    (args.out / "traces.json").write_text(json.dumps(traces, indent=2, allow_nan=False) + "\n")
    lines = ["# VPAIR cached-observation scheduling replay", "",
             "One real flight's derived observations, with artificial frame delays/covariance. "
             "No new flight, GPU run, timestamp latency measurement or independence claim.", "",
             f"Calibration: frames 0..9, {n} pairs. Evaluation: frames 10..{len(vo)-1}. "
             "Budget: 40 requests, one pending job. Settings fixed before this replay; all sensitivity cases retained.", "",
             "| Stride | Q / frame | Delay frames | Policy | Requests | Accepted | RMSE m | Max m | Within 50 m |", "|---:|---:|---:|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['stride']} | {r['q_m2_per_frame']:g} | {r['delay_frames']} | {r['policy']} | {r['requests']} | {r['accepted']} | {r['rmse_m']:.2f} | {r['max_error_m']:.2f} | {r['within_50m_fraction']:.3f} |")
    lines += ["", "## Limitations", ""] + ["- " + s for s in receipt["limitations"]]
    lines += ["", "[Full receipt](results.json) · [Traces](traces.json)", ""]
    (args.out / "report.md").write_text("\n".join(lines))
    print(f"{len(rows)} replay cases, {n} calibration pairs; {args.out}")


if __name__ == "__main__":
    main()
