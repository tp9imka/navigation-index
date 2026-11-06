# STGL (thermal geo-localization) - paper digest
<!-- about: res:thermal-geolocalization-iros-2023, repo:arplaboratory/satellite-thermal-geo-localization -->
**Long-range UAV Thermal Geo-localization with Satellite Imagery** - Xiao, Tortei, Roura, Loianno (NYU, TII), IROS 2023. [paper](https://arxiv.org/abs/2306.02994) | [code](https://github.com/arplaboratory/satellite-thermal-geo-localization) | Read: full text, arXiv HTML v3; repo README

## Problem
Locate a UAV at night, when RGB cameras are useless, by matching downward thermal images against daytime RGB satellite imagery. Two obstacles: paired thermal-satellite data is scarce, and thermal images over desert are low-contrast and self-similar.

## Method
- SGM (geo-localization module): image retrieval. The satellite map is tiled into a database (512x512 crops, 35 px stride); the thermal query is embedded and matched by nearest neighbour. ResNet-18 backbone + compression conv + NetVLAD (4096-d), triplet loss (margin 0.1). Positives within 35 m, negatives beyond 50 m.
- TGM (thermal generative module): pix2pix GAN that turns satellite tiles into synthetic thermal tiles, giving 79,950 extra pseudo-pairs for SGM training.
- Domain adaptation: DANN with gradient reversal (weight 0.1). Best variant applies it to positives only; using negatives fights the triplet loss.
- Contrast enhancement: linear scaling of thermal images, factor 3. Turns out to be critical (see Table II).
- Output: position = center of the best-matching tile, so precision is bounded by tile stride, and the query must be roughly north-aligned and at the map's scale.

## Data and sensors
- Sensors: nadir FLIR Boson thermal camera (640p, 8.7 mm, 50 deg HFOV), about 1 m/px after orthorectification. No IMU used by the method.
- Dataset: Boson-nighttime, six night flights (21:00-04:00), 33 km2, mostly desert with some farms and roads; reference is Bing (Maxar) satellite imagery. 3 flights train/val, 3 test. Flight altitude and raw image count not stated.
- Dataset card: [thermal datasets (Boson-nighttime)](../dataset-cards/thermal-datasets.md).
- Metrics: R@N (top-N within 50 m), R_512@N (search restricted to a 512 m radius around a prior), L2_512 position error in m.

## Headline results (as reported)
- Table I, baseline (no CE/DANN/generated data): R@1 69.3, R@5 81.8, R_512@1 81.1, L2_512 58.9 m.
- Table I, best (CE + DANN positives-only + generated data): R@1 92.1, R@5 96.9, R_512@1 96.5, R_512@5 99.1, L2_512 14.7 m.
- Table II, contrast enhancement is load-bearing: TGM lambda1=10 without CE gives R@1 7.2 and L2_512 299.6 m; with CE R@1 90.5, L2_512 17.1 m.
- Runtime (RTX 2080 Ti, Sec. V): embedding 12.84 ms/image (batch 1), matching 1.20 ms against 26,568 satellite embeddings.

## Limitations
- Stated by authors: failures are mostly in desert (offset errors >= 50 m and outright misses); TGM output distorts roads and desert; enhancement can distort buildings; single, mostly-desert area; 4096-d descriptor is heavy; TGM and SGM are not trained end-to-end.
- Our read: retrieval gives tile-center accuracy only (14.7 m mean is with a 512 m prior). For a filter you want a metric fix plus covariance - that is what STHN and UASTHN add.
- Our read: assumes the thermal image is nadir, north-aligned and at known scale. On a real UAV you must rotate/scale with heading and altitude first.
- Our read: the paper's split sizes read 10,256 / 13,011 / 26,568 (train / val / test), i.e. val > train; the HTML rendering duplicates numbers, check the PDF before quoting.
- Our read: the public SGM weights on Hugging Face are configured as ResNet-50 conv4 + GeM (per our integration card), not the paper's ResNet-18 + NetVLAD. Do not expect Table I numbers from the demo weights.

## Code, weights, license
- Repo: MIT (GitHub API), last push 2026-05-16. Inference demos live on the `demo` branch.
- Weights: Hugging Face `xjh19972/SGM` and `xjh19972/TGM`. No license field on either model card (checked HF API 2026-11-06) - treat weights license as not stated.
- Dataset: `xjh19972/boson-nighttime` on HF, gated (login, auto-approve), v1 about 74 GB. Satellite imagery provenance is Bing/Maxar; its terms are not addressed in the README.
- Integration card: [satellite-thermal-geo-localization](../integration-cards/arplaboratory__satellite-thermal-geo-localization.md).

## Reproduction effort (estimate)
Estimate:
- Hardware: one CUDA GPU on Linux (env.yml pins PyTorch 1.12 + CUDA 11.3 + faiss-gpu). Old stack - expect conda solving pain on new drivers.
- Data: 74 GB minimum for the full dataset; no small subset. Demo pairs in `examples/` are enough to show it working.
- Time to first result: 30-60 min to run `SGM_demo.py` with HF weights. Retraining TGM + SGM is multi-day GPU work and needs the full dataset.
- Not reproducible within 48 h: Table I numbers end-to-end. Not reproducible anywhere: your own flight data in the same conditions without a thermal UAV.

## What a hackathon team can take from it
- The "synthesize the missing modality" trick: train a satellite => thermal translator, then train the matcher on synthetic pairs. Works for any night/IR sensor where you have maps but few paired flights.
- Contrast stretching before matching is not optional for thermal - Table II shows a collapse without it. Cheap to add to any thermal front end.
- Use as the coarse stage: global retrieval within a prior radius (from dead reckoning) => candidate tile => hand off to STHN/UASTHN for metric alignment.
- Retrieval cost is tiny (about 14 ms/frame on a 2080 Ti) - fine for a 1 Hz absolute fix into an EKF; gate by descriptor distance margin between top-1 and top-2.
