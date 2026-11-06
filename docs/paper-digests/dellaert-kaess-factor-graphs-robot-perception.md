# Factor Graphs for Robot Perception - paper digest
<!-- about: res:dellaert-kaess-factor-graphs-robot-perception, repo:borglab/gtsam -->
**Factor Graphs for Robot Perception** - Dellaert, Kaess, Foundations and Trends in Robotics Vol. 6, No. 1-2, 2017 (DOI 10.1561/2300000043), about 139 pages. [paper](https://www.cs.cmu.edu/~kaess/pub/Dellaert17fnt.pdf) | [code](https://github.com/borglab/gtsam) | Read: full text extracted from the free author PDF (figures not viewed). This is a monograph: "headline results" below are its key worked examples and claims, not benchmarks.

## Problem
How to model and solve large-scale inference in robotics (SLAM, aided navigation, mapping) in one framework that is both a clean modeling language and an efficient solver. The monograph argues factor graphs fit because each sensor measurement maps to one factor.

## Method
Chapters, in order:
- 1 Introduction: Bayes nets as generative models, MAP inference, factor graphs as the posterior p(X|Z). Running toy example: 3 poses, 2 landmarks, bearing measurements (Fig. 1.1-1.3).
- 2 Smoothing and Mapping: nonlinear least squares; linearization; Gauss-Newton, Levenberg-Marquardt, Dogleg.
- 3 Exploiting Sparsity: the sparse Jacobian is the factor graph; QR / Cholesky = variable elimination; the Cholesky factor is a Bayes net, back-substitution solves it.
- 4 Elimination Ordering: fill-in, minimum degree (COLAMD), nested dissection, block-level ordering.
- 5 Incremental Smoothing and Mapping: Givens updates, marginalization, fixed-lag smoothing, Kalman filter / smoother as special cases, Bayes tree, iSAM2.
- 6 Optimization on Manifolds: rotations, exponential map, local coordinates, PoseSLAM, Lie groups and retractions.
- 7 Applications: inertial navigation, dense 3D mapping, field robotics (underwater, agriculture), robust / non-Gaussian inference, long-term sparsification, large-scale distributed SLAM. Appendices: multifrontal Cholesky, Lie group formulas (SO(2), SE(2), SO(3), SE(3), directions).

## Data and sensors
Not a benchmark text. Examples use the toy SLAM problem, a simulated 2D SLAM problem, Victoria Park (Fig. 4.8), MIT Stata Center multi-session maps (Fig. 5.1), [KITTI](../dataset-cards/kitti.md) for aided inertial navigation (Fig. 7.1, reproduced from cited work), sonar ship-hull inspection, crop monitoring.

## Headline results (as reported)
Worked examples and claims, not benchmarks:
- Fig. 4.2: a 2D SLAM problem with 3x95 + 2x24 = 333 unknowns and 1126 scalar measurement rows, used to show how ordering changes the Cholesky factor.
- Figs. 4.4-4.6: eliminating all landmarks first (the "Schur complement trick") densifies the pose graph; COLAMD ordering drops non-zeros in R from about 2.8 million to about 250 thousand.
- Fig. 4.7: block-level (pose / landmark) ordering gets to about 130K non-zeros, a factor of 20 below the original R; block-level AMD is about 2x better than scalar-level.
- Fig. 4.8: nested dissection on Victoria Park, 4 partition levels (basis of TSAM divide-and-conquer).
- Sec. 5.3: the Kalman filter and smoother are special cases of incrementally updating a linear system on a chain graph; fixed-lag smoothing = measurement update + marginalization (Fig. 5.4, lag n=3).
- Fig. 7.1 (cited work): on a KITTI sequence, incremental smoothing performs almost as well as full batch; fixed-lag results shown for several lags. Plot not viewed; no number extracted.
- Sec. 7.1: IMU preintegration between lower-rate camera / lidar measurements is presented as the way to combine high-rate IMU with fixed-lag smoothing (points to Forster et al.).
- Sec. 7.6 / Fig. 7.11: plug-and-play navigation architecture from the DARPA ASPN project; concurrent filtering and smoothing ran land, sea and air trials with sensors switching on and off.

## Limitations
- Stated by authors: the applications chapter is "not meant to be a comprehensive review". Finding an optimal ordering is NP-complete; heuristics only. Marginalization destroys sparsity in SLAM.
- Our read: the index summary says the book argues "smoothing beats filtering"; what it actually shows is that filtering is a special case of the same elimination machinery and that smoothing keeps sparsity. No head-to-head accuracy table.
- Our read: written for GTSAM 3/4-era APIs; code-level details are conceptual, not copy-paste for GTSAM 4.3.
- Our read: robust / non-Gaussian inference gets only a few pages; outlier handling for spoofed or multipath GNSS needs other sources.

## Code, weights, license
- Companion library GTSAM (`borglab/gtsam`): simplified BSD per LICENSE / LICENSE.BSD; GitHub API shows NOASSERTION because bundled third-party code uses BSD-3, MPL2 and Apache 2.0. Actively maintained, last push 2026-11-06. No weights.
- The monograph PDF is free on the author site; publisher copyright applies to the text.

## Reproduction effort (estimate)
Estimate:
- Nothing to reproduce as such. Reading time: 1-2 hours for chapters 1-3 and 5; skip 4 and 6 unless you hit ordering or manifold bugs.
- To turn chapters into running code: GTSAM Python examples, under 1 hour after `pip install gtsam`.

## What a hackathon team can take from it
- Mental model for multi-sensor nav: one factor per measurement type. Adding a magnetometer, a visual fix or a terrain match is a new factor, not a filter redesign. Start from the [GTSAM integration card](../integration-cards/borglab__gtsam.md).
- Fixed-lag smoothing (Sec. 5.3.2) is the bounded-compute choice for an onboard estimator; full iSAM2 for offline or short demos.
- When a solve gets slow: check ordering and fill-in first (chapter 4) before buying hardware.
- The plug-and-play ASPN architecture (Fig. 7.11) is a ready pitch for "sensors come and go under jamming" scenarios.
- Read chapter 7.1 together with the [Forster preintegration digest](forster-imu-preintegration.md) and the [iSAM2 digest](kaess-isam2.md).
