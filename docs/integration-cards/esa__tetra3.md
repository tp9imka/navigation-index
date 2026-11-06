# tetra3 - integration card
<!-- about: repo:esa/tetra3 -->
One-line: give it a night-sky image, get camera boresight RA/Dec/Roll with no prior pointing, in pure Python; the attitude half of a jam-proof celestial fix.

| | |
|---|---|
| Install | Not on PyPI. `pip install git+https://github.com/esa/tetra3.git` (has `setup.py`, version "0.1", ships `tetra3/data/*`) or clone and import. Deps (`requirements.txt`): `numpy >= 1.21.1`, `Pillow >= 8.3.1`, `scipy >= 1.7.1`. No releases or tags. README says use the `legacy` branch if the June 2023 `master` rewrite breaks you. |
| Runs on | Pure Python + NumPy/SciPy, CPU only, any OS/arch (incl. Apple Silicon, Raspberry Pi, Jetson CPU). No GPU path. |
| Inputs | Grayscale image (PIL `Image` or numpy array) for `solve_from_image`, or pixel centroids `(y, x)` + image `size` for `solve_from_centroids`. Optional `fov_estimate` / `fov_max_error` [deg], `distortion` (scalar or `(min, max)` range, fraction at width/2), `target_pixel`. A pattern database `.npz` (default bundled). |
| Outputs | Dict: `RA`, `Dec`, `Roll` [deg], `FOV` [deg], `distortion`, `RMSE` [arcsec], `Matches`, `Prob` (false-positive probability), `epoch_equinox`, `T_solve` [ms]; optional `RA_target`/`Dec_target`, `matched_stars`, visual. All `None` on failure. Frame: J2000 for Hipparcos/Tycho databases (docstring). |
| Key API / entry points | (confirmed in `tetra3/tetra3.py`) `Tetra3(load_database='default_database', debug_folder=None)`; `Tetra3.solve_from_image(image, fov_estimate=None, fov_max_error=None, pattern_checking_stars=8, match_radius=.01, match_threshold=1e-3, solve_timeout=None, target_pixel=None, distortion=0, return_matches=False, return_visual=False, **kwargs)`; `Tetra3.solve_from_centroids(star_centroids, size, ...)`; `Tetra3.generate_database(max_fov, min_fov=None, save_as=None, star_catalog='hip_main', pattern_stars_per_fov=10, ...)`; `load_database(path)`, `save_database(path)`; module-level `get_centroids_from_image(image, sigma=2, ...)`, `crop_and_downsample_image(...)`. Example: `examples/test_tetra3.py`; `examples/generate_database.py`. |
| Time to first result | Estimate: 15-30 min to solve the bundled example TIFFs (pip install, run `examples/test_tetra3.py`). Own camera: half a day for centroid tuning and, if FOV is outside 10-30 deg, a custom database build (generation time not stated). Assumes Python 3 with NumPy < 2 (see Gotchas). |
| License | Apache-2.0 (GitHub and README). Star catalogues are separate downloads under their providers' terms (not stated in the repo). |

## Minimal usage
From `examples/test_tetra3.py`, adapted. Not run.

```bash
pip install "numpy<2" git+https://github.com/esa/tetra3.git
```
```python
import tetra3
from PIL import Image
t3 = tetra3.Tetra3()  # loads bundled default_database (10-30 deg FOV, mag <= 7)
with Image.open("examples/data/2019-07-29T204726_Alt40_Azi-135_Try1.tiff") as img:
    sol = t3.solve_from_image(img, fov_estimate=11.4, distortion=[-.2, .1])
print(sol["RA"], sol["Dec"], sol["Roll"], sol["Matches"], sol["T_solve"])
```

Custom database (Hipparcos), per `generate_database` docstring: download `hip_main.dat` from https://cdsarc.u-strasbg.fr/ftp/cats/I/239/ into the `tetra3/` package directory, then `t3 = tetra3.Tetra3(load_database=None); t3.generate_database(max_fov=12, min_fov=8, star_max_magnitude=7, save_as='my_db')`.

## Star database generation
- Bundled `tetra3/data/default_database.npz` (about 49 MB in the repo) covers 10-30 deg FOV, stars to magnitude 7.
- For other FOVs you build your own from one of three catalogues (docstring): Yale Bright Star `BSC5` (285 KB, 9,110 stars, from tdc-www.harvard.edu, byte format), Hipparcos `hip_main` (51 MB, 118,218 stars, default and recommended) or Tycho `tyc_main` (355 MB), both from CDS `I/239`. The `.dat` file must sit in the package directory.
- Narrow FOV needs dimmer stars and a bigger database; README suggests about 10 deg FOV and at least 512x512 px as a starting camera.

## Wiring it into a nav stack
- Attitude only. RA/Dec/Roll of the boresight gives camera-to-inertial (J2000) rotation. For a position fix you also need UTC time and a local vertical (IMU gravity vector or a levelled mount): with those, the zenith RA/Dec gives latitude and longitude (celestial fix). Compose with camera-to-body extrinsics from calibration.
- Typical flow: camera frame => `get_centroids_from_image` (tune once, pass the same kwargs to `solve_from_image`) => quaternion => fuse as an attitude measurement in your INS filter, or compare with AHRS heading to show heading drift correction.
- See concept page [celestial navigation](../../catalog/concepts/celestial-nav.md).

## Gotchas
- **NumPy 2 break**: `solve_from_centroids` calls `np.math.factorial` (line 1395 of `tetra3.py` on master); `np.math` is gone in NumPy 2. Open issue #37. Pin `numpy<2` or use cedar-solve.
- ESA repo is effectively dormant: last commit 2023-12-10 (pushed 2024-08), no releases, open issues on solve-time spikes (#30) and parameter tuning (#34). Active development moved to the fork [cedar-solve](../../catalog/repos/smroid__cedar-solve.md), whose README says it is a tetra3 fork with "the calling API ... the same", faster and more uniform solve times, smaller database, on PyPI. The ESA README itself does not mention the fork.
- Centroiding is the usual failure point (issues #13, #11 "No solution with generated database"); daytime, cloud, moonlight, motion blur and a short exposure on a moving platform all reduce detectable stars.
- Performance claim "10 milliseconds ... with 10 arcsecond accuracy" excludes centroid extraction and is README text, not measured here.
- Databases generated with the pre-2023 code may not load in master (README note on the June 2023 rewrite).

## Alternatives
- [cedar-solve](../../catalog/repos/smroid__cedar-solve.md) - same API, maintained, PyPI; default choice for new work.
- [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md) - University at Buffalo star tracker with Bayesian star identification; compare if tetra3 pattern matching is unreliable on your optics.
- [astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md) - general blind astrometric solver over arbitrary images; use it offline to produce reference pointings for checking tetra3 (real-time suitability not assessed here). Also [NASA COTS star tracker](../../catalog/repos/nasa__cots-star-tracker.md), which adds camera calibration for COTS hardware.

Sources: README.rst, setup.py, requirements.txt, tetra3/tetra3.py (module docstring, `Tetra3` methods, `get_centroids_from_image`), examples/test_tetra3.py, tetra3/data listing, commits list, issues #11, #13, #30, #34, #37, smroid/cedar-solve README.rst and migrating.rst (read 2026-11-06).
