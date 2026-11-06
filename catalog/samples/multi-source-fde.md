# Sample: Multi-source fault detection and exclusion on one real flight: ARAIM-style subset exclusion across GNSS, visual fixes and two TRNs (VPAIR)

`sample:multi-source-fde` - code and walkthrough in [samples/multi-source-fde](../../samples/multi-source-fde/)

Extends two-source-integrity-vpair from detection to exclusion. One altpnt v2 EKF per subset of the absolute sources (16 filters: simulated GNSS, real visual fixes, LiDAR-heightmap TRN and GLO-30 TRN simulated over real terrain at the real VPAIR poses) runs on real nadir VO. A stdlib decision layer detects by solution separation, excludes only when exactly one candidate subset passes its own consistency test, declares unavailable when two or more do (or none), computes the PL from per-hypothesis priors and readmits after hold and probation. Seven scenarios over 10 seeds (GNSS drag-off spoof, visual misregistration, visual wrong-place lock, TRN secondary-peak ambiguity, two double faults) compare detection-only, single- and dual-fault subset FDE, and altpnt's largest-separation exclusion, which two-source reused. Reports detection latency, correct, partial and wrong exclusions, missed detections, HMI/MI and availability at AL 25/50/100 before and after exclusion.

**Verification:** Ran 2026-11-06 on Apple M2 Max, CPython 3.12.14 venv (numpy 2.5.4, scipy 1.18.1, rasterio 1.5.2): run_fde.py on the local VPAIR sample and two-source's NRW DSM / GLO-30 data, 10 seeds x 7 scenarios x 11 configurations, 164 s. Reproduces two-source's GNSS-denied three-source numbers with the reused max-separation monitor (84.7 % available at AL 50 nominal, 19 HMI at AL 50 under TRN ambiguity). Subset FDE: 0 HMI and 0 MI in every run at AL 25/50/100. GNSS 2 m/s drag-off: detected in 5-8 s, GNSS excluded 10/10, availability at AL 50 after onset 18.8 % detection-only => 83.8 %, error max 279 m => 21 m. Wrong exclusions: single-fault FDE 1 of 60 (a double fault, stayed unavailable, no HMI), dual-fault FDE 0 of 60, GNSS denied 0 of 30 with 7 runs unavailable instead; max-separation 27 of 60 and 25 of 30. Dual-fault monitoring drops GNSS-denied nominal availability at AL 50 from 84.7 % to 5.0 %. Tests: venv 17 pass; plain /opt/homebrew/bin/python3 3.14.7 14 pass, 3 skip. GNSS and TRN sensors simulated, faults injected, visual fixes and VO real.

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `integrity`, `fde`, `araim`, `solution-separation`, `fault-exclusion`, `protection-level`, `spoofing`, `gnss-spoofing`, `trn`, `visual-geolocalization`, `vpair`, `wrong-exclusion`, `availability`, `fault-injection`

## Related

- uses: [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md)
- uses: [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md)
- uses: [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md)
- uses: [VPAIR - Aerial Visual Place Recognition and Localization in Large-scale Outdoor Environments](../../catalog/resources/vpair-dataset-2022.md)
- uses: [Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models](../../catalog/resources/geobasis-nrw-dom1-dgm1.md)
- uses: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)
- explains: [MAAST for ARAIM](../../catalog/repos/stanford-gps-lab__maast_for_araim_2.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
