# iSAM2 - paper digest
<!-- about: res:kaess-isam2, repo:borglab/gtsam -->
**iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree** - Kaess, Johannsson, Roberts, Ila, Leonard, Dellaert, International Journal of Robotics Research 2012. [paper](https://www.cs.cmu.edu/~kaess/pub/Kaess12ijrr.pdf) | [code](https://github.com/borglab/gtsam) | Read: full text of the author PDF, which is marked "Draft manuscript, April 6, 2011. Submitted to IJRR" (text extracted from the PDF; figures not viewed). Final IJRR page numbers may differ.

## Problem
Online SLAM / sensor fusion needs the full smoothing solution (all past poses) updated every step. Batch sparse factorization gets too expensive as the graph grows. The original iSAM updates the linear system incrementally but needs periodic batch steps for variable reordering and relinearization, which cause spikes and fill-in.

## Method
- **Bayes tree**: a directed tree of cliques encoding the factored density; maps to the square-root information matrix (like a clique tree but directed). Adding a factor only touches the cliques on the path from the affected variables to the root.
- Incremental update = detach the affected top of the tree, re-eliminate it into a factor graph, re-insert orphaned subtrees. No matrix-level bookkeeping.
- **Incremental variable reordering**: the re-eliminated top is reordered with constrained COLAMD (CCOLAMD), forcing the most recent variables to the root so future updates stay cheap.
- **Fluid relinearization**: only variables whose delta exceeds threshold beta are relinearized, and only their cliques and ancestors are redone. No periodic batch relinearization.
- **Partial state updates**: back-substitution stops descending when the change falls below threshold alpha, so far-away variables are not touched.
- One step (Alg. 8): add factors, init new variables, fluid relinearization, redo top of tree, partial solve.

## Data and sensors
- Sensor-agnostic. 2D pose graphs: City20000, W10000 (simulated), Manhattan (Olson), Intel, Killian Court (laser). 2D with landmarks: Trees10000 (sim), Victoria Park (laser). 3D: Sphere2500, Torus10000 (simulated, from the iSAM1 distribution).
- No [dataset card](../dataset-cards/) exists for these classic SLAM sets.

## Headline results (as reported)
- Setup (Sec. 5): laptop with Intel 1.6 GHz i7-720, single-threaded research C++ implementation, CCOLAMD, alpha = 0.001, beta = 0.1, relinearization checked every 10 steps.
- Table 1, average / std / max per step [ms] and total [s], iSAM2 vs iSAM1 vs HOG-Man vs SPA:
  - City20000: iSAM2 16.1/65.6/1125 ms, 323 s; iSAM1 7.05 ms, 141 s; HOG-Man 548 s; SPA 977 s.
  - W10000: iSAM2 22.4 ms, 224 s; iSAM1 357 s; HOG-Man 16.4 ms, 164 s (fastest); SPA 1081 s.
  - Intel: iSAM2 1.74 ms, 1.59 s; iSAM1 5.28 s; HOG-Man 8.55 s; SPA 4.44 s.
  - Victoria Park (with landmarks): iSAM2 2.34 ms, 16.3 s; iSAM1 16.4 s.
  - Torus10000 (3D): iSAM2 35.2 ms, 352 s; iSAM1 864 s; HOG-Man 990 s.
- Sec. 5.1: iSAM2 consistently faster than SPA and similar to iSAM1; iSAM1 degrades on dense graphs (W10000, Intel) due to fill-in between its every-100-step reorderings. iSAM2 spikes follow SPA's pattern but are almost an order of magnitude higher (research code vs CHOLMOD). Fig. 15: elimination dominates iSAM2 time.
- Sec. 5.3 / Fig. 16: normalized chi-square of iSAM2 "very close" to the per-step converged least-squares solution; small spikes from relinearizing every 10 steps; HOG-Man consistently larger error.
- Fig. 8: iSAM2 fill-in stays close to batch, without the local fill-in growth iSAM1 shows.

## Limitations
- Stated by authors: update steps are not constant time; a large loop closure can cost as much as a batch solve. HOG-Man is faster on dense W10000. Per-step spikes are higher than SPA because no optimized library underlies the Bayes tree yet.
- Our read: the worst-case max column matters for real-time nav (1125 ms max on City20000). For an onboard estimator, bound the graph with a fixed-lag smoother rather than trusting the average.
- Our read: alpha and beta are accuracy / speed knobs with no automatic tuning; the paper's values are a starting point, not universal.

## Code, weights, license
- Production implementation is GTSAM's `ISAM2` (`ISAM2Params` exposes relinearize threshold and skip, mirroring beta and the every-10-steps setting). Also `IncrementalFixedLagSmoother` in gtsam_unstable / `BatchFixedLagSmoother`.
- GTSAM: simplified BSD per LICENSE / LICENSE.BSD (GitHub API shows NOASSERTION because of bundled third-party licenses: BSD-3, MPL2, Apache 2.0). Last push 2026-11-06. No weights (not learned).

## Reproduction effort (estimate)
Estimate:
- Hardware: any laptop.
- Data: GTSAM example data includes several classic pose-graph files (which ones match the paper's not checked).
- Time to first result: under 1 hour to run an ISAM2 Python example from GTSAM. Reproducing Table 1 exactly is not practical: HOG-Man / SPA versions from 2010 and the original research code are gone.

## What a hackathon team can take from it
- Use `gtsam.ISAM2` as the online back end for any IMU + intermittent-fix estimator: each new keyframe is one `update()` call, and a late or out-of-order GNSS / visual fix is just another factor. See the [GTSAM integration card](../integration-cards/borglab__gtsam.md).
- Tuning knobs with meaning: relinearization threshold (beta, paper 0.1) and relinearize skip (paper 10). Lower beta for agile platforms; raise skip if per-step latency spikes.
- For a demo that runs for hours, wrap in a fixed-lag smoother to cap the worst-case step time.
- Smoothing vs filtering argument for judges: iSAM2 revises past poses when a fix arrives after an outage, which an EKF cannot.
