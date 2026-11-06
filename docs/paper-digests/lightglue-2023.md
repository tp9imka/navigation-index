# LightGlue - paper digest
<!-- about: res:lightglue-2023, repo:cvg/lightglue -->
**LightGlue: Local Feature Matching at Light Speed** - Lindenberger, Sarlin, Pollefeys (ETH Zurich, Microsoft), ICCV 2023. [paper](https://arxiv.org/abs/2306.13643) | [code](https://github.com/cvg/LightGlue) | Read: full text incl. appendix, arXiv HTML v1

## Problem
SuperGlue-style learned matchers are accurate on hard pairs (viewpoint, day/night) but slow and hard to train. Tracking and large-scale mapping need low latency. LightGlue keeps SuperGlue's robustness while cutting run time and training cost.

## Method
- Input: two sets of sparse keypoints + descriptors from any extractor (trained for SuperPoint, DISK, SIFT; ALIKED weights added later in the repo).
- 9 layers (L=9), each one self-attention + one bidirectional cross-attention unit, 4 heads, d=256 (Sec. 4).
- Relative (rotary) positional encoding added in every self-attention unit instead of SuperGlue's absolute MLP encoding.
- Light assignment head: pairwise similarity plus a separate per-point "matchability" score replaces Sinkhorn optimal transport and the dustbin.
- Deep supervision: a match prediction after every layer. A small confidence classifier decides when to stop (exit when a ratio alpha of points is confident, Eq. 10).
- Point pruning: points confidently unmatchable (e.g. outside covisible area) are dropped between layers, so attention cost shrinks on low-overlap pairs.
- Training: pre-train on synthetic homographies (1M images), fine-tune on MegaDepth. Reported 2 GPU-days to beat SuperGlue's loss (Fig. 5).

## Data and sensors
Monocular images, any camera. Evaluated on HPatches (homography), MegaDepth-1500 (relative pose), Aachen Day-Night v1.1 and InLoc (localization via hloc), IMC 2020/2021/2023. None of these are aerial; no dataset card in this hub for them.

## Headline results (as reported)
- Table 1, HPatches, SuperPoint 1024 kpts: LightGlue R 94.3 / P 88.9; AUC RANSAC @1px 38.3, @5px 79.6; AUC DLT @1px 35.9, @5px 78.6. SuperGlue P 87.4, DLT @5px 76.7. LoFTR (top 1024 matches) RANSAC @5px 78.8.
- Table 2, MegaDepth-1500, SuperPoint 2048 kpts: LightGlue LO-RANSAC AUC 5/10/20 = 66.7 / 79.3 / 87.9 at 44.2 ms; adaptive variant 66.3 / 79.0 / 87.9 at 31.4 ms. SuperGlue 65.8 / 78.7 / 87.5 at 70.0 ms. LoFTR 66.4 / 78.6 / 86.5 at 181 ms.
- Table 2, DISK+LightGlue LO-RANSAC 61.3 / 74.3 / 83.8 at 44.5 ms vs DISK NN+ratio 57.2 / 69.5 / 78.6.
- Table 3, Aachen Day-Night: LightGlue night (0.25m,2deg)/(0.5m,5deg)/(1m,10deg) = 87.8 / 93.9 / 100 vs SuperGlue 86.7 / 92.9 / 100; throughput 17.2 pairs/s (26.1 optimized) vs SuperGlue 6.5.
- Table 5, adaptivity on MegaDepth: speedup over non-adaptive 1.86x on easy pairs, 1.16x on hard, 1.45x average. Fig. 8 caption: easy pairs stop after 2-3 layers, "close to 100 FPS".
- Hardware: all timings on a single RTX 3080 10GB, matching only, extraction and RANSAC excluded (Appendix D).

## Limitations
- Stated by authors: InLoc failures (6/356 images @1m) from matching repeated strongly textured objects instead of scene structure (Table 10, Fig. 10). Adaptive gains shrink on hard / low-overlap pairs (Table 5).
- Our read: all benchmarks are ground-level phototourism or indoor. No aerial nadir, no cross-modal (thermal/satellite) or seasonal-change evaluation. Timings exclude the extractor, which on Jetson can dominate. Accuracy ceiling is set by the extractor's repeatability, so low-texture terrain is still a weak spot for any sparse pipeline.

## Code, weights, license
- Repo: github.com/cvg/LightGlue, Apache-2.0 (GitHub API), last push 2026-10-25, actively maintained. Also in Hugging Face Transformers and kornia.
- LightGlue weights: Apache-2.0 (README).
- Extractor licenses differ (README "License"): SuperPoint weights and its inference file `lightglue/superpoint.py` are under Magic Leap's restrictive non-commercial license. DISK Apache-2.0. ALIKED BSD-3-Clause. SIFT has no weights.
- Gotcha: the README quick-start and the default `features` argument use SuperPoint. For anything beyond research, use ALIKED+LightGlue or DISK+LightGlue.

## Reproduction effort (estimate)
Estimate: inference in under 30 minutes on any CUDA GPU (or CPU, slower) via `pip install -e .`; weights download automatically. Reproducing Table 2 needs the MegaDepth-1500 test set and glue-factory, roughly half a day. Retraining needs the 1M-image homography set plus MegaDepth and about 4 GPU-days on 2x RTX 3090 class GPUs (Appendix C); not realistic in 48 h. Jetson timings are not in the paper; measure your own.

## What a hackathon team can take from it
- Drop-in fine matcher for frame-to-map-tile registration: retrieval gives top-k tiles, ALIKED+LightGlue + RANSAC homography gives the pose fix. See [LightGlue card](../integration-cards/cvg__lightglue.md) and [hloc card](../integration-cards/cvg__hierarchical-localization.md).
- Use the adaptive exit as a latency knob: `depth_confidence` / `width_confidence` trade accuracy for time; consecutive VO frames are the easy case (1.86x).
- Matchability score per point is a free outlier signal: count of confident matches after RANSAC is a usable gate before you feed a visual fix into the EKF.
- Deployment on Jetson: export with [LightGlue-ONNX](../integration-cards/fabio-sim__lightglue-onnx.md) to TensorRT.
- For a matcher shoot-out on your own drone/satellite pairs, run several matchers through [vismatch](../integration-cards/gmberton__vismatch.md) first.
