# Canciani AFIT MagNav dissertation - paper digest
<!-- about: res:canciani-afit-magnetic-anomaly-dissertation-2016 -->
**Absolute Positioning Using the Earth's Magnetic Anomaly Field** - Aaron J. Canciani (advisor John F. Raquet), PhD dissertation, Air Force Institute of Technology, Dept. of Electrical and Computer Engineering, 2016 (award date 2016-09-15; AFIT-ENG-DS-16-S-074, DTIC AD1017870). [record](https://scholar.afit.edu/etd/251) | [PDF](https://scholar.afit.edu/cgi/viewcontent.cgi?article=1250&context=etd) | code: none | Read: abstract only. The AFIT record page was read; the PDF on scholar.afit.edu, the DTIC copy and the core.ac.uk mirror all returned HTTP 403 to our fetcher. Everything below the abstract level is marked as not read.

## Problem
GPS alternatives tend to work only in some places or at some times. The crustal magnetic anomaly field is present everywhere, all the time, and cannot be jammed. The dissertation asks whether an aircraft can get absolute position by matching scalar magnetometer readings to an anomaly map while aiding an INS.

## Method
From the abstract:
- Navigation filter that aids an aircraft INS with scalar magnetic anomaly measurements.
- Sensor: optically pumped cesium (OPC) scalar magnetometers.
- Estimator: a marginalized particle filter (MPF) matching measurements against an anomaly map. (Our read of the generic MPF structure: particles over the nonlinear position states, Kalman updates for the remaining linear INS error states. How the dissertation splits the states was not read.)
- A simulation study over the continental United States to predict how accuracy varies with location and altitude.
- A method for a "self-building" magnetic anomaly model, to cope with places where no good map exists (a SLAM-like idea).
Not read: the state vector, measurement model, map interpolation and map-error handling, and the chapter structure.

## Data and sensors
- Real flight data at low altitude with a high-quality anomaly map (abstract). Aircraft, flight duration and map source: not read.
- OPC scalar magnetometers plus an INS.
- No dataset card exists for these flights. The later public flight data from the same research line is in [magnav-challenge-data](../dataset-cards/magnav-challenge-data.md) (Canciani is a co-author of the challenge paper).

## Headline results (as reported)
- Abstract: 13 m DRMS positioning accuracy with real flight data, at low altitude, with a high-quality anomaly map. Table/figure reference: not located (full text not read).
- Abstract: CONUS simulation predicts accuracy as a function of location and altitude. Numbers: not located.
- Self-building map: no result numbers in the abstract.

## Limitations
- Stated by author (abstract): limited availability of high-quality anomaly maps is the motivation for the self-building model; performance depends on location and altitude.
- Our read: 13 m DRMS is a best case (low altitude, high-quality survey map). Expect much worse at higher altitude where the anomaly signal is attenuated, and over magnetically flat terrain.
- Our read: the abstract does not say how the aircraft's own field was handled; check the full text before reusing the error budget.

## Code, weights, license
- No code released with the dissertation (none referenced on the AFIT record).
- The open implementation of this line of work is [MagNav.jl](../integration-cards/mit-ai-accelerator__magnav.jl.md), which ships an MPF (`src/mpf.jl`) next to the EKF. MagNav.jl `LICENSE.md`: public domain (17 U.S.C. 105) plus MIT-style text; GitHub reports NOASSERTION.
- Dissertation text: US government work posted open access on AFIT Scholar.

## Reproduction effort (estimate)
Estimate:
- The original flight data is not public as far as we found, so the 13 m DRMS number is not reproducible.
- A proxy is cheap: MagNav.jl `run_filt(..., :mpf)` on the public SGL Ottawa flights and maps, CPU only, half a day including Julia setup.
- The CONUS sensitivity study could be approximated with MagNav.jl `crlb(...)` over EMAG2 or NAMAD map tiles (both shipped as MagNav.jl constants), a day of work.

## What a hackathon team can take from it
- The architecture to copy: INS as the process model, scalar anomaly as the measurement, MPF to survive the multimodal likelihood of map matching. MagNav.jl has both MPF and EKF, so you can show why the particle filter matters.
- The 13 m DRMS figure is the headline to quote as "achievable with a good map at low altitude" - and the boundary of what a hackathon demo should claim.
- Self-building map idea: if the hackathon area has no survey map, consider a SLAM-style map built on revisits rather than claiming absolute fixes.
- Run a CRLB over the target area first; if the anomaly gradient is weak, MagNav is the wrong sensor for that region.
