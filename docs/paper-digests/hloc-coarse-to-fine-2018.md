# HF-Net / hloc - paper digest
<!-- about: res:hloc-coarse-to-fine-2018, repo:cvg/hierarchical-localization -->
**From Coarse to Fine: Robust Hierarchical Localization at Large Scale** - Sarlin, Cadena, Siegwart, Dymczyk (ETH Zurich ASL, Sevensense), CVPR 2019 (arXiv Dec 2018; venue per hloc README bibtex). [paper](https://arxiv.org/abs/1812.03506) | [code](https://github.com/cvg/Hierarchical-Localization) | Read: full text via ar5iv rendering of arXiv 1812.03506, plus hloc README

Note: the paper's own code is [ethz-asl/hf_net](https://github.com/ethz-asl/hf_net) (MIT). `cvg/Hierarchical-Localization` (hloc) is the later toolbox that implements the same retrieve-then-match pipeline with newer features (SuperPoint+SuperGlue/LightGlue) - it is what people actually use today.

## Problem
6-DoF localization of a single query image against a large 3D map under strong appearance change (day/night, seasons, weather), fast enough for mobile robots. Direct 2D-3D matching against the whole map is slow and brittle at scale.

## Method
- Coarse: a global descriptor (NetVLAD) retrieves the k nearest database images ("prior frames"; 10 in the appendix setup).
- Priors are grouped by covisibility in the SfM model into candidate places; each place is processed separately.
- Fine: local features (SuperPoint-style keypoints + descriptors) matched 2D-3D only against the 3D points of that place, then PnP + RANSAC. Modified ratio test 0.9; RANSAC reprojection thresholds 10 px (Aachen), 5 px (CMU), 12 px (RobotCar); minimum inliers 12 / 12 / 15.
- HF-Net: one MobileNetV2 encoder with three heads (keypoint scores, dense local descriptors, global descriptor), trained by multitask distillation from NetVLAD (global) and SuperPoint (local) teachers, with learned uncertainty loss weighting.
- Training data: 185k Google Landmarks + 37k BDD night/dawn images, grayscale 640x480.

## Data and sensors
- Monocular camera image + prebuilt SfM 3D model of the area. No IMU or GNSS.
- Aachen Day-Night (4,328 db, 824 day + 98 night queries), RobotCar Seasons (20,862 ref, 11,934 queries; see [Oxford RobotCar card](../dataset-cards/oxford-robotcar.md)), CMU Seasons (7,159 ref, 75,335 queries, evaluated on ~400-image submodels). Local features also checked on HPatches and an SfM photo-tourism set (Sec. 5.1).

## Headline results (as reported)
Table 3, % queries within 0.25 / 0.5 / 5 m (Aachen night: 0.5 / 1 / 5 m); orientation thresholds not located in our extraction.
- NV+SP (NetVLAD + SuperPoint): Aachen day 79.7/88.0/93.7, Aachen night 40.8/56.1/74.5, RobotCar night 6.6/17.1/32.2, CMU urban 91.7/94.6/97.7, CMU suburban 74.6/81.6/91.4.
- HF-Net: Aachen day 75.7/84.3/90.9, Aachen night 40.8/55.1/72.4, RobotCar night 2.7/6.6/15.8, CMU urban 90.4/93.1/96.1.
- Active Search baseline: Aachen night 19.4/30.6/43.9, CMU suburban 20.7/25.9/29.9.
- Table 5 runtime (ms, i7-7820X + GTX 1080): HF-Net total 45 (Aachen day), 55 (Aachen night), 36 (RobotCar dusk), 73 (RobotCar night); NV+SP 139-176; Active Search 375-1210. HF-Net feature extraction 15 ms. Text: ~20 FPS at large scale, ~10x faster than Active Search.
- hloc README results table (not the paper; Aachen version not stated there): SuperPoint + SuperGlue with NetVLAD top-50, Aachen day 89.6/95.4/98.8, Aachen night 86.7/93.9/100.

## Limitations
- Stated by authors: global retrieval is the bottleneck - if retrieval misses, localization fails; HF-Net's distilled global descriptor has less capacity than NetVLAD on large self-similar scenes (RobotCar night); SuperPoint keypoints less precise than DoG at the finest threshold; grayscale only (RGB hurt); no embedded hardware evaluation.
- Our read: needs a prebuilt SfM model of the operating area from ground-level images taken with a similar viewpoint. For a UAV over unmapped terrain you would build the map from satellite / orthophoto tiles or a prior flight, which the paper does not address.
- Our read: night results on RobotCar (single-digit % at 0.25 m) show the pipeline still fails under the hardest appearance change.

## Code, weights, license
- cvg/Hierarchical-Localization: Apache-2.0 (GitHub API), last push 2025-12-10, ~4.3k stars, actively maintained, Docker + Colab demo.
- Weights gotcha: the default SuperPoint/SuperGlue models come from Magic Leap's SuperGluePretrainedNetwork (GitHub license "Other" = Magic Leap non-commercial research license). hloc also supports LightGlue, DISK, SIFT, R2D2, D2-Net - use DISK/ALIKED + LightGlue for a permissive stack.
- ethz-asl/hf_net (original paper code, TensorFlow): MIT, last push 2024-07.
- Integration cards: [cvg__hierarchical-localization](../integration-cards/cvg__hierarchical-localization.md), [cvg__lightglue](../integration-cards/cvg__lightglue.md).

## Reproduction effort (estimate)
Estimate: hloc Colab demo (SfM + localize internet images) in under an hour, no local GPU needed. Aachen pipeline from `hloc/pipelines/` on a single GPU workstation: dataset download plus SfM triangulation, roughly half a day to a day. Exact HF-Net Table 3 numbers need the TF-era hf_net repo and the visuallocalization.net evaluation server - treat as not quickly reproducible.

## What a hackathon team can take from it
- The architecture pattern for any visual absolute fix: cheap global retrieval to shortlist (NetVLAD / AnyLoc / SALAD), expensive local matching only on the shortlist, geometric verification with an inlier threshold.
- Covisibility clustering of retrieved candidates is a cheap way to reject inconsistent retrieval hits before matching.
- hloc's modular extractor / matcher / retrieval config lets you swap in AnyLoc or SALAD descriptors and LightGlue without writing pipeline glue.
- Minimum-inlier thresholds (12-15) and per-dataset RANSAC pixel thresholds are a starting point for gating fixes before they enter a navigation filter.
- If you can fly the area once, building an SfM map with hloc and localizing later frames against it gives full 6-DoF fixes, not just 2D position.
