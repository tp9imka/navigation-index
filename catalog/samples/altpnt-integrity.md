# Sample: Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram

`sample:altpnt-integrity` - code and walkthrough in [samples/altpnt-integrity](../../samples/altpnt-integrity/)

A stdlib-only simulated UAV flight with INS, VIO-like velocity, intermittent visual-geolocalization fixes (repetitive-texture outliers, map-misregistration bias, dropouts over water), optional coarse MagNav-like fixes and a GNSS that is jammed and then spoofed. An 8-state EKF with chi-square innovation gating feeds a solution-separation bank that detects, excludes or (with only two sources) alerts and resolves by dead-reckoning consistency, computes horizontal protection levels against an alert limit, and reports MI/HMI, availability, time-to-alert and an ASCII/SVG Stanford diagram. A monitor-off negative control shows the misleading-information events the monitor removes. v2 (altpnt_v2.py, calibration.py) extracts measured error models from sibling samples (OpenVINS / KISS-ICP / nadir-VO heading and scale, real visual-geoloc availability, bias and residuals, TRN confidence-vs-error), adds heading and scale states, a DeCleene/Rife-style Gaussian overbound with a bias term, per-source fault priors and TRN measurement covariance from particle spread, and shows that v1's zero-MI result fails under measured models (MI* 0 => 8901 of 12000 epochs) while v2 restores zero MI at 13-26 % availability instead of 41.7 %.

**Verification:** ran with python3.14.7 stdlib on 2026-11-06: default run, --magnav, --no-gnss, --al-sweep, 20-seed Monte Carlo for 8 configurations, CSV and SVG writers (SVG rendered with macOS qlmanage and inspected); 15 unit tests pass (python3 -m unittest), and the detection tests were confirmed to fail with detection disabled. Synthetic data only; no real flight log or indexed repo was run. v2: ran with python3.14.7 and 3.12.14 stdlib on 2026-11-06: calibration.py --check reproduces calibration.json from the committed sibling results; 20-seed Monte Carlo over 29 world/filter rows (182 s), v1 rows identical to the v1 table; 10 v2 unit tests pass. Error models are measured on short real runs (27-197 s) and replayed over a synthetic 600 s flight; correlation times and fault-rate priors for GNSS are assumptions.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [uzh-fpv](../../docs/dataset-cards/uzh-fpv.md) (dataset-cards)

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `integrity`, `protection-level`, `alert-limit`, `raim`, `araim`, `solution-separation`, `fde`, `chi-square`, `innovation-gate`, `stanford-diagram`, `time-to-alert`, `spoofing`, `ekf`, `stdlib`, `overbounding`, `calibration`, `error-model`, `heading-bias`

## Related

- explains: [MAAST for ARAIM](../../catalog/repos/stanford-gps-lab__maast_for_araim_2.md)
- explains: [RAIM (MATLAB)](../../catalog/repos/michaelbeechan__raim.md)
- explains: [FilterPy](../../catalog/repos/rlabbe__filterpy.md)
- explains: [GTSAM](../../catalog/repos/borglab__gtsam.md)
- explains: [UASTHN](../../catalog/repos/arplaboratory__uasthn.md)
- uses: [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md)
- uses: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- uses: [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md)
- uses: [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)
- [Multi-source fault detection and exclusion on one real flight: ARAIM-style subset exclusion across GNSS, visual fixes and two TRNs (VPAIR)](../../catalog/samples/multi-source-fde.md) (uses)
- [Cooperative localization for a GNSS-denied team: UWB ranging, centralized EKF vs covariance intersection, and a spoofed anchor](../../catalog/samples/swarm-coop-localization.md) (explains)
- [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md) (uses)

_Indexed by lane(s): samples_
