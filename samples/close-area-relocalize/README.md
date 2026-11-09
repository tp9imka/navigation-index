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
  or a bounded hover with a fallback. Both are measured in the section on disambiguating moves below.

## Disambiguating moves after a hover timeout (loop-22b)

Adds the missing piece named above: when (c) has not accepted 1 s after a trigger, fly one short
move chosen to separate the hypotheses, then let the same `RatioPersistence` rule decide. Up to
4 moves per loss event, 1 s wait after each; then hover (never commit on a tie). Synthetic
inputs only, as above.

```sh
.venv/bin/python run_disambiguate.py --corridor --runs 20       # 22 s wall
.venv/bin/python run_disambiguate.py --layouts 100 --seed 0     # 75 s wall, 8 workers
```

[disambiguate.py](disambiguate.py) (map and hypotheses only, truth never used):

- Library: 8 directions x 1 m / 2 m, flown at up to 0.6 m/s in the raw estimator frame (VIO deltas
  are fine after a jump, only the anchor is wrong).
- Collision check against every live hypothesis and the estimate: the straight segment keeps
  ESDF >= 0.35 m (radius 0.15 + 0.20), or never gets closer than it starts if a start is already
  inside 0.35 m. Live = score >= best / 1.02^2.
- (e) `separation`, proposed: predict the scan at each hypothesis + move by ray cast on the map,
  score it with the matcher's own likelihood field at every other hypothesis + move, take the
  relative gap to the closest competitor, average over hypotheses. A beam that only one hypothesis
  sees counts only as far as the matcher can use it.
- (f) `infogain`, Fox 1998 style baseline: expected entropy reduction with a beam model
  (sigma 0.10 m, outlier floor 0.05, every 3rd beam).
- (d) `random`: uniform over collision-free moves.
- Verdict `none` (too few returns or no good match): (e) and (f) pick the move with the most
  predicted returns; (d) stays random.
- Near-ties (within 10 % of the best utility) go to the move ending closest to B, then the longer one.

Arms: (b) `single` and (c) `multi` are the experiment.py arms, rerun unchanged; their rows match
the tables above exactly. Ran 2026-11-09 on Apple arm64, CPython 3.11.15, numpy 2.4.6, scipy
1.17.1 (sample venv).

**Symmetric corridor**, 20 runs ([results/disamb_corridor.md](results/disamb_corridor.md), synthetic):

| arm | reached % | collision % | stuck % | wrong commits | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open |
|---|---|---|---|---|---|---|---|---|
| (b) single | 100.0 | 0.0 | 0.0 | 8 | 0 | 0.2 / 0.2 / 0.2 | - | - |
| (c) multi | 0.0 | 0.0 | 100.0 | 0 | 20 | 0.4 / 0.4 / 0.4 | - | - |
| (d) multi_random | 15.0 | 0.0 | 85.0 | 0 | 17 | 0.4 / 10.98 / 11.9 | 62 | 20 => 3 / 0 / 17 |
| (e) multi_sep | 70.0 | 0.0 | 30.0 | 0 | 7 | 0.4 / 11.1 / 11.3 | 54 | 20 => 15 / 0 / 5 |
| (f) multi_ig | 80.0 | 0.0 | 20.0 | 0 | 6 | 0.4 / 11.12 / 11.3 | 55 | 20 => 16 / 0 / 4 |

**Random layouts**, 100, seed 0 ([results/disamb_random_0.md](results/disamb_random_0.md), synthetic):

| fault | arm | reached % | collision % | stuck % | wrong commits | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open |
|---|---|---|---|---|---|---|---|---|---|
| dropout | (b) single | 100.0 | 0.0 | 0.0 | 2 | 1 | 0.2 / 0.2 / 0.2 | - | - |
| dropout | (c) multi | 80.0 | 0.0 | 20.0 | 0 | 20 | 0.4 / 0.4 / 3.3 | - | - |
| dropout | (d) multi_random | 97.0 | 0.0 | 3.0 | 0 | 4 | 0.4 / 0.6 / 13.2 | 40 | 22 => 19 / 0 / 3 |
| dropout | (e) multi_sep | 99.0 | 0.0 | 1.0 | 0 | 1 | 0.4 / 1.3 / 4.7 | 28 | 25 => 24 / 0 / 1 |
| dropout | (f) multi_ig | 99.0 | 0.0 | 1.0 | 0 | 2 | 0.4 / 1.3 / 4.7 | 26 | 25 => 24 / 0 / 1 |
| jump | (b) single | 100.0 | 0.0 | 0.0 | 4 | 0 | 0.2 / 0.2 / 0.2 | - | - |
| jump | (c) multi | 93.0 | 0.0 | 7.0 | 0 | 10 | 0.4 / 0.4 / 2.6 | - | - |
| jump | (d) multi_random | 98.0 | 0.0 | 2.0 | 0 | 5 | 0.4 / 0.4 / 11.8 | 20 | 9 => 7 / 0 / 2 |
| jump | (e) multi_sep | 100.0 | 0.0 | 0.0 | 0 | 3 | 0.4 / 0.4 / 5.7 | 9 | 9 => 9 / 0 / 0 |
| jump | (f) multi_ig | 99.0 | 0.0 | 1.0 | 0 | 4 | 0.4 / 0.4 / 3.9 | 12 | 9 => 8 / 0 / 1 |

"Recover s" is trigger to accept over all closed events, so the median stays at the 0.4 s of
events that never needed a move. Median recover after a move, from the `.md` files: corridor 11.0 s
(d), 11.0 s (e), 11.05 s (f); random dropout 2.6 / 2.2 / 2.4 s, jump 4.1 / 2.2 / 1.95 s for
(d) / (e) / (f). Moves happened in 22 (dropout) and 8 (jump) of 100 random runs.

**Verdict.**

- Random layouts: (e) nearly closes the gap to (b) and makes none of (b)'s wrong commits. 99 % /
  100 % reached against (b)'s 100 % / 100 % and (c)'s 80 % / 93 %. 0 wrong commits against
  (b)'s 2 / 4. 0 collisions in every arm.
- Corridor: (e) does not close the gap. 70 % reached against (b)'s 100 %, up from 0 % for (c),
  still 0 wrong commits against (b)'s 8.
- (e) beats (d) clearly in the corridor (70 % vs 15 %). In random layouts the gap is 2 runs per
  fault (99 vs 97, 100 vs 98), too few runs to call.
- (e) does not beat the Fox-style baseline (f). Corridor 70 % vs 80 %; random 99 / 100 % vs
  99 / 99 %. The separation score adds nothing measurable over expected entropy here.

Why the corridor runs fail (per-run `events[].moves` in the JSON):

- Greedy one-step choice. The first move had utility 0 to 0.014 for (e): from the corridor
  middle, no 2 m move brings a corridor end into the 6 m range. Recovery took 3 moves in 14 of
  15 accepted (e) events, about 11 s. This is the failure Fox 1998 notes for greedy entropy when
  the disambiguating place is far away.
- Direction. Every (e) run whose first move went -x (back toward A) failed: 6 of 6. Every +x run
  reached. In 5 of the 6, the event was still open and the last move still flying when the run
  ended; run 13 had accepted 2.4 s before.
- Scorer artifact. All failures are scored "stuck": the scorer's rule
  (`|p(t) - p(t - 10 s)| < 0.2 m`) fires when a backward move returns the drone to where it was
  10 s earlier, while it is still flying. The drone did not stop, but it had not localized by
  then either (5 of 6), so the score is not wrong about the outcome.

Design changes made while running, all kept in results/:

- [disamb_corridor_v1.md](results/disamb_corridor_v1.md) broke exact ties by candidate order,
  which silently preferred +x. The corridor's B is at +x. Replaced by the "closest to B"
  tie-break. (e) did not change (70 %); (f) went from 75 % to 80 %
  ([v2](results/disamb_corridor_v2.md)).
- [disamb_random_0_v2.md](results/disamb_random_0_v2.md) required 0.35 m clearance at every
  hypothesis start. One hypothesis next to a wall then blocked every move: all 5 (e) failures in
  that run logged "no feasible move". The relaxed check moved (e) from 97 % / 98 % to
  99 % / 100 %, with no collisions.
- Both fixes were chosen after seeing these runs, on the same layouts. No held-out seed was run.

Limits of this addition: no held-out seed (seed 1 was not flown with moves). Only one corridor
geometry and one jump size. The move library is axis-free but short (2 m), so long symmetric
corridors need several moves. Moves are flown in the raw estimator frame and stop within 0.08 m of the
raw-frame target; under dropout that frame drifts on IMU, and the truth-frame error of a move
was not logged. The clearance check trusts the
hypotheses. If truth is in none of them, the move can be unsafe; the `none` verdict and window
widening are the only guards.

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

### Held-out check (seed 1, run by the loop driver)

`.venv/bin/python run_disambiguate.py --layouts 100 --seed 1` (76.5 s,
[results/disamb_random_1.md](results/disamb_random_1.md); nothing was tuned on seed 1). Reached %
(wrong commits): dropout (b) 100 (2), (c) 84 (0), (d) 93 (0), (e) 99 (0), (f) 100 (0); jump
(b) 100 (3), (c) 95 (0), (d) 100 (0), (e) 99 (0), (f) 100 (0). The seed-0 picture holds: a move
after a hover timeout recovers almost every run without wrong commits, and the info-gain move (f)
is as good as or better than the proposed separation score (e). Earlier-iteration JSON files
(v1, v2) were dropped to keep the repo small; their .md tables stay.

### Held-out matrix: seeds 2-4, 7 families, harder faults (loop-56)

```sh
.venv/bin/python run_matrix.py --part parity   # 9 s: seed 1 random, 30 layouts, 180/180 runs match disamb_random_1.json
.venv/bin/python run_matrix.py --part matrix   # 385 s on 14 workers, 3780 runs
.venv/bin/python run_matrix.py --part rungs    # 12 s
.venv/bin/python run_matrix.py --part refs     # 167 s: truth and (a) estimator only, same layouts
```

All inputs are synthetic. The setup:
- Seeds 2-4, 30 layouts per seed per cell, nothing tuned on these seeds.
- Families: random, u_trap, narrow_gap, office, warehouse, maze, glass_office, with the default 72-ray 6 m fan, which sees glass.
- Faults: the arena's dropout (2 s) and jump (0.5 m).
- Arms: (b) single, (c) multi, (f) multi_ig, unchanged code.
- Time limit 60 s, 120 s for maze and warehouse (as in close-area-benchmark).
- Intervals are 95 % Wilson. Truth pose reached 100 % in every family ([results/reloc_matrix_refs.md](results/reloc_matrix_refs.md)).

Per-family verdict for (f), both faults pooled, 180 runs per family ([results/reloc_matrix_matrix.md](results/reloc_matrix_matrix.md)):

| family | (f) reached % (95 % CI) | (f) wrong commits | verdict: >= 95 % and 0 wrong | (b) reached % / wrong | (c) reached % / wrong |
|---|---|---|---|---|---|
| random | 100.0 (97.9-100.0) | 0 | PASS | 100.0 / 11 | 87.2 / 0 |
| u_trap | 100.0 (97.9-100.0) | 0 | PASS | 100.0 / 13 | 81.1 / 0 |
| narrow_gap | 85.6 (79.7-89.9) | 4 | FAIL | 78.3 / 67 | 57.8 / 1 |
| office | 94.4 (90.1-97.0) | 0 | FAIL | 92.8 / 0 | 94.4 / 0 |
| warehouse | 97.2 (93.7-98.8) | 33 | FAIL | 86.1 / 69 | 66.1 / 15 |
| maze | 97.2 (93.7-98.8) | 6 | FAIL | 99.4 / 5 | 92.8 / 3 |
| glass_office | 83.3 (77.2-88.1) | 0 | FAIL | 82.8 / 1 | 82.8 / 0 |

- **Random and u_trap reproduce the seed 0/1 picture.** (f) reached 100 %, (b) reached 100 % but made 11 and 13 wrong commits, and (c) reached 81-87 % by hovering.
- **Warehouse and maze fail on wrong commits, not on reach.** The wrong commits had a median error of 2.2 m in warehouse and 2.8 m in maze. That is about one aisle pitch or one 2 m maze cell: repeated geometry gives a look-alike place inside the 4 m widened window. In warehouse, 14 of (f)'s 33 wrong commits came after a disambiguating move. (b) is worse in warehouse: 69 wrong commits, and 17 of its 180 runs ended in a collision.
- **Office, glass_office and narrow_gap fail on collisions.** (f) collided in 4-7 % (office), 16-18 % (glass_office) and 10-12 % (narrow_gap) of runs. Office and glass_office had no wrong commit in those runs: errors under 0.5 m are enough to clip a 0.8-1.0 m doorway or a gap. Estimator-only (a) collided in 43-86 % of runs in these families. Relocalization cuts collisions but does not remove them. Why glass_office does worse than office is not logged.
- **The "none" deadlock (still hovering, fewer than 10 returns) appears only in (c).** It ended 10 random dropout runs, 1 random jump run and 1 u_trap dropout run. It never appeared in (b) or (f), and never in the complex families: walls are always in range there. Where (c) hovers to the end in those families, the last verdict is `ambiguous`: 23 to 37 events per cell in u_trap, narrow_gap and warehouse.

**Severity rungs**, random seed 2, 30 runs each ([results/reloc_matrix_rungs.md](results/reloc_matrix_rungs.md)):

| fault | (f) reached % (95 % CI) | (f) wrong commits | (b) reached % / wrong | (c) reached % / wrong |
|---|---|---|---|---|
| jump 1.0 m | 100.0 (88.6-100.0) | 0 | 100.0 / 2 | 83.3 / 0 |
| jump 2.0 m | 100.0 (88.6-100.0) | 0 | 100.0 / 2 | 86.7 / 0 |
| dropout 5 s | 100.0 (88.6-100.0) | 0 | 100.0 / 2 | 76.7 / 0 |

Rungs reuse the base fault's seeded start time and direction. In (c), the "none" deadlock appears under dropout 5 s (4 events open at the end).

Limits:
- 30 layouts per seed per cell, so the 95 % lower bound for a perfect cell is 95.9 % at 90 runs and 88.6 % at 30 runs.
- Collision locations and materials were not logged.
- Wrong commits are counted at the accepted scan, as above.

---end section---

Next action: paste the section above into `samples/close-area-relocalize/README.md` and add the evidence-matrix rows.

## Relocalization with a 4-beam sensor: hover and yaw-spin (loop-54)

The headline above uses the arena's ideal 72-beam, 6 m fan. `ScanMatcher` needs at least 10
finite returns per scan. The arena's `crazyflie` preset (Multi-ranger: 4 cones of 27 deg, front,
left, back, right, 3 m, 5 % dropout, [presets.py](../close-area-arena/presets.py),
[doc 08](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md)) gives at most 4. On
that sensor the existing arms never get a hypothesis. This section adds a spin-stack variant and
measures it. All inputs are **synthetic**.

```sh
.venv/bin/python run_sparse.py --layouts 100 --seed 0    # 245 s wall, 8 workers, 2 presets x 2 faults x 6 arms
.venv/bin/python run_sparse.py --tune                    # 5 s, static seed-1 sweep behind the two new constants
```

Ran 2026-11-09 on an Apple M3 Max, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1 (sample venv).

[sparse.py](sparse.py), on top of `relocalize.py` and `disambiguate.py` (neither edited):

- When VIO is lost (same triggers), hover. Once the raw estimate reads below 0.1 m/s (or 1 s after
  the trigger), yaw-spin at `SPIN_RATE_RAD_S` = 1.0 rad/s (57 deg/s) while lost.
- Each 10 Hz scan is stored with the raw estimator position and yaw. The stack is turned into one
  pseudo-scan in the body frame of the current pose (the hover point). Matching starts after a
  quarter turn: with 4 beams 90 deg apart, every bearing has then been seen once. After that, a
  sliding window over the last quarter turn (17 scans) is matched on every scan.
- Yaw comes from the IMU / gyro and is assumed good over a few seconds of spin. In the arena it is
  truth (the estimator passes yaw through). Gyro bias and scale error are not modelled.
- Cone correction (`cone_opening`). The arena cone reads the closest return in its 27 deg cone.
  Along the centre ray that puts walls short of the map. Over a spin, the true range at a bearing
  is at least every reading whose cone covers it, so the maximum of those readings recovers a flat
  wall. A reading covered by 2 or more no-return readings is dropped (wall edge with open space
  behind it).
- Acceptance: the same `RatioPersistence`, with ratio 1.10 instead of 1.02 (`SPARSE_RATIO`).
  S_MIN 0.6 and 3 scans in a row are unchanged. Arms (g) and (i) use it. Arm (h) commits to the best match at once.
- (i) adds the info-gain move from `disambiguate.py`, 1 s after the stack is complete. The stack
  is cleared while a move flies, and a new quarter turn is stacked at its end.

Why the two constants ([results/sparse_tune_seed1.json](results/sparse_tune_seed1.json), 300
static poses on seed 1, perfect hover, quarter-turn spin, window centred 0.5 m off truth,
synthetic). Without the cone correction, the score at the true pose had median 0.38 (p5 0.26),
below S_MIN 0.6. With the correction it was 0.79 (p5 0.69); with ideal 4-ray beams it was 0.83.
At ratio 1.02, 23 of 126 passing matches were more than 0.5 m wrong. At 1.10, 0 of 67 were.

**Results**, 100 random layouts, seed 0, A* known map, scored on truth
([results/sparse_random_0.md](results/sparse_random_0.md), all columns and per-run events in the
`.json`). The preset changes only the relocalizer's sensor; the planner does not read the scan.
"Spin s" is time spent yawing per loss event (trigger to accept, or to the end of the run). "Recover s"
is trigger to accept, over accepted events.

| preset | fault | arm | reached % | collision % | relocs accepted | wrong commits (> 0.5 m) | median / p95 recover s | median spin s per event |
|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (b) single | 64.0 | 1.0 | 0 | 0 | - | - |
| crazyflie | dropout | (f) multi_ig | 2.0 | 7.0 | 0 | 0 | - | - |
| crazyflie | dropout | (g) spin | 25.0 | 1.0 | 39 | 2 | 2.8 / 7.36 | 10.05 |
| crazyflie | dropout | (h) spin_single | 49.0 | 5.0 | 57 | 9 | 2.2 / 2.6 | 2.3 |
| crazyflie | dropout | (i) spin_ig | 48.0 | 3.0 | 76 | 0 | 8.8 / 27.48 | 12.2 |
| crazyflie | jump | (b) single | 38.0 | 6.0 | 0 | 0 | - | - |
| crazyflie | jump | (f) multi_ig | 12.0 | 23.0 | 0 | 0 | - | - |
| crazyflie | jump | (g) spin | 36.0 | 2.0 | 46 | 1 | 2.8 / 5.1 | 6.4 |
| crazyflie | jump | (h) spin_single | 50.0 | 8.0 | 80 | 16 | 2.6 / 2.6 | 2.6 |
| crazyflie | jump | (i) spin_ig | 64.0 | 7.0 | 76 | 0 | 7.3 / 24.6 | 9.1 |
| ideal | dropout | (f) multi_ig | 99.0 | 0.0 | 439 | 0 | 0.4 / 1.3 | - |
| ideal | dropout | (i) spin_ig | 98.0 | 0.0 | 356 | 0 | 2.4 / 8.6 | 2.4 |
| ideal | jump | (f) multi_ig | 99.0 | 0.0 | 359 | 0 | 0.4 / 0.4 | - |
| ideal | jump | (i) spin_ig | 100.0 | 0.0 | 322 | 0 | 2.4 / 9.0 | 2.4 |

- The ideal rows for (b), (e) and (f) in the `.md` match the published tables above exactly (same
  sensor noise stream), which checks the harness. (e) is within 1 run of (f) on both presets.
- On crazyflie, (b) closed 202 / 93 events at once with "no returns" and kept the raw estimate. It
  reached 64 % / 38 %, close to the estimator alone ([reloc_random_0.md](results/reloc_random_0.md):
  64 % / 36 %, 1 % / 9 % collisions). (e) and (f) hovered on `none`, fewer than 10 returns, in 100 / 90
  events and flew moves that could not help.
- Spin rate ([rate 0.5](results/sparse_random_0_rate0p5.md), [rate 2.0](results/sparse_random_0_rate2.md),
  arm (i), crazyflie). At 0.5 rad/s: 48 % / 67 % reached, 3 % / 1 % collisions, 1 / 0 wrong
  commits, median spin 15.5 / 12.3 s per event. At 2.0 rad/s: 34 % / 48 %, 6 % / 16 % collisions,
  5 / 2 wrong commits. A faster spin puts fewer scans in a quarter turn (median first-stack
  returns 7.5 / 11 at 2 rad/s, 12 / 16 at 1 rad/s).

**Verdict: the spin makes the matcher work on 4 beams. It does not make relocalization work for
the mission. FAIL against the 99-100 % headline.**

- The matcher works. Without the spin, 0 poses were accepted on crazyflie. With spin + move (i),
  76 of 101 (dropout) and 76 of 91 (jump) loss events were accepted, with 0 wrong commits.
- The mission does not work. (i) reached 48 % / 64 %, against 98 % / 100 % for the same arm on the
  72-beam sensor. Under dropout that is worse than not relocalizing (64 %). Under jump it is
  better (64 % vs 36-38 %), with 7 % collisions (estimator alone 9 %, (b) 6 %).
- Time cost: median 9-12 s of spinning per loss event, p95 33-35 s (`p95_spin_s_per_event` in the
  JSON). On the ideal sensor the same arm needs 2.4 s, and (f), without a spin, a median 0.4 s to recover.
- Committing at once on the stack (h) is faster (2.2-2.6 s) but made 9 / 16 wrong commits.

Why it falls short (per-run `events` in [sparse_random_0.json](results/sparse_random_0.json), arm (i)):

- Still lost when the run ended: 25 / 15 events. 15 / 11 of them had fewer than 10 returns after
  the stack (open space in a 3 m range), 10 / 4 were ambiguous. Hovering more than 10 s trips the
  scorer's stuck rule.
- Accepted, but B not reached: 27 / 19 runs. Accepted poses were 0.09 / 0.10 m off truth at the
  median and 0.31 / 0.22 m at p90 (`err_m`). The goal tolerance is 0.3 m. With 4 beams the
  innovation test never runs (it needs 10 returns per scan), so nothing corrects the pose after
  the accept. On the ideal sensor, dropping that test cut (b) from 100 % to 80 % / 71 % (`_noinnov` rows above).
- Collisions: 8 of the 10 (i) collisions happened while still lost, after 1-3 moves. The move
  clearance check trusts the hypotheses; with verdict `none` it only has the estimate. This limit
  is already stated in the disambiguating-move section.

Changes made while running, all kept in results/:

- [sparse_random_0_v1.md](results/sparse_random_0_v1.md), the first seed-0 run: no stop before
  stacking, and moves did not clear the stack. I read its accepted errors, then added both.
  Seed 0 is therefore not fully held out.
- Seed-1 dev flights, crazyflie only: [quarter turn](results/sparse_dev_seed1_arc90.md) (the final
  code), [half turn](results/sparse_dev_seed1_arc180.md) (not better, dropped), and a
  [degeneracy-aware accept](results/sparse_dev_seed1_degen.md) (correct only well-constrained
  directions; no gain, dropped).
- The sparse ratio 1.10 also hurts the dense stack. (g) on the ideal sensor reached 72 % / 73 %,
  ending ambiguous in 27 / 27 events. (i) recovers those runs with moves.

Limits of this addition:

- Yaw is truth. A real gyro's bias and scale error over a 10 s spin were not modelled. Doc 08
  section 3 says yawing makes the Flow deck drift (yaw flow is not separated from translation).
  The arena estimator does not model that either, so a real spin would be worse.
- The cone correction inverts the arena's own cone model (2nd-closest of 11 sub-rays). A real
  VL53L1x was not tested. Readings are instantaneous in the sim. At 1 rad/s a 100 ms reading
  spans 5.7 deg of yaw (derived), which is not modelled.
- One seed, one layout family, 3 m range only. `crazyflie_bright` (0.73 m) was not run; with
  less range it would see less.
- What might close the gap (not tried): a flying stack that feeds the innovation test (it needs a
  cone correction that works without a spin), a verification spin at B before landing, or a
  longer-range sensor.
