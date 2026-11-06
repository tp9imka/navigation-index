# Sample: Dismounted foot-mounted INS: stdlib 15-state ZUPT EKF on the real pyshoe hallway data, cross-checked against pyshoe, with corridor heading, UWB and TAK output

`sample:dismounted-foot-ins` - code and walkthrough in [samples/dismounted-foot-ins](../../samples/dismounted-foot-ins/)

A stdlib-only error-state EKF (position, velocity, attitude, accel and gyro bias) with SHOE, ARED, AMVD and MBGTD stance detectors, run on all 36 real foot-mounted IMU trials of the UTIAS pyshoe hallway dataset (214.6 m out-and-back route, surveyed floor markers) and compared with pyshoe's own INS on the same trials. It adds corridor-direction heading constraints, a floor-height constraint, simulated UWB ranges with NLOS outliers, and shows on the raw magnetometer logs why compass heading fails indoors. Positions go out as CoT blue-force events via samples/mavlink-to-tak-cot/cot.py and as navdash/1 tracks for templates/demo-dashboard.

**Verification:** Ran 2026-11-06 with python3.14.7 stdlib on all 36 real pyshoe hallway trials (downloaded from the UTIAS FTP): default 15-state filter 2.35 m mean ARMSE / 1.30 % final error of the 214.6 m route / 3.63 m mean max error vs pyshoe's own INS 2.51 m / 1.49 % / 3.92 m on the same trials (pyshoe 6bbc4df run in a Python 3.11 venv with numpy 1.23.5, scipy 1.10.1; LSTM/SVM detectors stubbed). Stdlib SHOE labels match pyshoe on 100 % of samples and the 9-state mode reproduces pyshoe to 2.7 mm at every marker. Corridor heading + floor + simulated UWB (inflated covariance + NIS gate) gives 1.07 m / 0.83 % / 2.80 m on held-out markers; magnetometer heading from the real raw logs is off by a median 14-40 deg and makes all 6 tested trials 2-9x worse. UWB ranges, anchors and NLOS are simulated, only at marker epochs; CoT/navdash export generated and parsed but not rendered in a browser or sent to a live TAK server. 18 unit tests pass; 4 planted mutations each fail at least one.

## Deep dives

- [pyshoe](../../docs/dataset-cards/pyshoe.md) (dataset-cards)

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `zupt`, `foot-mounted-ins`, `pedestrian-dead-reckoning`, `error-state-ekf`, `shoe`, `mbgtd`, `zero-velocity-detection`, `heuristic-drift-elimination`, `uwb`, `nlos`, `nis-gate`, `magnetometer`, `indoor`, `cot`, `tak`, `blue-force`, `navdash`, `stdlib`, `real-data`

**Domains:** dismounted

## Related

- uses: [PyShoe](../../catalog/repos/utiasstars__pyshoe.md)
- explains: [ZUPT-aided INS (OpenShoe MATLAB)](../../catalog/repos/hcarlsso__zupt-aided-ins.md)
- explains: [IEZ (INS-EKF-ZUPT)](../../catalog/repos/pajaraca__iez.md)
- explains: [OpenShoe: open source embedded foot-mounted INS](../../catalog/resources/openshoe-foot-mounted-ins-2012.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [University of Toronto Foot-Mounted Inertial Navigation Dataset](../../catalog/resources/uoft-foot-mounted-ins-dataset.md) (dataset_for)

_Indexed by lane(s): samples_
