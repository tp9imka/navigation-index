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

Demo command first (the headline arm, held-out seed 1, from
[demo-script-close-area](../../templates/demo-script-close-area.md)). `--out .venv/demo-out`
keeps the committed `results/` untouched:

```sh
cd samples/close-area-relocalize
uv venv .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python run_disambiguate.py --layouts 100 --seed 1 --arms single,multi,multi_ig --out .venv/demo-out < /dev/null
.venv/bin/python -c "import json; R=json.load(open('.venv/demo-out/disamb_random_1.json'))['results']['jump']; [print(a, R[a]['runs'][97]['outcome'], [(e['t_trigger'], e['recover_s'], e['result'], e['err_m']) for e in R[a]['runs'][97]['events']]) for a in ('single','multi','multi_ig')]"
# expect: the table rows of results/disamb_random_1.md, then: single reached (0.6281 m commit at 13.0 s),
# multi stuck (event at 13.0 s still open), multi_ig reached (accepted after 1.7 s at 0.0748 m)
```

The demo took 55.31 s wall in the [Day-1 dry run](../../docs/day1-dry-run.md#blockers) on a loaded
machine; the first run on a fresh venv can wait longer. Full experiments:

```sh
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

## Imperfect prior map (loop-55)

The headline above matches against the exact layout grid. The Day-1 intake default for Q7 is
"unknown and moved between runs" ([intake](../../docs/day1-close-area-intake.md)). This run
measures the same arms on a ladder of map errors. Synthetic inputs only.

```sh
.venv/bin/python run_stalemap.py --layouts 100 --seed 2 --workers 14   # 303 s wall
```

[map_perturb.py](map_perturb.py) builds the real world (what the range fan sees and the scorer
scores) and the map (what the planner, the matcher and the move check get) separately:

- a_exact: map = real.
- b_removed: 1-2 mapped obstacles within 3 m of the flown path are gone in reality (145 removed over 100 layouts).
- c_added: 1-2 unmapped boxes or cylinders, surface 0.45-1.5 m from the truth-arm flight path, >= 1 m from A and B (152 added). Placed off that path on purpose: the known-map planner ignores scans, so an obstacle on the path is hit by every arm.
- d_shift01 / d_shift02: every obstacle (not the walls) moved 0.1 / 0.2 m, each in its own random direction.
- e_selfmap: the unknown-map A* flies A => B on the estimator (no fault, dark zones). Its log-odds grid becomes the map, and the fault hits on the return leg B => A. Matcher: occupied cells only. Planner: occupied or unknown. The return estimate starts with the outbound end error, so it is in the map's frame. 99 of 100 outbound legs ended within 1 m of B (59 reached, 40 stuck close). Median outbound end error was 0.339 m. A median 0.142 of mapped cells lie more than 0.2 m from a real surface.

Cells are dropout / jump: reached % / collision % (of which during a move into an unmapped obstacle) / wrong commits (> 0.5 m) / p95 recover s
([results/stalemap_random_2.md](results/stalemap_random_2.md)). The truth-pose reference reached 100 % on a-d. On e it reached 92.9 % with 6.1 % collisions: the truth pose disagrees with the drifted map.

| rung | (b) single | (c) multi | (f) multi_ig |
|---|---|---|---|
| a_exact | 100 / 0 (0) / 8 / 0.2 ; 100 / 0 (0) / 7 / 0.2 | 84 / 0 (0) / 0 / 0.4 ; 94 / 0 (0) / 0 / 0.4 | 100 / 0 (0) / 0 / 0.82 ; 100 / 0 (0) / 0 / 0.4 |
| b_removed | 100 / 0 (0) / 8 / 0.2 ; 100 / 0 (0) / 6 / 0.2 | 71 / 0 (0) / 1 / 0.5 ; 85 / 0 (0) / 0 / 0.4 | 99 / 0 (0) / 0 / 2.29 ; 99 / 0 (0) / 0 / 1.22 |
| c_added | 98 / 2 (0) / 57 / 0.2 ; 99 / 1 (0) / 62 / 0.2 | 65 / 0 (0) / 4 / 0.4 ; 73 / 0 (0) / 7 / 0.6 | 89 / 7 (2) / 16 / 3.5 ; 88 / 7 (2) / 21 / 3.12 |
| d_shift01 | 100 / 0 (0) / 4 / 0.2 ; 100 / 0 (0) / 6 / 0.2 | 80 / 0 (0) / 0 / 0.4 ; 97 / 0 (0) / 3 / 0.4 | 100 / 0 (0) / 0 / 0.71 ; 100 / 0 (0) / 2 / 0.4 |
| d_shift02 | 100 / 0 (0) / 16 / 0.2 ; 100 / 0 (0) / 17 / 0.2 | 65 / 0 (0) / 9 / 0.6 ; 82 / 0 (0) / 7 / 0.5 | 97 / 0 (0) / 10 / 2.28 ; 97 / 0 (0) / 6 / 1.56 |
| e_selfmap | 98 / 0 (0) / 71 / 0.2 ; 97 / 0 (0) / 166 / 0.2 | 71.7 / 1 (0) / 10 / 0.4 ; 81.8 / 0 (0) / 11 / 0.4 | 93.9 / 2 (0) / 13 / 2.67 ; 92.9 / 2 (0) / 14 / 1.69 |

Median recover stays 0.2 s for (b) and 0.4 s for (c) and (f) on every rung. Wrong commits on e_selfmap are counted in the map frame: truth plus the outbound estimator error at the nearest outbound sample. In the truth frame they are higher (118 / 202 for (b)).

**Verdict.**

- The exact-map claim "(f) recovers almost every run with 0 wrong commits and 0 collisions" holds only for b_removed and d_shift01. **FAIL** on c_added: 7 % collisions per fault.
- (f)'s wrong commits are 6-21 per 100 runs once obstacles move 0.2 m, are added, or the map is self-built.
- All 12 (f) collisions into an unmapped obstacle came after a disambiguating move: 2 per fault during the move, 8 within 0.6-5.0 s after it ([results/stalemap_random_2_collisions.md](results/stalemap_random_2_collisions.md)). The move check trusts the map, and the known-map planner then flies on from where the move left it.
- (b) single + innovation test reaches the most (97-100 % on every rung) with 0-2 % collisions. Its wrong commits grow 7-8x on c_added and are corrected by later matches.
- (c) hover-only still ends runs hovering (65-97 %).

Limits: one seed (2), no held-out check. Added obstacles are off the truth path by construction. The 0.2 m shift is per obstacle, not a rigid map offset. The e_selfmap truth arm is not an upper bound. The arena's 2 s dropout and 0.5 m jump only. The move check still ignores the live scan; checking moves against scan endpoints is the obvious next fix and was not run.

## Yaw search: 3-DoF relocalization (loop-60)

The matcher above takes yaw from the estimator. [relocalize_yaw.py](relocalize_yaw.py) adds a
yaw search to arm (f) without editing it. `YawScanMatcher` scores the same 0.1 m xy lattice at
13 yaw offsets (+-15 deg in 2.5 deg steps) around the estimator yaw. It keeps the best yaw per
xy cell, runs the same 0.5 m peak suppression (up to 5 hypotheses), then refines each peak at
0.025 m x 0.25 deg. On accept, the xy offset is re-anchored as before and the yaw correction
rotates all later estimator deltas. Truth is never used in a decision. Synthetic inputs only.

    .venv/bin/python run_yaw.py --layouts 100 --seed 2      # 124 s wall, 12 workers
    .venv/bin/python run_yaw.py --corridor --runs 20        # 203 s wall

Fault: from the step where the arena jump fault fires (0.5 m step, reset_counter + 1), the
estimate is rotated by the bias (5 or 10 deg, sign seeded per run; or 180 deg). Later position
and velocity deltas are rotated, and the reported yaw is truth + bias. Vehicle model, both arms:
the setpoint is flown rotated by (true yaw - reported yaw), so a heading error bends the flight
as well as the estimate. Arms: (f) `multi_ig` unchanged; (f) + yaw search; (f) + yaw search +
heading first. The last arm was added after the first corridor run; see below.

**Random layouts**, 100, seed 2 ([results/yaw_random_2.md](results/yaw_random_2.md), synthetic).
The jump fault fired in 86 runs and opened a new loss event in 82; in the other 4 an event was
already open.

| bias | arm | reached % | collision % | wrong commits | jump event => accepted / wrong / open | jump recover s median / p95 | ms per matched scan, median |
|---|---|---|---|---|---|---|---|
| 0 | (f) no yaw search | 100 | 0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 1.69 | 1.8 |
| 0 | (f) + yaw search | 100 | 0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.88 | 20.1 |
| +-5 | (f) no yaw search | 38 | 0 | 7 | 82 => 68 / 1 / 14 | 0.4 / 6.13 | 7.0 |
| +-5 | (f) + yaw search | 100 | 0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.6 | 23.5 |
| +-10 | (f) no yaw search | 18 | 7 | 52 | 82 => 52 / 16 / 30 | 0.4 / 6.05 | 7.1 |
| +-10 | (f) + yaw search | 100 | 0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.78 | 23.4 |

- A 5 deg heading error alone takes (f) from 100 % to 38 %; 10 deg takes it to 18 % with 7 %
  collisions. The xy-only matcher scores a rotated scan, so verdicts go `none`. The window
  widened to +-4 m in 109 and 113 events, against 2-3 with yaw search; that widening is why the
  no-yaw arm costs 7 ms per scan.
- With yaw search, every jump event was accepted with no wrong commit, and the heading at run
  end was off by a median 0.25 deg (max 1.0 deg) under every bias.
- Cost: about 20-23 ms per matched scan against 1.8 ms. Medians come from 12 parallel workers
  on Apple arm64 (CPython 3.11.15, numpy 2.4.6, scipy 1.17.1), so these are load-dependent.
- The heading-first arm gave the same outcome rows here (100 / 100 / 100 %, 0 wrong commits).

**Corridor** (the 2 m x 14.8 m corridor above, corridor_jump fault, 20 runs,
[results/yaw_corridor.md](results/yaw_corridor.md), synthetic):

| bias | arm | reached % | collision % | stuck % | jump event => accepted / wrong / open | median run max err m |
|---|---|---|---|---|---|---|
| +-10 | (f) no yaw search | 0 | 50 | 45 | 20 => 17 / 13 / 3 | 2.24 |
| +-10 | (f) + yaw search | 45 | 25 | 15 | 20 => 15 / 0 / 5 | 0.99 |
| +-10 | (f) + yaw search + heading first | 70 | 0 | 30 | 20 => 16 / 0 / 4 | 0.60 |
| 180 | (f) no yaw search | 0 | 0 | 95 | 20 => 15 / 15 / 5 | 9.60 |
| 180 | (f) + yaw search | 0 | 0 | 100 | 20 => 16 / 16 / 4 | 9.64 |
| 180 | (f) + yaw search + heading first | 0 | 0 | 100 | 20 => 16 / 16 / 4 | 9.64 |

For reference, (f) in this corridor without a yaw bias reached 80 %
([results/disamb_corridor.md](results/disamb_corridor.md)).

- At 10 deg, yaw search alone collided in 5 of 20 runs. In all 5 the jump event was still open:
  the drone was flying disambiguating moves with the uncorrected heading in a 2 m corridor.
  Heading first fixes that case. When every live hypothesis agrees on the yaw correction within
  1 deg for 3 scans (best score >= 0.6, correction >= 1 deg), it applies the heading before the
  xy verdict. Result: 70 % reached, 0 collisions, 0 wrong commits. This rule was chosen after
  seeing the corridor run, on the same runs. No held-out seed was flown with it.

**Verdict on the 180 deg case: FAIL in every arm, and no scan-only fix exists in this corridor.**
The corridor is point-symmetric about its centre, so a pose and its twin (mirrored, yaw + 180)
see the same scan.

- Flights: a 180 deg heading error ended scored stuck in 19-20 of 20 runs. 15-16 of 20 jump
  events committed to the wrong pose (median run max error 9.6 m). The drone flies the mirror
  path back toward A while it believes it is heading to B.
- Static check, 20 poses near the middle: the +-15 deg search given a 180-off heading finds the
  twin with best score median 0.972 (min 0.963). That is far above the 0.6 floor, so nothing
  flags it.
- The true-heading best over the flipped-heading best has ratio median 1.0042 (range 1.0 to
  1.0098), below the 1.02 rule. So even a full-circle search could at best report "ambiguous".
- A full-circle search (144 yaws, median 250 ms per scan) filled all 5 hypothesis slots with
  flipped-heading copies along the corridor axis in 20 of 20 poses. The true heading was not
  in the set.
- The flipped copies score slightly higher because of a one-cell rasterization asymmetry. In
  corridor run 0 the lower wall's face cell is free and the upper wall's is occupied.
- Practical answer: keep the +-15 deg window and bound heading error from another source, such
  as VIO yaw (which drifts slowly and does not flip), a magnetometer outdoors, or an asymmetric
  landmark. A yaw prior is an assumption to state, not something this matcher checks.

Limits: one bias per run, applied once at the jump. No slow yaw drift, and no yaw error without
a reset_counter trigger. The move chooser predicts all hypotheses at one common yaw. The
setpoint-rotation vehicle model is an assumption. One corridor geometry, seed 2 only for
random layouts. The flight rows of a second run were identical; the timings differ by load.

## AF-MCL baseline: particle filter with random-particle injection (loop-67)

Doc 10's kill test: does a published-style particle filter (no hover gate, output = particle mean) do as well as the hub's (f)? The reference is AF-MCL, [arXiv 2610.32645](https://arxiv.org/abs/2610.32645) (full HTML read 2026-11-09). It runs on a Crazyflie with 4 single-point ranges plus heading. It uses an EDT likelihood field, rejects beams at the previous estimate, and injects random particles when the short-term likelihood falls below the long-term one. All inputs here are **synthetic**.

```sh
.venv/bin/python run_mcl.py                                          # 95.0 s wall, 14 workers, 2400 runs
.venv/bin/python run_mcl.py --arms mcl,mcl_gate --hardened --stem seed2_hardened   # 87.4 s
.venv/bin/python run_mcl.py --arms spin_ig --presets crazyflie --stem seed2_spin_ig  # 36.6 s
```

Ran 2026-11-09 on Apple arm64, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1 (sample venv). A second run of the main command gave the same outcome, time to goal and errors in all 2400 runs.

[mcl.py](mcl.py) follows the paper's Algorithm 1 and uses its Table I parameters unchanged:
- Likelihood: sigma_obs 0.15 m, geometric mean over the kept beams, on the `ScanMatcher` EDT.
- Beam filter: mixture 0.7 / 0.1 / 0.1 / 0.1, lambda_short 4, threshold 0.4, ray cast from the previous estimate.
- Injection: alpha_slow 0.001, alpha_fast 0.9, cap 0.3, drawn uniformly over unoccupied cells.
- Resampling: when ESS < 0.5 N; motion noise 0.03 m/sqrt(s).
- Output: the mean of the final particle set, injected particles included, as in the paper.

Two changes for the arena:
- 400 particles instead of 100. The arena is 20 x 20 m; 400 keeps the paper's 10 x 10 m density.
- The motion input is the raw estimator delta, the same VIO / IMU deltas the other arms use. A VIO jump therefore moves every particle.

Arms (A* known map, scored on truth, seed 2, 100 layouts per cell, held out):
- (f) `multi_ig`, unchanged.
- (m) `mcl`, the planner always flies on the mean.
- (m+g) `mcl_gate`, the same filter. It hovers while the particle spread is above 0.25 m and resumes after 3 scans at or below it.

Definitions:
- **Wrong commit:** the pose is more than 0.5 m off when navigation resumes. For (f) that is the accept; for the MCL arms, the spread back at or below 0.25 m for 3 scans.
- **Flown wrong:** a navigating step (quality > 0) with the pose more than 0.5 m off.
- **Truth recover:** AF-MCL's own definition. After the fault fires, the error goes above 0.2 m (the loss must start within 3 s after the fault ends). Recovery is the first time after that when the error stays at or below 0.2 m for 1 s, timed from the fault onset.

Main run ([results/mcl_seed2.md](results/mcl_seed2.md); all columns, per-run events and filter counters are in the `.json`):

| family | sensor | fault | arm | reached % (95 % CI) | collision % | wrong commits | runs flown on a > 0.5 m pose | truth recover s median (not recovered of loss runs) |
|---|---|---|---|---|---|---|---|---|
| random | ideal | dropout | (f) | 100.0 (96.3-100.0) | 0.0 | 0 | 12 | 2.43 (0 of 51) |
| random | ideal | dropout | (m) | 99.0 (94.6-99.8) | 1.0 | 5 | 46 | 3.78 (1 of 53) |
| random | ideal | dropout | (m+g) | 90.0 (82.6-94.5) | 0.0 | 6 | 8 | 3.63 (6 of 53) |
| random | ideal | jump | (f) | 100.0 (96.3-100.0) | 0.0 | 0 | 12 | 0.4 (0 of 86) |
| random | ideal | jump | (m) | 89.0 (81.4-93.7) | 10.0 | 32 | 87 | 4.8 (16 of 87) |
| random | ideal | jump | (m+g) | 68.0 (58.3-76.3) | 0.0 | 21 | 37 | 5.4 (29 of 85) |
| office | ideal | dropout | (f) | 93.0 (86.3-96.6) | 7.0 | 0 | 2 | 2.4 (0 of 31) |
| office | ideal | dropout | (m) | 86.0 (77.9-91.5) | 13.0 | 0 | 60 | 3.24 (5 of 43) |
| office | ideal | dropout | (m+g) | 92.0 (85.0-95.9) | 4.0 | 2 | 1 | 3.13 (1 of 45) |
| office | ideal | jump | (f) | 87.0 (79.0-92.2) | 13.0 | 0 | 2 | 0.4 (0 of 100) |
| office | ideal | jump | (m) | 55.0 (45.2-64.4) | 45.0 | 15 | 99 | 3.6 (39 of 98) |
| office | ideal | jump | (m+g) | 52.0 (42.3-61.5) | 5.0 | 18 | 14 | 3.7 (41 of 100) |
| random | crazyflie | dropout | (f) | 3.0 (1.0-8.5) | 3.0 | 0 | 7 | 3.77 (47 of 71) |
| random | crazyflie | dropout | (m) | 14.0 (8.5-22.1) | 81.0 | 6 | 100 | 6.21 (74 of 90) |
| random | crazyflie | dropout | (m+g) | 1.0 (0.2-5.4) | 1.0 | 1 | 15 | 1.78 (91 of 95) |
| random | crazyflie | jump | (f) | 16.0 (10.1-24.4) | 14.0 | 0 | 12 | 0.7 (82 of 85) |
| random | crazyflie | jump | (m) | 15.0 (9.3-23.3) | 77.0 | 14 | 100 | 1.55 (84 of 88) |
| random | crazyflie | jump | (m+g) | 0.0 (0.0-3.7) | 1.0 | 1 | 24 | 1.2 (25 of 28) |
| office | crazyflie | dropout | (f) | 9.0 (4.8-16.2) | 18.0 | 0 | 2 | 5.53 (39 of 54) |
| office | crazyflie | dropout | (m) | 1.0 (0.2-5.4) | 97.0 | 6 | 100 | 2.83 (50 of 63) |
| office | crazyflie | dropout | (m+g) | 0.0 (0.0-3.7) | 0.0 | 1 | 1 | 1.39 (80 of 84) |
| office | crazyflie | jump | (f) | 2.0 (0.6-7.0) | 50.0 | 0 | 1 | 10.95 (95 of 97) |
| office | crazyflie | jump | (m) | 0.0 (0.0-3.7) | 94.0 | 21 | 100 | 14.45 (79 of 81) |
| office | crazyflie | jump | (m+g) | 0.0 (0.0-3.7) | 1.0 | 7 | 8 | 1.4 (74 of 75) |

The (f) "flown on a > 0.5 m pose" count includes dark-zone drift before the fault: 5 and 7 of the 12 random-ideal runs were already more than 0.5 m off before it fired. The "runs > 0.5 m off before the fault" column in the `.md` shows this. Per scan, MCL took 0.4-0.75 ms and (f) 1.6-3.15 ms on the ideal sensor (medians of per-run medians, 14 parallel workers, so load-dependent).

**Verdict: yes, the hub's arm beats the published-style MCL baseline. The win is on the dense sensor and on the jump fault.**

- **Ideal sensor, jump:** (f) reached 100 % / 87 % (random / office) against (m) 89 % / 55 %. It made 0 wrong commits against 32 / 15, and its truth recover median was 0.4 s against 4.8 / 3.6 s. (m)'s 10 % and 45 % collisions were all flown on a pose more than 0.5 m off.
- **Ideal sensor, dropout:** the gap is small. Random 100 % vs 99 % is inside the CI; office is 93 % vs 86 %.
- **Hover gate on MCL:** it removes most collisions (random jump 10 % => 0 %, office 45 % => 5 %) but does not raise reach. Random jump drops 89 % => 68 %: the drone hovers until it is scored stuck while injection keeps the spread above 0.25 m. A gate on the filter's spread is not the hub's acceptance rule.
- **Why MCL misses jumps:** in 15 of the 16 random-ideal jump runs that never recovered, the beam filter rejected every beam on some updates. With no kept beam there is no divergence signal and no injection. The paper names this limitation in its "Empty beam set" paragraph.
- **Crazyflie (4 cones, 3 m range): FAIL in every arm.** MCL lost track before the fault in 62-85 of 100 runs and flew on a pose more than 0.5 m off in 100 of 100 runs in every cell, with 77-97 % collisions. The likely cause is that in a 20 x 20 m area most beams see nothing: the median run had 139-143 updates with every beam rejected in random layouts. (f) reached 2-16 %, because it needs 10 returns per scan. The hub's 4-beam arm (i) `spin_ig` reached 36 % / 53 % (random dropout / jump) and 52 % / 52 % (office), with 0 wrong commits and 3-35 % collisions ([results/mcl_seed2_spin_ig.md](results/mcl_seed2_spin_ig.md)). It beats MCL but is still far from usable.
- **The paper's 2.9 s kidnap recovery** (Webots, its own two-room map) is not comparable with these numbers: different sim, map size, sensor model and fault.

**Extra: hardened MCL** ([results/mcl_seed2_hardened.md](results/mcl_seed2_hardened.md)). Two changes, chosen after a 14-layout probe on seed 2, so this run is not held out:
- Report the weighted mean before injection.
- After 5 updates in a row with every beam rejected, use all in-range beams. This is the extension the paper itself suggests.

Ideal sensor, reached % / wrong commits:
- (m) random: 100 / 4 dropout, 94 / 30 jump.
- (m) office: 90 / 0 dropout, 71 / 25 jump.
- (m+g) random: 100 / 3 dropout, 93 / 23 jump.
- (m+g) office: 93 / 0 dropout, 75 / 28 jump.

This closes most of the reach gap in random layouts, but (f) still makes 0 wrong commits against 23-30. On Crazyflie the hardened (m) reached 1-24 % with 75-81 % collisions.

Limits:
- Seed 2 only; corridor, u_trap and the other families were not run.
- The 0.25 m gate threshold is a proposal and was not tuned.
- The motion input is the estimator's position delta, not Flow-deck velocities.
- Yaw is truth for every arm.
- The arena's cone sensor is not the paper's single-point ray model.
- Table I was tuned by the authors for 6-10 m Webots maps, not for this arena.

---

## Rolling submap: collect returns while flying (loop-68)

The 4-beam arms above collect returns only after the loss. They spin (sparse.py) or rely on a particle filter (mcl.py). This arm keeps a rolling local submap of range returns while flying. On loss, it matches the whole submap against the map. All inputs are **synthetic**.

```sh
.venv/bin/python run_submap.py --tune                       # 18 s, seed-1 static sweep
.venv/bin/python run_submap.py                              # 209 s wall, 14 workers, 2400 runs
.venv/bin/python run_submap.py --presets crazyflie --arms submap_arc_ig,submap_fwd,submap_fwd_ig,submap_arc_ig_notrack,submap_bridge --stem seed2_extras   # 709 s
```

These ran on 2026-11-09, Apple arm64, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1 (sample venv).

### How it works

[submap.py](submap.py) builds on `relocalize.py`, `sparse.py` and `disambiguate.py` without editing them.

- **Submap.** It keeps the last `WINDOW_S` = 6 s of nominal flight in the raw estimator frame, with at most `MAX_POINTS` = 300 finite returns. A scan is added only after 0.05 m or 0.05 rad of motion, so hovering does not fill the window. While lost, the time window is frozen.
- **Drift budget.** The arena VIO drifts 0.047 m per sqrt(m), so 6 m of flight in the window gives 0.12 m (1 sigma). Inside a dark zone it is 4x that, which is over budget.
- **Inertial bridge.** A VIO jump moves the raw frame by about 0.5 m over roughly 0.5 s. The bridge dead-reckons from the EKF velocity at the trigger call, with a simulated accelerometer (bias 0.03 m/s², white noise 0.05 m/s²). Once the raw frame agrees with the bridge for 3 scans, the submap is shifted into the new frame. Settling took a median 0.4-0.8 s.
- **Match.** It uses the ScanMatcher and the `RatioPersistence` rule with ratio 1.10 and S_MIN 0.6. Verdicts are none / ambiguous / pending / accept.
- **Innovation test.** The innovation test (score of the submap at the estimate) now runs in nominal flight. A single 4-beam scan could not run it.
- **Info-gain move.** The (s+ig) arm adds the info-gain move from disambiguate.py. It predicts the 4 beams at 5 points along the move.
- **Tracking.** Every 2 scans, a +-0.3 m local search re-anchors the estimate halfway to a better match. I added this after seed-1 dev flights collided on 0.2-0.9 m of dark-zone drift, long after a correct accept.

### Why the specified cone correction fails

From the seed-1 sweep (6 s window, raw positions, score at the true pose):

- **Raw cone readings:** median score 0.37 (random layouts).
- **With the moving-submap version of `cone_opening`:** median 0.51 (random) and 0.66 (office), with p5 0.13 and 0.33.
- **Ideal rays from the same flights:** median 0.83-0.89.
- **Cause:** when flying straight there is no bearing diversity, so the opening has nothing to take a maximum over. Oblique walls then read about 17 % short at 45 deg incidence.

Two extra scorings followed from this, both chosen on seed 1:

- **`arc`:** each reading scores the best point on its 27 deg cone arc. Median score at truth was 0.89-0.93, and 0 of 158 / 265 passing matches were wrong at ratio 1.10.
- **`arc_fwd`:** the arc hypotheses are re-scored with a forward cone model. It ray-casts 11 sub-rays and takes the 2nd closest, as the arena sensor does. It also uses no-return readings.

### Results

Seed 2, 100 layouts per cell, A* known map, scored on truth ([submap_seed2.md](results/submap_seed2.md), [submap_seed2_extras.md](results/submap_seed2_extras.md)). Each cell shows reached % / collision % / wrong commits.

| family / fault | (i) spin_ig | (m) mcl | (s) submap | (s+ig) | (a+ig) arc | (v+ig) arc_fwd | (x) bridge only |
|---|---|---|---|---|---|---|---|
| random / dropout | 36 / 3 / 0 | 14 / 81 / 6 | 0 / 1 / 5 | 26 / 5 / 21 | 65 / 1 / 5 | 71 / 1 / 4 | 58 / 4 / 23 |
| random / jump | 53 / 3 / 0 | 15 / 77 / 14 | 1 / 0 / 4 | 30 / 4 / 19 | 87 / 1 / 2 | 89 / 0 / 2 | 54 / 5 / 10 |
| office / dropout | 52 / 35 / 0 | 1 / 97 / 6 | 15 / 12 / 16 | 22 / 23 / 23 | 54 / 20 / 2 | 66 / 19 / 6 | 40 / 46 / 19 |
| office / jump | 52 / 26 / 0 | 0 / 94 / 21 | 26 / 13 / 15 | 28 / 18 / 21 | 74 / 20 / 1 | 71 / 26 / 0 | 45 / 46 / 1 |

- **Harness parity:** the (i) and (m) rows match [mcl_seed2_spin_ig.md](results/mcl_seed2_spin_ig.md) and [mcl_seed2.md](results/mcl_seed2.md) exactly.
- **Ideal-sensor sanity row (random):** (s+ig) reached 99 % / 100 % with 1 / 2 wrong commits. (s) alone reached 81 % / 82 %.
- **Tracking ablation:** without tracking, (a+ig) drops to 58 / 75 / 32 / 59 %.

**Verdict: FAIL in every cell for every submap arm.**

- **(s) and (s+ig):**
  - The low scores trip the innovation test 120-184 times per 100 random runs.
  - Events then end `none` (score below 0.6) or `ambiguous`.
  - 15-20 of the 19-21 random-layout wrong commits came from innovation-triggered matches.
- **Extras:** collecting returns in flight plus a cone-aware score roughly doubles spin_ig in random layouts (89 % vs 53 % under jump), but it still makes 0-6 wrong commits per cell.
  - In random layouts, the remaining failures are mostly `ambiguous` after 4 moves: the second peak sits 0.4-0.6 m away along a wall.
  - In office, 16-26 % of runs collide. Those collisions happen in nominal flight with 0.1-0.7 m of error at 0.8-1.0 m doorways. For comparison, the 72-beam arm (f) collided in 7-13 %.
- **Bridge only (x):** the bridge without a map match is not enough. It reached 40-58 %, with up to 23 wrong commits.

### Limits

- Seed 2 was partly seen during development (a 6-layout probe). The scorings, tracking and move settings were tuned on seed 1.
- The bridge's accelerometer is simulated, because the arena estimator does not expose its IMU.
- Yaw is truth.
- The forward model and the arc model assume the arena's cone model, not a measured VL53L1x.
- 6 s window and 3 m range only. Only random and office layouts.
