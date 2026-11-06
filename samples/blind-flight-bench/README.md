# Blind-flight bench: radar altimeter + GLO-30, six navigators, one harness

## Goal

Reproduce the 2026 "Polyot vslepuyu" (Blind flight) hackathon case on real terrain and score
navigators on the same flights. The case: an aircraft at a constant 1500 m MSL (barometric), a
radar altimeter at 1-10 Hz in NMEA `$GPGGA`, a Copernicus GLO-30 map, a known start point, heading
and speed hints, no GNSS, no IMU. Find position and velocity. Problem statement and team teardown:
[docs/landscape/blind-flight-teardown.md](../../docs/landscape/blind-flight-teardown.md).

The terrain is real. The flights, the altimeter and the altitude reference are simulated.

## What is in the box

| File | What |
|---|---|
| `regions.py` | Four GLO-30 windows (~36 x 35 km each), fetched by importing `../terrain-heightmap-pf/fetch_dem.py` and cached in `data/` (git-ignored, ~18 MB) |
| `sim.py` | Truth flights, the world surface the radar sees, the radar altimeter model, baro reference error, NMEA writer/parser |
| `navs.py` | The navigators below, plus `beam_map()` |
| `metrics.py` | Error at 5/10/20 km along-track, median/p95, divergence rate (stdlib only) |
| `run_bench.py` | Full grid (`out/results.json`, `out/results_leaderboard.md`) and `--ablation` (`out/ablation.json`, `out/ablation.md`) |
| `test_bench.py` | 10 unittest tests: metrics (stdlib), NMEA round trip and checksum, footprint geometry, beam map vs radar model, bias sign, DR and TERCOM sanity |
| `ext.py` | Loads `fetch_dem.py` and `core.py` from `../terrain-heightmap-pf` by file path so their `sim.py` does not shadow ours |

### Navigators

| Name | What | Origin |
|---|---|---|
| `dr_hint` | Start fix + heading/speed hints, straight line. No terrain. Floor reference | ours |
| `tercom_ours` | `core.tercom_fix` from [terrain-heightmap-pf](../terrain-heightmap-pf/) (mean-removed MAD, translation grid, ambiguity ratio 0.9) every 1 km on the last 2 km. The case has no odometry, so the track shape is a constant-velocity guess, corrected by an alpha-beta velocity update after each accepted fix; the search radius grows with distance since the last fix (600 m to 3 km) | ours, reused by import |
| `pf_ours` | SIR particle filter in the structure of [terrain-relative-nav-pf](../terrain-relative-nav-pf/) (gaussian terrain likelihood, systematic resampling, bias states). Without an INS the state is east, north, speed, heading, turn rate (piecewise constant, jump process) and altitude-reference bias; 4000 particles, update every ~60 m, gaussian + 5% uniform outlier likelihood | ours |
| `*_beam` | Same navigator, matched against `beam_map()` instead of the DEM: the terrain height a 40 deg leading-edge altimeter at 1500 m would report over each cell. Computable once per map because the case fixes the flight level (~8 s per 36 km window) | ours |
| `gagarin_cr` | Clean-room of the Gagarin checkpoint pipeline (`danilka88/gag27062026`) from its README: 360 deg NCC azimuth scan on the first 60 samples, top-3, 29 speeds by mean-removed MAD, 200-sample windows every 50, +-4 px grid, minima-ratio discrimination, roughness and pre-rejection gates, RANSAC-style innovation test, DR + `clamp((discr-1)/10)` weighted correction, multi-start, 7x7 lost-position recovery | re-implemented from text |
| `gagarin_cr_az200` | Same, azimuth scan on 200 samples instead of 60 | variant |
| `gagarin_cr_hint` | Same as az200, scan restricted to hint +-20 deg | variant (deviation: Gagarin always scans 360) |
| `gorizont_cr` | Clean-room of the GORIZONT tracker (`t1Gr20an06-k/Hackathon-Blind-Flight`) from its README flag table: median-3 + 3 Hz low-pass prefilter, bootstrap over azimuth (5 deg) x speed (0.2 px/s) x start offsets (+-8 px, 4 px), corr >= 0.65, up to 6 candidates with NMS; per hypothesis a constant-velocity KF; every 50 samples the last 300 samples of track are rotated (+-8 deg, 4 deg steps) and shifted (+-10 px) to re-match, ranked by corr minus offset/rotation/rank/innovation penalties, 35 px endpoint gate, measurement sigma 1-25 px by quality; up to 8 hypotheses | re-implemented from text |
| `gorizont_cr_hint` | Same with the README's `--initial-az-window-deg 20` instead of the default 180 | README flag |

Clean-room means: written from the README descriptions only, no team code read for the
navigators and nothing copied. Where a README leaves something open, the choice is ours and listed
in the class docstring: GORIZONT's penalty weights have no stated units (normalised to [0, 1] here),
its local grid step is 10 px in the README (2 px here, the README value gives a 3x3 grid), its
offline RTS/refit stages are not reproduced (the bench scores causal estimates), and the speed range
is widened from 45 to 60 m/s to cover the bench flights. Gagarin's RANSAC and multi-start
selection are post-hoc in the original and made causal here. A failure of a `*_cr` navigator is a
failure of our reading of the text, not proof the team's code fails the same way.

## Simulation model (`sim.py`)

- **Terrain**: four GLO-30 windows reprojected to UTM at 30 m by `fetch_dem.py`.

  | region | where | heights | local relief std (DEM minus 1 km low-pass) |
  |---|---|---|---|
  | khibiny | Khibiny massif, Kola peninsula: Arctic mountains, lakes | 126-1200 m | 77.8 m |
  | ural | Middle Urals near Kachkanar: forested ridges | 55-870 m | 25.2 m |
  | taiga | Yenisei ridge taiga near the GORIZONT test area | 24-233 m | 14.7 m |
  | flat | South of Moscow, inside the 55-56 N, 37-38 E bounds of the map KROT says it received | 116-255 m | 9.6 m |

- **Flights**: 20.5 km. `straight`: one heading, constant speed U(30, 55) m/s (the organiser
  checkpoint shape). `turns`: legs of 3-7 km joined by 30-120 deg turns at 3 deg/s, speed
  wandering +-2 m/s. Placed at random so the track stays 3 km inside the window.
- **World surface the radar sees**: DEM + correlated map error (sigma 3 m, 150 m correlation) minus
  canopy penetration of 2-8 m on 40% of the area. Assumption, not a measured GLO-30 error model.
- **Altitude**: true altitude = 1500 m + bias N(0, 25 m) + drift N(0, 0.03 m/s) x t + AR(1) wander
  (3 m, 20 s). The navigators only know "1500 m".
- **Radar altimeter**: leading-edge range, i.e. the shortest slant range to any surface point inside
  a 40 deg cone (flat attitude, 16 x 24 sample points); noise 0.5 m + 0.5% of range; 2% dropped
  messages plus 1-5 s loss-of-lock bursts (about 8% of samples lost in total); 0.5% outliers of
  +-30-300 m. Beam width and noise are assumptions for a "simple" altimeter, not a datasheet.
- **Input path**: written as `$GPGGA` lines with the height in field 9 (the case's format), parsed
  back with checksum validation, so the navigators get 0.1 m quantised heights with gaps.
- **Prior**: start fix N(0, 30 m), heading hint N(0, 5 deg), speed hint N(0, 2 m/s).

How large the footprint effect is: see Findings 1.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy rasterio
.venv/bin/python regions.py                 # fetch 4 windows, ~30 s
.venv/bin/python -m unittest discover    # 10 tests; 3 run without numpy, 7 skip
.venv/bin/python run_bench.py               # 10 runs x 4 regions x 2 families x 10 navigators, ~6 min
.venv/bin/python run_bench.py --ablation --runs 4 --navs tercom_ours tercom_ours_beam pf_ours pf_ours_beam gagarin_cr_hint gorizont_cr_hint
```

## Results

Ran 2026-11-06 on an Apple M2 Max laptop, CPython 3.13.15, numpy 2.5.4, scipy 1.18.1,
rasterio 1.5.2, one Python process. Evaluation seeds 0-9 (`straight`) and 1000-1009 (`turns`) per
region, so 40 flights per family. `pf_ours` knobs (measurement sigma, bias random walk, turn jump
rate) were picked on seeds 500-503; the `*_cr` navigators use their README defaults and were not
tuned. Error numbers are deterministic: two full runs gave identical errors for every navigator
whose code did not change between them. CPU and latency columns are wall-clock per update and
vary by tens of percent: other jobs were running on the same machine.

"Diverged" = error above 500 m at 20 km. "CPU s per 1000 s flown" = total update time over flight
time. "Worst step" = the slowest single `update()` call, i.e. the latency spike an onboard thread
must absorb.

### straight flights, all regions pooled

| navigator | 5 km med/p95 | 10 km med/p95 | 20 km med/p95 | diverged | CPU s per 1000 s flown | worst step ms |
|---|---|---|---|---|---|---|
| dr_hint | 416 / 910 | 810 / 1836 | 1582 / 3659 | 92% | 0.0 | 11 |
| tercom_ours | 387 / 910 | 668 / 2359 | 1289 / 5806 | 72% | 0.4 | 92 |
| tercom_ours_beam | 320 / 910 | 526 / 1316 | 939 / 2670 | 62% | 0.4 | 44 |
| pf_ours | 424 / 2896 | 483 / 7992 | 760 / 16420 | 57% | 0.4 | 44 |
| pf_ours_beam | 173 / 737 | 154 / 845 | 148 / 983 | 18% | 0.4 | 27 |
| gagarin_cr | 5633 / 14655 | 11878 / 27703 | 22394 / 55499 | 98% | 0.4 | 30 |
| gagarin_cr_az200 | 5095 / 12681 | 9818 / 25352 | 19673 / 50689 | 95% | 0.4 | 30 |
| gagarin_cr_hint | 1591 / 8046 | 2914 / 16620 | 6549 / 32591 | 92% | 0.4 | 40 |
| gorizont_cr | 3177 / 7570 | 7726 / 14042 | 17501 / 25191 | 92% | 3.1 | 254 |
| gorizont_cr_hint | 894 / 4660 | 2955 / 9881 | 13973 / 21126 | 88% | 2.4 | 75 |

### turns flights, all regions pooled

| navigator | 5 km med/p95 | 10 km med/p95 | 20 km med/p95 | diverged | CPU s per 1000 s flown | worst step ms |
|---|---|---|---|---|---|---|
| dr_hint | 772 / 1988 | 5720 / 9028 | 18495 / 25645 | 100% | 0.0 | 5 |
| tercom_ours | 806 / 2015 | 5994 / 9754 | 19121 / 25624 | 100% | 0.3 | 48 |
| tercom_ours_beam | 636 / 1988 | 5703 / 9437 | 17970 / 25645 | 100% | 0.3 | 58 |
| pf_ours | 835 / 2752 | 3519 / 7944 | 8135 / 15648 | 95% | 0.4 | 42 |
| pf_ours_beam | 295 / 1293 | 1557 / 5892 | 3908 / 13364 | 80% | 0.4 | 68 |
| gagarin_cr | 5590 / 14347 | 10423 / 31098 | 19589 / 56314 | 100% | 0.3 | 31 |
| gagarin_cr_az200 | 2736 / 10172 | 7407 / 19522 | 15928 / 47295 | 100% | 0.3 | 54 |
| gagarin_cr_hint | 2023 / 4159 | 7007 / 12479 | 16863 / 33162 | 100% | 0.3 | 38 |
| gorizont_cr | 3674 / 6468 | 8014 / 12071 | 13064 / 22738 | 100% | 2.8 | 221 |
| gorizont_cr_hint | 2323 / 4328 | 6423 / 8830 | 10042 / 20110 | 100% | 2.2 | 80 |

### Per region, 20 km error median / p95 (m) and divergence rate

| region | family | dr_hint | tercom_ours | tercom_ours_beam | pf_ours | pf_ours_beam | gagarin_cr | gagarin_cr_az200 | gagarin_cr_hint | gorizont_cr | gorizont_cr_hint |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flat | straight | 1526 / 2373 (100%) | 1289 / 2086 (100%) | 1526 / 2373 (100%) | 736 / 4765 (50%) | 193 / 2310 (20%) | 12198 / 28071 (90%) | 23191 / 35392 (90%) | 7754 / 29172 (100%) | 18504 / 26553 (90%) | 14968 / 20457 (90%) |
| khibiny | straight | 1562 / 2896 (80%) | 742 / 4484 (50%) | 66 / 1582 (10%) | 9278 / 20073 (80%) | 44 / 660 (10%) | 22583 / 48336 (100%) | 18965 / 38899 (100%) | 4267 / 32425 (100%) | 18100 / 22478 (100%) | 13070 / 19985 (100%) |
| taiga | straight | 1723 / 2466 (100%) | 1878 / 4748 (100%) | 1058 / 2249 (80%) | 586 / 4917 (60%) | 310 / 890 (30%) | 30854 / 66315 (100%) | 18376 / 43199 (100%) | 11027 / 25065 (100%) | 16330 / 27154 (80%) | 15973 / 21424 (100%) |
| ural | straight | 2084 / 4351 (90%) | 393 / 5039 (40%) | 734 / 5233 (60%) | 227 / 11282 (40%) | 132 / 601 (10%) | 26790 / 52626 (100%) | 20028 / 53083 (90%) | 5588 / 14841 (70%) | 15677 / 19927 (100%) | 10808 / 19542 (60%) |
| flat | turns | 16520 / 25541 (100%) | 16520 / 25541 (100%) | 16520 / 25541 (100%) | 11733 / 15214 (100%) | 7048 / 14209 (100%) | 20086 / 42988 (100%) | 15928 / 38896 (100%) | 16661 / 28762 (100%) | 11701 / 33804 (100%) | 10635 / 21791 (100%) |
| khibiny | turns | 18909 / 25517 (100%) | 19230 / 29111 (100%) | 18579 / 24856 (100%) | 8189 / 15069 (100%) | 393 / 4204 (40%) | 17598 / 49921 (100%) | 20256 / 48976 (100%) | 16112 / 31799 (100%) | 12374 / 18049 (100%) | 9725 / 14976 (100%) |
| taiga | turns | 18590 / 25268 (100%) | 20735 / 24451 (100%) | 17742 / 25268 (100%) | 6871 / 18088 (100%) | 6569 / 14927 (100%) | 23637 / 57018 (100%) | 18534 / 27171 (100%) | 21613 / 38483 (100%) | 10037 / 19127 (100%) | 11259 / 19427 (100%) |
| ural | turns | 19121 / 24731 (100%) | 19121 / 24784 (100%) | 18640 / 26939 (100%) | 3315 / 13759 (80%) | 3518 / 6983 (80%) | 15996 / 43247 (100%) | 16419 / 47520 (100%) | 16135 / 32546 (100%) | 14273 / 22048 (100%) | 9869 / 20910 (100%) |


### Ablation: which impairment hurts (straight flights, 4 per region, 16 per cell)

20 km error, median and divergence rate. "ideal" is a nadir point altimeter with no noise, no
dropouts, a perfect 1500 m reference and a perfect map; each following row adds one impairment;
"all" is the default model above.

| case | tercom_ours | tercom_ours_beam | pf_ours | pf_ours_beam | gagarin_cr_hint | gorizont_cr_hint |
|---|---|---|---|---|---|---|
| ideal | 24 (12%) | 151 (31%) | 108 (12%) | 291 (31%) | 635 (50%) | 35 (0%) |
| +footprint 40 deg | 236 (44%) | 39 (19%) | 526 (50%) | 79 (19%) | 3195 (75%) | 1363 (62%) |
| +range noise | 148 (25%) | 1091 (75%) | 104 (6%) | 424 (44%) | 1150 (69%) | 34 (6%) |
| +dropouts, outliers | 24 (0%) | 167 (31%) | 112 (12%) | 281 (38%) | 1480 (62%) | 59 (6%) |
| +baro reference error | 55 (12%) | 485 (50%) | 173 (12%) | 430 (38%) | 1694 (69%) | 70 (31%) |
| +map error, canopy | 1044 (56%) | 822 (62%) | 105 (19%) | 396 (44%) | 5749 (75%) | 8492 (75%) |
| all (default) | 1201 (81%) | 939 (62%) | 480 (44%) | 141 (25%) | 9199 (100%) | 13536 (88%) |
| all, 1 Hz | 797 (69%) | 616 (50%) | 1013 (81%) | 241 (38%) | 660 (75%) | 419 (38%) |
| all, 2% range noise | 1182 (81%) | 1182 (75%) | 9935 (88%) | 4232 (75%) | 13532 (100%) | 2267 (81%) |

## Findings

1. **The beam footprint is the largest error source nobody modelled.** With a 40 deg beam at
   300-1400 m AGL the altimeter reports the nearest high ground in the cone. Over the 10 straight
   evaluation flights per region, measured terrain minus the DEM under the aircraft (baro bias
   removed) has a per-flight median of 18 m in the Khibiny window (range -1 to +54 m), 6 m in the
   Urals, 0-3 m in the taiga and flat windows. Matching against `beam_map()` instead of the DEM
   brings the Khibiny figure to -3 m and turns `pf_ours` from 9278 m to 44 m median at 20 km in
   the Khibiny window, and from 760 m to 148 m pooled. In the ablation, the footprint alone moves
   `tercom_ours` from 24 m to 236 m and `pf_ours` from 108 m to 526 m; the beam variants pay for it
   when the radar really is a point (`ideal` row).
2. **Only one navigator beats dead reckoning reliably.** On straight flights `pf_ours_beam` holds
   148 m median / 983 m p95 at 20 km with 18% divergence; dead reckoning on the hints is 1582 m.
   Per region: 44 m Khibiny, 132 m Urals, 310 m taiga, 193 m flat (20% diverged in the flat window
   and 30% in the taiga). Everything else diverges in most runs at the default noise level.
3. **The two team approaches work in the clean case and break on realistic errors.** With an ideal
   sensor `gorizont_cr_hint` reaches 35 m median at 20 km with no divergence, the same order as the
   tens of metres GORIZONT reports on its own generated data. With map error and canopy alone it
   goes to 8.5 km, with the footprint alone 1.4 km. The failure is a self-reinforcing wrong lock:
   a correlation of 0.55 over a shifted and rotated 300-sample history is easy to find in hilly
   terrain, the Kalman velocity follows it, and the hypothesis score keeps rising. `gagarin_cr`
   loses most runs at the initial azimuth/speed search (60 samples is 6 s at 10 Hz); restricting it
   to the hint (+-20 deg) helps but its velocity is frozen after initialisation, so every early
   error grows linearly. On straight flights all five team-approach rows end further from truth at
   20 km than dead reckoning on the hints (6.5-22 km median vs 1.6 km).
4. **Window units matter.** At 1 Hz the 200-sample windows of the two team approaches cover 6-11 km
   instead of 0.6-1.1 km, and they improve (`gorizont_cr_hint` 13.5 km => 419 m,
   `gagarin_cr_hint` 9.2 km => 660 m), while the distance-based particle filter gets worse
   (141 => 241 m) because it has ten times fewer measurements. Size windows in metres.
5. **Range noise is the cliff.** At 2% of range (about 20-28 m at the case's AGL) every navigator
   diverges in most runs; `pf_ours_beam` goes from 141 m to 4.2 km. The altimeter's accuracy at
   1000+ m AGL decides whether the case is solvable at all.
6. **Turns without a heading sensor defeat everything.** On `turns` flights every method diverges
   in at least 40% of runs; the best cell is `pf_ours_beam` in the Khibiny window (393 m median,
   40% diverged). Every team solution assumes long straight legs.
7. **Compute is not the constraint.** All navigators use under 3.1 s of CPU per 1000 s of flight in
   one Python process. The slowest single update ranges from 27 ms (`pf_ours_beam`) to 254 ms
   (`gorizont_cr`, its bootstrap search); `dr_hint` at 11 ms for two lines of arithmetic shows the
   scheduling noise floor. Spikes like these belong in a separate thread with timestamped results,
   not in the autopilot loop.

## Limitations

- Flights, altimeter, altitude reference and map error are simulated. The beam width, noise level,
  canopy penetration and map-error model are assumptions chosen to be plausible, not measured; the
  ablation table shows how much each one matters.
- The beam-aware variants assume the navigator knows the true beam width (40 deg) and flat
  attitude; bank angle in turns tilts a real beam and is not modelled.
- `pf_ours` was tuned lightly on separate seeds; the `*_cr` navigators were not tuned at all and
  carry our reading of README text where it was ambiguous. Their numbers are evidence about the
  published algorithm descriptions under this error model, not about the teams' code.
- No offline smoothing is scored; GORIZONT's headline median uses RTS smoothing and refit.
- 10 flights per region and family: p95 values rest on a handful of runs.
