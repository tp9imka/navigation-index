# Q-CTRL quantum-assured MagNav - paper digest
<!-- about: res:qctrl-quantum-assured-magnav-2025 -->
**Quantum-assured magnetic navigation achieves positioning accuracy better than a strategic-grade INS in airborne and ground-based field trials** - Muradoglu, Johnsson, Wilson, ..., Hush, Anderson, Szigeti, Biercuk (19 authors, Q-CTRL), arXiv 2025 (v1, 2025-04-10; no later version). [paper](https://arxiv.org/abs/2504.08167) | code: none | Read: full text via arXiv HTML v1.

## Problem
GNSS is jammable and INS error grows without bound. Earlier MagNav work was mostly simulation or limited flight tests, held back by magnetometer noise, platform interference and the need for calibration maneuvers. The paper reports field trials of a full MagNav system on aircraft and a ground vehicle, benchmarked against a strategic-grade INS.

## Method
- Sensor: Q-CTRL scalar optically pumped rubidium magnetometer (<80 fT/sqrt(Hz) at Earth field, 250 Hz bandwidth, ~70 g, 144 cm3, <15 W) plus a Bartington Mag619U fluxgate.
- Denoising and map matching are done jointly in one estimator, not as two stages (proprietary; not specified in detail).
- An adaptive physics-based platform interference model (TL-like coefficients) is learned online from zero ("cold start"), or reused from a prior flight on the same vehicle ("warm start"). No calibration maneuvers.
- Tolerates initial position error up to 4 km.
- Maps: IGRF-13 core field, EMAG2v3 crustal, Geoscience Australia TMI grid 2019 (7th ed.) for the trials, upward/downward continued to platform altitude.
- Filter updates up to 250 Hz "on standard embedded microprocessors".

## Data and sensors
- Air: Cessna 208B Grand Caravan, >6,700 km over a week in February 2025 near Griffith, Australia, from near ground level to 19,000 ft. Magnetometers mounted onboard (inside the airframe) and outboard.
- Ground: rental van, strapdown, three days in November 2024 south of Orange, NSW; 15-20 km routes, 75% sealed roads, 750-950 m elevation.
- Reference INS: strategic-grade COTS, Table 2: gyro bias instability 0.001 deg/hr, accelerometer bias instability 7 ug.
- Data not public. No dataset card in this hub. Nearest public analogue: [magnav-challenge-data](../dataset-cards/magnav-challenge-data.md) (same aircraft type).

## Headline results (as reported)
Table 1, final position error, INS vs MagNav:
- (a) 3,600 ft, onboard mag, airspeed-aided INS, 365 km: INS 19,313 m (5.3%) vs MagNav 515 m (0.14%), 38x.
- (a) same, with 3D velocity aiding: INS 319 m (0.09%) vs MagNav 22 m (0.006%), 15x. This is the "22 m best final accuracy" in the abstract.
- (a) outboard mag, 3D velocity, 420 km: INS 5,125 m (1.2%) vs 112 m (0.027%), 46x (Fig. 4a).
- (b) 16,000-18,000 ft, outboard, airspeed, 580 km: 40,000 m (6.9%) vs 2,000 m (0.34%), 20x.
- (b) 15,000-19,000 ft, onboard, airspeed, 300 km: 40,000 m (13.3%) vs 2,000 m (0.67%), 20x.
- (c) ground, onboard, 18 km: INS 1,200 m (6.9%) vs MagNav 180 m (1.03%), 7x (Fig. 7; anomaly range ~600 nT, noise up to 30,000 nT).
- Fig. 5 (19,000 ft): onboard magnetometer RMS noise ~13x the stinger magnetometer, positioning comparable.
- Fig. 6 (19,000 ft, 750 km): cold start and warm start "statistically indistinguishable".
- Runtime: up to 250 Hz updates on embedded processors (text); no per-update timing table located.

## Limitations
- Stated by authors: maps are not available everywhere and the method degrades over magnetically flat regions; extreme solar events can mask anomalies; public global maps are ~2 arc-min (~3 km) with ~6 km reference heights and poor ocean coverage; not yet validated at airline cruise altitude, under highly dynamic maneuvers or over water; optimal sensor count/architecture is open; INS comparisons are not head-to-head under identical conditions (Fig. 4 caption).
- Our read: the text quotes an "11-38x" advantage for onboard magnetometers, but no 11x row appears in Table 1 (onboard airborne rows are 15x-38x; all rows 7x-46x). Other small inconsistencies: Fig. 4a text ~0.024% vs Table 1 0.027%; sensor volume "~63 cc" in text vs 144 cm3 in the sensor section; ground route 17.5 km in text vs 18 km in Table 1.
- Our read: the comparator is an INS with weak aiding (airspeed). The 22 m result uses 3D velocity aiding for both sides, a much stronger baseline.
- Our read: vendor paper about its own product, single region (inland Australia, good TMI survey grid), algorithm not disclosed enough to reimplement.

## Code, weights, license
- No code, no data, no model released. Algorithm and sensor are proprietary (Q-CTRL).
- Maps used are public (IGRF-13, EMAG2v3, Geoscience Australia TMI grid).

## Reproduction effort (estimate)
Estimate:
- Not reproducible: hardware, flight data and estimator are all closed.
- A conceptual proxy on public data: MagNav.jl on the SGL Ottawa flights with online TL estimation inside the filter (MagNav.jl has `ekf_online.jl` and `ekf_online_nn.jl` in `src/`). CPU only, 1-2 days to a comparable INS-vs-MagNav plot.

## What a hackathon team can take from it
- Evaluation protocol: report final error as absolute metres, % of distance travelled and the factor over a free/airspeed-aided INS, per trajectory and altitude. Table 1 is a good template.
- Online interference learning without calibration maneuvers is the operational trick. Prototype it by putting TL coefficients into the filter state (MagNav.jl `ekf_online`) instead of fitting TL offline.
- The ground-vehicle row (7x with ~50x noise-to-signal) shows MagNav can help land vehicles, but only as a slow drift bound.
- Use the stated limits as a site check: flat magnetic terrain, ocean, coarse public maps => do not expect these numbers.
- Integration: [MagNav.jl integration card](../integration-cards/mit-ai-accelerator__magnav.jl.md) for the open stack to imitate this.
