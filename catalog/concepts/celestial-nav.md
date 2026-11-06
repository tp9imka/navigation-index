# Celestial and star-tracker navigation

`concept:celestial-nav`

Star trackers, sun/sky polarization, celestial fixes.

**Parent:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

## Samples (1)

- [Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical](../../catalog/samples/celestial-star-tracker.md) - Runs cedar-solve (tetra3 API, v0.6.0 on NumPy 2) lost-in-space on 40 real SkyView Mellinger cutouts with a known WCS (12 and 20 deg FOV, random pointing and roll) and on the 20 real camera frames shipped with cedar-solve

## Repositories (16)

- [Skyfield](../../catalog/repos/skyfielders__python-skyfield.md) - fit: high - Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.
- [tetra3](../../catalog/repos/esa__tetra3.md) - fit: high - Fast lost-in-space plate solver for star trackers from ESA: identifies stars in an image and returns attitude using a precomputed pattern database.
- [cedar-solve](../../catalog/repos/smroid__cedar-solve.md) - fit: high - Actively maintained fork of tetra3 with speed and robustness improvements, used in the Cedar telescope-aiming product.
- [Astrometry.net](../../catalog/repos/dstndstn__astrometry.net.md) - fit: medium - Blind astrometric solver that identifies star fields in arbitrary images and returns the precise sky pointing, using geometric hash indexes of star catalogs.
- [OpenStarTracker](../../catalog/repos/ubnanosatlab__openstartracker.md) - fit: medium - Open-source star tracker using a Bayesian star identification approach, developed by the University at Buffalo Nanosatellite Lab.
- [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md) - fit: medium - NASA software for building a star tracker from commercial off-the-shelf cameras, including calibration and attitude solution.
- [LOST](../../catalog/repos/uwcubesat__lost.md) - fit: medium - Open-source star tracker (C++) covering centroiding, star identification and attitude estimation, from the UW CubeSat team.
- [celnav](../../catalog/repos/ms8r__celnav.md) - fit: medium - Small Tkinter desktop app for celestial navigation on a boat: computes the Nautical Almanac daily-page data with PyEphem, reduces sights and fixes position from two LOPs, correcting for vessel motion between sights.
- [celestial-navigation toolkit](../../catalog/repos/alinnman__celestial-navigation.md) - fit: medium - Python toolkit for classic celestial navigation sight reduction, usable offline on a phone.
- [ccompass](../../catalog/repos/benjaminpotter__ccompass.md) - fit: medium - Header-only C library for processing sky polarization images to support heading estimation; successor to compyss.
- [SPEL Open Star Tracker](../../catalog/repos/spel-uchile__star_tracker.md) - fit: low - Open star tracker software from the University of Chile space lab, flown on SUCHAI nanosatellites.
- [Deep learning celestial navigation](../../catalog/repos/gregtozzi__deep_learning_celnav.md) - fit: low - Exploratory project on automating celestial navigation with deep learning and edge inference on synthetic sky images.
- [OpenCPN celestial navigation plugin](../../catalog/repos/seandepagnier__celestial_navigation_pi.md) - fit: low - OpenCPN plugin for entering sextant sights and plotting lines of position and fixes on the chart.
- [navalm](../../catalog/repos/kq6up__navalm.md) - fit: low - Nautical almanac and celestial sight reduction for Unix/Linux with CLI, ncurses and web interfaces.
- [PVI polarization navigation dataset](../../catalog/repos/ts-fupeng__pvi-dataset.md) - fit: low - Dataset combining stereo camera, IMU, polarization camera and high-precision GPS for polarization-aided navigation research.
- [GNSS-AK_model - GNSS + astro-corrector model](../../catalog/repos/ledesha__gnss-ak_model.md) - fit: low - Diploma C++ code modelling a moving user, GNSS operation and an astro-corrector (star-tracker style celestial correction), with integrator and linear-algebra helpers.

## Documents, talks, courses, datasets (7)

- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS](../../catalog/resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../../catalog/resources/honeywell-vision-aided-navigation.md) - product - Honeywell's VAN correlates live visible or IR imagery against onboard reference maps for an absolute fix, paired with its inertial units.
- [JPL DE421 planetary ephemeris (NAIF SPK kernel)](../../catalog/resources/jpl-de421-ephemeris.md) - dataset - The DE421 planetary and lunar ephemeris as a NAIF SPK binary kernel (de421.bsp, about 16 MB), an older but compact JPL Development Ephemeris commonly loaded with Skyfield.
- [NASA SkyView virtual observatory](../../catalog/resources/nasa-skyview-virtual-observatory.md) - dataset - A NASA service that cuts FITS images with a reference WCS from many all-sky surveys at any position, scale and projection.
- [OpenSky: A Modular and Open-Source Simulator of Sky Polarization Measurements](../../catalog/resources/opensky-sky-polarization-simulator-2024.md) - paper - Open simulator of what a polarimetric camera sees of the sky (intensity, angle and degree of polarization), validated against real captures, for developing polarization compasses.
- [tetra3 documentation](../../catalog/resources/tetra3-docs.md) - doc - Usage and API documentation for the tetra3 lost-in-space star plate solver, including database generation and solving images.
- [Навигация без GPS, которая уже работает](../../catalog/resources/habr-nav-without-gps-overview-2025.md) - blog - English: 'Navigation without GPS that already works'.

