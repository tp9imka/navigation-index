# AnyVisLoc - paper digest
<!-- about: res:anyvisloc-uav-localization-benchmark-2025, repo:uav-avl/benchmark -->
**Exploring the best way for UAV visual localization under Low-altitude Multi-view Observation Condition: a Benchmark** - Ye, Teng, Chen et al., arXiv 2025 (README: accepted to CVPR 2026 Findings). [paper](https://arxiv.org/abs/2503.10692) | [code](https://github.com/UAV-AVL/Benchmark) | Read: full text, arXiv HTML v2 (13 Apr 2026), last ~2% of the page not read; repo README

## Problem
Absolute visual localization (AVL) of a UAV against geo-tagged maps when GNSS is denied. Prior work mostly assumes nadir views and planar scenes. Low-altitude oblique imagery breaks that, and nobody had measured how far current retrieval and matching methods fall off there.

## Method
Not a new model - a benchmark plus a unified coarse-to-fine baseline:
- Retrieval: crop the reference map into a gallery, rank tiles against the UAV image (template matching NCC/MI, NetVLAD, CNN/transformer cross-view models such as CAMP, Sample4Geo, MCCG).
- Matching: pixel correspondences between UAV image and top tiles (SIFT, ORB, SuperPoint+LightGlue variants incl. GIM/MINIMA weights, XFeat, LoFTR, DKM, RoMa ...).
- Pose: 2D-3D via the map's DSM, then P3P + RANSAC => 6-DoF pose and position.
- Strategies compared: Top-1 matching, Top-N re-rank by inlier count, match all tiles ("Most Inliers"), match without retrieval.
- Priors: altitude, pitch and yaw are used to set tile scale and rotation and to shrink the search space.
- Retrieval weights trained on University-1652 at 384x384 (not on AnyVisLoc).
- New retrieval metric PDM@K (distance-weighted, normalized by image width and map resolution; lambda 6, alpha 0.9).

## Data and sensors
- Sensors assumed: monocular RGB stills plus coarse altitude/attitude priors. No IMU stream, no video.
- Dataset card: [AnyVisLoc](../dataset-cards/anyvisloc.md). Two 2.5D references per scene: aerial orthomosaic + DSM (avg 0.070 m GSD) and Google Earth satellite + ALOS 30 m DSM (avg 0.197 m GSD).
- Paper v2 numbers: 18,000 images, 7 DJI models, 15 cities / 25 regions, altitude 30-300 m, pitch 20-90 deg. The repo README describes the public release differently: 20,077 images, 24 scenes, about 6-500 m, pitch about 5-90 deg (three scenes removed, two added). Paper tables were computed on the paper version, not the release.
- Metric: A@T = share of images localized within T m (T = 5, 7, 10, 15, 20).

## Headline results (as reported)
- Table 6, baseline CAMP + RoMa + Top-N re-rank, aerial map: A@5m 74.1, A@10m 87.7, A@20m 94.2; retrieval R@1 61.6.
- Table 6, same baseline, satellite map: A@5m 18.5, A@10m 38.7, A@20m 58.5; R@1 42.8.
- Table 2, retrieval R@1/R@3/R@5: CAMP 62.4/82.7/88.3, Sample4Geo 58.6/79.9/86.4, MCCG 56.7/80.5/88.6, NetVLAD 31.1/53.9/64.9, NCC 0.3/1.5/2.6.
- Table 4, matchers with Top-1 + CAMP (A@5m / A@20m, ms/frame): RoMa 70.1/87.6, 659 ms; DKM (GIM) 65.6/86.4, 4915 ms; SP+LG (GIM weights) 57.0/84.8, 105 ms; SP+LG 46.6/71.7, 76 ms; SIFT 43.9/62.5, 316 ms CPU; ORB 3.9/13.6, 44 ms CPU.
- Table 5, strategies (A@5m / A@10m / A@20m, s/frame): no retrieval 34.3/45.7/54.3, 1.4 s; Top-1 55.8/74.3/84.0, 0.3 s; Top-5 re-rank 62.2/82.4/91.5, 0.8 s; Most Inliers 64.0/83.2/92.6, 10.2 s.
- Table 7, yaw prior noise (A@5m, 0-noise ref 74.6): std 10 deg 72.7, 30 deg 70.5, 60 deg 48.9. Pitch std 30 deg: 69.7.
- Hardware: i9-10920X, 128 GB RAM, RTX 3090 24 GB.

## Limitations
- Stated by authors: retrieval is the weak link (wrong Top-1 kills Top-1 matching); dense matchers are slow and the best strategy is not real-time; satellite references give poor precision while aerial references need a prior photogrammetry survey; yaw/pitch noise degrades accuracy; 74.1% A@5m "may not meet" precise AVL needs; China only.
- Our read: the abstract/Table 6 baseline (74.1) and the Table 7 reference (74.6) disagree slightly; quoted drops use 74.6.
- Our read: the realistic case for a team without a pre-surveyed aerial map is the satellite row - A@20m 58.5, i.e. roughly 4 in 10 fixes worse than 20 m. That needs outlier gating before it touches a filter.
- Our read: all per-frame; no temporal fusion, no VIO, so it says nothing about how fixes behave inside a nav filter.

## Code, weights, license
- Repo UAV-AVL/Benchmark: GitHub API reports no license for the code (no LICENSE file; only docs/LICENSE_DATASET.md). Last push 2026-10-10. Active.
- Dataset: AnyVisLoc Dataset License - non-commercial research/education/internal evaluation only, no redistribution or mirroring, no public derived subsets. Download via Baidu NetDisk / OneDrive only.
- Weights: none of their own. Pulls third-party checkpoints (CAMP, RoMa + DINOv2 ViT-L/14, GIM LightGlue, MINIMA LightGlue), each "subject to the licenses ... of their original authors" (README). SuperPoint-based pipelines inherit Magic Leap's non-commercial SuperPoint terms.
- Satellite imagery is Google Earth historical imagery under Google's terms; DSM is JAXA AW3D30.

## Reproduction effort (estimate)
Estimate:
- Hardware: one 24 GB NVIDIA GPU (README tested on RTX 4090, Python 3.10, PyTorch 2.5.1, CUDA 12.1). RoMa with DINOv2 ViT-L is the memory hog.
- Data: full dataset via Baidu/OneDrive (size not stated); weights from 5 separate sources or one Baidu bundle. Baidu can be slow or blocked outside China - budget time.
- Time to first result: half a day to get `run_avl.py` on one scene; full-benchmark sweep is GPU-days at 0.8-10 s/frame.
- Not reproducible here: the exact paper numbers (release differs from paper split); anything you would publish, given the licence.

## What a hackathon team can take from it
- The pipeline shape: retrieval => matching => PnP against an orthophoto + DSM. Use [RoMa](../integration-cards/parskatt__roma.md) when accuracy matters, [LightGlue](../integration-cards/cvg__lightglue.md) (or [LightGlue ONNX](../integration-cards/fabio-sim__lightglue-onnx.md)) when you need ~100 ms.
- Top-5 re-rank by inlier count is the cheap win: Table 5 shows +6.4 pts A@5m over Top-1 for 0.5 s more per frame.
- Inlier count after re-rank is a natural gate for whether to pass the fix to the EKF; tune the threshold on a held-out scene.
- Use attitude/altitude from the autopilot to pre-rotate and scale tiles; Table 7 says yaw error up to 10-30 deg is tolerable, 60 deg is not.
- A@5/10/20 m is a clean, team-agnostic evaluation protocol to report in a demo.
