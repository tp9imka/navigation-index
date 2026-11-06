# Kassas Starlink navigation - paper digest
<!-- about: res:kassas-starlink-navigation -->
**Enter LEO on the GNSS Stage: Navigation with Starlink Satellites** - Kassas, Neinavaie, Khalife, Khairallah, Haidar-Ahmad, Kozhaya, Shadram (ASPIN Lab, UC Irvine / Ohio State), Inside GNSS, Nov/Dec 2021 (web 2021-11-29). [paper](https://escholarship.org/content/qt9td3n8wd/qt9td3n8wd.pdf) | [web version](https://insidegnss.com/enter-leo-on-the-gnss-stage-navigation-with-starlink-satellites/) | code: none | Read: full text via the Inside GNSS web version (the eScholarship PDF could not be text-extracted here; assumed to be the same article). Table 1, Table 4 and several figures were not in the extracted text.

## Problem
Use Starlink downlinks for opportunistic navigation without any cooperation from SpaceX. Three obstacles: no broadcast ephemerides (TLE/SGP4 errors of km level), satellite clocks not atomic or not disclosed, and a proprietary signal so a specialized receiver must extract observables blind. This is a magazine overview of the lab's two receiver approaches and its first experiments.

## Method
- Approach 1 (carrier phase, their ref [13]): at 11.325 GHz, 2.5 MHz sampling, the FFT shows nine peaks ~44 kHz apart, treated as carriers. Tracked with a Costas-style loop whose loop filter is replaced by an adaptive Kalman filter PLL. The unknown offset of each peak from the true center frequency gives a Doppler ambiguity, absorbed in the navigation filter.
- Approach 2 (unknown periodic sync signal, ref [14]): model the downlink as an unknown periodic signal; matched-subspace detection; acquisition searches period and initial Doppler in 2D; tracking uses a linear chirp model with FFT estimates of Doppler and Doppler rate per coherent interval.
- Tracked Doppler shows a constant bias vs TLE predictions (Fig. 8, six satellites), estimated as a state.
- Ephemeris: SGP4 ~3 km error at TLE epoch, growing until the next daily TLE; error mostly along-track (Fig. 9, vs HPOP from SpaceX state vectors). TLE epoch times are shifted to minimize residuals.
- Navigation: weighted nonlinear least squares for static fixes; STAN (simultaneous tracking and navigation), an INS-aided EKF with LEO Doppler, for the vehicle.

## Data and sensors
- Static: NI USRP 2945R, two consumer antennas, Ku-band LNBs, octo-clock. Six Starlink satellites.
- Differential: base Ettus E312, rover USRP 2974, octo-clock-synchronized; 3 satellites over 320 s; 1.004 km baseline.
- Vehicle: Septentrio AsteRx-i V GNSS-INS (role as truth vs baseline not stated in the extracted text), VectorNav VN-100 MEMS IMU, USRP for Starlink at 11.325 GHz, VHF antenna + E312 for Orbcomm at 137-138 MHz. CA-55 freeway, 4.15 km in 150 s.
- Simulated UAV: tactical IMU, OCXO, 74 Starlink satellites with assumed chip-scale atomic clocks, 20 deg mask, Irvine, 300 s.
- Data not released. No dataset card in this hub.

## Headline results (as reported)
- Static positioning (Figs. 10-11, Table 2), initial error 179 km: 3D error 33.5 m (Approach 1), 22.9 m (Approach 2). With an altimeter, 2D error 7.7 m (Approach 1), 10 m (Approach 2).
- Differential Doppler (Figs. 12-14), rover initial error ~200 km: 3D 33.4 m, 2D 5.6 m.
- Ground vehicle (Figs. 16-17, Table 3), 3 Starlink + 2 Orbcomm, GNSS cut for the last 70 s (1.82 km): 3D RMSE GNSS-INS 118.5 m vs STAN LEO-aided INS 21.6 m.
- Simulated UAV (Fig. 18, Table 4): numbers not located in the extracted text.
- No runtime or hardware-timing numbers reported.

## Limitations
- Stated by authors: signal structure is proprietary, so both approaches rely on inferred models; TLE orbits carry km-level errors; Doppler bias and clocks must be estimated; channel outages and burst errors (a spike in the differential Doppler).
- Our read: very short experiments (150 s drive, 320 s differential, stationary fixes with 3-6 satellites). Good proof of concept, not a performance characterization.
- Our read: the sub-10 m 2D numbers need an altimeter or a nearby base station; the stand-alone 3D numbers are 23-34 m.
- Our read: the UAV result assumes future Starlink satellites with CSACs, so it does not say much about today's signals.
- Our read: the "nine carriers ~44 kHz apart" model predates the OFDM structure published later by Humphreys et al. (see [humphreys-2023-starlink-signal-structure](humphreys-2023-starlink-signal-structure.md)); the two views should be reconciled before building a receiver.

## Code, weights, license
- No code or data. Article is free to read on Inside GNSS and on eScholarship (UC open-access repository). The lab's algorithms are spread across its journal papers (refs [13], [14], [16]-[18]).

## Reproduction effort (estimate)
Estimate:
- Hardware: Ku-band LNB + dish or flat antenna, an SDR that can sample >= 2.5 MHz at the LNB IF, a GPSDO/octo-clock. Roughly a few hundred to a few thousand USD; a day to get a first Doppler track if the team has done SDR work.
- Software from scratch: FFT-peak tracking (Approach 1) is a weekend; matched-subspace sync tracking (Approach 2) is harder without the original refs.
- Not reproducible from this article alone: exact filter tuning, the STAN EKF, and the UAV simulation.

## What a hackathon team can take from it
- Simplest Starlink observable: FFT tone tracking near 11.325 GHz at 2.5 MHz sample rate with a Kalman PLL. No knowledge of the OFDM frame needed.
- Estimate a per-satellite Doppler bias and shift TLE epochs to absorb along-track error; both are cheap and visible in residuals.
- STAN pattern: LEO Doppler as an EKF update on an INS, which turned a 118.5 m GNSS-INS drift into 21.6 m over 70 s. Plugs straight into an existing INS/EKF stack.
- Mix constellations (Starlink Ku + Orbcomm VHF) to get enough satellites; geometry matters more than any single signal.
- For the estimator and its GDOP limits, see [psiaki-transit-on-steroids-2021](psiaki-transit-on-steroids-2021.md).
