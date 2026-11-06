# Sample4Geo - paper digest
<!-- about: res:sample4geo-2023, repo:skyy93/sample4geo -->
**Sample4Geo: Hard Negative Sampling For Cross-View Geo-Localisation** - Deuser, Habel, Oswald (Univ. of the Bundeswehr Munich), ICCV 2023 (venue per repo README). [paper](https://arxiv.org/abs/2303.11851) | [code](https://github.com/Skyy93/Sample4Geo) | Read: full text via ar5iv rendering of arXiv 2303.11851, plus repo README

## Problem
Cross-view geo-localization: retrieve the satellite image that matches a street-level or drone image. Prior work leans on polar transforms, special aggregation modules or multi-stage refinement, and triplet loss struggles with hard negatives (can collapse). The paper asks how far a plain shared encoder gets with a better loss and better negative sampling.

## Method
- One shared (Siamese) ConvNeXt-B encoder (88M params) for both views, mean-pooled features, no polar transform, no extra modules (Sec. 3.2, 4.2).
- Symmetric InfoNCE loss over the whole batch (street=>sat and sat=>street), label smoothing 0.1, learnable temperature (Sec. 3.1).
- GPS-based sampling in early epochs: batches are filled with geographic neighbours (haversine for CVUSA/VIGOR, UTM Euclidean for CVACT), so in-batch negatives are hard (Sec. 3.3).
- Dynamic Similarity Sampling (DSS): every 4 epochs, recompute embeddings and build batches from visually similar but wrong pairs - k=64 of K=128 neighbours, half by similarity, half random (Sec. 3.4).
- University-1652 has no GPS per image, so it uses shuffling plus a custom sampler that avoids same-class duplicates in a batch.
- Training: 40 epochs, batch 128, AdamW, LR 1e-3 cosine with 1 epoch warm-up; synchronized flip/rotation, dropout-style and color augmentations.

## Data and sensors
- RGB images only; output is a retrieved satellite tile (location), not a metric pose.
- CVUSA, CVACT (street panorama => satellite), VIGOR (street => satellite, SAME and CROSS area splits), University-1652 drone <=> satellite ([dataset card](../dataset-cards/university-1652.md)).
- University-1652 input 384x384 for drone and satellite (Sec. 4.1.2).

## Headline results (as reported)
- Table 2, University-1652: drone=>satellite R@1 92.65, AP 93.81; satellite=>drone R@1 95.14, AP 91.39.
- Table 1: CVUSA R@1 98.68; CVACT Val R@1 90.81; CVACT Test R@1 71.51.
- Table 3: VIGOR SAME R@1 77.86, CROSS R@1 61.70.
- Table 6, cross-dataset generalization: CVUSA=>CVACT R@1 56.62, CVACT=>CVUSA R@1 44.95.
- Table 5 sampling ablation (VIGOR CROSS R@1): random 36.38, GPS 57.17, DSS 58.59, GPS+DSS 61.70.
- Table 9 loss ablation (CVUSA R@1): triplet 0.00 (collapse), soft-margin triplet 91.83, InfoNCE 98.68.
- Table 4: shared encoder beats separate encoders (VIGOR SAME 77.86 vs 75.81).
- Training hardware and time: not specified (acknowledges a GPU cluster only). No inference latency reported.

## Limitations
- Stated by authors: generalization to unseen regions is below same-area performance; CVUSA/CVACT are saturating and assume a centered, north-aligned satellite crop; University-1652 drone images are close to the building, which makes matching easier; GPS sampling is impossible on University-1652; switch point from GPS to DSS sampling not specified.
- Our read: the 92.65 R@1 is on University-1652, whose drone views are Google Earth renders orbiting a single building - not real nadir flight frames over open terrain. Expect a big drop on real flight data (compare [UAV-VisLoc](../dataset-cards/uav-visloc.md), [DenseUAV](../dataset-cards/denseuav.md)).
- Our read: retrieval returns "which tile", so position accuracy is bounded by tile size and spacing unless followed by local matching.

## Code, weights, license
- Repo Skyy93/Sample4Geo: GitHub API reports NO license. Default copyright applies - you may read and run it for evaluation but have no granted right to redistribute or build products on it. Ask the authors if that matters.
- Weights: Google Drive folder linked from README, no license stated.
- Training and eval scripts per dataset (`train_university.py`, `eval_university.py`, etc.), `requirements.txt`. Last push 2025-08-08, ~172 stars.
- University-1652 data itself is research-only, non-commercial, no redistribution (request template in layumi/University1652-Baseline `Request.md`).
- No integration card yet.

## Reproduction effort (estimate)
Estimate: evaluation with released weights on University-1652 on one 12-24 GB GPU: a few hours, mostly waiting on the dataset request email (README says replies usually come within minutes) and download. Retraining 40 epochs with batch 128 on ConvNeXt-B at 384 px needs a large GPU or several; time not reported by authors - plan for overnight at least.

## What a hackathon team can take from it
- Recipe for training any drone=>satellite retriever: shared encoder + symmetric InfoNCE + hard-negative batches. Data sampling moves VIGOR CROSS R@1 from 36 to 62 (Table 5) with the same model.
- GPS-neighbour batching is directly usable on your own flight logs: you have GNSS during data collection, so build batches of nearby tiles to force fine discrimination.
- Released University-1652 weights are a quick baseline to compare against AnyLoc / SALAD on your area's tiles.
- Pair it with a local matcher (LightGlue / RoMa, see [cvg__lightglue](../integration-cards/cvg__lightglue.md)) to turn a tile hit into a metric fix; use the retrieval similarity margin as a confidence gate before the navigation filter.
