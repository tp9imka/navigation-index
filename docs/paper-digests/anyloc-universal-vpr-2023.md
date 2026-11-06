# AnyLoc - paper digest
<!-- about: res:anyloc-universal-vpr-2023, repo:anyloc/anyloc -->
**AnyLoc: Towards Universal Visual Place Recognition** - Keetha et al. (CMU, IIIT Hyderabad, MIT, Adelaide), IEEE RA-L 2023 (venue per repo README bibtex). [paper](https://arxiv.org/abs/2308.00688) | [code](https://github.com/AnyLoc/AnyLoc) | Read: full text via ar5iv rendering of arXiv 2308.00688, plus repo README

## Problem
State-of-the-art VPR models are trained on urban street imagery and break in unstructured domains (indoor, subterranean, aerial, underwater). The paper asks whether off-the-shelf foundation-model features plus unsupervised aggregation give one VPR method that works everywhere without VPR-specific training.

## Method
- Backbone: DINOv2 ViT-G14, frozen, features from layer 31, "value" facet; per-patch features, CLS token discarded (Sec. III-B, IV-B2).
- Aggregation: hard-assignment VLAD with 32 clusters (AnyLoc-VLAD-DINOv2), or GeM (AnyLoc-GeM-DINOv2). Hard assignment beat soft and is ~1.4x faster (Sec. V-C3, Table VII).
- Vocabulary (VLAD cluster centers) is built without labels from database images. Three options compared: map-specific, domain-specific (pooled over maps of the same domain, e.g. all aerial), global (Table V). Domain-specific is best.
- Optional PCA-whitening down to 512-d for a ~100x smaller descriptor at similar recall (Sec. V-A1).
- No training, no fine-tuning; "training-free" still needs reference-database statistics for the vocabulary and PCA.

## Data and sensors
- Monocular RGB only.
- Structured (Table III): Baidu Mall, Gardens Point, 17 Places, Pittsburgh-30k, St Lucia, Oxford RobotCar ([card](../dataset-cards/oxford-robotcar.md)).
- Unstructured (Table I, IV): Hawkins (degraded indoor), Laurel Caverns (subterranean), Nardo-Air (drone queries at 50 m vs satellite reference, 102 db / 71 queries, 700 m span), Nardo-Air R (same, drone images rotated to match satellite orientation), VP-Air (aircraft at ~300 m, 2.7k queries, 12.7k db incl. 10k distractors, 100 km; see [VPAIR card](../dataset-cards/vpair.md)), Mid-Atlantic Ridge (underwater).

## Headline results (as reported)
- Table IV, aerial, R@1/R@5: AnyLoc-VLAD-DINOv2 Nardo-Air 76.1/94.4, Nardo-Air R 85.9/100, VP-Air 66.7/79.2.
- Same table, baselines: MixVPR Nardo-Air 32.4/42.2, VP-Air 10.3/18.3; CosPlace Nardo-Air 0/1.4 but Nardo-Air R 91.6/100, VP-Air 8.1/14.2; NetVLAD VP-Air 6.4/17.7; DINOv2-CLS VP-Air 45.2/59.9.
- Table IV, average over the six unstructured sets: AnyLoc-VLAD-DINOv2 R@1 65.0, R@5 86.5 vs MixVPR 33.2/57.8, CosPlace 29.3/43.8.
- Table III, structured average: AnyLoc-VLAD-DINOv2 R@1 86.5, R@5 93.5 vs MixVPR 83.9/91.7.
- Table V, aerial R@1 by vocabulary: domain-specific 76.2, map-specific 62.9, global 57.1.
- Descriptor size: VLAD 49,152-d, GeM 1,536-d (Table VII); PCA 512-d (Sec. V-A1). Hardware: RTX 3090 (Sec. IV-B). No per-image latency figure located.

## Limitations
- Stated by authors / evident in text: 3-4% behind task-trained methods on daytime urban (Pitts-30k, St Lucia, Sec. V-A1); CosPlace beats it on rotation-aligned aerial (Nardo-Air R, Table IV); vocabulary transfer across indoor maps degrades (Sec. V-B2); foundation model may have seen structured scenes in pretraining (footnote 4).
- Our read: ViT-G is ~1.1B parameters (SALAD paper Table 5) - not something to run per frame on a Jetson-class companion computer. Smaller ViT-S/B backbones are compared in Table VIII. 49k-d descriptors are heavy for a large tile database unless PCA is applied.
- Our read: the aerial sets are small (Nardo-Air: 71 queries), so per-dataset R@1 has wide uncertainty. Nardo-Air vs Nardo-Air R shows heading alignment still matters a lot for some methods.
- Our read: the newer SALAD paper (Table 4 of arXiv 2311.15937) shows plain AnyLoc well behind fine-tuned DINOv2 methods on urban benchmarks (e.g. MSLS Val R@1 68.7) - AnyLoc's value is out-of-domain robustness, not urban top score.

## Code, weights, license
- Repo AnyLoc/AnyLoc, BSD-3-Clause (GitHub API), last push 2024-03-13, ~649 stars - stable, not actively developed.
- No trained weights of its own: DINOv2 is pulled from facebookresearch/dinov2 (Apache-2.0 per GitHub API). Precomputed VLAD cluster centers and datasets on an IIIT OneDrive public release.
- Self-contained `demo/` folder, Colab notebooks and a Hugging Face Space (no local GPU needed to try it).
- Integration card: [anyloc__anyloc](../integration-cards/anyloc__anyloc.md). Benchmarking harness that includes AnyLoc: [gmberton__vpr-methods-evaluation](../integration-cards/gmberton__vpr-methods-evaluation.md).

## Reproduction effort (estimate)
Estimate: Colab demo works in minutes. Local run of `demo/anyloc_vlad_generate.py` on a 16-24 GB GPU (README says one GPU; a 16 GB GPU "should also work"): ~1-2 hours incl. DINOv2 download. Re-running the full Table IV needs the dataset tarballs from the public release and lots of CPU RAM for NN search; README warns of minor result differences across GPU/CUDA versions. Nardo-Air and VP-Air reproduction is feasible; a day for the aerial rows.

## What a hackathon team can take from it
- Zero-training coarse retriever for "which satellite tile am I over": DINOv2 + VLAD over your tile set, then pass top-k tiles to a local matcher (WildNav / LightGlue) for a metric fix. This is the hloc retrieve-then-match pattern applied to aerial.
- Build the VLAD vocabulary from your own satellite tiles of the operating area (map/domain-specific) - Table V shows this choice moves aerial R@1 by ~13-19 points.
- Rotate drone frames to north-up using heading before retrieval - Nardo-Air vs Nardo-Air R is the evidence.
- Use the PCA-512 variant or a smaller ViT if you need it onboard; precompute tile descriptors offline.
- The top-1 vs top-2 descriptor distance gap is a cheap confidence signal to gate when a retrieval result is trusted.
