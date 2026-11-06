# University-1652 - paper digest
<!-- about: res:university-1652-benchmark-2020, repo:layumi/university1652-baseline -->
**University-1652: A Multi-view Multi-source Benchmark for Drone-based Geo-localization** - Zheng, Wei, Yang, ACM Multimedia 2020. [paper](https://arxiv.org/abs/2002.12186) | [code](https://github.com/layumi/University1652-Baseline) | Read: full text via ar5iv rendering of arXiv 2002.12186, plus repo README and Request.md

## Problem
Cross-view geo-localization had ground<=>satellite benchmarks only; the viewpoint gap is huge. The paper adds the drone as a third platform with intermediate oblique views, and defines two drone-centric tasks: drone=>satellite ("drone-view target localization") and satellite=>drone ("drone navigation").

## Method
- Dataset: 1,652 buildings from 72 universities; 1,402 have all three views, 250 are gallery distractors. Train 701 buildings / 33 universities / 50,218 images; test 701 buildings / 39 universities, no university overlap with train (Sec. 3, Table 2).
- Drone views are synthetic: rendered with the Google Earth 3D engine, camera spiraling around each building three times while descending from 256 m to 121.5 m, 54 frames per building (one every 15 frames of 30 fps video).
- One satellite image per building; ~3.38 Google Street View images per building; extra 21,099 noisy Google Image photos for training only.
- Metrics: Recall@K and AP (AP because each query has multiple true matches).
- Baseline: ResNet-50 (ImageNet init), 512-d embedding, instance loss (treat each building as a class) with a classifier shared across views; satellite and drone branches share weights (Model-III = three sources). SGD, 256x256 input by default, cosine similarity retrieval.

## Data and sensors
- RGB only; drone metadata (altitude, heading, tilt, range) recorded but not used by the baseline.
- Test queries: 37,855 drone, 701 satellite, 2,579 ground; gallery: 51,355 drone, 951 satellite, 2,921 ground (Table 2).
- Labels are building IDs, so this is retrieval, not metric localization.
- Dataset card: [University-1652](../dataset-cards/university-1652.md). Related multi-height benchmark: [SUES-200](../dataset-cards/sues-200.md); dense real-flight: [DenseUAV](../dataset-cards/denseuav.md).

## Headline results (as reported)
- Table 3, Model-III, single query, R@1 / AP: drone=>satellite 58.49 / 63.13; satellite=>drone 71.18 / 58.74. Off-the-shelf ImageNet ResNet-50 features: 10.11 / 13.04 and 33.24 / 11.59.
- Table 4, multi-query (several drone views of the same building): drone=>satellite R@1 69.33, AP 73.14. Ground=>satellite stays near zero: R@1 1.20, AP 2.52.
- Table 5: instance loss beats contrastive / triplet (drone=>satellite R@1 58.23 vs 52.39-55.18) under the same data.
- Table 6: not sharing satellite/drone weights drops drone=>satellite R@1 from 58.49 to 39.84.
- Table 7: input 384 px best (drone=>satellite R@1 62.99, AP 67.69); 512 px drops to 59.69.
- Real drone video: qualitative only - one 4K YouTube video of an unseen university, top-5 retrievals shown. No quantitative real-flight numbers.
- For scale: later methods reach drone=>satellite R@1 92.65 on this benchmark (Sample4Geo, Table 2 of arXiv 2303.11851).

## Limitations
- Stated / evident in the paper: drone images are synthetic Google Earth renders; ground-view images are noisy and ground=>satellite barely works; satellite=>drone uses only 701 queries; drone metadata unused; baseline not tuned for state of the art.
- Our read: building-centric oblique orbits at 121-256 m are far from a nadir camera over fields or forest - strong scores here say little about GNSS-denied flight over unstructured terrain. Many papers now saturate it (90%+ R@1), so it is a sanity check, not a deployment signal.
- Our read: Google Earth renders and satellite tiles of the same source share texture and color, which flatters cross-view matching compared to real camera vs satellite.

## Code, weights, license
- Repo layumi/University1652-Baseline: MIT (GitHub API), last push 2026-10-07, ~700 stars, still maintained (now also hosts ACM MM UAV workshop challenge material).
- Data: by email request only (Request.md: research purposes only, no third-party sharing, no selling or profit). Maintainer says replies come within minutes. Not redistributable - cannot be bundled into a public demo.
- Trained baseline model on Google Drive / OneDrive, linked from README; no separate weights license. README asks for GPU memory >= 8 GB. Includes a GNN-based GPU re-ranking add-on.

## Reproduction effort (estimate)
Estimate: dataset request + download same day if the email reply arrives. Eval with the released baseline on one 8 GB+ GPU: ~1-2 hours. Training the ResNet-50 baseline: a few hours on a single modern GPU (training time not reported in the paper). Real-drone results are not reproducible (qualitative, single YouTube video).

## What a hackathon team can take from it
- Standard evaluation protocol (drone=>satellite R@1 + AP, building-disjoint split) - report your retriever on it so judges can compare to published numbers.
- Pretraining source for a drone=>satellite retriever before fine-tuning on your own flight area; check the non-commercial terms first.
- Multi-query trick: aggregating several consecutive drone frames lifts R@1 from 58.49 to 69.33 (Table 4) - in a nav stack, fuse retrieval over a short window instead of trusting one frame.
- Weight sharing between drone and satellite branches matters (Table 6) - keep a single encoder when training your own.
- Treat it as a smoke test only; validate on real nadir flight data ([UAV-VisLoc](../dataset-cards/uav-visloc.md), [AerialVL](../dataset-cards/aerialvl.md)) before trusting any number.
