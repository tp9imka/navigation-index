# Celestial fix: star-tracker attitude plus an IMU vertical

<!-- about: concept:celestial-nav, repo:smroid/cedar-solve, repo:esa/tetra3, repo:skyfielders/python-skyfield -->

Star-field image => [cedar-solve](../../catalog/repos/smroid__cedar-solve.md) lost-in-space
plate solve (camera attitude in J2000) => star elevations above the IMU's gravity vertical =>
least-squares latitude/longitude, with [Skyfield](../../catalog/repos/skyfielders__python-skyfield.md)
for the ephemeris. RF-passive: nothing to jam or spoof. Two questions answered with numbers:

1. How well does an off-the-shelf solver turn real star images into attitude, and how fast?
2. How does attitude become position, and what limits it? Short answer: the vertical. One
   arcminute of level error is one nautical mile of position error.

| Part | Input | Status |
|---|---|---|
| Plate solving, accuracy vs a reference WCS | real: 40 NASA SkyView cutouts of the Mellinger all-sky optical mosaic | ran |
| Plate solving, real camera frames | real: 20 test frames shipped with cedar-solve (8 of them ESA tetra3's) | ran, no reference attitude |
| Position from the 8 ESA frames (mount pointing as the vertical) | real | ran, capture site not documented |
| Position fix error budget | synthetic: Skyfield truth for the 5,041 Hipparcos stars to mag 6 | ran |
| Geometry unit tests | stdlib | ran, plain `python3` |

## Run

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install --no-deps "cedar-solve @ git+https://github.com/smroid/cedar-solve.git@v0.6.0"
python3 fetch_data.py                       # ~5 min: 20 cedar frames, 40 SkyView FITS (~170 MB), DE421 (16 MB)
.venv/bin/python plate_solve_eval.py        # ~10 s; --fov-hint passes the true FOV
.venv/bin/python esa_mount_fix.py           # < 1 s, reads results/plate_solve.json
.venv/bin/python position_fix_sim.py        # ~5 s for 100 runs per row (--runs 200 used below)
python3 -m unittest -v                      # stdlib; the skyfield test skips without the venv
```

`--no-deps` matters: cedar-solve's `pyproject.toml` pins `numpy<2` and `Pillow<9` (Pillow 8 has
no wheels past Python 3.10). Tag v0.6.0 ran here on numpy 2.5.4 and Pillow 13.0.0 with no
errors; the `np.math` call that breaks ESA tetra3 on NumPy 2 is fixed in this tag. PyPI
`cedar-solve` (0.5.1, 2024) predates that fix, so install from the tag. See the
[cedar-solve](../../docs/integration-cards/smroid__cedar-solve.md) and
[tetra3](../../docs/integration-cards/esa__tetra3.md) integration cards.

SkyView sometimes answers "Too Many Processes" (an HTML page) under load; `fetch_data.py`
checks for the FITS header, waits and retries, and skips files already downloaded.

Files: `celestial_geom.py` (stdlib fix solver and error formulas), `plate_solve_eval.py`,
`esa_mount_fix.py`, `position_fix_sim.py`, `fetch_data.py`, `test_celestial_geom.py`,
`results/*.json` (outputs quoted below).

## 1. Plate solving (ran 2026-11-06)

Setup: cedar-solve v0.6.0 (git tag), its bundled `default_database.npz` (10-30 deg FOV, stars
to mag about 8, Hipparcos), `tetra3.get_centroids_from_image` with defaults, brightest 30
centroids to `solve_from_centroids`, `solve_timeout=5000` ms. Python 3.12.14, numpy 2.5.4,
Apple M2 Max, one process. Times are wall clock around each call.

### 1a. Accuracy against a known WCS

Reference: SkyView cutouts of the Mellinger Red mosaic, 1024 x 1024 px, TAN projection, at 20
seeded random sky positions and roll angles per FOV (`fetch_data.py --seed 1`). The requested
centre and rotation are the reference attitude. The images are real photographs (a mosaic of
DSLR frames), resampled by SkyView; they are not a camera on a vehicle. The mosaic's own
astrometric error is part of the measured error (not stated by the survey). Pixel scale: 42
arcsec/px at 12 deg, 70 arcsec/px at 20 deg.

Error = rotation between the solved and the WCS attitude, fitted on a 5 x 5 grid of image points,
split into cross-boresight (pointing) and about-boresight (roll).

| FOV | solved | pointing median / p95 / max | roll median / p95 / max | grid RMS median / max | extract | solve median / p95 / max |
|---|---|---|---|---|---|---|
| 12 deg | 20 / 20 | 5.2 / 16.4 / 17.9 arcsec | 19.8 / 50.2 / 96.5 arcsec | 8.1 / 24.2 arcsec | 29 ms | 3.5 / 39.0 / 52.4 ms |
| 20 deg | 20 / 20 | 12.1 / 106.3 / 115.2 arcsec | 18.2 / 89.1 / 130.7 arcsec | 15.3 / 138.0 arcsec | 23 ms | 1.1 / 14.8 / 33.8 ms |
| 20 deg, `--fov-hint` | 20 / 20 | 5.4 / 21.5 / 25.6 arcsec | 19.8 / 89.1 / 130.7 arcsec | 11.2 / 28.4 arcsec | 24 ms | 1.2 / 15.2 / 35.0 ms |

- Every image solved, no false match (false-positive `Prob` at most 1e-31).
- Pointing is good to about 0.1-0.2 px median. Roll is 3-4x worse, as expected for a
  narrow-field tracker: a roll error moves edge stars by only about roll x sin(FOV/2).
- Without a FOV hint, three 20 deg frames solved with 78-115 arcsec pointing error. The solver's
  own `RMSE` flagged them at 84-97 arcsec, against 14-55 for 16 of the other 17 (one more frame
  showed 98 with a 131 arcsec roll error). Passing `fov_estimate` cut those three to 8-26 arcsec.
  Pass the known FOV, and treat a high `RMSE` as a reason to down-weight the solve.
- FOV estimate error median 0.02 %, max 0.15 % against the pinhole FOV of the WCS. (SkyView's
  `Size=12` means 1024 x CDELT; a pinhole camera spans 2 atan(512 tan CDELT) = 11.957 deg.
  Comparing against 12 shows a fake 0.36 % error.)
- Runtime: about 25-30 ms per 1 MP frame, almost all of it Python centroiding. The pattern match
  itself takes 1-4 ms median.

### 1b. Real camera frames (no reference attitude)

The 20 jpgs in cedar-solve `examples/data/medium_fov` at tag v0.6.0 (`master` has 3 more):

- 18 / 20 solved, FOV 10.2-15.5 deg, solver RMSE 5-29 arcsec, solve median 1.3 ms, extract
  5-24 ms.
- Not solved: `tree.jpg` (lit branches over the right half, 287 centroids) and `roof.jpg`
  (roof edge, 119 centroids). The brightest 30 centroids are clutter, not stars, and each
  frame takes 2.6-3.4 s to return `NO_MATCH`. Blanking the obstructed columns by hand
  (`OBSTRUCTION_MASKS`) gives `MATCH_FOUND` in 7.2 ms (14 matches) and 1.8 ms (26 matches).
  On a vehicle, mask known structure (airframe, mast, canopy frame) before centroiding.

### 1c. The 8 ESA frames as a crude real-data position fix

The ESA tetra3 frames are named with the mount's pointing (`Alt40|60_Azi+-45|+-135`) and a
timestamp `2019-07-29T204726`. The mount's alt/az plays the role of the vertical plus heading
reference. `esa_mount_fix.py` converts each solved J2000 RA/Dec to apparent of date (Skyfield),
then fits latitude and longitude, treating the timestamp as UTC:

```
fit lat, lon only: 52.070 N 4.756 E
  per-frame residual deg: 1.05 1.26 1.36 1.47 1.18 1.26 1.38 1.48
  distance to ESTEC (unverified site): 28.3 km (N -16.5, E +23.0)
fit lat, lon, mount alt/az offsets: 52.071 N 4.488 E, mount offsets alt +1.28 deg az -0.46 deg
  per-frame residual deg: 0.18 0.11 0.31 0.09 0.28 0.14 0.02 0.18
  distance to ESTEC (unverified site): 17.0 km (N -16.4, E +4.6)
```

The capture site isn't documented in either repo. The images are credited "ESA/Gustav
Pettersson", and the fit lands 17 km from ESA ESTEC in Noordwijk (Wikipedia coordinates). So
treat this as a plausibility check, not a measured error. What it does show: the mount's
"vertical" was off by about 1.3 deg, and with that left in, the fix is wrong by tens of km. The
star side was not the problem. Frame times probably differ by minutes (one timestamp for
all 8), which also smears longitude (section 2: 1 s = 299 m at 50 N).

## 2. Position from stars plus a vertical

### Method

Per identified star i: catalog direction => apparent GHA_i and declination dec_i at the
navigator's clock time (Skyfield: precession, nutation, annual aberration). The camera gives
the star's unit vector m_i, the IMU gives the up vector u, both in the body frame, and the
observed elevation is h_i = asin(m_i . u). Subtract refraction (Bennett formula, scaled by
pressure and temperature), then solve

    sin h_i = sin(lat) sin(dec_i) + cos(lat) cos(dec_i) cos(GHA_i + lon)

for (lat, lon) by Gauss-Newton (Marcq St Hilaire intercept method, iterated, all stars at
once): `celestial_geom.solve_fix`, stdlib only. No camera heading is needed, only the
vertical. Equivalently, the zenith expressed in the Earth-fixed frame *is* (lat, lon)
(`zenith_fix`).

### Why 1 arcmin of level is about 1.85 km

Astronomic latitude and longitude are, by definition, the direction of the local vertical.
If the vertical estimate is tilted by e, the zenith used for the fix moves by e of arc on the
celestial sphere. The solved position then moves by the same arc on the Earth: d = R e.
With e = 1 arcmin = 2.909e-4 rad and R = 6371.0 km, d = 1853 m, which is the nautical mile
(1852 m, historically one arcminute of latitude). On WGS84 at 50 N, the meridian radius
gives 1854 m and the prime-vertical radius 1859 m per arcmin. The error points in the
direction of the tilt and doesn't average out over stars, because every elevation shares
the same vertical.

Clock error: the sky turns at 7.292e-5 rad/s, so dt seconds of clock error is a pure
east-west error of R cos(lat) x 7.292e-5 x dt: 464 m/s at the equator, 299 m/s at 50 N.

Checked numerically in two places:

- `test_celestial_geom.py` (stdlib, spherical Earth): for tilts of 0.5, 1 and 5 arcmin in 4
  directions, fix error / (R e) = 1 to 6 decimal places; the error points in the tilt direction;
  1 s of clock error = exactly R cos(lat) w dt east-west with zero north error. A planted sign
  flip in the solver's Jacobian fails 4 of these tests.
- `position_fix_sim.py` (Skyfield truth, WGS84): noise-free, 1 arcmin of level error gives
  1852-1866 m per arcmin across 200 random tilt directions (ellipsoid radii plus the 5 m floor
  below).

### Error budget (ran 2026-11-06, `--runs 200`)

Truth: 50 N 10 E, 2026-01-15 22:00 UTC, sea level, 1013 hPa / 10 C. Camera: 20 deg circular
FOV at 60 deg elevation, random azimuth, stars to mag 6 (44 in view, median). The solver starts
from a prior 1 deg off on each axis. Centroid noise 20 arcsec per star unless stated. That's
an assumption: section 1a measured 8-15 arcsec grid RMS on 42-70 arcsec pixels, and a
calibrated tracker does better. Median / p95 horizontal error over 200 runs:

| Error source | Setting | Median | p95 |
|---|---|---|---|
| none (floor) | centroid noise 0 | 5.4 m | 6.2 m |
| centroid noise | 20 arcsec / star | 371 m | 1,016 m |
| centroid noise | 60 arcsec / star | 1,114 m | 3,042 m |
| level bias | 0.5 arcmin | 1,001 m | 1,614 m |
| level bias | 1 arcmin | 1,896 m | 2,506 m |
| level bias | 2 arcmin | 3,738 m | 4,314 m |
| level bias | 5 arcmin | 9,298 m | 9,867 m |
| level bias | 10 arcmin | 18,589 m | 19,162 m |
| level bias | 30 arcmin | 55,730 m | 56,303 m |
| clock (noise 0) | 0.1 s | 35 m | 36 m |
| clock (noise 0) | 1 s | 305 m (predicted 299 + 5 m floor) | 306 m |
| clock (noise 0) | 10 s | 3,001 m | 3,002 m |
| clock (noise 0) | 60 s | 17,978 m | 17,979 m |
| vibration, 0.5 deg per sample | 1 sample | 66 km | 136 km |
| vibration, 0.5 deg per sample | mean of 100 | 6.6 km | 13.2 km |
| vibration, 0.5 deg per sample | mean of 10,000 | 752 m | 1,657 m |
| vibration, 3 deg per sample | mean of 10,000 | 4.1 km | 8.4 km |
| accel bias / unmodelled accel | 0.1 mg (0.34 arcmin) | 742 m | 1,330 m |
| accel bias / unmodelled accel | 1 mg (3.44 arcmin) | 6.4 km | 7.0 km |
| accel bias / unmodelled accel | 5 mg (17.2 arcmin) | 31.9 km | 32.5 km |
| accel bias / unmodelled accel | 10 mg (34.4 arcmin) | 63.9 km | 64.4 km |

The 5 m floor matches the size of diurnal aberration (0.32 arcsec x cos(lat), about 6 m at 50 N).
Skyfield's topocentric truth includes it; the navigator's geocentric GHA/dec model leaves it out.

Refraction (centroid noise 0 to isolate it). Bennett correction vs none, by boresight
elevation:

| Boresight elevation | sea level, corrected | sea level, ignored | 10 km (265 hPa, -50 C), corrected | 10 km, ignored |
|---|---|---|---|---|
| 30 deg | 3.6 m | 3,398 m | 3.3 m | 1,131 m |
| 45 deg | 4.6 m | 1,932 m | 4.5 m | 643 m |
| 60 deg | 5.4 m | 1,145 m | 5.5 m | 383 m |
| 90 deg | 6.4 m | 117 m | 6.4 m | 35 m |

The truth refraction (Skyfield) and the correction (Bennett) are near-identical models with
the true pressure and temperature, so "corrected" is optimistic. Real refraction anomalies
and unknown temperature are not modelled.

Field of view and star count (centroid noise 20 arcsec):

| FOV, mag limit | stars in view (median) | median | p95 |
|---|---|---|---|
| 10 deg, mag 6 | 10 | 1,677 m | 5,156 m |
| 20 deg, mag 4 | 5 | 1,186 m | 4,296 m |
| 20 deg, mag 6 | 44 | 371 m | 1,016 m |
| 30 deg, mag 6 | 101 | 178 m | 484 m |

### Reading the budget

- The vertical dominates everything. Star measurement noise averages over tens of stars; a
  level bias does not. A 0.1 mg accelerometer bias is already worth about 640 m (0.34 arcmin x
  1853 m). A navigation-grade 25 ug bias works out to about 5 arcsec, or about 160 m
  (computed from the same formula, not simulated).
- Camera-to-IMU misalignment enters exactly like level error. A boresight calibration of
  0.5 arcmin costs about 0.9 km.
- On a moving vehicle the accelerometers measure specific force, not gravity. An unmodelled
  0.01 g of horizontal acceleration tilts the "vertical" by 34 arcmin, about 64 km. Raw
  gravity averaging works only when stationary (stopped vehicle, hover, ship averaged over
  many swell periods). Otherwise you need an INS whose Schuler-damped vertical is the level
  reference (a stellar-inertial system), and the fix is only as good as that INS's tilt.
- Deflection of the vertical (gravity vs ellipsoid normal) adds a floor that a perfect IMU
  can't remove. Commonly a few to tens of arcsec, so hundreds of metres; more in mountains.
  Not modelled here; would need a geoid/gravity model.
- Clock: 1 s => 300 m east-west at 50 N. A free-running crystal is fine for hours. A clock
  that drifts minutes is not.
- Geometry: pointing near the zenith gives stars in all azimuths, so the fix is well
  conditioned and refraction is tiny. Low elevations make refraction the main correction.
- Floor achieved here: about 5 m with perfect inputs. So the star side (Skyfield reduction
  plus the stdlib solver) is not the bottleneck at any realistic level accuracy.

## 3. When to use it at a hackathon

Useful when:

- The sky is visible and it's night. High altitude (above cloud: HAPS, balloons, high-flying
  UAS) or at sea are the natural cases. Fewer clouds, less air above, and on a ship the
  vertical can be averaged.
- You need an absolute fix that RF can't jam or spoof, to bound INS drift over hours.
  Kilometre-level accuracy with a MEMS-grade vertical still beats hours of free INS drift.
- Heading alone is enough. The plate solve gives full attitude, so true heading, with no
  vertical needed. That's the easiest win: a heading reference immune to magnetic
  disturbance.

Limits:

- Clouds, fog, smoke, twilight and daylight. Visible-band star cameras need dark sky; SWIR
  star trackers that work in daylight exist commercially (not in the index, not tested).
- The level reference (section 2). It is the whole error budget on a moving platform.
- Moon glare, light pollution, foreground clutter (section 1b), motion blur at long
  exposures.
- Default database covers 10-30 deg FOV. Other optics need `generate_database` and
  Hipparcos (time not measured here).

Daytime alternatives:

- Sun sight. The same `solve_fix` works on the sun (GHA/dec from Skyfield): one elevation
  gives a line of position, and two sights hours apart give a running fix. Same level
  sensitivity.
- Sky polarization. A polarization camera gives heading from the sun's position even when
  the sun is hidden: [ccompass](../../catalog/repos/benjaminpotter__ccompass.md),
  [OpenSky simulator](../../catalog/resources/opensky-sky-polarization-simulator-2024.md),
  [PVI dataset](../../catalog/repos/ts-fupeng__pvi-dataset.md). Heading, not position.

Related in the index:

- Solvers: [cedar-solve](../../catalog/repos/smroid__cedar-solve.md),
  [tetra3](../../catalog/repos/esa__tetra3.md) ([docs](../../catalog/resources/tetra3-docs.md)),
  [astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md) (offline reference solves),
  [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md),
  [LOST](../../catalog/repos/uwcubesat__lost.md),
  [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md) (camera calibration).
- Sight reduction: [celestial-navigation toolkit](../../catalog/repos/alinnman__celestial-navigation.md),
  [celnav](../../catalog/repos/ms8r__celnav.md).
- Context: [concept page](../../catalog/concepts/celestial-nav.md),
  [primer: absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md),
  [GAO-21-320SP](../../catalog/resources/gao-21-320sp-gps-alternatives.md) (DoD alt-PNT
  assessment incl. celestial), [hackathon playbook](../../docs/hackathon-playbook.md).

## Not verified

- No camera on a moving vehicle and no real IMU: section 2 is simulation. Vibration is
  modelled as white per-sample tilt noise, not real vibration spectra or coning.
- SkyView images are resampled mosaics. Real lens distortion, rolling shutter and blur were
  not tested (cedar-solve's `distortion` parameter was left at 0).
- Section 1c has no ground truth: the site is inferred from the image credit, and the timestamp
  is assumed to be UTC.
- `generate_database`, the Rust Cedar-Detect centroider and ESA tetra3 itself were not run.
- Daytime methods (sun sight, polarization, SWIR) are discussed, not run.

## Licences of the inputs

cedar-solve and tetra3: Apache-2.0. ESA frames: "ESA/Gustav Pettersson CC BY-SA 3.0 IGO"
(cedar-solve `credits.txt`). The other cedar frames are released as tetra3 test images (same
file). Mellinger mosaic (via SkyView): (c) Axel Mellinger, "use in research and personal,
non-commercial use", per the FITS header. Fetched at run time, not redistributed. DE421: JPL,
public. Hipparcos star table: inside cedar-solve's database.
