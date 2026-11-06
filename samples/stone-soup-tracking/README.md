# Stone Soup multi-target tracking for C-UAS airspace awareness

Goal: the "what is in our airspace" picture for a counter-UAS or airspace-awareness demo.
One ground radar reports noisy bearing/range plots of two small UAVs plus clutter. Stone
Soup's Extended Kalman filter and Joint Probabilistic Data Association (JPDA) keep one
track per UAV, and the OSPA metric scores the tracks against ground truth. This is the
detect-and-track layer only: it feeds a display or an alerting rule, nothing else.

## Repo used

| Repo | Why |
|---|---|
| `repo:dstl/stone-soup` | Dstl's open tracking framework. Swappable transition/measurement models, predictors, updaters, hypothesisers, data associators and metric generators, with tutorials that use exactly these classes. |

Class names follow the Stone Soup tutorials `docs/tutorials/02_ExtendedKalmanFilterTutorial.py`
(`CartesianToBearingRange`, `ExtendedKalmanPredictor`, `ExtendedKalmanUpdater`),
`docs/tutorials/08_JPDATutorial.py` (`PDAHypothesiser`, `JPDA`, `gm_reduce_single`,
`GaussianStateUpdate`) and `docs/examples/metrics/Metrics.py` (`OSPAMetric`, `MultiManager`).

## Prerequisites

- Python 3.10+ (ran with 3.12.14).
- `python3 -m pip install -r requirements.txt` (stonesoup 1.9.1, numpy 2.5.4, scipy 1.18.1).

## Run

```sh
cd samples/stone-soup-tracking
python3 -m pip install -r requirements.txt
python3 radar_jpda_ospa.py
```

## Observed output (stonesoup 1.9.1, Python 3.12.14, 2026-11-06)

```
scans=60 tracks=2 truths=2
OSPA (c=100 m, p=1): mean=17.0 m max=53.0 m final=27.1 m
track 0 final position x=-776 m y=437 m
track 1 final position x=-546 m y=461 m
truth 0 final position x=-770 m y=458 m
truth 1 final position x=-556 m y=430 m
```

Identical on three consecutive runs. Each track ends within ~33 m of the truth it started
on, and mean OSPA stays well below the 100 m cutoff, so neither target was lost or
swapped in this run. One seed, one scenario: not a Monte Carlo result.

The first run of the original sketch gave different numbers on every run despite
`np.random.seed`: truths and tracks were kept in `set`s, whose order follows random
UUIDs, so the noise draws were applied to the two targets in a different order each
time. They are lists now and are wrapped in `set(...)` only where Stone Soup wants sets
(`JPDA.associate`, `MultiManager.add_data`).

## What the script does

1. Builds two `GroundTruthPath`s with `CombinedLinearGaussianTransitionModel` of two
   `ConstantVelocity` models (state `[x, vx, y, vy]`).
2. Simulates a radar at the origin with `CartesianToBearingRange`: `TrueDetection` with
   probability `PROB_DETECT`, plus Poisson-count `Clutter` uniform in bearing and range.
3. Tracks with `ExtendedKalmanPredictor` / `ExtendedKalmanUpdater`, `PDAHypothesiser` and
   `JPDA`, merging each track's weighted hypotheses with `gm_reduce_single`.
4. Scores with `OSPAMetric(c, p, measure=Euclidean((0, 2)))` inside a `MultiManager`
   (position only; velocity in the distance would mix units).

## Extending it in a hackathon

- Replace known priors with `MultiMeasurementInitiator` and a `UpdateTimeStepsDeleter`
  (tutorial `09_Initiators_&_Deleters.py`) so pop-up drones start tracks on their own.
- Fuse a second sensor (RF direction-finding or an EO camera bearing-only model) by
  running the updater with each detection's own `measurement_model`.
- Feed live plots: wrap your radar's UDP output in a Stone Soup detection reader.
- Push confirmed tracks to TAK as CoT using `samples/mavlink-to-tak-cot/cot.py` with an
  unknown/suspect affiliation type instead of the friendly one.
- Compare `GNN` (`GlobalNearestNeighbour`) against `JPDA` on OSPA when targets cross.

## Pitfalls

- `clutter_spatial_density` must match the clutter you simulate: expected false alarms
  divided by measurement-space volume (here `2*pi*MAX_RANGE_M` in bearing x range).
- Bearing wraps at +-pi; build clutter with `Bearing(...)` so residuals wrap correctly.
- `OSPAMetric` without `measure=Euclidean((0, 2))` measures the full state vector.
- `np.random.seed` makes the run repeatable only if the draw order is fixed too: iterate
  over lists, not sets of Stone Soup objects (their hash is a random UUID).
  Remove the seed for Monte Carlo runs.
- The generated metric title is `"OSPA distances"`; check it if you upgrade Stone Soup.
