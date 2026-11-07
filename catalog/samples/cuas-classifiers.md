# Sample: C-UAS classifiers on public data: radar tracks (UAV vs bird) and DroneRF spectra

`sample:cuas-classifiers` - code and walkthrough in [samples/cuas-classifiers](../../samples/cuas-classifiers/)

Two defensive drone-detection baselines on openly licensed recordings. Per-track kinematic and RCS features from the NRC Echodyne radar dataset feed gradient boosting and random forest for UAV vs bird, evaluated with session-grouped CV and a cross-site split. Welch band-power and burstiness features on a DroneRF subset give drone-vs-background detection and 4-class identification with segment-grouped and temporal splits. Radar detections can be emitted as unknown-affiliation rotor-UAS Cursor-on-Target via the mavlink-to-tak-cot builder.

**Verification:** Ran on 2026-11-06 with Python 3.12.14, scikit-learn 1.9.1 on an Apple M2 Max. Radar: 510 labelled tracks (379 BIRD, 131 UAV, 42 sessions); 5-fold GroupKFold by session HistGB balanced accuracy 0.928, AUC 0.964, UAV P/R 0.913/0.885; train Alma 2019 => test Laval 2020-21 balanced accuracy 0.90-0.92 on 89 tracks. DroneRF low-band subset (73 segments, 4 classes): detection balanced accuracy 0.977-0.994 on a temporal holdout, 4-class identification 0.94 GroupKFold / 0.85 temporal holdout. cuas_cot.py produced a-u-A-M-H-Q / how m-a CoT for one Laval session (31 of 110 tracks reported: 9 labelled UAV, 1 HUMAN, 21 unlabelled). 11 unit tests on synthetic fixtures pass; mutations of the vertical axis and the R1/R2 session merge fail 4. Not verified: DroneRF sample rate, radar site geometry (CoT positions are placeholders), the H band and other flight modes, ATAK rendering. Each DroneRF class in the subset is one recording session, so identification numbers include session effects.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [drone-rf-datasets](../../docs/dataset-cards/drone-rf-datasets.md) (dataset-cards)
- [nrc-cuas-sensing](../../docs/dataset-cards/nrc-cuas-sensing.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Tracking and data association](../../catalog/concepts/target-tracking.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `c-uas`, `drone-detection`, `drone-vs-bird`, `radar`, `echodyne`, `rcs`, `rf`, `dronerf`, `spectrogram`, `psd`, `scikit-learn`, `random-forest`, `gradient-boosting`, `cot`, `tak`

## Related

- uses: [NRC UAV vs bird radar tracks](../../catalog/repos/nrc-cnrc__cuas-sensing-dataset.md)
- uses: [DroneRF](../../catalog/repos/al-sad__dronerf.md)
- uses: [MAVLink telemetry to TAK Cursor-on-Target](../../catalog/samples/mavlink-to-tak-cot.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [DroneRF dataset: A dataset of drones for RF-based detection, classification, and identification](../../catalog/resources/dronerf-mendeley-dataset.md) (dataset_for)

_Indexed by lane(s): samples_
