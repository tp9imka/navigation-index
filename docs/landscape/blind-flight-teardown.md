# "Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions

<!-- about: res:iqarium-polet-vslepuyu-hackathon-2026, repo:t1gr20an06-k/hackathon-blind-flight, repo:danilka88/gag27062026, repo:rub1kub/where-are-we-barista, repo:solarwarlock/flyingblind_hakaton, repo:eliseyavdeev/hackatoncodereal, repo:drones-voronka/drones-backend, repo:radagastttt/terrain-relative-navigation, repo:mzahana/tercom_nav, repo:alti3/python-tercom, res:copernicus-dem-aws, sample:terrain-heightmap-pf, sample:terrain-relative-nav-pf, concept:terrain-nav -->

The closest real precedent we have for a navigation hackathon brief: a 48-hour case (26-28 June
2026, Krasnodar, track "Robotics and sensing") where teams had to find position, ground speed and
heading of an aircraft from a radar altimeter and a DEM, with no GNSS and no IMU.

**How this was built.** READMEs, two organiser PDFs and selected source files were read as text
through the GitHub API on 2026-11-06. Nothing was cloned or run. Every accuracy number below is the
team's own claim unless it says "bench", which means it comes from our own harness in
[samples/blind-flight-bench](../../samples/blind-flight-bench/README.md). The bench re-implements two
team approaches from their README text only (no code copied).

## 1. Reconstructed problem statement

### Source documents

The organiser PDFs are committed in the GORIZONT repo root: `Описание первичное.pdf` (short
version, the same text as the event page) and `Расширенное описание.pdf` (extended brief, two
pages). The event page itself (`res:iqarium-polet-vslepuyu-hackathon-2026`) names no sensors.

### Story (both PDFs)

A commercial operator runs light unmanned and optionally piloted aircraft delivering cargo to taiga
villages, geology camps, Arctic weather stations and mountain bases, over featureless taiga, tundra,
steppe and plateaus. GNSS fails there: poor satellite geometry at high latitude, narrow sky in
gorges, unintentional or deliberate jamming/spoofing near industrial sites, heavy cloud and
geomagnetic storms. The aircraft must still know position, speed and direction, and be able to
correct its course.

### Task (extended PDF, translated)

Build, in 48 hours, an algorithm that, in real time or post-flight, determines from a simple radar
altimeter and a digital terrain map:

- the current velocity vector: where the aircraft flies and how fast;
- an exact map position (x, y), so the course can be corrected.

**Inputs**

| Input | What the brief says |
|---|---|
| DEM | From open sources: Copernicus GLO-30, SRTM, ALOS AW3D30 |
| Radar altimeter | Teams generate it themselves. NMEA-0183 v3, e.g. `$GPGGA,123519.111,,,,,,,,545.4,M,46.9,M,,*47` where `545.4` is the height in metres. Rate 1-10 Hz |
| Barometric altitude | 1500 m, "absolute flight altitude above sea level", constant |

Note the format abuse: the radar height sits in the GGA *MSL altitude* field (field 9), and every
position field is empty. A parser that validates GGA fix quality rejects every line.

**Required**

1. Convert radar heights into a profile of absolute terrain heights along the track (1500 - AGL).
2. Correlation: build reference profiles in all directions from an arbitrary start point in the
   map centre, azimuth 0-360 deg in 1 deg steps; find the angle and offset with the maximum
   correlation coefficient.
3. Motion vector: speed in m/s, track angle / azimuth, ground speed.
4. Visualisation: heatmap of correlation coefficients over all directions; the found trajectory
   on the height map.

**Optional:** Kalman filter for noise, self-assessment of accuracy, adaptation to flat terrain,
run-time optimisation for a low-power onboard computer, "other improvements".

**Judging:** "teams must implement a working algorithm that solves positioning". Business
scenarios must be strictly civilian and describe the aircraft, hardware and software. Weights and
criteria were not published (event page, per the index record).

### Organiser clarifications recorded in team READMEs

From KROT (`rub1kub/where-are-we-barista`, section "Что уточнили у технического эксперта"):

- the judged object is the positioning algorithm from radar altimeter + height map;
- no additional sensors: no IMU, camera, FPV, GNSS track or external truth trajectory as input;
- flight level is constant 1500 m MSL;
- on the final day the organisers hand out a validation altimeter log to run together with a map;
- by the third checkpoint the organisers switched to a new input format: a TXT file with one
  radar height (metres AGL) per line, a start point `x,y`, a heading in degrees from north, the
  initial speed, the altimeter rate, and a GeoTIFF map patch; expected output is local and global
  trajectory coordinates plus a visualisation;
- bonus for compute speed, lower load and robustness to altimeter noise and outliers.

KROT's local example of that format (`examples/route_1.txt`): start pixel 2396/1000, azimuth
294 deg, 15 m/s, 10 Hz. KROT's sample of the map it received spans 55-56 N, 37-38 E (Moscow
region lowland, heights 109.5-273.6 m in its 420x420 resample).

From Gagarin: a "fourth checkpoint" module takes a DEM file, a TXT of heights, a start point and
flight parameters. From GORIZONT: their test inputs are `heights_m.txt` (one height per line), a
packed DEM over Siberian taiga at about 61.5 N, 89.1 E, start pixel (422, 297) and an initial
heading of 95 deg; they also show one run on "real data provided by specialists" (a photo dated
2026-07-14, no error numbers).

### What the evaluation actually became

The PDF asks for a global search from the map centre. By checkpoint 3 the organisers supplied the
start point, heading and speed, so the scored problem turned into **tracking from a known start**,
with heading and speed only as initial hints. A team that over-invested in the 360-degree global
search solved the PDF, not the checkpoint.

## 2. Teams

Seven public repos are indexed. Six are hackathon entries; `radagastttt/terrain-relative-navigation`
is a later personal project on the same idea. Commit counts and creation dates are from the GitHub
API on 2026-11-06.

### GORIZONT - `repo:t1gr20an06-k/hackathon-blind-flight`

16 commits, created 2026-06-27. Python, one 71 KB script `Radiometr_v2/tercom_final.py` plus data
generators and drafts.

- **Pipeline (README).** Median + low-pass filter on the radar channel, a Kalman filter on baro.
  *Bootstrap:* from the last GNSS point, hundreds of (azimuth x speed) hypotheses plus small start
  offsets (radius 8 px, grid 4 px), scored by correlation over a 200-sample window; candidates
  must reach corr 0.65 and are re-checked on several window lengths. *Tracking:* up to 8 parallel
  hypotheses, each a Kalman filter; every 50 samples the whole recent history (up to 300 samples)
  is shifted and rotated (+-8 deg) to re-match the DEM ("history" mode) or a short segment is
  re-searched ("segment" mode, for manoeuvres). Candidates are ranked by correlation minus
  penalties for offset, rotation, rank, Kalman innovation, flat terrain and no-candidate; an
  endpoint gate of 35 px rejects far jumps; measurement noise in the filter scales from 1 to 25 px
  with match quality. *Offline:* RTS smoothing weighted by confidence, a final "snap" of the last
  point onto the local correlation peak, and an optional `--refit` that re-anchors the whole track
  every ~0.8 s inside a +-2 px window with a 1.5 px rejection gate.
- **Engineering.** Every threshold is a CLI flag with a documented default; `--profile` writes
  stage timings; `--truth` is used only for error plots. Input as TXT heights or NMEA.
- **Reported results** (`ОТЧЁТ_точность.md`, their own generated flight over their Siberian DEM):
  final error 19.4 => 9.8 m, mean 80.9 => 23.5 m, median 46.4 => 15.8 m, p95 140 => 57 m, worst
  ~600 => ~57 m after the three offline steps. They estimate a ~11 m ceiling for that data.
- **Failures they report.** A false lock 40-60 s after capture (up to ~28 px, ~600 m) during which
  their own confidence fell from 0.99 to 0.48; a point at t = 60 s where the correlation peak is
  99 m from truth at corr 0.94. They tried per-measurement sub-pixel refinement fed back into the
  tracker, saw errors jump 19 => 62 => 115 m and dropped it. A wrong initial heading (70 vs 95 deg)
  gave the same final 9.8 m.
- **Caveats.** The test flight is from their own generator over the same DEM the matcher uses.
  The generator (`Radiometr/generation.py`) models engine vibration at 80 Hz (aliased at a 10 Hz
  output rate), turbulence and outliers, not a beam footprint, map error or baro bias. The headline
  median includes offline smoothing and refit, so it is not a causal number.

### Gagarin - `repo:danilka88/gag27062026`

66 commits, created 2026-06-27; README sections say work continued "June-July 2026" (index shows
last push 2026-06-28). Python package (`gagarin/`), FastAPI + SSE step-by-step UI, CLI, 53 tests.

- **Checkpoint pipeline (README, `checkpoint.py`).** (1) Azimuth heatmap 0-360 deg at 1 deg on
  the first 60 samples, top-3 by |NCC|. (2) Speed: 29 hypotheses, 10-150 m/s in 5 m/s steps, by
  mean-subtracted MAD. (3) Sliding windows of `min(200, n/2)` samples, step `ws/4`: dead
  reckoning, then a +-4 px translation grid, MAD, NCC. (4) Roughness gate: relative difference of
  `std(diff(profile))` between observed and reference > 0.5 => false fix. (5) Pre-rejection gates:
  peak-to-valley < 5 m, MAD > 30 m, NCC < 0.3, discrimination < 1.0. (6) RANSAC on positions
  (median + 2 MAD). (7) "DR + weighted correction": `w = clamp((discr - 1)/10, 0, 1)`,
  `filtered = dr + w (meas - dr)`. (8) Multi-start over the top-3 azimuths when the first window's
  std is under 20 m, best by mean NCC. (9) Ambiguity flag when two azimuths > 30 deg apart score
  within 10% (fires on their Crimea coast case, 296 vs 166 deg).
- **Other modules.** "Minima ratio" (second-best / best MAD with a 2 px exclusion ring), adaptive
  NCC (detrended above 20 m terrain std, raw below 10 m), lost-position recovery (5 poor windows
  in a row => 7x7 grid at 150 m, accepted if peak sharpness >= 0.3), pre-flight route
  fingerprinting (std, gradient, minima ratio, NCC under lateral offset; SQLite with R-tree +
  GeoTIFF informativeness map), route replanning, battery check and landing-zone search.
- **Engineering notes.** A full 6D error-state Kalman filter exists in the pipeline but was
  replaced in the checkpoint by DR + weighted correction because "with dt of 3-4 s between windows
  the ESKF covariance grew until the gain went to zero". That reads like a process-noise tuning
  problem, not a property of the ESKF. They found and fixed a ~450 m bias from tagging window
  estimates with the start index instead of the centre. The onboard-hardware table (RPi, Jetson,
  Orange Pi, NUC) is extrapolated linearly from one ~60 ms/search laptop benchmark ("+-30%"); no
  board was measured.
- **Reported results** (8 cases on their own synthetic DEMs): correct azimuth in 4/8 (filtered
  error 54-323 m), wrong azimuth in 4/8 (287-1313 m). The README states the failures plainly.
- **Caveats.** Several of their test DEMs peak at 3489-4114 m, above the 1500 m flight level the
  case fixes. Literature cited for MAD and minima ratio ("Akinci et al. 2026, Hurjet FTI") was not
  checked here.

### KROT ("Где мы, Бариста?") - `repo:rub1kub/where-are-we-barista`

48 commits, created 2026-06-26. TypeScript/React/Three.js operator panel; separate C++ and Rust
console cores.

- **Algorithm (README + `src/terrainMatcher.ts`).** Optional 1D Kalman smoothing of the measured
  profile; downsample to 260 points; brute force over azimuth 0-359 deg x speed range x along-track
  shift in {-3000, -1500, 0, 1500, 3000} m from the map centre; each cell scored by Pearson
  correlation and RMSE on absolute heights.
- **Quality layer.** `confidence = 0.46 corr + 0.22 relief + 0.12 peak + 0.20 rmse` (each term
  clamped to [0, 1]) and five statuses: `LOW RELIEF` if relief < 35 m or std < 9 m; `NO FIX` if
  corr < 0.42 or RMSE > 180 m; `FIX AMBIGUOUS` if best minus second-best correlation < 0.008;
  `FIX DEGRADED` below confidence 72 / corr 0.78 / RMSE 80 m; else `FIX VALID`. When the fix is
  not usable the CLI withholds coordinates and keeps the best candidate only as diagnostics.
- **Engineering.** NMEA checksum validation; a checkpoint-3 adapter (TXT + GeoTIFF + start pixel,
  CSV export of local and WGS-84 coordinates); a negative control (a PX4-derived log that must
  return `NO FIX`); smoke tests for flat noisy terrain lowering confidence.
- **Caveats (from reading the code).** The second-best correlation is tracked over all cells, so
  it is usually the neighbouring azimuth or speed of the same peak: the "ambiguity" number measures
  peak sharpness, not a competing mode. RMSE on absolute heights is shifted by any baro bias.
  The README makes no accuracy claim and says the final organiser log had not been run.

### FlyingBlind - `repo:solarwarlock/flyingblind_hakaton`

12 commits, repo created 2026-07-31 (after the event). Streamlit app; Rust core via ctypes for the
hypothesis sweep.

- **Algorithm (README + `core/search.py`, `core/matching.py`).** Projects the DEM to UTM; grid
  search over start x/y, speed 10-50 m/s and azimuth 0-359; coarse-to-fine with a seed sweep
  around the centre, micro and "nano" refinement of the start, and a denser retry when the first
  result is weak. Primary metric is RMSE on absolute heights; "weighted scoring" multiplies each
  sample's squared error by `1 + clip((|grad| + 0.5 |curv|)/mean, 0, 4)`. Confidence =
  `sqrt(global_contrast x spot_contrast)` where the contrasts compare the best error with the
  median and the 10th percentile of the error grid. Flat check: profile variance <= 1 m^2.
  "Bridge mode" carries a confident straight segment across flat gaps.
- **Caveats.** Assumes one straight, constant-speed segment. The synthetic generator adds only
  Gaussian noise (default 2 m). No accuracy numbers in the README.

### SKB "FIZ-TECH" - `repo:eliseyavdeev/hackatoncodereal`

24 commits, created 2026-06-27. Python GUI, Webots world for generating flights.

- **Algorithm (`src/matcher.py`).** Exhaustive: 21x21 candidate starts at 400 m spacing x azimuth
  (1 deg) x speed (20-70 m/s, 2 m/s), NCC; multiprocessing per speed (tested on 24 cores). A
  sliding-window real-time mode adds a Kalman filter; moving-average filtering of the altimeter.
- **Reported result.** 13 m error on a ~10x10 km map with 10 m simulated altimeter noise. The
  README says post-processing is more stable than real time.
- **Caveat.** "Constant self-assessment of accuracy based on the true parameters": the accuracy
  readout uses truth, so it is not a confidence estimate that would work in flight.

### drones-voronka - `repo:drones-voronka/drones-backend`

2 commits (squashed upload), created 2026-06-28. A ground control station platform: Go telemetry
gateway, RabbitMQ, FastAPI modular monolith, PostgreSQL schema-per-module, Redis, Qdrant,
Prometheus/Grafana/Loki, MAVSDK bridge, swarm simulator, Docker Compose.

- **What the TRN code is.** The README and `docs/domain.md` describe a particle filter with Qdrant
  relocalisation. In the files read, `services/worker/navcore.py` is dead reckoning on IMU speed and
  heading with a confidence that decays by 0.05 per step, and
  `services/app/app/modules/navigation/correlation.py` (`TrnSolver`) is Pearson correlation along
  rays from an anchor over 360 azimuths x 64 offsets, one DEM cell per sample (speed is not
  searched), with confidence = raw peak correlation. No particle filter or Qdrant lookup was found
  in those files; the rest of the 591-file tree was not searched exhaustively.
- **Takeaway.** Strong platform engineering, thin estimator. Useful as an architecture reference,
  not as a navigation baseline.

### Related, not an entry: `repo:radagastttt/terrain-relative-navigation`

2 commits, created 2026-11-02. Particle filter over (x, y) with speed and heading assumed known
from an INS, measurement `z = h(x, y) + AR(1) bias + noise + 2% outliers`, gating when no particle
explains a sample. On 30 random 3 km routes per area over Bulgarian GLO-30 (initial error 100 m,
1 m noise, 5000 particles): success (final error < 30 m) 33% on the Upper Thracian plain, 93% in
the Pre-Balkan hills, 97% in the Central Balkan. The report gives the most useful rule of thumb in
the set: along-track height std > ~10 m almost always works, < ~5 m almost never. It also states
the limits plainly: measurements are generated from the same DEM, and GLO-30 is a DSM so a radar
altimeter over forest and towns sees something else.

## 3. Comparison

| | GORIZONT | Gagarin | KROT | FlyingBlind | FIZ-TECH | drones-voronka |
|---|---|---|---|---|---|---|
| Matcher | NCC on profile windows; history shift + rotate | mean-sub MAD + NCC on windows | Pearson + RMSE, full profile | RMSE (optionally gradient-weighted) + Pearson | NCC, full profile | Pearson along rays |
| Search | az x speed x small start offsets, then local | 360 deg az, 29 speeds, +-4 px per window | 360 x speed x 5 along-track shifts | start x/y x speed x az, coarse-to-fine | 21x21 starts x az x speed | 360 x 64 offsets, fixed speed |
| Tracking | multi-hypothesis KF (8), gates, penalties | DR + discrimination-weighted correction (ESKF in pipeline) | none (one fit per log) | none (straight segment), KF/moving-average smoothing | sliding window + KF (real-time mode) | re-anchored per window |
| Quality signal | per-hypothesis score, confidence | good/marginal/poor, gates, ambiguity flag | 5 statuses, withholds unusable fixes | contrast confidence, accuracy heuristic | uses truth | raw peak corr |
| Flat terrain | min roughness to bootstrap/track | p2v gate, multi-start, pre-flight map | LOW RELIEF status | variance check, bridge mode | not described | not handled |
| Baro bias | NCC (bias-free) | mean-sub MAD, NCC | RMSE on absolute heights (biased) | RMSE on absolute heights (biased) | NCC (bias-free) | Pearson (bias-free) |
| Turns | history rotation +-8 deg, segment mode | no (velocity fixed after init) | no | no (straight segment) | not described | per-window re-anchor |
| Beam footprint | not modelled | not modelled | not modelled | not modelled | not modelled | not modelled |
| Offline extras | RTS, final snap, refit | RANSAC, consensus | - | coarse-to-fine retries | multiprocessing | - |
| Claimed accuracy | 15.8 m median, 9.8 m final (own synthetic) | 54-1313 m (own synthetic, 4/8 wrong azimuth) | none | none | 13 m (own synthetic) | none |
| Stack | Python CLI | Python pkg, FastAPI UI, 53 tests | TS/React, C++ and Rust cores | Streamlit + Rust | Python GUI, Webots | Go + Python microservices |

## 4. What the bench says about the two most distinctive approaches

Bench, not team claims. Ten 20 km flights per region and flight family over four real GLO-30
windows (Khibiny mountains, Middle Urals, Yenisei taiga, the flat region south of Moscow inside the
map.tif bounds KROT cites), 10 Hz, 40 deg leading-edge radar beam, range noise 0.5 m + 0.5%,
dropouts and outliers, a 1500 m baro reference with N(0, 25 m) bias and drift, map error and canopy.
Full method, numbers and caveats: [samples/blind-flight-bench](../../samples/blind-flight-bench/README.md).

Straight flights (the checkpoint shape), 40 flights pooled, error at 20 km:

| navigator | origin | median / p95 | diverged (> 500 m) |
|---|---|---|---|
| dead reckoning on the given heading and speed | floor | 1582 / 3659 m | 92% |
| `tercom_ours` (terrain-heightmap-pf `tercom_fix`) | ours | 1289 / 5806 m | 72% |
| `pf_ours` | ours | 760 / 16420 m | 57% |
| `pf_ours_beam` (same PF, beam-aware map) | ours | **148 / 983 m** | 18% |
| `gorizont_cr_hint` (GORIZONT tracker, heading window +-20 deg) | clean-room | 13973 / 21126 m | 88% |
| `gagarin_cr_hint` (Gagarin pipeline, 200-sample scan, +-20 deg) | clean-room | 6549 / 32591 m | 92% |

What that says about the two team approaches, with the ablation behind it:

- **Both work on clean data.** With an ideal point altimeter and a perfect map, the GORIZONT-style
  tracker reaches 35 m median at 20 km with no divergence, in line with what GORIZONT reports on
  its own generated flight. The Gagarin-style pipeline reaches 635 m; its velocity is frozen after
  the initial search, so any early azimuth or speed error grows linearly.
- **Both break on realistic errors, and end worse than dead reckoning.** Map error plus canopy
  alone takes the GORIZONT-style tracker to 8.5 km, the footprint alone to 1.4 km. The failure is a
  self-reinforcing wrong lock: a 0.55 correlation over a shifted and rotated history is easy to find
  in hilly terrain and the Kalman velocity follows it.
- **The full-circle azimuth scan is a liability when a heading is given.** The 360-degree variants
  of both are worse again (17.5 km and 22.4 km median).
- **At 1 Hz their sample-count windows become 6-11 km long and both improve sharply** (419 m and
  660 m), while the distance-based particle filter gets worse. Window length belongs in metres.

The single largest gain on the bench is modelling the beam: the same particle filter goes from
760 m to 148 m pooled, and from 9.3 km to 44 m in the Khibiny window. These are our
re-implementations from README text, scored causally, under an assumed error model; they are
evidence about the published algorithm descriptions, not about the teams' code.

## 5. Lessons for our team

### What a winning 48 h entry looks like

Judging by the brief and what the checkpoints turned into:

1. **A CLI that eats the checkpoint format on day one.** TXT heights or NMEA (validate the
   checksum, read field 9), a GeoTIFF of any CRS, start x/y in pixels or lat/lon, heading, speed,
   rate. Output: per-epoch CSV with local x/y, lat/lon, speed, track angle, a confidence and a
   status, plus the two required plots (direction x speed correlation heatmap; trajectory on the
   DEM). KROT and GORIZONT both had this; it is what the final-day validation log needs.
2. **Bias-free matching.** NCC or mean-removed MAD, never RMSE on absolute heights. The 1500 m
   "baro" level is a reference, not truth.
3. **Use the prior, then check it.** Seed the search at the given heading and speed (+-20-30 deg),
   keep the 360-degree scan as a fallback behind an ambiguity test. On the bench the global-scan
   variants lose to plain dead reckoning on the hints.
4. **A causal tracker with honest uncertainty.** Particle filter or multi-hypothesis KF over
   position, speed, heading and baro bias; a status that can say "no fix" (KROT's five states are a
   good template). Report offline smoothing separately from the causal track.
5. **Evidence slide.** Error vs distance on several terrain types, flat terrain shown failing
   safely, a noise/outlier sweep, and measured ms per update on the laptop with the onboard
   extrapolation labelled as such.
6. **Civil business case** with a concrete aircraft and computer, as the brief requires.

### Traps

- **Flat-terrain ambiguity.** Along-track height std under ~5-10 m carries no position
  information at 1500 m (radagastttt's rule of thumb, and the bench flat region). Detect it, widen
  uncertainty, coast on the motion model, and say so. Pre-flight route scoring (Gagarin's
  fingerprinting) turns this into a planning feature.
- **Altitude reference errors.** The case's 1500 m is barometric. A 1 hPa QNH error is about 8 m
  and an ISA temperature deviation of 15 deg C at 1500 m is about 75 m. Mean-removed metrics remove
  a constant bias; drift needs a bias state or short windows. FlyingBlind ranks candidates by RMSE
  on absolute heights, and KROT feeds absolute RMSE into its confidence and status thresholds.
- **DEM vs DSM.** GLO-30 is an X-band radar DSM: forest canopy and buildings are in it, partly. A
  C-band radar altimeter over forest returns from somewhere between canopy and ground. Every team
  generated its altimeter data from the same DEM it matches against, which hides this error.
- **Radar beam footprint.** At 1500 m MSL the aircraft is 300-1400 m above ground. A wide-beam
  altimeter tracks the leading edge: the nearest surface inside the cone, often a ridge to the side,
  not the point below. On the bench, measured terrain minus the DEM under the aircraft has a
  per-flight median of 18 m in the Khibiny window (range -1 to +54 m over 10 flights) and 6 m in
  the Urals, with the error concentrated next to ridges. No team models it. Because the flight level is
  fixed, a "beam-aware" reference map (what an altimeter at 1500 m would report over each cell) can
  be precomputed once per map; on the bench it is the single largest improvement.
- **Latency and window units.** Windows defined in samples change meaning with the rate: Gagarin's
  60-sample azimuth scan is 6 s at 10 Hz but 60 s at 1 Hz. Size windows in metres. Global
  searches are bursty: our GORIZONT re-implementation has ~0.25 s worst-case steps on a laptop,
  so on a companion computer they need a separate thread and a timestamped result, and the
  autopilot must accept a delayed fix.
- **Turns without a heading sensor.** Every entry assumes long straight segments. With no IMU or
  compass a 90 deg turn is only observable through terrain, and on the bench every method
  diverges on at least 40% of turning flights in every region (most do on 80-100%). If the real
  brief allows a compass or gyro, use it.
- **Self-generated test data.** Same DEM, Gaussian noise, known start: every team's numbers come
  from this setting and are optimistic. Build the harness with map error, footprint and bias first.
- **Altimeter accuracy decides solvability.** On the bench, range noise of 2% (about 20-28 m at
  the case's AGL) makes every navigator diverge in most runs; at 0.5% the beam-aware PF holds
  ~150 m. Ask the organisers what altimeter and accuracy the data assume.

### How our samples compare

- [terrain-relative-nav-pf](../../samples/terrain-relative-nav-pf/README.md)
  (`sample:terrain-relative-nav-pf`): stdlib SIR particle filter with an INS. Its structure
  (gaussian terrain likelihood, systematic resampling, bias states) is the base of the bench's
  `pf_ours`, which replaces the INS with speed, heading and turn-rate states and adds an altimeter
  bias state, since the case has no INS.
- [terrain-heightmap-pf](../../samples/terrain-heightmap-pf/README.md)
  (`sample:terrain-heightmap-pf`): its `tercom_fix` (mean-removed MAD, translation search,
  ambiguity ratio) is the bench's `tercom_ours`, and its `fetch_dem.py` fetches the bench terrain.
  Its own TERCOM relies on odometry for the track shape; the blind-flight case has none, so on the
  bench the track shape comes from a constant-velocity guess, which is why it degrades quickly
  once a fix is missed.
- Neither sample handles the case's specific traps out of the box: no beam model, no turn handling
  without an INS, no NMEA/TXT front end. The bench adds those.

## Sources

- Organiser PDFs: `Описание первичное.pdf`, `Расширенное описание.pdf` in
  [t1Gr20an06-k/Hackathon-Blind-Flight](https://github.com/t1Gr20an06-k/Hackathon-Blind-Flight).
- Team READMEs and the files named above, read via `gh api repos/<o>/<n>/contents/<path>` on
  2026-11-06.
- Index records: `res:iqarium-polet-vslepuyu-hackathon-2026` and the repo records in
  `data/repos/ua-ru-sources.json` and `data/repos/ua-ru-round2.json`.
