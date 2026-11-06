# Sample: Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical

`sample:celestial-star-tracker` - code and walkthrough in [samples/celestial-star-tracker](../../samples/celestial-star-tracker/)

Runs cedar-solve (tetra3 API, v0.6.0 on NumPy 2) lost-in-space on 40 real SkyView Mellinger cutouts with a known WCS (12 and 20 deg FOV, random pointing and roll) and on the 20 real camera frames shipped with cedar-solve, reporting solve rate, pointing/roll error against the WCS and runtime on an M2 Max. A stdlib Marcq St Hilaire least-squares solver turns star elevations above the gravity vertical into latitude/longitude; a Skyfield-truth Monte Carlo sweeps level bias, vibration, accelerometer bias, clock error, refraction and FOV, and confirms 1 arcmin of level error = about 1.85 km. The 8 ESA tetra3 frames (mount alt/az in the file names) give a crude real-data fix.

**Verification:** ran on 2026-11-06 with Python 3.12.14 (numpy 2.5.4, cedar-solve git tag v0.6.0 installed --no-deps, skyfield 1.55, astropy 8.0.2) on an Apple M2 Max: plate_solve_eval.py with and without --fov-hint, esa_mount_fix.py, position_fix_sim.py --runs 200; outputs in results/ and quoted in the README. Plate solving uses real images (SkyView Mellinger mosaic cutouts, reference = requested WCS; cedar-solve test frames, no reference). The position-fix budget is simulation with Skyfield truth; centroid noise, vibration and bias levels are stated assumptions. The ESA-frame position has no ground truth (capture site undocumented). 11 unittest tests pass in the venv; with plain Homebrew python3 10 pass and the Skyfield test skips. A planted Jacobian sign flip fails 4 tests. No real IMU, moving camera, lens distortion, ESA tetra3, Cedar-Detect or database generation was run.

**Concepts:** [Celestial and star-tracker navigation](../../catalog/concepts/celestial-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `star-tracker`, `plate-solving`, `tetra3`, `cedar-solve`, `skyfield`, `sight-reduction`, `level-error`, `stdlib`

## Related

- uses: [cedar-solve](../../catalog/repos/smroid__cedar-solve.md)
- uses: [Skyfield](../../catalog/repos/skyfielders__python-skyfield.md)
- explains: [tetra3](../../catalog/repos/esa__tetra3.md)
- explains: [Astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md)
- explains: [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md)
- explains: [LOST](../../catalog/repos/uwcubesat__lost.md)
- explains: [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md)
- explains: [celestial-navigation toolkit](../../catalog/repos/alinnman__celestial-navigation.md)
- explains: [celnav](../../catalog/repos/ms8r__celnav.md)
- explains: [ccompass](../../catalog/repos/benjaminpotter__ccompass.md)
- explains: [PVI polarization navigation dataset](../../catalog/repos/ts-fupeng__pvi-dataset.md)
- uses: [tetra3 documentation](../../catalog/resources/tetra3-docs.md)
- explains: [OpenSky: A Modular and Open-Source Simulator of Sky Polarization Measurements](../../catalog/resources/opensky-sky-polarization-simulator-2024.md)
- explains: [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS](../../catalog/resources/gao-21-320sp-gps-alternatives.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [JPL DE421 planetary ephemeris (NAIF SPK kernel)](../../catalog/resources/jpl-de421-ephemeris.md) (dataset_for)
- [NASA SkyView virtual observatory](../../catalog/resources/nasa-skyview-virtual-observatory.md) (dataset_for)

_Indexed by lane(s): samples_
