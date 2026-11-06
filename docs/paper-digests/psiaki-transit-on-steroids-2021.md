# TRANSIT on steroids (LEO Doppler nav) - paper digest
<!-- about: res:psiaki-transit-on-steroids-2021 -->
**Navigation using carrier Doppler shift from a LEO constellation: TRANSIT on steroids** - Mark L. Psiaki (Virginia Tech), NAVIGATION: Journal of the ION, vol. 68 no. 3, pp. 621-641, 2021. [paper](https://navi.ion.org/content/68/3/621) ([DOI](https://doi.org/10.1002/navi.438)) | code: none | Read: full text via the open-access HTML on navi.ion.org. Table 1 and Table 2 are images that did not text-extract; Table 2 numbers below come from the Sec. 5 text that describes it.

## Problem
Can a mega-constellation in LEO give GNSS-class positioning using only carrier Doppler shift, with no ranging codes and no atomic clocks on the satellites? TRANSIT did Doppler positioning with one satellite at a time; a constellation with many satellites in view could give an instantaneous point solution including time.

## Method
- Doppler measurement models (Sec. 2): an analytic model (Eq. 7), a 5-point finite difference of accumulated delta range (Eq. 10), and a simplified model (Eq. 13) used only for GDOP.
- Point-solution batch filter (Sec. 4): weighted nonlinear least squares, Gauss-Newton with bisection line search.
- 8 unknowns: 3D position, receiver clock offset, 3D velocity, clock offset rate. Needs >= 8 Doppler measurements.
- Sec. 9: time stays observable without satellite atomic clocks or ranging codes, but weakly (our read: through the fast change of satellite geometry, so a clock offset maps into a position/velocity mismatch).
- Generalized GDOP analysis (Sec. 6) and per-constellation GDOP maps (Sec. 7): Iridium, OneWeb, Starlink, Kuiper.

## Data and sensors
- Simulation only, no hardware. Single-antenna Doppler receiver assumed.
- Sec. 5: 2,825-satellite final Starlink constellation, 7.5 deg mask, 89-189 visible satellites. 200 cases (100 with perfect ephemerides/clocks, 100 with errors), random global locations, altitude 0-9,144 m, velocity per axis Gaussian 137 m/s, clock offset uniform +-0.25 s.
- Filter knowledge errors (second set): satellite position 2 m per axis, velocity 0.002 m/s, clock frequency 3.3e-11 s/s. Range-rate noise 0.01 m/s (abstract and conclusions).
- Initialization: horizontal error 143-151 km.
- No dataset card applies.

## Headline results (as reported)
- Table 2 (via Sec. 5 text): position error perfect ephemerides 1.35 m RMS / 4.16 m peak; erroneous ephemerides 2.27 m RMS / 5.43 m peak.
- Table 2 (via Sec. 5 text): velocity ~0.01 m/s RMS, erroneous-ephemeris peak 0.0435 m/s; clock offset error roughly 0.0002-0.0009 s.
- Convergence: max 17 iterations (perfect), 14 (erroneous), average 8-9 (Sec. 5).
- Figs. 2-3: final Starlink GDOP below 2 globally.
- Fig. 4: initial Starlink GDOP rises sharply above +50 and below -50 deg latitude (no high-inclination shells).
- Figs. 5-6: OneWeb with alternating ascending/descending node grouping drops max GDOP below 4.3, a factor of 23 improvement over the original grouping.
- Abstract/Sec. 9: 1-5 m position and 0.01-0.05 m/s velocity "may be achievable" at 0.01 m/s range-rate accuracy. Timing is the weak point.
- Iridium alone cannot support the concept (users typically see one satellite).

## Limitations
- Stated by author (Sec. 8): communication footprints overlap little, so 8+ strong main-lobe signals are unlikely (side lobes, INS-aided sparse use, or beacons proposed); 11-40 GHz downlinks suffer foliage and rain; multipath and atmosphere not analyzed; multiple access for 100+ simultaneous satellites is unsolved; convergence only tested from ~150 km, a true cold start could be "as large as 20,000 km"; ephemeris and clock frequency prediction without other GNSS is the largest challenge (Sec. 8.7).
- Our read: clock offset accuracy is quoted three ways - abstract 0.0001-0.0010 s, Sec. 5 0.0002-0.0009 s, conclusions 0.0002-0.0004 s.
- Our read: 0.01 m/s range-rate noise and 2 m ephemerides are far better than what opportunistic Starlink with TLEs gives today (Kassas reports km-level TLE errors). This paper is a design study for a cooperative system, not an opportunistic receiver.

## Code, weights, license
- No code. The paper text is open access on navi.ion.org (ION open-access journal).

## Reproduction effort (estimate)
Estimate:
- Easy in simulation: TLEs from CelesTrak, SGP4 (e.g. Python `sgp4`), synthetic Doppler with 0.01 m/s noise, 8-state Gauss-Newton. One person, half a day to a GDOP map and an RMS error.
- Not reproducible: the final 2,825-satellite constellation used here differs from today's deployed Starlink, and the paper's exact noise model value did not text-extract.

## What a hackathon team can take from it
- The 8-state Doppler point solution (position, velocity, clock offset, clock rate) is the minimal estimator for any LEO Doppler demo. Write it once, swap constellations.
- GDOP as a go/no-go: compute Doppler GDOP for the hackathon site and time before collecting any data; high latitudes with early Starlink are bad.
- Initialization is a real issue (tested only from ~150 km). Pair with [leo-doppler-cold-start-2025](leo-doppler-cold-start-2025.md) for an initializer.
- Treat the 1-5 m numbers as an upper bound under cooperative assumptions; with TLEs expect tens to hundreds of metres (see [kassas-starlink-navigation](kassas-starlink-navigation.md)).
