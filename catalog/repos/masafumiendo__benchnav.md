# BenchNav

`repo:masafumiendo/benchnav` - <https://github.com/masafumiendo/benchnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 60 | Python | ? | 2024-06-15 | False | research-prototype | medium |

Gymnasium-based PyTorch simulator for benchmarking off-road navigation planners under uncertain, probabilistic traversability, with synthetic terrain generation.

**Why it matters:** Lightweight way to compare off-road planners without a robot.

**Hackathon notes:** Docker setup via make build-gpu or build-cpu, or pip install from the clone (not on PyPI); fetch the dataset and models with scripts/download_dataset_and_model.sh, then run the tutorial notebooks. No LICENSE file, so all rights reserved by default.

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `off-road`, `benchmark`, `gymnasium`

**Domains:** ground, space

## Related

- evaluated_on: [Wild Visual Navigation](../../catalog/repos/leggedrobotics__wild_visual_navigation.md)

## Referenced by

- [HOUND](../../catalog/repos/prl-mushr__hound_core.md) (alternative_to)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
