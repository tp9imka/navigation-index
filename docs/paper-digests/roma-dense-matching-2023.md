# RoMa - paper digest
<!-- about: res:roma-dense-matching-2023, repo:parskatt/roma -->
**RoMa: Robust Dense Feature Matching** - Edstedt, Sun, Bokman, Wadenback, Felsberg (Linkoping Univ. et al.), CVPR 2024. [paper](https://arxiv.org/abs/2305.15404) | [code](https://github.com/Parskatt/RoMa) | Read: full text, arXiv HTML v2

## Problem
Dense matchers trained from scratch on limited 3D-supervised data (MegaDepth, ScanNet) overfit and break under extreme appearance or viewpoint change. RoMa targets robustness: matching pairs where most methods fail (the WxBS benchmark).

## Method
- Built on DKM (dense kernelized matching): global coarse match, then a stack of ConvNet refiners at strides 8/4/2/1 that predict warp residuals and certainty.
- Coarse features: frozen DINOv2 (foundation model). Table 1 shows DINOv2 features are much more robust than VGG19/ResNet50 for coarse matching.
- Fine features: a separate specialized VGG19 ConvNet, because DINOv2 patches are too coarse to localize. Not sharing weights between coarse and fine features helped (Table 2, setup II).
- Transformer match decoder that predicts anchor probabilities (classification over coarse cells) instead of regressing coordinates, so the coarse stage can express multimodal hypotheses.
- Loss: regression-by-classification for the coarse stage, robust (generalized Charbonnier) regression for refinement.
- Output: a dense warp A=>B plus per-pixel certainty; matches are sampled from it (10,000 matches with balanced sampling in the paper, Sec. 4.3).
- Trained on MegaDepth + ScanNet at 560x560 (Sec. 4.2).

## Data and sensors
Monocular RGB pairs. Evaluated on IMC2022, WxBS, MegaDepth-1500, ScanNet-1500, MegaDepth-8-Scenes, InLoc. No aerial or satellite benchmark in the paper; no matching dataset card in this hub.

## Headline results (as reported)
- Table 4, WxBS mAA@10px: RoMa 80.1 vs DKM 58.9, LoFTR 55.4, DISK+LightGlue 41.7, SP+SuperGlue 31.4. This is the "36%" headline.
- Table 3, IMC2022 mAA@10: RoMa 88.0 vs DKM 83.1, ASpanFormer 83.8, LoFTR 78.3.
- Table 5, MegaDepth-1500 AUC 5/10/20: RoMa 62.6 / 76.7 / 86.3 vs DKM 60.4 / 74.9 / 85.1, LightGlue 51.0 / 68.1 / 80.7.
- Table 6, ScanNet-1500 AUC 5/10/20: RoMa 31.8 / 53.4 / 70.9 vs DKM 29.4 / 50.7 / 68.3.
- Table 8, InLoc DUC1 / DUC2 at (0.25m,2deg)/(0.5m,5deg)/(1m,10deg): RoMa 60.6 / 79.3 / 89.9 and 66.4 / 83.2 / 87.8.
- Runtime (Sec. 4.5): 198.8 ms per pair vs DKM 186.3 ms, at 560x560, batch size 8, on an RTX6000.

## Limitations
- Stated by authors: relies on supervised correspondences, which limits usable training data; trained on matching as a proxy rather than on downstream pose/localization directly (Sec. 5).
- Our read: ~200 ms per pair on a workstation GPU with a ViT-L DINOv2 backbone is far from real time on a Jetson; this is a relocalization / map-building tool, not a per-frame VO matcher. Note the LightGlue numbers in Table 5 (51.0 AUC@5) are lower than LightGlue's own paper (Table 2 there: 66.7 with LO-RANSAC), because protocols and RANSAC differ; do not compare across papers.

## Code, weights, license
- Repo: github.com/Parskatt/RoMa, MIT (GitHub API), last push 2026-01-23. PyPI package `romatch`.
- README: "All our code except DINOv2 is MIT license. DINOv2 has an Apache 2 license."
- Weights: `roma_outdoor.pth`, `roma_indoor.pth`, `tiny_roma_v1_outdoor.pth` downloaded from GitHub releases of Parskatt/storage, plus DINOv2 ViT-L/14 from Meta's CDN (`romatch/models/model_zoo/__init__.py`). No separate weights license stated in README.
- Tiny RoMa v1 uses XFeat as backbone (same file). The source also references a separate RoMaV2 repo; not reviewed here.

## Reproduction effort (estimate)
Estimate: inference in 30-60 min on a CUDA GPU (`uv pip install romatch`, first run downloads RoMa weights plus DINOv2 ViT-L/14 weights). Running the MegaDepth-1500 test is a few hours including data. Training uses 4 GPUs via torchrun plus the DKM data pipeline; not feasible in a hackathon. The README notes float32 matmul precision must be "highest" or the model raises an error.

## What a hackathon team can take from it
- Best-in-class robustness for hard pairs: drone frame vs older satellite tile, different season or sensor. Use it as the offline or low-rate (e.g. 1 Hz) absolute fix, not in the VO loop. See [RoMa card](../integration-cards/parskatt__roma.md).
- The certainty map is a ready-made gate: sample only above `sample_thresh`, and use certainty mass or RANSAC inlier count to decide whether to trust the fix.
- Coarse-to-fine split is a reusable idea: frozen foundation features for "which region", small CNN for "which pixel".
- If you need a lighter variant, try Tiny RoMa (XFeat backbone) and compare on your own data via [vismatch](../integration-cards/gmberton__vismatch.md).
