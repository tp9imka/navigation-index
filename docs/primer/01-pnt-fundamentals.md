# 1. PNT fundamentals

After this chapter you can describe any navigation system as "a state, an uncertainty,
a set of measurements and a way to check they agree", and you will know the vocabulary
judges use when they ask whether your solution is "assured".

Next: [GNSS and its threats](02-gnss-and-threats.md) | [Primer index](README.md)

## What PNT actually is

PNT means three related outputs:

- **Position** - where you are, in some coordinate frame.
- **Navigation** - position over time plus velocity and attitude (which way you face),
  so you can steer.
- **Timing** - a shared clock. GNSS is the world's main time source as well as its main
  position source, which is why a jammer can upset telecom and power grids, not just
  vehicles ([ION webinar on timing-first PNT](../../catalog/resources/ion-webinar-tpn.md)).

As a software engineer, think of a navigation system as a state estimator:

```
state x = [position, velocity, attitude, sensor biases, clock offset, ...]
P       = covariance of x (how unsure you are about each element)
```

Sensors come in two flavours, and nearly every design in this hub mixes both:

| Kind | Examples | Strength | Weakness |
|------|----------|----------|----------|
| **Relative / dead reckoning** | IMU, wheel odometry, visual odometry, LiDAR odometry, DVL | Smooth, high rate, hard to jam | Error grows without bound over time or distance |
| **Absolute fixes** | GNSS, image-to-map matching, terrain matching, magnetic anomaly, star tracker, radio beacons | Error does not grow with time | Intermittent, can be denied, spoofed or ambiguous |

The core pattern of resilient navigation is: **dead-reckon between absolute fixes, and
check every fix before you trust it.** Chapters 3 and 4 cover the dead-reckoning side,
chapters 2 and 5 the absolute side.

## Coordinate frames (the number one source of hackathon bugs)

You will meet these frames constantly (chapter 7 covers the tooling):

- **Geodetic (lat, lon, height)** on an ellipsoid, usually WGS84. Height can be above the
  ellipsoid or above the geoid (roughly mean sea level); GNSS gives ellipsoidal height,
  DEMs usually give orthometric height. Mixing them is a classic error
  ([GeographicLib docs](../../catalog/resources/geographiclib-docs.md)).
- **ECEF** - Earth-centred, Earth-fixed Cartesian. What GNSS solvers compute in.
- **Local tangent planes: ENU or NED** - east-north-up (ROS convention) or north-east-down
  (aerospace and PX4/ArduPilot convention). Feeding ENU into an NED consumer silently
  flips axes ([PX4 external position docs](../../catalog/resources/px4-external-position-estimation.md)).
- **Body frame** - attached to the vehicle; IMU and cameras measure here, each with its own
  mounting offset (extrinsics).

Rule: write down the frame of every variable, and convert with a library
([pymap3d](../../catalog/repos/geospace-code__pymap3d.md),
[pyproj](../../catalog/repos/pyproj4__pyproj.md)), never by hand.

## Uncertainty, consistency and integrity

- **Accuracy** - how close your estimate is to truth.
- **Covariance** - how close your filter *thinks* it is. A filter whose covariance is much
  smaller than its real error is *overconfident* and will reject good measurements.
- **Integrity** - the ability to detect that the solution is wrong and warn in time. In
  aviation this is formalised as RAIM (receiver autonomous integrity monitoring): use
  redundant measurements to test for a faulty one and exclude it
  ([Navipedia](../../catalog/resources/navipedia.md) has good RAIM pages;
  [Groves](../../catalog/resources/groves-pnt-book-2e.md) covers fault detection).

The key operational lesson from real spoofing incidents is that **integrity beats
accuracy**: crews and systems were hurt most by positions that looked plausible but were
wrong, and some avionics stayed degraded after GNSS returned
([OPSGROUP spoofing report](../../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md)).
For a hackathon this means an "is my position plausible?" monitor is often a better demo
than a slightly more accurate filter.

The basic consistency test, used everywhere from RAIM to EKF innovation gates:

```
innovation   y = z - h(x)          # measurement minus prediction
innovation covariance S = H P H^T + R
normalised   d2 = y^T S^-1 y        # chi-square distributed if the model is right
reject the measurement if d2 > threshold for the chosen false-alarm rate
```

PX4 and ArduPilot both expose these innovation tests as tuning parameters
([PX4 EKF2 guide](../../catalog/resources/px4-ekf2-tuning-guide.md),
[ArduPilot EKF overview](../../catalog/resources/ardupilot-ekf-overview.md)).

## Assured PNT: the vocabulary

Defense and critical-infrastructure documents use a shared framing you should reuse in
your pitch:

- **Prevent / respond / recover.** The DHS
  [Resilient PNT Conformance Framework](../../catalog/resources/dhs-resilient-pnt-conformance-framework.md)
  grades equipment on four levels from basic recovery up to full threat tolerance.
- **Identify / protect / detect / respond / recover.** NIST maps the Cybersecurity Framework
  onto PNT users and treats GNSS as an untrusted external input
  ([NIST IR 8323r1](../../catalog/resources/nist-ir-8323r1-pnt-profile.md)).
- **Source diversity, integrity checking, holdover.** The architectural patterns in the
  [DHS reference architecture](../../catalog/resources/dhs-resilient-pnt-reference-architecture.md).
- **Complementary PNT.** No single technology fully backs up GPS
  ([DOT demonstration report](../../catalog/resources/dot-complementary-pnt-report-2021.md);
  the [JRC A-PNT assessment](../../catalog/resources/jrc-assessing-apnt-2023.md) recommends a
  system-of-systems approach).
- **DoD view:** keep GPS at the core and add complements, with integration and testing as
  the recurring challenge ([GAO-21-320SP](../../catalog/resources/gao-21-320sp-gps-alternatives.md)).

For a contrarian counterweight to "GPS loss is catastrophic", read
[RAND RR-2970](../../catalog/resources/rand-rr2970-resilient-pnt.md).

## Timing in one paragraph

A receiver's clock offset is a state like any other: GNSS solves for it alongside
position (chapter 2). Without GNSS, time drifts at the rate of your local oscillator.
Holdover - keeping usable time without GNSS - is what better clocks buy you; DARPA's
[ROCkN](../../catalog/resources/darpa-rockn.md) programme targets portable optical
clocks for exactly this. In a hackathon, timing shows up as: timestamp alignment between
sensors (a common VIO failure), PPS discipline via
[gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md), and spoofers that push time
rather than position (TEXBAT includes time-push scenarios, see chapter 2).

## Failure modes under EW

| Threat | What it does | What the system sees |
|--------|--------------|----------------------|
| **Jamming** | Raises the noise floor in the GNSS band | Loss of fix, C/N0 drop, AGC change. Annoying but obvious. |
| **Spoofing** | Transmits counterfeit GNSS signals | A confident, wrong position or time. Hard to see. Regulators treat it as the higher-risk threat ([EASA SIB](../../catalog/resources/easa-sib-2022-02r4.md)). |
| **Meaconing** | Rebroadcasts real signals with delay | Consistent but shifted solution; defeats data authentication alone ([OSNMA receiver guidelines](../../catalog/resources/galileo-osnma-receiver-guidelines.md)). |
| **Link jamming** | Denies C2 / telemetry radio | Vehicle must navigate and decide on its own ([IEEE Spectrum on Ukraine](../../catalog/resources/ieee-spectrum-ukraine-drones-ew-2025.md)). |
| **Contaminated fusion** | Spoofed GNSS pulls a GNSS/INS filter along | Hybrid solutions can also be corrupted ([FAA SAFO 24002](../../catalog/resources/faa-safo-24002.md)). |

The environment you are designing for: reporting from the war in Ukraine describes GNSS
as often effectively unavailable near the front line
([IISS dossier](../../catalog/resources/iiss-uavs-isr-deterrence-war-2026.md)), and
interference around the Baltic, Black Sea and Middle East affects civil aviation and
shipping daily ([GPSJam](../../catalog/resources/gpsjam-org.md)).

## Learn it

1. [How to fool a GPS (TEDx, Humphreys)](../../catalog/resources/ted-humphreys-how-to-fool-a-gps.md) - accessible motivation: why civil GNSS is easy to counterfeit.
2. [ION Online Tutorial: Basics of Satellite Navigation](../../catalog/resources/ion-online-tutorial-basics-satnav.md) - free, short.
3. [Stanford GPS MOOC (van Diggelen, Enge)](../../catalog/resources/stanford-gps-mooc-van-diggelen-enge.md) - pseudoranges and receivers.
4. [Navipedia](../../catalog/resources/navipedia.md) - lookup reference for any GNSS term.
5. [SKYbrary: GNSS jamming and spoofing](../../catalog/resources/skybrary-gnss-jamming-spoofing.md) - how interference propagates through real avionics.
6. [GAO-21-320SP: DoD PNT alternatives to GPS](../../catalog/resources/gao-21-320sp-gps-alternatives.md) - the alt-PNT landscape on a few pages.
7. [NIST IR 8323r1 PNT profile](../../catalog/resources/nist-ir-8323r1-pnt-profile.md) and [DHS conformance framework](../../catalog/resources/dhs-resilient-pnt-conformance-framework.md) - resilience vocabulary for your pitch.
8. [OPSGROUP GPS spoofing report](../../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md) - ground truth on what spoofing does in service.
9. [Groves, Principles of GNSS, Inertial and Multisensor Integrated Navigation](../../catalog/resources/groves-pnt-book-2e.md) - the reference book for everything in chapters 1 to 5.

## Build with it

- [pymap3d](../../catalog/repos/geospace-code__pymap3d.md) - pure-Python geodetic/ECEF/ENU/NED conversions.
- [pyproj](../../catalog/repos/pyproj4__pyproj.md) - CRS transforms and geodesics.
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - receiver daemon, PPS timing.
- [RAIM (MATLAB)](../../catalog/repos/michaelbeechan__raim.md) - small, readable fault detection and exclusion; port it to Python.
- [MAAST for ARAIM](../../catalog/repos/stanford-gps-lab__maast_for_araim_2.md) - aviation integrity availability maps.
- [MaRS](../../catalog/repos/aau-cns__mars_lib.md) - modular fusion where sensors can drop in and out.
- [galmon](../../catalog/repos/berthubert__galmon.md) - public GNSS monitoring data.

Related concepts: [assured PNT](../../catalog/concepts/assured-pnt.md),
[timing](../../catalog/concepts/timing.md), [EW resilience](../../catalog/concepts/ew-resilience.md).
