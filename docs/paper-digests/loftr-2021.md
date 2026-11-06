# LoFTR - paper digest
<!-- about: repo:zju3dv/loftr -->
**LoFTR: Detector-Free Local Feature Matching with Transformers** - Sun, Shen, Wang, Bao, Zhou (Zhejiang Univ., SenseTime), CVPR 2021. [paper](https://arxiv.org/abs/2104.00680) | [code](https://github.com/zju3dv/LoFTR) | Read: main paper, arXiv HTML v1 (supplementary not included in that render)

## Problem
Detector-based pipelines fail when the detector finds no repeatable keypoints: low texture, repetitive patterns, motion blur, illumination change. LoFTR skips detection and matches on a dense grid, using transformer attention for global context so even blank regions get distinctive features.

## Method
- ResNet-18 + FPN backbone gives coarse features at 1/8 and fine features at 1/2 resolution (Sec. 3.1).
- Coarse features + 2D sinusoidal positional encoding go through N_c=4 interleaved self/cross-attention layers using linear attention (O(N) instead of O(N^2)) (Sec. 3.2, 3.6).
- Coarse matching by dual-softmax (DS) or optimal transport (OT) on the score matrix; keep mutual nearest neighbours above confidence 0.2 (Sec. 3.3, 3.6).
- Coarse-to-fine: for each coarse match, crop a 5x5 window at 1/2 resolution, run one more small transformer (N_f=1), and take the expectation of a correlation heatmap for sub-pixel position (Sec. 3.4).
- Supervision: NLL on coarse confidence from depth + pose ground truth, uncertainty-weighted L2 on fine positions.
- Separate indoor (ScanNet) and outdoor (MegaDepth) models. Indoor training: 24 h on 64 GTX 1080Ti (Sec. 3.6).

## Data and sensors
Monocular image pairs. Evaluated on HPatches, ScanNet-1500, MegaDepth-1500, Aachen Day-Night v1.1, InLoc. No aerial benchmark; no dataset card in this hub for these.

## Headline results (as reported)
- Table 1, HPatches homography AUC @3/5/10px: LoFTR-DS 65.9 / 75.6 / 84.6 vs SP+SuperGlue 53.9 / 68.3 / 81.7.
- Table 2, ScanNet pose AUC @5/10/20: LoFTR-DS 22.06 / 40.8 / 57.62 vs SP+SuperGlue 16.16 / 33.81 / 51.84.
- Table 3, MegaDepth pose AUC @5/10/20: LoFTR-DS 52.8 / 69.19 / 81.18 vs SP+SuperGlue 42.18 / 61.16 / 75.96.
- Table 4, Aachen v1.1 full localization with hloc, night: LoFTR-OT 78.5 / 90.6 / 99.0 vs SP+SuperGlue 77.0 / 90.6 / 100.0; day slightly worse than SP+SuperGlue (88.7 vs 89.8 at the tightest threshold).
- Table 5, InLoc DUC1: LoFTR-OT 47.5 / 72.2 / 84.8 vs SP+SuperGlue 49.0 / 68.7 / 80.8.
- Runtime (Sec. 3.6): 116 ms per 640x480 pair with dual-softmax, 130 ms with OT, on an RTX 2080Ti.
- Later context, not from this paper: LightGlue Table 2 reports LoFTR at 181 ms on MegaDepth-1500 (840 px) on an RTX 3080, about 4x slower than SuperPoint+LightGlue at similar LO-RANSAC accuracy.

## Limitations
- Stated by authors: no dedicated limitations section in the main paper. They note OT vs DS choice matters per domain (DS better outdoors, Table 3) and that LoFTR is slightly worse than SP+SuperGlue on Aachen day queries.
- Our read: fixed 1/8 coarse grid means matches cluster where the transformer is confident; at 116 ms per VGA pair it is not a per-frame VO matcher on embedded hardware. The main paper describes no rotation augmentation or in-plane rotation test, so assume yaw-misaligned drone frames vs north-up tiles need pre-rotation (from heading) and verify on your data. Superseded on accuracy by RoMa and on speed by LightGlue, but remains the standard detector-free baseline.

## Code, weights, license
- Repo: github.com/zju3dv/LoFTR, Apache-2.0 (GitHub API), last push 2024-05-31, effectively in maintenance mode.
- Weights: 4 pretrained models (indoor-ds, indoor-ot, outdoor-ds, outdoor-ot, about 45 MB each) via a Google Drive link in the README. No separate weights license stated.
- Gotcha: the OT variant needs `superglue.py` from Magic Leap's SuperGluePretrainedNetwork, which the README says it cannot redistribute "due its strict LICENSE"; the webcam demo also pulls Magic Leap's `utils.py`. Use the DS variant to stay inside Apache-2.0.
- Easiest path: `kornia.feature.LoFTR` (integrated since kornia 0.5.11) with pretrained indoor/outdoor weights.

## Reproduction effort (estimate)
Estimate: first matches in 15-30 min via `pip install kornia`. Reproducing Tables 2-3 with the repo needs the ScanNet-1500 (~1 GB) and MegaDepth-1500 (~600 MB) test sets from the README link and the pytorch-lightning env: a few hours. Retraining (64 GPUs x 24 h) is out of scope.

## What a hackathon team can take from it
- Detector-free baseline for low-texture terrain (fields, desert, water edges) where keypoint extractors return too few points. Run it against LightGlue/XFeat/RoMa on your own drone-vs-tile pairs via [vismatch](../integration-cards/gmberton__vismatch.md).
- Coarse confidence threshold (0.2) and the count of mutual coarse matches are a simple, tunable gate on whether a visual fix is usable.
- The coarse-to-fine window refinement (expectation over a local heatmap) is a reusable pattern for sub-pixel accuracy on top of any coarse matcher.
- For the stronger dense successor with certainty output, see [RoMa](../integration-cards/parskatt__roma.md).
