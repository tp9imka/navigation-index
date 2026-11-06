# Jamming and Spoofing Detection Review - paper digest
<!-- about: res:rados-2024-jamming-spoofing-detection-review -->
**Recent Advances on Jamming and Spoofing Detection in GNSS** - Radoš, Brkić, Begušić (Univ. of Split FESB, Ericsson Nikola Tesla), MDPI Sensors 24(13):4210, 2024. [paper](https://www.mdpi.com/1424-8220/24/13/4210) | code: none | Read: full text via Europe PMC (PMC11244045) XML, including Tables 1-5. The MDPI site returned "Access Denied" to our fetch.

## Problem
Cheap SDRs (HackRF, USRP, LimeSDR) make jamming and spoofing easy, and detection research is fragmented. Most earlier surveys cover spoofing only. This review also covers jamming detection and methods for combined jamming plus spoofing, with an emphasis on recent ML/DL work.

## Method
- Narrative literature review: citations run to [101]. Of the references with a year tagged in the XML, most are dated 2020-2024. It is not a systematic review, and there are no PRISMA-style inclusion counts.
- Background (Sec. 2): jamming types (single-frequency, pulse, sweep, deception) and the simplistic / intermediate / sophisticated spoofing tiers taken from Humphreys et al.
- Spoofing-detection taxonomy (Sec. 3, Table 1):
  - signal processing: correlation peak / SQM, power-based, antenna array;
  - "data bit methods": ToA, DoA, NMEA message analysis;
  - positioning: pseudorange consistency;
  - radio-frequency fingerprinting (RFF);
  - ML/DL.
- Combined jamming plus spoofing detection (Sec. 4). Key logic: the joint pattern of AGC and C/N0 separates jamming (both drop) from spoofing (AGC drops, C/N0 flat or rising). It cites the GNSSAlarm Android app.
- Summary tables:
  - Table 3: ML/DL method, features, reported accuracy, interference type, per cited paper;
  - Table 4: qualitative jamming versus spoofing comparison;
  - Table 5: nine detection methods with principle, spoofing/jamming capability, pros and cons.

## Data and sensors
- No new data ("No new data were created or analyzed").
- Datasets the review highlights: [TEXBAT](../dataset-cards/texbat.md) and OAKBAT (Oak Ridge) as the two main public spoofing benchmarks (Sec. 3.5, Sec. 5). It also mentions SatGrid, Spirent-simulated sets, and smartphone (GnssLogger) captures.
- Sensors in the cited work: single-antenna receivers, smartphones, CRPA/antenna arrays, single rotating antennas, SDR front ends.

## Headline results (as reported)
All numbers are re-quoted from cited papers. Datasets and metrics differ row to row, so the numbers are not comparable with each other.
- Table 3 (examples):
  - SVM / NN on average power plus correlation distortion: 98.20 [48];
  - KNN on phase difference: 95 for delay greater than 0.4 chip [23];
  - C-SVM on lock time, pseudorange, C/N0 and Doppler: 98.77 [16];
  - XGBoost on C/N0, pseudorange, carrier phase and correlators: 95.52 [64];
  - MLP on Q-channel SQM, C/N0 and early-late phase: 82 [19];
  - several jamming classifiers at 99-100.
- Sec. 3.1.1: a Q-channel energy detector improves detection ratio by "at least 20%" over traditional SQM when C/N0 exceeds 32 dB-Hz, tested on all TEXBAT scenarios [43].
- Sec. 3.1.2: the improved ratio with C/N0 moving variance detects 98% at a 5 dB spoofer power advantage, versus 30% for classical SQM [47].
- Sec. 3.3: pseudorange double differences across two receivers reach Pd 99.99% at a false-alarm rate of 0.001 [61].
- Sec. 3.4: RFF classification with SVM is 99.99% pre-correlation versus 87.72% post-correlation [30].
- Sec. 3.1.2, Fig. 5 (smartphone, Redmi 8): under spoofing, C/N0 of two PRNs was 35-55 dB-Hz with Pearson correlation 0.99, versus 20-40 dB-Hz and -0.76 without an attack [70].
- Sec. 5: ML has become the most popular detection family, but "ML and DL methods still have a limited use in the industry".

## Limitations
- Stated by authors:
  - Few public datasets; most work validates on TEXBAT/OAKBAT only.
  - Combined interference datasets are missing.
  - Multi-antenna methods are costly.
  - ML is computationally complex.
- Our read:
  - The Table 3 accuracies come from different datasets, splits and class balances. Many are 99-100% on simulated or single-dataset tests, and the review does not assess leakage or generalisation.
  - Some taxonomy choices are loose: DoA and ToA sit under "data bit methods", and the Table 3 row labelled "DME" is a jammer type, not an ML method.
  - Some background statements are imprecise. For example, Sec. 2.2 says the spreading code is "transmitted as part of the navigation message". Read the primary sources before relying on a detail.
  - Cryptographic authentication (OSNMA) gets only a passing mention.

## Code, weights, license
No code or weights. The article is open access under CC BY 4.0 (stated in the article), which allows reuse of its tables with attribution.

## Reproduction effort (estimate)
Estimate: this is a survey, so there is nothing to reproduce directly. To reproduce one cited ML detector:
- Data: TEXBAT (about 430 GB raw; UT's `processed/` observables are about 0.8 GB for ds3) or Jammertest logs.
- Tooling: GNSS-SDR for observables and correlator outputs, plus scikit-learn.
- Time: 1-2 days for a feature-based SVM/XGBoost baseline on receiver observables.
- Not reproducible from the review alone: exact features, splits and hyperparameters of the cited works.

## What a hackathon team can take from it
- **A ready taxonomy and comparison table (Table 5)** for the "related work / why our approach" slide, under CC BY.
- **The AGC versus C/N0 decision rule (Sec. 4):** both drop means jamming; AGC drops while C/N0 holds or rises means spoofing. It is cheap, explainable and available on u-blox and Android. See the hub's `samples/gnss-interference-monitor` and [pyubx2](../integration-cards/semuconsulting__pyubx2.md).
- **A feature list for an ML baseline** (Table 3 column 2): C/N0, pseudorange residual, Doppler consistency, clock drift, correlator early/late/prompt. Train on one dataset and test on another (e.g. TEXBAT => Jammertest, [jammertest card](../dataset-cards/jammertest-data.md)) to avoid the inflated single-dataset numbers this review collects.
- **For defense-in-depth, combine with primary sources:** [Psiaki and Humphreys 2016](psiaki-humphreys-2016-gnss-spoofing-detection.md) for the attack/defense matrix, [Kriezis 2025](kreizis-ion-itm-2025-spoofing.md) for what fired in a real event, and [OSNMA](galileo-osnma.md) for cryptographic data authentication.
