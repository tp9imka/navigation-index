# Sample: Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay

`sample:golden-demo` - code and walkthrough in [samples/golden-demo](../../samples/golden-demo/)

One command flies ArduCopter 4.6.3 SITL in Docker on a survey and drags its GPS east. v1 uses SIM_GPS_GLITCH (position only), simulated visual geoloc and navapp's windowed chi-square test. v2 injects the GPS from a pymavlink companion as GPS_INPUT so the drag can be coherent (position + velocity), takes visual-geoloc fixes from real ALIKED+LightGlue matching of frames rendered from a 2019 NAIP orthophoto against a 2023 NAIP map (replayed from a 425-node table, or live), runs a solution-separation FDE bank with a horizontal protection level ported from samples/altpnt-integrity plus a GNSS-vs-VIO velocity test, and on alarm commands MAV_CMD_SET_EKF_SOURCE_SET 2 with the companion's GNSS-free reference as ExternalNav. A 52-flight Monte Carlo (seed x rate 0.3/1/3 m/s x spoof type, monitor vs shadow) reports time-to-detect, misses, false alarms and deviation with and without the monitor; an experiment localises v1's EKF lane switching to the SITL GPS path. Logs convert to navdash/1 for templates/demo-dashboard (PL vs AL ring in v2).

**Verification:** Ran 2026-11-06 on Apple Silicon (linux/arm64 Docker, Copter-4.6.3 SITL image from samples/sitl-docker, pymavlink 2.4.50, Python 3.12). v1 (one run per mode, seed 7): chi-square alarm 9.4 s after onset, max cross-track deviation 7.6 m with the monitor vs 75.0 m without. v2 reference (coherent 1 m/s, replayed real geoloc): velocity-test alarm 3.0 s after onset, 6.8 m vs 75.0 m, EKF GPS_GLITCHING never set. v2 Monte Carlo, 52 flights in 1201 s wall (3 parallel SITLs, speedup 3): ss+vel detected 24/24 monitor flights with 0 pre-onset false alarms and 0/4 false alarms without spoof; median TTD 45/22.5/6.2 s (position 0.3/1/3 m/s) and 37.4/2.8/1 s (coherent); v1 chi-square false-alarmed in 4/4 no-spoof flights with real geoloc. Real geoloc table: 246/425 frames fixed, median 3.3 m. One live-matching flight completed (68% fixes after AUTO, ~3.5 s per match). Lane-switch experiment: 4-6 switches with SITL GPS, 0 with injected GPS (2 seeds each); mechanism not found. 17 unit tests pass. VIO is truth plus noise; frames are rendered nadir from a real orthophoto; amd64 and ArduPilot 4.7+ not tested.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | cache-required | unknown | unknown | linux-arm64 | integrated |

**Main limitation:** Autopilot simulation with recorded/modelled aiding; not field or hardware validation.

**Readiness evidence:** [samples/golden-demo/README.md](../../samples/golden-demo/README.md), [samples/golden-demo/sample.json](../../samples/golden-demo/sample.json)

## Deep dives

- [naip-planetary-computer](../../docs/dataset-cards/naip-planetary-computer.md) (dataset-cards)

**Concepts:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `aliked`, `ardupilot`, `chi-square`, `coherent-spoof`, `dashboard`, `demo`, `docker`, `ekf3`, `externalnav`, `gps-drag`, `gps-input`, `integrity`, `lightglue`, `monte-carlo`, `naip`, `navdash`, `protection-level`, `pymavlink`, `raim-like`, `sitl`, `solution-separation`, `source-switch`, `spoofing`, `vision-position-estimate`

## Related

- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- uses: [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md)
- uses: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Three selective offline starter bundles](../../docs/starter-bundles.md) (mentions)
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) (dataset_for)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../../catalog/samples/altpnt-integrity.md) (uses)
- [Fixed-wing golden demo: ArduPlane 4.6.3 SITL on a 27.6 km route, coherent GPS drag, golden-demo monitor, EKF3 switch to ExternalNav fed by measured day (VPAIR) and night (thermal) geoloc fix models vs airspeed dead reckoning only](../../catalog/samples/golden-demo-fixedwing.md) (uses)

_Indexed by lane(s): samples_
