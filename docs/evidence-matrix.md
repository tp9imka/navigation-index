# Evidence matrix

Every measured number in the hub's samples, by capability, with the kind of input it was
measured on. This is the page to cite from in a pitch. Numbers are copied from each sample's
README (snapshot 2026-11-06); the link in the first column goes to the README section that
holds the full table. Nothing here was re-run for this page.

**Input column.** `real` = recorded public data (named). `SITL` = real autopilot firmware in
simulation, simulated sensors. `synthetic` = simulated vehicle and sensors, sometimes over real
terrain, maps or traffic (named). A synthetic or SITL number shows that a method works under the
stated model; it is not a field result. Say which kind it is when you quote it.

**Runs column.** How many seeds, flights or trials stand behind the number. One run is an
example, not a statistic.

Sample index with status and first command: [samples/README.md](../samples/README.md).
Which statement each capability answers: [problem-statement-decoder.md](problem-statement-decoder.md).

Contents: [1 Spoof detection on a vehicle](#1-gnss-spoof-detection-on-a-vehicle) -
[2 Receiver and signal level](#2-receiver-and-signal-level-detection) -
[3 Integrity metrics](#3-integrity-metrics-protection-level-misleading-information) -
[4 Absolute alt-PNT](#4-absolute-alt-pnt-position-error) -
[5 Relative nav and drift](#5-relative-navigation-and-drift-without-gnss) -
[6 Jammer localization and mapping](#6-jammer-localization-and-interference-mapping) -
[7 Maritime](#7-maritime) - [8 Dismounted](#8-dismounted) - [9 Swarm](#9-swarm) -
[10 Timing](#10-timing-holdover) - [11 C-UAS](#11-counter-uas-detection) -
[12 GNSS processing](#12-gnss-processing-baselines) -
[13 Functional checks](#13-functional-checks-no-accuracy-metric)

## 1. GNSS spoof detection on a vehicle

Time to detect (TTD) is measured from attack onset. "Deviation" is the true cross-track or
horizontal error of the vehicle or filter.

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [golden-demo v1](../samples/golden-demo/README.md#v1-results-ran-2026-11-06-one-run-each-seed-7) | ArduCopter 4.6.3, `SIM_GPS_GLITCH` drag 1 m/s east, windowed chi-square, switch to ExternalNav | TTD 9.4 s (offset 9.3 m); max cross-track 7.6 m with monitor vs 75.0 m without; EKF error at mission end 88.3 m without, GPS_GLITCHING never set | SITL; vgeo = truth + 1.5 m | 1 flight per mode, seed 7 | SITL GPS has no horizontal noise, so the pre-attack margin is flattering |
| [golden-demo v2 reference](../samples/golden-demo/README.md#v2-reference-run-ran-2026-11-06-one-run-each-seed-7-speedup-1) | Coherent 1 m/s drag via `GPS_INPUT`, replayed real geoloc, SS + velocity test | Velocity test TTD 3.0 s; chi2 +19 s, SS +27 s; max cross-track 6.8 m vs 75.0 m; max EKF error 8.0 m vs 93.7 m | SITL; geoloc = real matches on rendered NAIP frames; VIO = truth + noise | 1 flight per mode, seed 7 | VIO is an oracle with noise and bias |
| [golden-demo v2 MC](../samples/golden-demo/README.md#v2-monte-carlo-ran-2026-11-06-52-flights), position drag | 0.3 / 1 / 3 m/s | TTD median 45 / 22.5 / 6.2 s; deviation with monitor median 8.4 / 17.4 / 7.4 m vs 25.7 / 75 / 64.6 m without; 0 missed, 0 false alarms | SITL, replayed real geoloc | 4 flights per cell (seeds 1-4), speedup 3 | Small MC; TTD resolution 1 s; thresholds are the author's |
| [golden-demo v2 MC](../samples/golden-demo/README.md#v2-monte-carlo-ran-2026-11-06-52-flights), coherent drag | 0.3 / 1 / 3 m/s | TTD median 37.4 / 2.8 / 1 s; deviation median 11.1 / 7.4 / 5.8 m (worst 29.1 m) vs 28.8 / 75 / 84 m without | SITL, replayed real geoloc | 4 flights per cell | At 0.3 m/s one "detection" 1 s after onset is a false alarm landing after onset |
| [golden-demo v2 MC](../samples/golden-demo/README.md#v2-monte-carlo-ran-2026-11-06-52-flights), no spoof | Per-detector false alarms | chi2 4 of 4 flights; SS 0 of 4; velocity test 0 of 4 | SITL, real geoloc (registration bias 3-5 m) | 4 flights | Why v2 does not act on chi-square |
| [golden-demo live mode](../samples/golden-demo/README.md#real-visual-geoloc-v2) | Live ALIKED + LightGlue in the loop, coherent 1 m/s | Velocity test 3.0 s; max cross-track 7.8 m; 23 of 34 match attempts fixed (68 %), median fix error 4.5 m, ~3.5 s per match on CPU | SITL + real image matching | 1 flight | "One flight, not a statistic" |
| [altpnt-integrity](../samples/altpnt-integrity/README.md#observed-output-python3147-2026-11-06) | 600 s at 30 m/s (18 km), GNSS jammed then spoofed, full monitor | Spoof detected 15 s after onset, GNSS blamed at 65 s; with `--magnav` excluded 28 s after onset | synthetic | seed 1 | 2D model, illustrative thresholds |
| [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/README.md#expected-output-observed-python3147-2026-11-06) | Spoof walk-off vs chi-square gate (3 rejects = alarm) | 1.0 m/s: alarm 20 s after onset, EKF error 122.8 m (no gate) => 46.5 m (gate + latch); 2.0 m/s: alarm 7 s; 0.05-0.5 m/s: never | synthetic | seed 7 | Slow drags are absorbed before the gate fires |
| [usv-gnss-denied-nav](../samples/usv-gnss-denied-nav/README.md#results-5-seeds-real-outputs) | Drag 0.003 m/s^2 to 0.6 m/s, radar-chart + DR reference, SS + 30 s mean test | Coastal onset: alarm and exclusion 125-131 s, offset 23-26 m; open-water onset: alarm 202-250 s, exclusion 235-285 s; 1.5 km radar range: alarm 397-602 s | synthetic sensors over real OSM chart and real DMA AIS traffic | 5 seeds | Radar sees the same chart it matches against |
| [swarm-coop-localization](../samples/swarm-coop-localization/README.md#results-10-seeds) | One GNSS anchor of 6 spoofed, centralized solution separation | Detected 9 of 10 seeds, 1 false alarm, latency median 30 s [24, 34]; with bearings 10/10, 0 false, 28 s | synthetic UWB | 10 seeds | NLOS and comms models assumed |

## 2. Receiver and signal level detection

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [gnss-signal-chain](../samples/gnss-signal-chain/README.md#before--after) dragoff | gps-sdr-sim => mixer => GNSS-SDR 0.0.19 => scorer; drag starts t=80 s | First alert t=89 s (CV prior, fix 20.5 m off) / t=86 s (static reference, 10.7 m off): 9 / 6 s after drag start; PVT captured to 977.8 m off truth | simulated IQ, real receiver software | 2 runs (numbers from run 2) | GNSS-SDR runs not bit-identical; AGC is a file-power proxy |
| [gnss-signal-chain](../samples/gnss-signal-chain/README.md#results-ran-it-2026-11-06-apple-silicon-docker-arm64-4-vcpu) clean / denial | clean, overpower, jam-then-spoof | Clean: median 2.9 m, 0 alarm epochs; overpower: lost-fix alarm t=81 s; jam-then-spoof: t=76 s (PVT outage, not capture) | simulated IQ | 2 runs | Not validated on a hardware receiver |
| [gnss-interference-monitor](../samples/gnss-interference-monitor/README.md#run-verified-part) soak | iid Gaussian noise, 20 seeds x 3600 epochs per mode | 0 alert epochs (CV prior); 3 alert epochs, 2 alarms (static reference) | synthetic | 20 h per mode | "Treat this as a floor, not a rate" |
| [gnss-interference-monitor](../samples/gnss-interference-monitor/README.md#run-verified-part) drag sensitivity | Static receiver, accelerating or constant drag | Static reference: 0.002 m/s^2 => 137 s / 19 m; 0.02 => 38 s / 14 m; 0.5 => 4 s / 4 m; 0.2 m/s constant => 97 s / 19 m; 0.1 m/s => none in 600 s. CV prior: nothing below 0.05 m/s^2 in 240 s | synthetic | 1 per row | Thresholds are starting points |
| [gnss-interference-monitor](../samples/gnss-interference-monitor/README.md#run-pyubx2-offline-replay-of-a-synthetic-capture) UBX replay | 180 s synthetic UBX capture through pyubx2 | 109 clean / 30 jamming / 41 spoofing epochs; alarm latched 60-98 s and 120-169 s | synthetic capture | 1 | Values invented, not recorded |
| [osnma-authentication](../samples/osnma-authentication/README.md#results-on-the-real-recording-ran-2026-11-06) | OSNMAlib on a 76 min real Galileo I/NAV recording, 10 manipulations of 20 min | Clean: 4711 tags, 0 failures (76 min); forged OMEGA_0 on 3 SVs => 277 tag failures; random keys => 97 key-chain failures; 120 s GST shift => 590 pages rejected + 73 key failures; replay without independent clock and 3 s meaconing => authenticate normally; 1 h replay with clock => nothing authenticated, no failure | real recording, manipulated in memory | 1 per scenario | Forged data after authentication stayed "authenticated" 10 min (same IOD) |
| [maritime-ais-spoofing](../samples/maritime-ais-spoofing/README.md#results-on-injected-episodes-all-ran-2026-11-06) | Track-plausibility detectors on AIS, injected offset / drift / circle / group episodes | Recall 0.79 (0.82 observable), TTD median 7 s, p90 80 s (tuning day); 1-2 m/s drift 0.10. Held-out day: recall 0.75, TTD 8 s / 106 s, offsets >= 2 km 0.90, drift 0.39. Precision per run 0.64-0.70 | real DMA AIS with synthetic episodes | 3 seeds x 2 days, 738 + 741 episodes | No real spoofing in the 8.8 h analysed; one held-out day |

## 3. Integrity metrics: protection level, misleading information

MI = position error above the protection level while the PL is below the alert limit (AL);
HMI = error above the AL while the PL says it is fine.

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [altpnt-integrity](../samples/altpnt-integrity/README.md#observed-output-python3147-2026-11-06) | AL 50 m, monitor none / gate / full | Availability 90.9 / 89.0 / 41.7 %; MI epochs 5127 / 4614 / 0; HMI 3217 / 2371 / 0; missed hazards 25 / 16 / 0 | synthetic | 20 seeds x 600 epochs | Pessimistic noise models on purpose |
| [altpnt-integrity](../samples/altpnt-integrity/README.md#observed-output-python3147-2026-11-06) `--no-gnss` | Same, GNSS off | Full monitor availability 5.0 %, 0 MI, 0 HMI; no monitor 1173 HMI epochs | synthetic | 20 seeds | Low availability is the honest answer without GNSS |
| [golden-demo v2](../samples/golden-demo/README.md#v2-monte-carlo-ran-2026-11-06-52-flights) | Solution separation, AL 50 m | HPL median before onset 12.8 m; 801 of 2875 monitor-flight epochs unavailable; 0 misleading epochs in no-spoof flights | SITL | 52 flights | Noise model guessed, not fitted to a receiver |
| [relative-nav-benchmark](../samples/relative-nav-benchmark/README.md#altpnt-integrity-with-a-measured-relative-source) | altpnt-integrity re-run with drift models fitted on real runs, GNSS off, AL 50 m | OpenVINS model as tuned: HPE max 842 m, 358 of 600 MI epochs; retuned: HPE RMS 16.9 m, availability 2.6 %. KISS-ICP model: 0 MI | synthetic, error models fitted on real data | seeds 1-5 | 50 s and 28 s real runs do not characterise long flights |
| [terrain-heightmap-pf](../samples/terrain-heightmap-pf/README.md#4-no-truth-confidence-output) | Particle spread as a no-truth confidence | Spearman rho vs true error +0.84 pooled (+0.30 to +0.72 per region); error below 1x spread on 82 % of updates, below 2x on 99 % | real GLO-30 terrain, simulated flights | 80 runs, 4720 updates | A correlation check, not a PL validation |

## 4. Absolute alt-PNT: position error

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [visual-geolocalization-lightglue](../samples/visual-geolocalization-lightglue/README.md#run) | SuperPoint + LightGlue + homography vs ortho | 0.04-0.21 m over yaw 0-135 deg, tilt, 60-150 m prior; 30.67 m wrong fix accepted (162 inliers) at the ortho edge; other city: no fix | synthetic pairs cut from one real OpenAerialMap ortho (Tbilisi) | 1 per case | Same survey for frame and map: a pipeline check, not robustness |
| [geoloc-license-clean](../samples/geoloc-license-clean/README.md#measured-results-ran-2026-11-06) same map | ALIKED / DISK / SIFT + LightGlue | 20/20 fixes each; median 0.11 / 0.11 / 0.10 m; 1.43 / 2.79 / 0.28 s per frame (CPU) | synthetic frames from NAIP 2023 | 20 frames, seed 7 | |
| [geoloc-license-clean](../samples/geoloc-license-clean/README.md#measured-results-ran-2026-11-06) cross-season | Frames from NAIP 2019 vs 2023 map | Fixes 20 / 16 / 13 of 20; median 3.88 / 4.82 / 1.90 m; no wrong fix accepted (worst 15.6 m) | synthetic frames from real NAIP 2019 | 20 frames | |
| [geoloc-license-clean](../samples/geoloc-license-clean/README.md#what-the-real-frame-result-says) real frames | 5 real eBee frames vs NAIP | 1 of 5 fixed (ALIKED, 2019 map, tight prior), 11.0 m error; 0 of 5 in every other configuration; no wrong fix accepted | real (ODM Aukerman, 2016) | 5 frames | "Read it as a warning, not a rate" |
| [golden-demo](../samples/golden-demo/README.md#real-visual-geoloc-v2) geoloc table | ALIKED + LightGlue, rendered 150 m AGL frames from NAIP 2019 vs NAIP 2023 | 246 of 425 nodes fixed (58 %); error median 3.3 m, p90 5.6 m, max 9.9 m | real imagery, rendered nadir | 425 nodes, one match each | Timing and per-frame variability not real |
| [terrain-heightmap-pf](../samples/terrain-heightmap-pf/README.md#results-ran-2026-11-06-cpython-31315-apple-m2-max-single-python-process) v1, 10 km | Gradient-magnitude heightmap PF vs TERCOM vs odometry | Median at 10 km: hilly 26 / 32 / 311 m; mixed 32 / 123 / 404 m; flat 41 / 210 / 334 m; synthetic smooth control 539 / 334 / 334 m | real GLO-30 terrain, simulated flight and sensors | 20 runs per cell | PF update ~1.1 ms, TERCOM fix ~20 ms (M2 Max) |
| [terrain-heightmap-pf](../samples/terrain-heightmap-pf/README.md#1-information-gate-never-worse-than-odometry-on-flat-terrain) v2, 10 km | + information gate, compass-bias state | Median / p90 at 10 km: hilly 12 / 14 m, mixed 27 / 59 m, flat 25 / 130 m; smooth control 336 m vs odometry 334 m (1 update of ~1300 passed the gate) | real GLO-30, simulated flights | 20 runs | v2 thresholds tuned on seeds 100-111 of the same regions |
| [terrain-heightmap-pf](../samples/terrain-heightmap-pf/README.md#2-compass-bias-as-a-particle-state-0-20-deg) compass bias | v2 with 0-20 deg compass bias | 10 km median 8-10 m (hilly), 26-53 m (mixed); bias estimated within 0.3-2 deg | real GLO-30, simulated | 12 runs per cell | |
| [terrain-heightmap-pf](../samples/terrain-heightmap-pf/README.md#3-real-1-m-airborne-lidar-binary-edges-vs-gradients-1-m-vs-30-m) LiDAR | v2 gradient on 1 m vs 30 m DSM | Final error median 0.4 m (1 m DSM) vs 13.9 m (30 m); 1 m DTM 6.5 m | real Geobasis NRW 1 m LiDAR; onboard map = same DSM + noise | 10 runs of 4 km | Map and sensor share acquisition |
| [blind-flight-bench](../samples/blind-flight-bench/README.md#straight-flights-all-regions-pooled) straight | Radar altimeter only, 20 km at 1500 m | Median / p95 at 20 km: beam-aware PF 148 / 983 m (18 % diverged); PF 760 / 16420 m; TERCOM 1289 / 5806 m; dead reckoning 1582 / 3659 m (92 %); team re-implementations 6549-22394 m median | real GLO-30 terrain (4 regions), simulated flights and altimeter | 40 flights | Team navigators re-implemented from README text, not their code |
| [blind-flight-bench](../samples/blind-flight-bench/README.md#turns-flights-all-regions-pooled) turns | Same, with turns, no heading sensor | Best: beam-aware PF 3908 m median, 80 % diverged; all others 95-100 % diverged | real terrain, simulated | 40 flights | |
| [terrain-relative-nav-pf](../samples/terrain-relative-nav-pf/README.md#observed-output-python3147-2026-11-06) | Stdlib PF, INS + radar altimeter | PF error 4-25 m vs INS 380.3 m at 200 s; flat control 1-sigma 229-301 m | synthetic DEM | seed 7 (and seed 3) | Single seed |
| [magnav-quickstart](../samples/magnav-quickstart/README.md#observed-output-2026-11-06) | MagNav.jl Tolles-Lawson + EKF, line 1006.08 | EKF DRMS 31.2 m; INS-only final error 218.8 m; CRLB DRMS 13 m | real SGL 2020 flight data | 1 line (14 min), 2 identical runs | Tolles-Lawson did not lower the residual here; INS re-zeroed at line start |
| [usv-gnss-denied-nav](../samples/usv-gnss-denied-nav/README.md#radar-chart-matching-by-route-leg-seed-1-default-6-km-range) radar fixes | Radar returns matched to the chart (ICP) | Accepted-fix error median 1.1-3.7 m per leg, p95 3.1-8.6 m (6 km range) | synthetic radar over real OSM chart | seed 1 | Optimistic: simulated world equals the chart |

## 5. Relative navigation and drift without GNSS

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [relative-nav-benchmark](../samples/relative-nav-benchmark/README.md#results) LiDAR | KISS-ICP 1.3.0 | ATE 0.23 m; final drift 0.12 % of 393.6 m; KITTI t_rel 0.41 % | real KITTI 04 | 1 sequence | Short, straight sequence: best case |
| [relative-nav-benchmark](../samples/relative-nav-benchmark/README.md#results) VIO | OpenVINS v2.7 stereo + IMU | ATE 0.36 m; final 0.26 % of 278.3 m; max 1.57 m | real UZH-FPV indoor_forward_3 (49.5 s GT) | 2 runs, same ATE to 1 mm | |
| [relative-nav-benchmark](../samples/relative-nav-benchmark/README.md#results) mono VO | OpenCV mono VO, GT scale oracle | ATE 0.80 m; final 0.68 % | real UZH-FPV | 1 | Scale given: not a fair competitor |
| [relative-nav-benchmark](../samples/relative-nav-benchmark/README.md#results) nadir VO | SIFT + RANSAC on nadir frames | Image only: final 15.5 % of 8980 m; attitude-aided 0.65 %; +2 deg yaw bias 3.2 %, +5 deg 8.1 % | real VPAIR (199 frames) | 1 | Attitude from recorded GNSS/INS = idealised AHRS |
| [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/README.md#observed) | PX4 EKF2, 15 s GPS denial | Max horizontal error 8.37 m and 17.71 m; 12.7 s and 8.5 s to 5 m | SITL (PX4 v1.17.0 SIH) | 2 runs | "Quote a range over several runs, not one number" |
| [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/README.md#expected-output-observed-python3147-2026-11-06) | 2D GNSS/INS EKF, 60 s outage | EKF max 7.7 m; INS-only max 1303.8 m in the same segment | synthetic | seed 7 | INS-only starts from the true state |
| [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/README.md#contrast-run-gps-cut-without-the-source-switch) | GPS cut without source switch | EKF coasts ~6 s, then failsafe LAND; ~3.6 m DR error the EKF had not reported | SITL (Copter 4.6.3) | 1 | Variances stayed "good" throughout |
| [dismounted-foot-ins](../samples/dismounted-foot-ins/README.md#result-1-stdlib-filter-vs-pyshoe-shoe-g--85e7-w--5-all-36-trials) | See section 8 | | | | |

## 6. Jammer localization and interference mapping

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [jammer-sensor-network](../samples/jammer-sensor-network/README.md#monte-carlo-evaluatepy-40-trials-per-row-one-10-s-snapshot-of-static-nodes) node count | 4 x 4 km, 6 dB shadowing; grid Bayes / RSS least squares / grid + 3 DF stations | Median error: 4 nodes 602 / 566 / 55 m; 16 nodes 313 / 264 / 40 m; 32 nodes 173 / 200 / 38 m | synthetic (log-distance path loss, assumed constants) | 40 trials per row | One 10 s snapshot of static nodes |
| [jammer-sensor-network](../samples/jammer-sensor-network/README.md#monte-carlo-evaluatepy-40-trials-per-row-one-10-s-snapshot-of-static-nodes) density, shadowing | 16 nodes | 2 km side: grid 144 m, grid+DF 19 m; 8 km side: 777 m, 124 m. Shadowing 2 dB: grid 100 m; 10 dB: 520 m | synthetic | 40 trials per row | DF model has no bearing bias: optimistic |
| [jammer-sensor-network](../samples/jammer-sensor-network/README.md#scenarios-demopy-seed-1) scenarios | 12 static nodes + 2 vehicles | Static 10 dBm: grid 599 m, DF 23 m, grid+DF 57 m; moving jammer: grid 338 m; detection 5 s after jammer on | synthetic | seed 1 | Seeds 2 and 4 gave 794 m and 200 m |
| [interference-geolocation-to-tak](../samples/interference-geolocation-to-tak/README.md#run-all-of-this-was-run-on-2026-11-06) | 3 DF stations, 300 s, 111 outliers in 900 bearings | Error ls 14 m, pf 12 m, ukf 8 m; 95 % ellipse 49 x 33 m (ls); 30 s window: 68-81 m; truth inside the ellipse in every run | synthetic bearings | 1 seed | Real DF multipath not modelled: ellipses are best case |
| [osint-jamming-map](../samples/osint-jamming-map/README.md#ads-b-outadsb_summaryjson) ADS-B | GPSJam-style NACp hexes, SE Baltic, 2026-10-01 | 110 of 129 aircraft NACp < 8, 64 red hexes; NL/DE control 19 of 879, 108 green | real ADS-B Exchange samples | 121 / 13 snapshots | Control sampled 10x more sparsely: compare ratios |
| [osint-jamming-map](../samples/osint-jamming-map/README.md#sentinel-1-outs1_summaryjson) Sentinel-1 | C-band RFI z-score over 18 passes | Target pass 0.128 % of pixels z > 3, 0 candidate hexes; ESA rfiDetected on 9 of 18 dates; 2026-08-14 pass: 38 candidate hexes, 25 over water | real Sentinel-1 GRD | 18 scenes | No link between C-band RFI and GNSS jammers shown |

## 7. Maritime

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [usv-gnss-denied-nav](../samples/usv-gnss-denied-nav/README.md#results-5-seeds-real-outputs) | 19.6 km Oresund transit, GNSS drag; monitor vs baselines | Max error with monitor: coastal 10-25 m, open water 71-102 m, 1.5 km radar range 175-1024 m; GNSS + DR without monitor 1391-2261 m; DR only 510-539 m; jamming: 3-6 m with radar fixes vs 20-44 m GNSS + DR coasting; 0 false alarms | synthetic sensors, real OSM chart, real DMA AIS traffic | 5 seeds x 5 scenarios | Radar physics simplified; thresholds tuned on these runs |
| [maritime-ais-spoofing](../samples/maritime-ais-spoofing/README.md#results-on-injected-episodes-all-ran-2026-11-06) | See section 2 | | | | |
| [maritime-ais-spoofing](../samples/maritime-ais-spoofing/README.md#what-the-detectors-flag-on-unaltered-real-data) unaltered data | Detectors on 8.8 h of real AIS | 132 / 159 alerts on 61 / 70 vessels per day (mostly on-land: Kiel Canal, fjords); no crop-circle cluster; no spoofing found | real DMA AIS | 2 days | Alerts on real data count as false in the precision figure |

## 8. Dismounted

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [dismounted-foot-ins](../samples/dismounted-foot-ins/README.md#result-1-stdlib-filter-vs-pyshoe-shoe-g--85e7-w--5-all-36-trials) | Stdlib 15-state ZUPT EKF vs pyshoe's own INS | Mean ARMSE 2.35 m, final error 1.30 % of 214.6 m, mean max 3.63 m; pyshoe 2.51 m / 1.49 % / 3.92 m; 95 % radius covers the true error at 31 % of markers | real pyshoe hallway set | 36 trials | One tuning on one dataset |
| [dismounted-foot-ins](../samples/dismounted-foot-ins/README.md#result-3-aiding-ins15_py--shoe-85e7-all-36-trials) aided | + corridor heading + floor height + UWB (inflate + NIS gate) | 1.07 m / 0.83 % / 2.80 m; corridor heading alone 1.32 m / 0.83 % | real IMU; UWB simulated (4 anchors, 30 % NLOS) | 36 trials | Aiding tuned on an 18-trial subset, no held-out set |
| [dismounted-foot-ins](../samples/dismounted-foot-ins/README.md#result-4-the-magnetometer-indoors-real-logs-6-walk-trials) magnetometer | Mag heading indoors | Heading residual median 13.6-39.5 deg; position 2-9x worse, max error up to 28.44 m | real raw logs | 6 trials | Soft iron not modelled |

## 9. Swarm

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [swarm-coop-localization](../samples/swarm-coop-localization/README.md#results-10-seeds) | 6 vehicles, 2 with GNSS, UWB ranges | Team RMSE: dead reckoning 49.1 m, centralized robust 2.0 m, covariance intersection robust 5.5 m; bandwidth 138.1 vs 24.0 B/s per agent | synthetic | 10 seeds | No real UWB data |

Spoofed-anchor detection: section 1.

## 10. Timing holdover

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [timing-holdover](../samples/timing-holdover/README.md#output-ran-on-2026-11-06-python-3147-default-arguments-about-5-s) holdover | GNSS-disciplined oscillator, 6 h discipline, then outage; no temperature term | Median / 95th \|TE\| at 24 h: TCXO 59.58 / 64.26 us; CSAC 1.27 / 2.41 us; OCXO 610.0 / 680.7 ns; Rb 43.8 / 107.5 ns. At 1 h: 145.9 / 19.2 / 2.1 / 1.5 ns (medians) | synthetic, datasheet parameters | 20 runs | White FM + aging only: a floor for a datasheet, not a unit |
| [timing-holdover](../samples/timing-holdover/README.md#output-ran-on-2026-11-06-python-3147-default-arguments-about-5-s) with temperature | 0.1 of spec over 24 h | 24 h median: TCXO 3.41 ms, CSAC 3.08 us, OCXO 6.52 us, Rb 2.05 us | synthetic | 20 runs | Temperature fraction assumed |
| [timing-holdover](../samples/timing-holdover/README.md#output-ran-on-2026-11-06-python-3147-default-arguments-about-5-s) time-walk spoof | 0.5-10 ns/s walk; internal vs cross-source monitor | Cross-source alarm 120-660 s for every grade; guarded TE at end 4.1-94.8 ns (CSAC, OCXO, Rb) vs 3.53-71.98 us when following GNSS; no-spoof control 0/5 false alarms | synthetic | 1 seed per row, 5 control runs | "Five runs is a smoke test, not a false-alarm rate" |

## 11. Counter-UAS detection

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [cuas-classifiers](../samples/cuas-classifiers/README.md#1-radar-uav-vs-bird-from-tracks) radar | UAV vs bird from track features, HistGB | Balanced accuracy 0.928, AUC 0.964, UAV P/R 0.913 / 0.885 (5-fold GroupKFold by session); cross-site train Alma => test Laval 0.902 (HistGB), 0.918 (RF) | real NRC Echodyne radar tracks (510 tracks, 42 sessions) | 5 folds; 89 cross-site test tracks | Test site has only 22 bird tracks |
| [cuas-classifiers](../samples/cuas-classifiers/README.md#2-rf-dronerf-detection-and-identification) RF | DroneRF low band, RandomForest / HistGB | Detection balanced accuracy 0.977-0.994 (temporal holdout); 4-class identification 0.940 GroupKFold, 0.852 temporal | real DroneRF subset (73 segments) | holdout + GroupKFold | One recording session per class: "do not quote as field performance" |
| [remote-id-to-tak](../samples/remote-id-to-tak/README.md#1-decoder-validated-against-opendroneid-core-c-ran-it) decoder | Stdlib ASTM F3411 decoder vs opendroneid-core-c | Field-for-field equal on 500 encoded vectors, 500 random raw messages, 81 payloads from public captures | real captures + generated vectors | - | Validates a decoder, not detection rates |
| [remote-id-to-tak](../samples/remote-id-to-tak/README.md#3-track-management-and-anomaly-flags-ran-it-synthetic-data) flags | Plausibility flags (duplicate id, impossible speed, operator far) | Each flag fired on its scripted track | synthetic scenario | 1 | Shows the rules fire, not that thresholds are right |

## 12. GNSS processing baselines

| Sample | Setup | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [gnss-rinex-processing](../samples/gnss-rinex-processing/README.md#observed-results-2026-11-06) | RTKLIB demo5 SPP / RTK, gnss_lib_py WLS, 2 h GPS only | RTK E/N/U rms 0.084 / 0.055 / 0.071 m, 97 % fix; SPP 0.624 / 1.244 / 1.021 m; gnss_lib_py 0.65 / 1.28 / 1.10 m | real NOAA CORS P730 / P731, 2024-04-09 | 241 epochs, 1 day | One station pair, one day |

## 13. Functional checks (no accuracy metric)

| Sample | What was shown | Input |
|---|---|---|
| [mavlink-to-tak-cot](../samples/mavlink-to-tak-cot/README.md#part-2---bridge-offline-end-to-end-verified) | Well-formed CoT at ~1 Hz over TCP and UDP to a local sink | fake autopilot |
| [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/README.md#ardupilot-arducopter-copter-463-sitl) | EKF3 (flags 0x033f) and EKF2 (cs_ev_pos True) fuse a stationary ODOMETRY pose | SITL |
| [stone-soup-tracking](../samples/stone-soup-tracking/README.md#observed-output-stonesoup-191-python-31214-2026-11-06) | 2 tracks held on 2 truths, OSPA mean 17.0 m, max 53.0 m (c = 100 m) | synthetic, 1 seed |
| [llm-mission-agent](../samples/llm-mission-agent/README.md#what-was-verified-2026-11-06) | MCP tools flew takeoff, survey, GPS loss => degraded health => ExternalNav => RTL; fence and altitude rejections | SITL, scripted client (no LLM run) |
| [llm-agent-usage](../samples/llm-agent-usage/README.md) | MCP server answered 7 JSON-RPC requests | the hub's own index |
| [sitl-docker](../samples/sitl-docker/README.md#what-was-verified-2026-11-06-docker-2952-apple-silicon-linuxarm64) | Both SITL images built (ArduPilot ~8.5 min, PX4 ~26 min) and flew the other samples | - |
