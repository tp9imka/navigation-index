# cedar-solve - integration card
<!-- about: repo:smroid/cedar-solve -->
One-line: maintained fork of ESA tetra3 (same `tetra3` import and calling API) that turns a night-sky image or star centroid list into boresight RA/Dec/Roll with no prior pointing, with faster and more uniform solve times, a solve timeout and status codes; the attitude half of a jam-proof celestial fix.

| | |
|---|---|
| Install | PyPI `pip install cedar-solve` gives **0.5.1 (uploaded 2024-06-22)**, the only version on PyPI; it predates the NumPy 2 fix (#19, closed 2024-11-05) and the v0.6.0 changes. For current code: `pip install git+https://github.com/smroid/cedar-solve.git` (GitHub tag v0.6.0, 2025-02-22; master pushed 2026-08-06; `pyproject.toml` still says `version = "0.5.1"`). Deps pinned in `pyproject.toml`: `numpy >=1.21.1,<2`, `Pillow >=8.3.1,<9`, `scipy >=1.7.1,<2`. Optional `[cedar-detect]` adds grpcio + protobuf for the Rust centroider. CLI `tetra3-gen-db`. |
| Runs on | Pure Python + NumPy/SciPy, CPU only, any OS. Used on Raspberry Pi per `migrating.rst` paths. Optional Cedar-Detect server is a Rust binary you build with `cargo build --release` and copy into `tetra3/bin/` (separate repo smroid/cedar-detect). |
| Inputs | Grayscale image (PIL or numpy) for `solve_from_image`, or centroids `[(y, x)]` plus image `size` `(height, width)` for `solve_from_centroids`. Optional `fov_estimate`/`fov_max_error` [deg], `distortion`, `target_pixel`, `target_sky_coord`. Pattern database `.npz` (bundled `default_database.npz`, ~14.7 MB per git tree, 10-30 deg FOV, stars to magnitude 8 per module docstring). Catalogue files for custom databases: BSC5, Hipparcos `hip_main`, Tycho `tyc_main`. |
| Outputs | Dict with `RA`, `Dec`, `Roll` [deg], `FOV`, `distortion`, `RMSE`, `Matches`, `Prob` (false-positive probability), `T_solve` and `T_extract` [ms], and `status` = `MATCH_FOUND` (1), `NO_MATCH` (2), `TIMEOUT` (3), `CANCELLED` (4), `TOO_FEW` (5) (module constants). Optional `RA_target`/`Dec_target`, matched stars, catalog stars, rotation matrix (`return_rotation_matrix=True`), visual. |
| Key API / entry points | (confirmed in `tetra3/tetra3.py`, `tetra3/__init__.py`) `tetra3.Tetra3(load_database='default_database', debug_folder=None)`; `.solve_from_image(image, fov_estimate=None, fov_max_error=None, match_radius=.01, match_threshold=1e-5, solve_timeout=5000, target_pixel=None, target_sky_coord=None, distortion=0, return_matches=False, return_visual=False, match_max_error=.002, pattern_checking_stars=None, **kwargs)`; `.solve_from_centroids(star_centroids, size, fov_estimate=None, ..., return_catalog=False, return_rotation_matrix=False, ...)`; `.cancel_solve()`; `.generate_database(max_fov, min_fov=None, save_as=None, star_catalog='hip_main', lattice_field_oversampling=100, patterns_per_lattice_field=50, verification_stars_per_fov=150, star_max_magnitude=None, pattern_max_error=.001, multiscale_step=1.5, epoch_proper_motion='now', pattern_stars_per_fov=None, linear_probe=False)`; `.load_database(path)`, `.save_database(path)`; module `tetra3.get_centroids_from_image(image, sigma=2, ...)`, `crop_and_downsample_image(...)`, `transform_to_image_coords(...)`, `transform_to_celestial_coords(...)`; `tetra3.cedar_detect_client.CedarDetectClient(binary_path=None, port=50051)` with `.extract_centroids(image, sigma, use_binned, binning=None, detect_hot_pixels=True, normalize_rows=True)`. |
| Time to first result | Estimate: 30-60 min to solve the bundled `examples/data/medium_fov` images with `examples/test_tetra3.py`, most of it on dependency pins (see Gotchas). Cedar-Detect adds a Rust toolchain install and build. Own camera with a FOV outside 10-30 deg: half a day or more incl. database generation (generation time not stated beyond the docstring's "a few minutes" to "many hours"). |
| License | Apache-2.0 (GitHub metadata, `LICENSE.txt`). Repo also has `TRADEMARKS.md` (not read). Star catalogues come from their providers under their own terms. |

## Minimal usage
Adapted from `examples/test_tetra3.py` (centroids first, then solve; falls back to the Python centroider when no Cedar-Detect binary). Not run.

```bash
python3.10 -m venv .venv && . .venv/bin/activate      # Pillow<9 has wheels only up to cp310
pip install git+https://github.com/smroid/cedar-solve.git
```
```python
import numpy as np, tetra3
from PIL import Image
t3 = tetra3.Tetra3(load_database='default_database')
img = np.asarray(Image.open('examples/data/medium_fov/orion_belt.jpg').convert('L'), dtype=np.uint8)
cent = tetra3.get_centroids_from_image(img)
sol = t3.solve_from_centroids(cent[:30], size=img.shape[:2], fov_estimate=None, solve_timeout=2000)
print(sol['status'], sol.get('RA'), sol.get('Dec'), sol.get('Roll'), sol.get('T_solve'))
```
`cent[:30]`: the example comments say about 30 centroids is "more than enough" and more just slow the solve.

## Wiring it into a nav stack
- Same role as [tetra3](./esa__tetra3.md): RA/Dec/Roll gives camera-to-J2000 attitude; add UTC time and a local vertical (IMU gravity or levelled mount) for a latitude/longitude celestial fix; fuse as an attitude measurement in the INS filter. See [celestial navigation](../../catalog/concepts/celestial-nav.md).
- Real-time use: `solve_timeout` (default 5000 ms) and `cancel_solve()` let a nav loop bound latency, and `status` distinguishes "too few stars" (cloud, daylight, blur) from "no match" so the filter can mark the measurement missing instead of wrong. `Prob` is the gate for rejecting false matches.
- Cedar-Detect runs as a gRPC subprocess on port 50051 with shared memory (`cedar_detect_client.py`); on a companion computer budget for one extra process.

## Differences from tetra3 (read this if you have tetra3 code)
- Import path and class are identical (`import tetra3`, `Tetra3`); `migrating.rst` says to switch by putting cedar-solve on `PYTHONPATH`. Installing both packages into one environment collides on the `tetra3` package name.
- Defaults changed: `match_threshold` 1e-5 (tetra3: 1e-3), `solve_timeout` 5000 ms (tetra3: None), `pattern_checking_stars` no longer needed. New: `status`, `T_extract`, `target_sky_coord`, `cancel_solve()`, `return_rotation_matrix`.
- `generate_database` parameters differ (`lattice_field_oversampling`, `patterns_per_lattice_field`, `epoch_proper_motion`, `linear_probe`); tetra3 scripts that pass `pattern_stars_per_fov` etc. need review. Maintainer in #22: cedar databases are "intended to be compatible" with legacy tetra3.
- Default database is smaller (~14.7 MB vs about 49 MB in esa/tetra3) and goes to magnitude 8 (tetra3 docstring: 7). v0.6.0 notes: regenerated for 2025 with new parameters.

## Gotchas
- **Dependency pins**: `Pillow<9` means the newest allowed is Pillow 8.4.0, whose PyPI wheels stop at cp310; on Python 3.11+ pip will try to build Pillow 8 from source (needs libjpeg/zlib headers, may fail). Maintainer in #25: does not recall why the pin exists, suggests trying a newer Pillow and running the tests. `numpy<2` is still pinned although the `np.math` call (#19) was fixed in source. Workaround (not run): `pip install --no-deps git+...` then install numpy/scipy/Pillow yourself and run `pytest`.
- `migrating.rst` snippets drift from the code: it calls `t3.get_centroids_from_image(image)` (it is a module function, `tetra3.get_centroids_from_image`), omits the required `size` argument of `solve_from_centroids`, and passes `max_size=10` to `extract_centroids`, which has no such parameter. Use `examples/test_tetra3.py` as the reference.
- `size` is `(height, width)` per the `solve_from_centroids` docstring, but the docstring's own example passes PIL `image.size`, which is `(width, height)`. With a numpy image use `img.shape[:2]`.
- README defers all documentation to esa/tetra3 and readthedocs for tetra3, so parameter docs there describe the old defaults.
- Open issue #6 (PyPI wheels and packaging). Closed #20 (`IndexError` in `solve_from_centroids`), #23/#24 (robust parameter choices).

## Alternatives
- [tetra3](./esa__tetra3.md) - upstream ESA code, same API, dormant since 2023, NumPy 2 break; only if you must match ESA's version.
- [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md) - different star-ID approach (Bayesian); compare if pattern matching fails on your optics.
- [astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md) - blind general-purpose solver; good offline reference to check cedar-solve answers, not tuned for a real-time loop.

Sources: `gh api repos/smroid/cedar-solve` (Apache-2.0, fork of esa/tetra3, pushed 2026-08-06), releases and tags (v0.6.0 notes), README.rst, migrating.rst, pyproject.toml (master and v0.6.0), tetra3/__init__.py, tetra3/tetra3.py (module docstring, `Tetra3` methods, status constants, `get_centroids_from_image`), tetra3/cedar_detect_client.py, tetra3/cli/generate_database.py, examples/test_tetra3.py, repo tree (database size), commits list, issues #6, #19, #20, #22, #23, #24, #25; PyPI JSON for cedar-solve (0.5.1) and Pillow 8.4.0 (read 2026-11-06).
