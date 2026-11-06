# STHN - paper digest
<!-- about: res:sthn-thermal-homography-2024, repo:arplaboratory/sthn -->
**STHN: Deep Homography Estimation for UAV Thermal Geo-localization with Satellite Imagery** - Xiao, Zhang, Tortei, Loianno (NYU, TII), IEEE RA-L 2024. [paper](https://arxiv.org/abs/2405.20470) | [code](https://github.com/arplaboratory/STHN) | Read: full text, arXiv HTML v3 (26 Sep 2025); repo README

## Problem
Retrieval-based thermal geo-localization (STGL) is only as precise as the tile database is dense, is slow on big databases, and assumes north-aligned queries. STHN instead regresses a homography that places the thermal image directly inside a larger satellite crop, giving a metric position in one forward pass.

## Method
- Input: thermal image (512 px, about 1 m/px) and a satellite crop of width W_S centered on a position prior (W_S = 512, 1024 or 1536 m, i.e. the thermal image covers 100%, 25% or 11% of the crop). Both resized to 256 px.
- Coarse stage: IHN-style network - CNN features, correlation volume, iterative estimator (6 updates) predicting four-corner displacements.
- Refinement stage (optional, "two stages"): crop a box around the warped thermal corners, resize, run a second non-shared network (6 updates), compose displacements.
- DLT => homography H; UAV position = H applied to the image center.
- Training data boosted with TGM-generated thermal images from unpaired satellite imagery (satellite set grown from 79,950 to 163,344 images, 215.78 km2).
- Training: AdamW, LR 1e-4, batch 16, 200k iterations per module.

## Data and sensors
- Sensors: nadir thermal camera (FLIR Boson dataset), plus a position prior within D_C of the truth (from a coarse localizer or dead reckoning). Rotation and scale assumed roughly known.
- Dataset: Boson-nighttime extended (v3), 10,256 / 13,011 / 26,568 train / val / test pairs. Card: [thermal datasets](../dataset-cards/thermal-datasets.md).
- Metrics: MACE (mean corner error, m) and CE (center error, m, = geo-localization error), swept over prior offset D_C = 50 ... 512 m.

## Headline results (as reported)
- Table I, test MACE at D_C 50 / 128 / 256 / 512 m:
  - IHN baseline: 5.91 / 51.74 / 190.93 / 367.24
  - STHN W_S=512: 4.24 / 14.97 / 142.71 / 347.50
  - STHN W_S=1536: 6.50 / 7.27 / 16.78 / 16.42
  - STHN W_S=1536 two stages: 7.51 / 7.51 / 14.99 / 12.70
- Table I, keypoint baselines fail: SIFT+RANSAC 99.6% failure, ORB+RANSAC 82.6%, R2D2+RANSAC 88.9%; LoFTR+RANSAC 0% failure but MACE 1123.74-2564.65 m.
- Table II, D_C=512 m, CE / latency (RTX 2080 Ti): STGL-GeM-ResNet50 13.52 m / 4918.9 ms; STHN one-stage 15.90 m / 35.2 ms; STHN two stages 12.12 m / 63.9 ms; AnyLoc-VLAD-DINOv2 258.21 m / 352,404 ms.
- Table III, robustness (D_C=512, W_S=1536, MACE one-stage / two-stage): baseline 16.42 / 12.70; rotation 10 deg 33.78 / 14.55; rotation 30 deg 64.63 / 33.48; scale +-0.2 36.79 / 15.16; perspective 16 px 34.07 / 16.24.

## Limitations
- Stated by authors: refinement hurts at small D_C (50-128 m) - extra iterations add noise; 30 deg rotation breaks even the two-stage model; best W_S depends on D_C, so no single setting wins everywhere.
- Our read: the text claims latency drops "to just 7.2%" and "13.0%" of STGL-GeM, but Table II gives 35.2/4918.9 = 0.7% and 63.9/4918.9 = 1.3%. Trust the table.
- Our read: no uncertainty output. A wrong alignment comes out as a confident position - fine for a benchmark, dangerous in a filter. UASTHN fixes this.
- Our read: single region, night, mostly desert; no daytime thermal, no seasons. Needs heading within about 10 deg to stay near the baseline error.

## Code, weights, license
- Repo: MIT (GitHub API), last push 2026-05-16. `STHN_demo.py` downloads weights and runs on a sample pair (`--two_stages` for refinement).
- Weights: Hugging Face `xjh19972/STHN`, plus a Google Drive folder. No license field on the HF model card (checked 2026-11-06) - weights license not stated.
- Dataset: HF `xjh19972/boson-nighttime`, v3 = 122 GB per README, gated.

## Reproduction effort (estimate)
Estimate:
- Hardware: one NVIDIA GPU (paper latency measured on a 2080 Ti). conda env.yml; training scripts are SLURM sbatch (rename to .sh).
- Data: 122 GB for v3; there is no small subset. Demo pair is bundled.
- Time to first result: under an hour for `STHN_demo.py`. Full Table I needs the dataset and evaluation scripts - a day including download. Retraining (2 x 200k iterations) is multi-day.
- Not reproducible: anything on your own thermal data without retraining or at least fine-tuning (domain is one desert area at night).

## What a hackathon team can take from it
- The fine stage of a coarse-to-fine map matcher: given a prior within about 512 m, one 35-64 ms forward pass returns a metric position. Coarse prior from [STGL](thermal-geolocalization-iros-2023.md) retrieval or from VIO dead reckoning.
- Search window sizing as a tunable: pick W_S from your expected drift (Table I shows the trade-off clearly) - grow W_S as INS covariance grows.
- Keypoint matchers fail on thermal-vs-RGB (Table I); learned homography is the working baseline for cross-modal night matching.
- Pre-rotate the thermal image with autopilot heading: Table III shows error doubling past 10 deg for the one-stage model.
- Plug-in: position fix => EKF update in [filterpy](../integration-cards/rlabbe__filterpy.md) or a [GTSAM](../integration-cards/borglab__gtsam.md) GPS-like factor; add your own innovation gate since STHN reports no covariance.
