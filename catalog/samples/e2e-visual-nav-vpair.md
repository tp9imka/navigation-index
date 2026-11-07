# Sample: End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)

`sample:e2e-visual-nav-vpair` - code and walkthrough in [samples/e2e-visual-nav-vpair](../../samples/e2e-visual-nav-vpair/)

Chains four sibling samples by import on the real VPAIR light-aircraft flight (199 nadir frames, 8.98 km, ~320 m AGL): attitude-aided nadir VO (with and without a 2 deg heading error), every frame DINOv2 GeM top-5 retrieval over VPAIR's orthophoto renders (other capture time, leave-own-render-out, map thinned to 45/180/360 m tile spacing, plus 200 distractors), ALIKED+LightGlue fine matching with an inlier gate, single-frame vs multi-frame voting fixes (VO carries earlier candidates forward), fused by the altpnt-integrity v2 EKF with heading/scale states and no gate, chi-square gate or solution-separation FDE. Reports error vs distance, fix availability, false fixes produced and fused, protection level and HMI, runtime per frame on M2, and exports navdash/1 for templates/demo-dashboard.

**Verification:** Ran 2026-11-06 on Apple M2 Max (Python 3.12.14, torch 2.15.0 MPS, LightGlue 5a650c4, DINOv2 ViT-S/14) on the VPAIR Zenodo sample: frontend.py twice (recorded yaw and yaw +2 deg, 231 s each for strides 1/4/8), run_fusion.py 148 configurations in 16 s, screenshot.sh headless Chrome at frames 100 and 198. After GNSS loss (8.53 km): VO only with +2 deg heading 271 m final / 156 m RMS (57.7 m final with recorded yaw); VO + single-frame strict-gate fixes 4.8 m RMS, 19 m max, 149/188 frames fixed, 0 false; 360 m map spacing 9.7 m RMS, 47 % fixed. Loose match gate without the filter gate fused 15 false fixes (errors to 65 km, 151 HMI epochs); voting and the chi-square gate each removed all false fixes in every run. Solution-separation PL median 1.25 km (1.6 % available): one absolute source cannot be protected. 0.73 s per frame. Tests: venv 15 pass; plain python3 5 pass, 10 skip. Limits: one 199-frame flight, map renders posed from the same GNSS/INS truth, map tiles on the flown track, no IMU, VO error model fitted on this flight.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| optional-gpu | none | cache-required | unknown | 861.249 MB | macos-arm64 | integrated |

**Main limitation:** One flight; map renders share the GNSS/INS reference and the VO error model was fitted on this flight.

**Readiness evidence:** [samples/e2e-visual-nav-vpair/README.md](../../samples/e2e-visual-nav-vpair/README.md), [samples/e2e-visual-nav-vpair/sample.json](../../samples/e2e-visual-nav-vpair/sample.json), [docs/dataset-cards/vpair.md](../../docs/dataset-cards/vpair.md)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `vpair`, `nadir-vo`, `dinov2`, `gem`, `lightglue`, `aliked`, `vpr`, `voting`, `integrity`, `protection-level`, `solution-separation`, `chi-square-gate`, `gnss-denied`, `fixed-wing`, `navdash`, `mps`

## Related

- uses: [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md)
- uses: [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md)
- uses: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- uses: [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md)
- uses: [VPAIR](../../catalog/repos/aervisloc__vpair.md)
- uses: [VPAIR - Aerial Visual Place Recognition and Localization in Large-scale Outdoor Environments](../../catalog/resources/vpair-dataset-2022.md)
- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- explains: [AnyLoc](../../catalog/repos/anyloc__anyloc.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Three selective offline starter bundles](../../docs/starter-bundles.md) (mentions)
- [Fixed-wing golden demo: ArduPlane 4.6.3 SITL on a 27.6 km route, coherent GPS drag, golden-demo monitor, EKF3 switch to ExternalNav fed by measured day (VPAIR) and night (thermal) geoloc fix models vs airspeed dead reckoning only](../../catalog/samples/golden-demo-fixedwing.md) (uses)
- [Multi-source fault detection and exclusion on one real flight: ARAIM-style subset exclusion across GNSS, visual fixes and two TRNs (VPAIR)](../../catalog/samples/multi-source-fde.md) (uses)
- [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md) (uses)

_Indexed by lane(s): samples_
