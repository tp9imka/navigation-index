# UASTHN - paper digest
<!-- about: res:uasthn-uncertainty-thermal-2025, repo:arplaboratory/uasthn -->
**UASTHN: Uncertainty-Aware Deep Homography Estimation for UAV Satellite-Thermal Geo-localization** - Xiao, Loianno (NYU), ICRA 2025. [paper](https://arxiv.org/abs/2502.01035) | [code](https://github.com/arplaboratory/UASTHN) | Read: full text, arXiv HTML v2 (24 Feb 2025); repo README

## Problem
Thermal-to-satellite homography (STHN) outputs a position with no confidence. Textureless or corrupted thermal frames, outdated or self-similar maps, heading noise and thermal frames that run off the satellite crop all produce confident wrong fixes. UASTHN adds uncertainty estimation so bad fixes can be rejected.

## Method
- Base: a deep homography estimator (DHN, IHN or STHN two-stage) predicting four-corner displacements => DLT => homography => center position.
- CropTTA (data uncertainty): take N_C random crops of the thermal image (offset o_c, 32 best), run each through the network, map the corner predictions back, use per-corner std as uncertainty. Reject when all corner stds exceed a threshold s_c.
- Deep Ensembles (model uncertainty): N_m models trained with different seeds, std across models.
- Merge: CropTTA and DE combined by max (default), min or add.
- Early stopping: run all samples only for the first k refinement iterations to estimate uncertainty, then continue with one sample - cuts latency.
- Training: 100k steps, then 200k fine-tuning with CropTTA augmentation; 5 samples at evaluation.
- Evaluation of rejection: ROC with predictions above 25 m MACE treated as should-reject.

## Data and sensors
- Sensors: nadir thermal camera at night plus a position prior within D_C. Same assumptions as STHN.
- Dataset: Boson-nighttime (v3 layout, satellite as one full map, thermal crops in h5), satellite crops W_S = 1536 px. Card: [thermal datasets](../dataset-cards/thermal-datasets.md).
- Metrics: MACE, CE (m), SR = success rate (share not rejected), at D_C = 128, 256, 512 m.

## Headline results (as reported)
- Abstract: 7 m geo-localization error at 97% success rate within a 512 m search radius. Matches Table I, STHN + CropTTA at D_C=512: CE 7.25 m, SR 97.5%.
- Table I, D_C=512 m, MACE / CE / SR:
  - STHN no UE: 12.70 / 12.12 / 100%
  - STHN + DE: 8.29 / 7.58 / 97.3%
  - STHN + CropTTA: 7.93 / 7.25 / 97.5%
  - STHN + CropTTA + DE: 7.83 / 7.15 / 97.0%
  - IHN no UE: 16.42 / 15.90 / 100%; IHN + CropTTA: 9.27 / 8.06 / 95.0%
- Table I, D_C=256 m: STHN no UE 14.99 / 14.34 / 100% vs STHN + CropTTA 7.85 / 7.31 / 95.8%.
- Table II, inference time ms (RTX 2080 Ti, 5 samples), STHN: no UE 63.9; CropTTA 87.0 (78.2 with early stop); DE 130.2 (81.9); CropTTA+DE 186.0 (118.6).
- Fig. 3: CropTTA saturates above 4 samples, DE above 3.

## Limitations
- Stated by authors: at D_C=128 m baselines without UE do better (error floor); CropTTA is not best in every cell (weak for DHN and for IHN at 128 m); deep-matching-based variant (DM) underestimates uncertainty on low-error frames; CropTTA+DE hurts when either component is bad; night thermal only - day, seasons and moving objects untested; adaptive rejection threshold left as future work.
- Our read: "error improvement" is partly selection - the mean is computed over accepted frames. 2.5-5% of frames are dropped, so the filter must coast on VIO through those.
- Our read: the uncertainty is a per-corner std, not a calibrated covariance. Mapping it to an EKF measurement noise R needs your own calibration on held-out data.
- Our read: the table numbers for the split sizes render garbled in arXiv HTML ("1010K / 1313K / 2727K"); likely the same 10K/13K/27K pairs as STHN. Check the PDF.

## Code, weights, license
- Repo: MIT (GitHub API), last push 2026-02-28. `UASTHN_demo.py` downloads weights from HF and runs a sample pair. Also contains scripts for image-matching baselines.
- Weights: Hugging Face `xjh19972/UASTHN` plus a Google Drive folder. No license field on the HF model card (checked 2026-11-06) - weights license not stated.
- Dataset: shared Boson-nighttime HF repo, 122 GB, gated.

## Reproduction effort (estimate)
Estimate:
- Hardware: one NVIDIA GPU; CropTTA alone runs at about 80-90 ms/frame on a 2080 Ti (Table II), so a Jetson-class board is roughly 1-3 Hz (our guess, not measured).
- Data: 122 GB for retraining or full eval; demo needs none.
- Time to first result: under an hour for the demo. Reproducing one Table I row: a day including download.
- Not reproducible quickly: deep ensembles (needs N_m separately trained models; check whether the Drive folder ships several seeds before planning on DE).

## What a hackathon team can take from it
- CropTTA is model-agnostic: wrap any regression localizer (homography, absolute pose, even a learned VIO head) with N random crops and use the spread as uncertainty. No retraining needed to try it, though their gains include CropTTA fine-tuning.
- Two-number interface for the nav stack: position + reject flag. Feed accepted fixes as an EKF update ([filterpy](../integration-cards/rlabbe__filterpy.md)) or GPS-like factor ([GTSAM](../integration-cards/borglab__gtsam.md)); on reject, keep propagating.
- Scale measurement noise R with the CropTTA std (after calibrating it against true error on a held-out split) instead of a fixed R.
- Early-stop trick: estimate uncertainty during the first few iterations only, then finish with one sample - keeps latency close to the no-UE model.
- Natural chain: [STGL](thermal-geolocalization-iros-2023.md) retrieval => [STHN](sthn-thermal-homography-2024.md) alignment => UASTHN gate => filter.
