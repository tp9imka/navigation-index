#!/usr/bin/env python3
"""Reproduce all three falsifiable navigation mechanism experiments (stdlib)."""
import argparse
import csv
import hashlib
import html
import json
import math
import platform
import random
import statistics
import sys
import time
from pathlib import Path

import adaptation
import disambiguation
import scheduling

ROOT = Path(__file__).resolve().parent
TRAIN = tuple(range(16))
EXPERIMENTS = {
    "H1": (disambiguation, "efficient", "success"),
    "H2": (scheduling, "predictive_speed", "success"),
    "H3": (adaptation, "selective", "velocity_rmse"),
}


def objective(name, result):
    if name == "H1":
        return 100 * result["false_accept"] + 10 * result["abstain"] + result["distance"]
    if name == "H2":
        return 100 * (1 - result["success"]) + result["duration"] / 20 + result["requests"] / 10
    return result["velocity_rmse"]


def grid(name, policy):
    if name == "H1":
        return (0, 0.04, 0.12, 0.3) if policy in ("efficient", "no_unknown") else (0.12,)
    if name == "H2":
        if policy in ("periodic", "opportunity"):
            return (3, 5, 7, 10, 14)
        if policy == "threshold":
            return (0.5, 0.8, 1.1, 1.5, 2)
        return (0.7, 1, 1.3, 1.6)
    return (0.1, 0.3, 0.6, 1) if policy in ("selective", "no_reference_gate") else (0.3,)


def tune(name, module, policy):
    scenarios = {"H1": ("nominal",), "H2": ("nominal", "slow_compute"),
                 "H3": ("nominal", "no_excitation")}[name]
    scores = []
    for setting in grid(name, policy):
        losses = [objective(name, module.run(seed, scenario, policy, setting))
                  for scenario in scenarios for seed in TRAIN]
        scores.append({"setting": setting, "loss": statistics.mean(losses)})
    selected = min(scores, key=lambda x: x["loss"])["setting"]
    return {"selected": selected, "training_scenarios": scenarios, "grid": scores}


def paired_interval(a, b, resamples=1000):
    """Percentile bootstrap of paired per-seed differences, candidate minus baseline.

    Descriptive 95% interval; no multiple-comparison correction or field inference.
    """
    if len(a) != len(b) or not a:
        raise ValueError("paired, nonempty equal-length samples required")
    delta = [x - y for x, y in zip(a, b)]
    rng = random.Random(4242)
    bootstrap = sorted(statistics.mean(rng.choices(delta, k=len(delta))) for _ in range(resamples))
    return {"mean": statistics.mean(delta), "low": bootstrap[int(resamples * 0.025)],
            "high": bootstrap[min(resamples - 1, int(resamples * 0.975))]}


def aggregate(rows):
    groups = {}
    for r in rows:
        key = (r["hypothesis"], r["scenario"], r["policy"])
        groups.setdefault(key, []).append(r)
    summary = []
    for (name, scenario, policy), group in groups.items():
        metrics = {k: statistics.mean(r[k] for r in group) for k in group[0]
                   if k not in ("hypothesis", "scenario", "policy", "seed")}
        summary.append({"hypothesis": name, "scenario": scenario, "policy": policy, "n": len(group), **metrics})
    comparisons = []
    for name, (module, candidate, metric) in EXPERIMENTS.items():
        for scenario in module.SCENARIOS:
            candidates = (candidate, "predictive") if name == "H2" else (candidate,)
            metrics = (metric, "distance", "false_accept") if name == "H1" else (metric,)
            for candidate_policy in candidates:
                chosen = groups[(name, scenario, candidate_policy)]
                for policy in module.POLICIES:
                    if policy == candidate_policy:
                        continue
                    baseline = groups[(name, scenario, policy)]
                    assert [r["seed"] for r in chosen] == [r["seed"] for r in baseline]
                    for endpoint in metrics:
                        comparisons.append({"hypothesis": name, "scenario": scenario, "candidate": candidate_policy,
                                            "baseline": policy, "metric": endpoint,
                                            **paired_interval([r[endpoint] for r in chosen], [r[endpoint] for r in baseline])})
    return summary, comparisons


def markdown(summary, comparisons, settings, n):
    lines = ["# Navigation innovation POCs: measured synthetic evidence", "",
             f"{n} paired evaluation seeds per scenario, disjoint from 16 tuning seeds. "
             "Descriptor-level / scalar stochastic simulations only. No camera inference, "
             "autopilot, aircraft dynamics, hardware, real flight, or formal safety guarantee.", "",
             "Configuration, per-seed rows, code hashes and timing: [results.json](results.json). "
             "One evaluation seed per policy/scenario: [traces.json](traces.json).", ""]
    fields = {
        "H1": ("success", "false_accept", "abstain", "steps", "distance"),
        "H2": ("success", "violation_fraction", "rmse", "requests", "duration"),
        "H3": ("velocity_rmse", "position_error", "updates", "k_error"),
    }
    for name in EXPERIMENTS:
        lines += [f"## {name}", "", "Selected settings: " + ", ".join(
            f"`{p}={v['selected']}`" for p, v in settings[name].items()), "",
            "| Scenario | Policy | " + " | ".join(fields[name]) + " |",
            "|---|---|" + "---:|" * len(fields[name])]
        for r in summary:
            if r["hypothesis"] == name:
                lines.append(f"| {r['scenario']} | {r['policy']} | " + " | ".join(f"{r[k]:.4f}" for k in fields[name]) + " |")
        lines += ["", "### Paired differences", "",
                  "Candidate minus baseline; positive favors the candidate for success, negative for RMSE. "
                  "95% paired-bootstrap intervals describe this synthetic seed distribution only. "
                  "Degenerate intervals at 0 or 1 do not establish a zero failure probability.", "",
                  "| Scenario | Candidate | Baseline | Metric | Mean difference | 95% interval |", "|---|---|---|---|---:|---|"]
        for r in comparisons:
            if r["hypothesis"] == name:
                lines.append(f"| {r['scenario']} | {r['candidate']} | {r['baseline']} | {r['metric']} | {r['mean']:.4f} | [{r['low']:.4f}, {r['high']:.4f}] |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_dashboard(summary, traces, path):
    # Standalone inspection artifact; no CDN, JavaScript dependencies or network.
    sections = []
    metrics = {"H1": "success", "H2": "success", "H3": "velocity_rmse"}
    colors = ("#2563eb", "#0891b2", "#16a34a", "#9333ea", "#ea580c", "#be123c")
    for name, (module, candidate, _) in EXPERIMENTS.items():
        cards = []
        for scenario in module.SCENARIOS:
            rows = [r for r in summary if r["hypothesis"] == name and r["scenario"] == scenario]
            scale = max(1, max(r[metrics[name]] for r in rows))
            bars = []
            for color, r in zip(colors, rows):
                value = r[metrics[name]]
                bars.append(f'<div class="row"><span>{html.escape(r["policy"])}</span>'
                            f'<div class="track"><div style="width:{100*value/scale:.2f}%;background:{color}"></div></div>'
                            f'<b>{value:.3f}</b></div>')
            cards.append(f'<article><h3>{scenario}</h3><p>{metrics[name]} — '
                         f'{"higher" if name != "H3" else "lower"} is better</p>{"".join(bars)}</article>')
        sections.append(f'<section><h2>{name} · candidate: {candidate}</h2><div class="grid">{"".join(cards)}</div></section>')
    # H1's actual decision-dependent paths, one seed. Path coordinates are local.
    paths = []
    for color, policy in zip(colors, disambiguation.POLICIES):
        trace = traces[f"H1/nominal/{policy}"]["trace"]
        points = " ".join(f'{25+20*r["x"]:.1f},{100-22*r["y"]:.1f}' for r in trace)
        paths.append(f'<polyline points="25,100 {points}" fill="none" stroke="{color}" stroke-width="2"><title>{policy}</title></polyline>')
    content = '<!doctype html><meta charset="utf-8"><title>Navigation hypothesis lab</title>'
    content += '<style>body{font:15px system-ui;margin:32px auto;max-width:1200px;padding:0 20px;color:#172033;background:#f5f7fb}h1{font-size:32px}p{line-height:1.6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}article,svg{background:white;border:1px solid #dce2ee;border-radius:10px;padding:18px}.row{display:flex;align-items:center;gap:10px;margin:10px 0}.row span{width:155px;font-size:13px}.row b{width:50px;font-size:13px}.track{flex:1;background:#edf0f6;height:12px}.track div{height:12px}section{margin:30px 0}.notice{border-left:4px solid #c2410c;padding:12px;background:#fff7ed}</style>'
    content += '<h1>Navigation hypothesis lab</h1><p class="notice">SYNTHETIC MECHANISM TESTS · No field validation or proof of novelty. Bars include failures and ablations. Read the paired intervals and assumptions before comparing methods.</p><p><a href="report.md">Full tables and intervals</a> · <a href="results.json">Per-seed evidence</a> · <a href="traces.json">Traces</a></p>'
    content += "".join(sections) + '<h2>H1 nominal paths · one seed</h2><p>Local x/y in synthetic metres. Hover a path for its policy. This is not an aircraft trajectory.</p><svg viewBox="0 0 440 200" width="90%">' + "".join(paths) + '</svg>'
    path.write_text(content + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    if args.seeds < 2 or args.seed_start < 1000:
        parser.error("use >=2 evaluation seeds, starting >=1000 (tuning uses 0..15)")
    start = time.perf_counter()
    settings, rows, traces = {}, [], {}
    for name, (module, _, _) in EXPERIMENTS.items():
        settings[name] = {policy: tune(name, module, policy) for policy in module.POLICIES}
        for scenario in module.SCENARIOS:
            for policy in module.POLICIES:
                setting = settings[name][policy]["selected"]
                for seed in range(args.seed_start, args.seed_start + args.seeds):
                    result = module.run(seed, scenario, policy, setting, trace=seed == args.seed_start)
                    if "trace" in result:
                        traces[f"{name}/{scenario}/{policy}"] = {"seed": seed, "trace": result.pop("trace")}
                    rows.append({"hypothesis": name, "scenario": scenario, "policy": policy, "seed": seed, **result})
        print(f"{name}: {len(module.SCENARIOS) * len(module.POLICIES) * args.seeds} evaluations", flush=True)
    summary, comparisons = aggregate(rows)
    receipt = {"input_type": "synthetic", "schema_version": 1,
               "tuning_seeds": TRAIN, "evaluation_seeds": list(range(args.seed_start, args.seed_start + args.seeds)),
               "python": sys.version.split()[0], "platform": platform.platform(),
               "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob("*.py"))},
               "elapsed_seconds": time.perf_counter() - start, "settings": settings,
               "summary": summary, "paired_comparisons": comparisons, "rows": rows}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    (args.out / "traces.json").write_text(json.dumps(traces, indent=2, allow_nan=False) + "\n")
    (args.out / "report.md").write_text(markdown(summary, comparisons, settings, args.seeds))
    with (args.out / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in summary for k in r)), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)
    write_dashboard(summary, traces, args.out / "dashboard.html")
    print(f"Results: {args.out}; {receipt['elapsed_seconds']:.2f}s")


if __name__ == "__main__":
    main()
