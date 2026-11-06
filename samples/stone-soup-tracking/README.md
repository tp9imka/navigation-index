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

- Python 3.10+.
- `python3 -m pip install stonesoup` (pulls numpy, scipy and friends). Not installed in the
  environment this sample was written in.

## Run

```sh
cd samples/stone-soup-tracking
python3 radar_jpda_ospa.py
```

## Expected output

Not run here (no numpy/Stone Soup available), so no observed numbers. The script prints:

```
scans=60 tracks=2 truths=2
OSPA (c=100 m, p=1): mean=<m> m max=<m> m final=<m> m
track <id8> final position x=<m> m y=<m> m
track <id8> final position x=<m> m y=<m> m
```

Sanity expectation, not a measured result: with 10 m range noise and 1 deg bearing noise
at ~1.5 km (about 26 m cross-range), mean OSPA should sit well under the 100 m cutoff. A
value pinned at 100 m means a track was lost or swapped.

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
- `np.random.seed` makes the run repeatable; remove it for Monte Carlo runs.
- The generated metric title is `"OSPA distances"`; check it if you upgrade Stone Soup.
