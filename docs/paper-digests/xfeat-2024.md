# XFeat - paper digest
<!-- about: res:xfeat-2024, repo:verlab/accelerated_features -->
**XFeat: Accelerated Features for Lightweight Image Matching** - Potje, Cadar, Araujo, Martins, Nascimento (UFMG, Google, Univ. Bourgogne), CVPR 2024. [paper](https://arxiv.org/abs/2404.19174) | [code](https://github.com/verlab/accelerated_features) | Read: full text incl. appendix, arXiv HTML v1

## Problem
Learned local features (SuperPoint, DISK, ALIKE) are robust but too slow for CPU-only or small embedded boards at useful resolutions. XFeat aims at SuperPoint/DISK-level matching quality at a fraction of the compute, with no hardware-specific optimization.

## Method
- Featherweight CNN backbone on grayscale input: channels {4, 8, 24, 64, 64, 128} over six blocks, tripling instead of doubling channels, very thin early layers where resolution is high (Sec. 3.1).
- Descriptor head: 64-D dense descriptor map at 1/8 resolution, fused from 1/8, 1/16, 1/32 scales; plus a reliability map R.
- Separate keypoint branch: image reshaped into 8x8 cells => 64-D vectors, then 1x1 convs; keypoint head distilled from ALIKE-Tiny keypoints (Sec. 3.3).
- Two modes from the same weights: sparse XFeat (up to 4,096 keypoints, mutual nearest neighbour matching) and semi-dense XFeat* (top 10,000 features at two scales, plus a small MLP that classifies an 8x8 pixel offset to refine coarse matches).
- Losses: dual-softmax NLL on descriptors, L1 on reliability, NLL on refinement offsets and keypoints.
- Training: MegaDepth + synthetically warped COCO at 6:4, 800x600, converges in 36 h on one RTX 4090 (Sec. 4).

## Data and sensors
Monocular grayscale. Evaluated on MegaDepth-1500 and ScanNet-1500 (relative pose), HPatches (homography), Aachen Day-Night (localization via hloc). No aerial benchmark; no dataset card in this hub for these.

## Headline results (as reported)
- Table 1, MegaDepth-1500 (LO-RANSAC, 1200 px max dim), AUC 5/10/20 and CPU FPS at VGA on an i5-1135G7 laptop: XFeat 42.6 / 56.4 / 67.7 at 27.1 FPS; XFeat* 50.2 / 65.4 / 77.1 at 19.2 FPS; SuperPoint 37.3 / 50.1 / 61.5 at 3.0 FPS; DISK* 55.2 / 66.8 / 75.3 at 1.2 FPS; ALIKE 49.4 / 61.8 / 71.4 at 5.3 FPS; ORB 17.9 / 27.6 / 39.0 at 44.3 FPS.
- Table 2, ScanNet-1500 AUC@20: XFeat / XFeat* 47.8 / 50.3 vs SuperPoint 36.7, DISK 4k/10k 30.4 / 33.9.
- Table 3, HPatches MHA viewpoint @3/5/7px: XFeat 68.6 / 81.1 / 86.1 vs SuperPoint 71.1 / 79.6 / 83.9.
- Table 4, Aachen night (0.25m,2deg)/(0.5m,5deg)/(5m,10deg): XFeat 77.6 / 89.8 / 98.0 vs SuperPoint 77.6 / 85.7 / 95.9, DISK 83.7 / 89.8 / 99.0.
- Appendix C: on an Orange Pi Zero 3 (Cortex-A53) at 480x360, XFeat 1.8 FPS vs SuperPoint 0.16 and ALIKE 0.58 FPS (extraction only).
- Table 6 (appendix F), MegaDepth-1500 pairs per second on an i7-6700K CPU: XFeat* 1.33 vs LightGlue 0.31 vs LoFTR 0.06; LoFTR AUC@5 68.3 and LightGlue 61.4 are still well above XFeat* 50.2.

## Limitations
- Stated by authors: as a local descriptor with nearest neighbour matching, XFeat has limited robustness to aggressive viewpoint change and highly ambiguous pairs compared with transformer matchers (appendix F). Halving channels degrades results sharply (Table 5).
- Our read: pose accuracy in sparse mode is clearly below DISK and learned matchers; the win is FPS per watt. CPU-only timings in the paper; no Jetson GPU numbers. No evaluation on nadir aerial imagery or cross-season satellite pairs.

## Code, weights, license
- Repo: github.com/verlab/accelerated_features, Apache-2.0 (GitHub API and README), last push 2025-01-15, so lightly maintained.
- Weights ship in the repo and via `torch.hub`; README states Apache-2.0 for the repo with no separate weights terms. Training code available (Colab notebook).
- Later addition (README, not in paper): XFeat + LighterGlue, a smaller LightGlue trained with glue-factory, about 3x faster than LightGlue. README table, MegaDepth-1500 AUC 5/10/20 at 1024 px / 4096 kpts: 0.564 / 0.710 / 0.819 vs SuperPoint+LightGlue 0.591 / 0.738 / 0.841.
- Unlike SuperPoint, no non-commercial extractor license in the chain.

## Reproduction effort (estimate)
Estimate: first matches in 15-30 min on a CPU laptop (`pip install torch opencv-contrib-python tqdm`, torch.hub load). The repo has a realtime webcam demo. MegaDepth-1500 eval in a few hours with data download. Retraining is feasible (36 h on one RTX 4090) but not inside a 48 h event alongside other work.

## What a hackathon team can take from it
- Default front-end when there is no GPU or the GPU is busy: XFeat on CPU for frame-to-frame VO tracks or for keyframe-to-tile matching. See [XFeat card](../integration-cards/verlab__accelerated_features.md).
- XFeat* semi-dense mode helps on low-texture terrain where sparse keypoints run out, at a moderate FPS cost.
- XFeat + LighterGlue is a permissive-license replacement for SuperPoint+LightGlue with a small accuracy gap (README table).
- Inlier count and mean inlier ratio (MIR, reported in Table 1) are cheap health signals to gate a visual fix.
- Compare against SuperPoint/ALIKED on your own imagery via [vismatch](../integration-cards/gmberton__vismatch.md); Tiny RoMa in [RoMa](../integration-cards/parskatt__roma.md) also uses XFeat as backbone.
