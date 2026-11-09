# close-area-relocalize: multi-hypothesis relocalization after VIO loss

Goal: answer "what happens when VIO is lost indoors?" in the shared
[close-area-arena](../close-area-arena/README.md). After a loss is detected, match the range scan
against the known map, keep up to 5 pose hypotheses, hover until one wins, then re-anchor the
estimate and resume. Compared against no relocalization and against "commit to the best match at
once". Backup headline from [doc 04 section 4](../../docs/research/close-area-nav/04-innovation-prior-art.md)
(scored 23/30 there).

All inputs are **synthetic** (simulated layouts, vehicle, VIO-like estimator and range fan). No
SITL, no flight.

## Run

```sh
cd samples/close-area-relocalize
uv venv .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python experiment.py --layouts 100 --seed 0     # 71 s wall on 8 workers
.venv/bin/python experiment.py --corridor --runs 20       # 21 s, symmetric corridor case
.venv/bin/python tune.py                                  # 18 s, seed-1 threshold calibration
.venv/bin/python -m unittest test_smoke -v                # skips without numpy
```

The arena is loaded by path ([arena.py](arena.py)); no arena file is edited.

## What is in it

| File | Does |
|---|---|
| [relocalize.py](relocalize.py) | `ScanMatcher`: correlative grid search over the known 0.1 m grid. Likelihood field exp(-d^2 / 2 sigma^2), sigma 0.10 m, d = EDT distance from each scan endpoint to the nearest occupied cell; score = mean over finite returns, in [0, 1]. 0.1 m lattice in a +-2 m window around the estimate, candidates closer than 0.1 m to an occupied cell dropped, greedy peaks 0.5 m apart, up to 5, refined at 0.025 m. Yaw is taken from the estimator. `RatioPersistence` (the acceptance rule) and `RelocPoseSource` (the pose source) |
| [experiment.py](experiment.py) | The arms below, A* known-map planner (`planners/astar_esdf.py`), dropout and jump faults, `HoverGate` (zero velocity while pose quality is 0), the corridor world and its fault |
| [tune.py](tune.py) | Static calibration on seed 1 (seed 0 held out): scores at truth vs offset, ratio of best to second |
| [test_smoke.py](test_smoke.py) | Matcher finds a pose 0.5 m off within 0.2 m; rule verdicts; one flight |

**Acceptance rule `RatioPersistence`** (per scan, on the ranked hypotheses):

- `none`: best score < 0.6, or fewer than 10 finite returns. None of them explains the scan:
  keep hovering. After 10 such scans the window doubles to +-4 m (the "truth not in the set" path).
- `ambiguous`: best < 1.02 x second. Keep hovering.
- `pending`: passes, but not yet best for 3 scans in a row (same place within 0.3 m after the
  odometry delta).
- `accept`: passes for 3 scans in a row. Re-anchor: offset = hypothesis - raw estimate, output =
  raw + offset from then on.

**Loss triggers** in `RelocPoseSource`: `reset_counter` changed, `quality` fell to 0, or an
innovation test (scan score at the current estimate < 0.5 for 3 scans). After a trigger it
reports quality 0 and waits 2 scans (0.2 s) so the EKF absorbs a VIO step before matching.

**Arms** (all A* known map, the arena estimator with its 2 dark zones per layout):

| Arm | Meaning |
|---|---|
| truth | Planner sees truth (reference) |
| estimator | (a) estimator only, no relocalization |
| hover_only | Control: hover while lost, resume on the raw estimate, no matching |
| single | (b) same pipeline, rule disabled: commit to the best hypothesis on the first scan |
| multi | (c) up to 5 hypotheses, `RatioPersistence`, hover until accept |
| single_noinnov, multi_noinnov | Ablation: (b) / (c) triggered only by reported loss, no innovation test |

Thresholds came from [results/tune_seed1.json](results/tune_seed1.json) (seed 1, 600 static poses,
synthetic): score at truth p5 0.80 (0 of 579 below the 0.5 innovation threshold); at 0.5 m offset
86 % of poses score below 0.5. With the window centred 0.5 m off truth, the best hypothesis was more
than 0.5 m wrong in 30 of 579 scans; their best / second ratio had p95 1.0027 and none of the 30
passed the rule. 93.6 % of the correct ones pass.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

`python experiment.py --layouts 100 --seed 0`, random family, wall 70.7 s on 8 workers
([results/reloc_random_0.md](results/reloc_random_0.md), per-run events in `.json`). A second run
gave the same table.

| fault | arm | runs | reached % | collision % | stuck % | timeout % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median recover s | median run max err m | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dropout | truth | 100 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| dropout | estimator | 100 | 64.0 | 1.0 | 35.0 | 0.0 | - | - | - | - | - | 0.4554 | 100 |
| dropout | hover_only | 100 | 59.0 | 4.0 | 37.0 | 0.0 | 0/104/0 | - | - | 0 | 1.8 | 0.4683 | 100 |
| dropout | single | 100 | 100.0 | 0.0 | 0.0 | 0.0 | 96/96/287 | 461 | 2 | 1 | 0.2 | 0.2866 | 100 |
| dropout | multi | 100 | 80.0 | 0.0 | 20.0 | 0.0 | 83/96/227 | 386 | 0 | 20 | 0.4 | 0.2938 | 100 |
| dropout | single_noinnov | 100 | 80.0 | 0.0 | 20.0 | 0.0 | 100/102/0 | 189 | 0 | 0 | 0.2 | 0.3483 | 100 |
| dropout | multi_noinnov | 100 | 67.0 | 0.0 | 33.0 | 0.0 | 91/103/0 | 178 | 0 | 16 | 0.4 | 0.3364 | 100 |
| jump | truth | 100 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| jump | estimator | 100 | 36.0 | 9.0 | 55.0 | 0.0 | - | - | - | - | - | 0.6275 | 89 |
| jump | hover_only | 100 | 38.0 | 6.0 | 56.0 | 0.0 | 89/4/0 | - | - | 0 | 0.2 | 0.6453 | 89 |
| jump | single | 100 | 100.0 | 0.0 | 0.0 | 0.0 | 88/2/331 | 419 | 4 | 0 | 0.2 | 0.3453 | 88 |
| jump | multi | 100 | 93.0 | 0.0 | 7.0 | 0.0 | 87/3/259 | 339 | 0 | 10 | 0.4 | 0.4832 | 87 |
| jump | single_noinnov | 100 | 71.0 | 0.0 | 29.0 | 0.0 | 89/3/0 | 91 | 0 | 0 | 0.2 | 0.4168 | 89 |
| jump | multi_noinnov | 100 | 76.0 | 0.0 | 24.0 | 0.0 | 89/2/0 | 89 | 0 | 2 | 0.4 | 0.5113 | 89 |

"Median recover s" is trigger to accept (or to resume for hover_only), over closed events. It is
0.2 s for (b) (the settle wait) and 0.4 s for (c) (settle plus 3 scans); p95 is the same in both.
"Still hovering at end" counts events open when the run ended. The jump fault arms only near an
obstacle, so it fired in 87-89 of 100 runs.

**(c) does not beat (b).** Single-hypothesis (b) reached 100 % under both faults; multi-hypothesis
(c) reached 80 % (dropout) and 93 % (jump). (c) made 0 wrong commits against 2 and 4 for (b), but
(b) lost nothing to them: all 6 came from innovation-test triggers, and all 5 runs with a wrong
commit still reached B (later matches corrected the pose). (c) failed by hovering until the scorer's 10 s stuck rule ended the
run. From `open_by_last_verdict` in the JSON:

| (c) runs that ended hovering | dropout | jump |
|---|---|---|
| `none`, fewer than 10 returns (open space, nothing within 6 m) | 14 | 2 |
| `ambiguous` (best < 1.02 x second) | 6 | 5 |
| of the ambiguous: truth within 0.5 m of a first-scan hypothesis | 5 | 5 |

Both faults vs no relocalization: (a) reached 64 % / 36 % with 1 % / 9 % collisions; every
relocalizing arm had 0 % collisions. Hovering alone (hover_only) does not help: 59 % / 38 %, with
4 % / 6 % collisions. Most of the gain comes from the innovation test, which also corrects
dark-zone drift: with only reported-loss triggers, (b) drops to 80 % / 71 % and (c) to 67 % / 76 %.
"Stuck" in the estimator arms is mostly the vehicle stopping at the estimated B more than 0.3 m
from the real one.

Scan matching cost: median 1.7-1.9 ms per scan (median of per-run medians, max 2.8 ms), 1681
candidates x about 70 beams, on this machine.

### Symmetric case: a 2 m x 14.8 m corridor

`python experiment.py --corridor --runs 20`, wall 21.3 s ([results/reloc_corridor.md](results/reloc_corridor.md)).
One corridor along x (walls area y 8.7-9.0 and 11.0-11.3), entered at the left end, left at the
right end. A 0.5 m VIO step along the corridor axis (sign seeded) fires when truth is at area
x 9.5-10.5, where no corridor end is within the 6 m range: shifted poses along x look the same.
No dark zones. Point A varies by +-0.3 m per run.

| fault | arm | runs | reached % | collision % | stuck % | timeout % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median recover s | median run max err m | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corridor_jump | truth | 20 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| corridor_jump | estimator | 20 | 15.0 | 25.0 | 60.0 | 0.0 | - | - | - | - | - | 0.6037 | 20 |
| corridor_jump | hover_only | 20 | 15.0 | 25.0 | 60.0 | 0.0 | 20/0/0 | - | - | 0 | 0.2 | 0.6056 | 20 |
| corridor_jump | single | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20/0/66 | 86 | 8 | 0 | 0.2 | 0.4974 | 20 |
| corridor_jump | multi | 20 | 0.0 | 0.0 | 100.0 | 0.0 | 20/0/15 | 15 | 0 | 20 | 0.4 | 0.5733 | 20 |
| corridor_jump | single_noinnov | 20 | 20.0 | 40.0 | 40.0 | 0.0 | 20/0/0 | 20 | 10 | 0 | 0.2 | 0.8294 | 20 |
| corridor_jump | multi_noinnov | 20 | 0.0 | 0.0 | 100.0 | 0.0 | 20/0/0 | 0 | 0 | 20 | - | 0.5523 | 20 |

- (c) does what the rule says: the 5 hypotheses sit 0.5 m apart along the corridor with equal
  scores, the verdict stays `ambiguous`, and the drone hovers in all 20 runs until the run is
  scored stuck (median hover 10.5 s). Truth was in the first hypothesis set in 19 of 20. Hovering
  gives no new information here, because a hovering scan does not change.
- (b) committed wrong in 8 of 20 runs. Without a check the error shows up as collisions at the
  corridor exit (single_noinnov: 10 wrong commits, 40 % collisions). With the innovation test, all
  20 reached: once the corridor end is in range the score at the wrong estimate drops below 0.5
  and a new match corrects it. In all 8 runs the wrong commit (0.59-1.43 m) was followed by an
  innovation-triggered match within 0.1 m of truth, 7.3-9.4 s later (per-run `events` in the JSON).
- So "hover until one wins" alone is a deadlock in a corridor. Hypothesis tracking only pays off
  with a move that separates the hypotheses (Fox 1998, Platt 2012 in
  [innovation-prior-art 01](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md)),
  or a bounded hover with a fallback. Neither is built or measured here.

## Limits

- 2D xy search only; yaw comes from the estimator, which passes truth yaw. A real yaw error
  widens the search to 3 DoF and makes symmetric rooms worse (180 deg look-alikes).
- The map is the exact prior grid of the layout (known-map case). No map error, no unmapped
  obstacles, no people. In a never-seen room there is nothing to match against.
- The relocalizer reads its own scan: the arena sensor model at the true pose with its own noise
  stream, at the same instant as the planner's scan. On a drone it is the same lidar read.
- Hover is perfect in the sim (zero velocity setpoint on a velocity-controlled point mass). A real
  hover without position drifts on IMU only.
- The innovation test runs on every 10 Hz step and fires often (227-331 triggers per 100 runs),
  so (b) and (c) are partly a continuous map-based correction, not only VIO-loss recovery. The
  `_noinnov` rows separate the two.
- Thresholds were set on seed 1 static poses, then the seed-0 flights were run once with them; the
  rule was not retuned on seed 0. Only the random family and one corridor were run, not u_trap or
  narrow_gap. Faults are the arena's 2 s dropout and 0.5 m jump, nothing larger.
- Wrong commit is counted at the accepted scan (> 0.5 m from truth). An accepted pose that drifts
  away later is not counted as a commit error; `median run max err m` shows the drift.

## Sources

- Hub docs read: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [03 close-area localization](../../docs/research/close-area-nav/03-close-area-localization.md)
  (reset_counter semantics, failure modes, "degenerate corridors" for lidar),
  [04 section 4](../../docs/research/close-area-nav/04-innovation-prior-art.md) (relocalization 23/30),
  [innovation-prior-art 01](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md)
  (Fox, Burgard, Thrun 1998 active Markov localization in a symmetric corridor; Platt et al. 2012;
  "truth not in the set" null hypothesis). These are hub docs, not re-read primary sources.
- Likelihood-field scoring and correlative grid search are textbook methods (Thrun, Burgard, Fox,
  Probabilistic Robotics, 2005, likelihood field model; Olson, "Real-time correlative scan
  matching", ICRA 2009). Named from memory, not re-read in this job; the code does not depend on
  any detail of them.
- Arena: [CONTRACT.md](../close-area-arena/CONTRACT.md), `estimator.py`, `faults.py`,
  `planners/astar_esdf.py`, used as checked out.
