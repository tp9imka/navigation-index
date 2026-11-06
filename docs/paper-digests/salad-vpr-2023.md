# SALAD - paper digest
<!-- about: res:salad-vpr-2023, repo:serizba/salad -->
**Optimal Transport Aggregation for Visual Place Recognition** (DINOv2 SALAD) - Izquierdo, Civera (Univ. of Zaragoza), CVPR 2024 (venue per repo README bibtex). [paper](https://arxiv.org/abs/2311.15937) | [code](https://github.com/serizba/salad) | Read: full text via arXiv HTML v2, plus repo README

## Problem
Visual place recognition as image retrieval: given a query image, find geo-tagged database images of the same place under illumination, weather, season and viewpoint change. Goal is a compact global descriptor that beats prior single-stage methods and two-stage re-ranking methods, and trains fast.

## Method
- Backbone: DINOv2-B (86M params), only the last 4 transformer blocks fine-tuned (Sec. 4.1; Table 6 ablates this).
- Patch tokens get assignment scores to m clusters from a small 2-layer MLP (not k-means init as in NetVLAD).
- A learnable "dustbin" column lets uninformative features be dropped (Eq. 2) - qualitatively it discards sky, road and dynamic objects (Figs. 3-5).
- Sinkhorn optimal transport replaces NetVLAD's per-feature softmax, so assignment is balanced feature-to-cluster and cluster-to-feature (Eq. 3).
- Features reduced to l dims, summed per cluster (no centroid residual), concatenated with a projected global (CLS) token, intra- and global L2 norm.
- Default m=64, l=128, global 256 => 8192+256-d. Smaller: 2048+64, 512+32.
- Training: GSV-Cities, multi-similarity loss, 4 epochs, ~30 min on one RTX 3090; train 224x224, eval 322x322.

## Data and sensors
- Monocular RGB, ground-level street / dashcam / train imagery.
- Evaluated on MSLS Val and MSLS Challenge, Pitts250k-test, SPED, NordLand, SF-XL (Sec. 4). Correct = within 25 m (NordLand: within 2 frames).
- No aerial or drone-to-satellite evaluation in the paper.

## Headline results (as reported)
- Table 1, DINOv2 SALAD 8192+256, R@1/R@5: MSLS Challenge 75.0/88.8, MSLS Val 92.2/96.4, NordLand 76.0/89.2, Pitts250k 95.1/98.5, SPED 92.1/96.2.
- Table 1, compact 512+32: MSLS Val 89.3/94.9, NordLand 61.2/78.9 - still above MixVPR (4096-d) on MSLS Val (88.0) and NordLand (58.4).
- Table 2: beats two-stage re-ranking methods without re-ranking, e.g. MSLS Challenge R@1 75.0 vs R2Former 73.0.
- Table 3, SF-XL R@1: Test v1 88.6, Test v2 94.8 (EigenPlaces 84.1 / 90.8).
- Table 4 ablation: AnyLoc (frozen DINOv2, 49152-d) MSLS Val R@1 68.7, NordLand 16.1; DINOv2 NetVLAD 24576-d is on par or slightly higher on MSLS / Pitts250k (e.g. MSLS Val 92.4) but SALAD is clearly better on NordLand (76.0 vs 71.8).
- Table 7: removing dustbin => MSLS Val R@1 91.4; dual softmax instead of Sinkhorn => 91.9; full 92.2.
- Runtime (Table 2, Table 5): 2.41 ms per image on RTX 3090 for DINOv2-B; backbone scaling S 1.30 ms / L 7.82 ms / G 24.93 ms (MSLS Val R@1 90.5 / 92.6 / 91.7).

## Limitations
- Stated by authors (Sec. 5): DINOv2 slower than ResNet methods; the aggregation depends on high-resolution backbone features and is less suited to coarse CNN features; OT uses its simplest form; a re-ranking stage could add recall at more compute.
- Our read: trained only on street-level GSV-Cities. Its value for drone-to-satellite or nadir aerial retrieval is untested in the paper; expect to fine-tune or at least benchmark against AnyLoc on aerial data before relying on it.
- Our read: the 2.41 ms figure is a desktop RTX 3090 number at 322x322; embedded latency not reported.

## Code, weights, license
- Repo serizba/salad, GPL-3.0 (GitHub API), last push 2025-10-27, ~386 stars.
- License gotcha: GPL-3.0 is copyleft - linking it into a distributed stack forces GPL on that stack. Fine for a hackathon demo, check before productizing.
- Weights: three checkpoints (8192+256, 2048+64, 512+32) on Google Drive, linked from README; README states no separate weights license. One-liner Torch Hub load: `torch.hub.load("serizba/salad", "dinov2_salad")`. Underlying DINOv2 is Apache-2.0 (facebookresearch/dinov2, GitHub API).
- Built on MixVPR / GSV-Cities code. Tested on PyTorch 2.1.0, CUDA 12.1, xformers.
- No integration card for SALAD yet; the harness in [gmberton__vpr-methods-evaluation](../integration-cards/gmberton__vpr-methods-evaluation.md) and the comparison point [anyloc__anyloc](../integration-cards/anyloc__anyloc.md) are the nearest.

## Reproduction effort (estimate)
Estimate: inference via Torch Hub on any CUDA GPU in under 30 min. Reproducing MSLS Val / NordLand numbers: dataset downloads dominate, half a day. Retraining: GSV-Cities download plus ~30 min on an RTX 3090 per README. Aerial fine-tuning would need your own drone/satellite pairs - nothing in the repo for that.

## What a hackathon team can take from it
- Drop-in global descriptor for the coarse "retrieve candidate tiles / keyframes" stage, 2.41 ms per image on desktop GPU; use 512+32 if you must store descriptors for many tiles.
- The dustbin idea - learn to throw away uninformative patches - maps directly to aerial scenes (water, uniform fields, clouds) that poison matches.
- Compare SALAD vs AnyLoc on your own aerial tiles in an afternoon with a 25 m / R@1 protocol before picking one; the paper gives no aerial evidence either way.
- Fast fine-tuning recipe (freeze all but last 4 DINOv2 blocks, 4 epochs, multi-similarity loss) is reusable if you have labeled drone/satellite pairs (e.g. [University-1652](../dataset-cards/university-1652.md), [SUES-200](../dataset-cards/sues-200.md)).
