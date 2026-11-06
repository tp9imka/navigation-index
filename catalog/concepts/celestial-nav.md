# Celestial and star-tracker navigation

`concept:celestial-nav`

Star trackers, sun/sky polarization, celestial fixes.

**Parent:** [Assured / resilient PNT](../concepts/assured-pnt.md)

## Repositories (15)

- [Skyfield](../repos/skyfielders__python-skyfield.md) - fit: high - Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.
- [tetra3](../repos/esa__tetra3.md) - fit: high - Fast lost-in-space plate solver for star trackers from ESA: identifies stars in an image and returns attitude using a precomputed pattern database.
- [cedar-solve](../repos/smroid__cedar-solve.md) - fit: high - Actively maintained fork of tetra3 with speed and robustness improvements, used in the Cedar telescope-aiming product.
- [Astrometry.net](../repos/dstndstn__astrometry.net.md) - fit: medium - Blind astrometric solver that identifies star fields in arbitrary images and returns the precise sky pointing, using geometric hash indexes of star catalogs.
- [OpenStarTracker](../repos/ubnanosatlab__openstartracker.md) - fit: medium - Open-source star tracker using a Bayesian star identification approach, developed by the University at Buffalo Nanosatellite Lab.
- [NASA COTS Star Tracker](../repos/nasa__cots-star-tracker.md) - fit: medium - NASA software for building a star tracker from commercial off-the-shelf cameras, including calibration and attitude solution.
- [LOST](../repos/uwcubesat__lost.md) - fit: medium - Open-source star tracker (C++) covering centroiding, star identification and attitude estimation, from the UW CubeSat team.
- [celnav](../repos/ms8r__celnav.md) - fit: medium - Small Tkinter desktop app for celestial navigation on a boat: computes the Nautical Almanac daily-page data with PyEphem, reduces sights and fixes position from two LOPs, correcting for vessel motion between sights.
- [celestial-navigation toolkit](../repos/alinnman__celestial-navigation.md) - fit: medium - Python toolkit for classic celestial navigation sight reduction, usable offline on a phone.
- [ccompass](../repos/benjaminpotter__ccompass.md) - fit: medium - Header-only C library for processing sky polarization images to support heading estimation; successor to compyss.
- [SPEL Open Star Tracker](../repos/spel-uchile__star_tracker.md) - fit: low - Open star tracker software from the University of Chile space lab, flown on SUCHAI nanosatellites.
- [Deep learning celestial navigation](../repos/gregtozzi__deep_learning_celnav.md) - fit: low - Exploratory project on automating celestial navigation with deep learning and edge inference on synthetic sky images.
- [OpenCPN celestial navigation plugin](../repos/seandepagnier__celestial_navigation_pi.md) - fit: low - OpenCPN plugin for entering sextant sights and plotting lines of position and fixes on the chart.
- [navalm](../repos/kq6up__navalm.md) - fit: low - Nautical almanac and celestial sight reduction for Unix/Linux with CLI, ncurses and web interfaces.
- [PVI polarization navigation dataset](../repos/ts-fupeng__pvi-dataset.md) - fit: low - Dataset combining stereo camera, IMU, polarization camera and high-precision GPS for polarization-aided navigation research.

## Documents, talks, courses, datasets (5)

- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS](../resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../resources/honeywell-vision-aided-navigation.md) - product - Honeywell's VAN correlates live visible or IR imagery against onboard reference maps for an absolute fix, paired with its inertial units.
- [OpenSky: A Modular and Open-Source Simulator of Sky Polarization Measurements](../resources/opensky-sky-polarization-simulator-2024.md) - paper - Open simulator of what a polarimetric camera sees of the sky (intensity, angle and degree of polarization), validated against real captures, for developing polarization compasses.
- [tetra3 documentation](../resources/tetra3-docs.md) - doc - Usage and API documentation for the tetra3 lost-in-space star plate solver, including database generation and solving images.
- [Навигация без GPS, которая уже работает](../resources/habr-nav-without-gps-overview-2025.md) - blog - English: 'Navigation without GPS that already works'.

