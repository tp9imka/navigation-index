# 5. Absolute alternative PNT

After this chapter you can explain the five main ways to get an absolute position without
GNSS - image-to-map matching, terrain matching, magnetic anomaly matching, celestial fixes
and signals of opportunity - pick the one that fits your platform, and feed its output into
a filter as a measurement with honest uncertainty.

Prev: [Vision, LiDAR and radar odometry](04-vision-lidar-radar-odometry.md) | Next: [Autopilots and C2](06-autopilots-and-c2.md) | [Primer index](README.md)

## The common pattern: map matching

Four of the five techniques share one structure:

```
1. A reference map M(position) of something observable (imagery, height, magnetic field, star catalogue).
2. A sensor reading z, plus a predicted position from dead reckoning (chapter 3/4).
3. Search positions near the prediction for the best match of z to M.
4. Report the match as a position measurement WITH a covariance, or reject it.
```

Because maps have repeated patterns, the match likelihood is often multi-modal, so a
**particle filter** or a gated multi-hypothesis search is the usual estimator. Uncertainty
matters as much as the fix: work such as UASTHN adds uncertainty estimation precisely so a
navigation filter can weight or reject visual fixes
([UASTHN](../../catalog/resources/uasthn-uncertainty-thermal-2025.md)).

## Visual geo-localization (image-to-map)

Match a downward or oblique camera frame against georeferenced satellite or orthophoto
tiles. This is the technique most visible in current conflict reporting: Ukrainian drone
developers use onboard optical navigation to keep flying after links and GNSS are jammed
([IEEE Spectrum](../../catalog/resources/ieee-spectrum-ukraine-drones-ew-2025.md),
[IISS dossier](../../catalog/resources/iiss-uavs-isr-deterrence-war-2026.md)). Vendor
performance claims there are not independently tested
([Militarnyi report](../../catalog/resources/militarnyi-vermeer-optical-nav-2025.md)).

Pipeline (retrieve-then-match, from chapter 4):

1. **Retrieve** candidate tiles near the predicted position with a global descriptor
   ([AnyLoc](../../catalog/resources/anyloc-universal-vpr-2023.md),
   [Sample4Geo](../../catalog/resources/sample4geo-2023.md) for cross-view).
2. **Match** keypoints between frame and tile ([LightGlue](../../catalog/resources/lightglue-2023.md),
   [RoMa](../../catalog/resources/roma-dense-matching-2023.md) for cross-season,
   [MASt3R](../../catalog/resources/mast3r-2024.md) for extreme viewpoint change).
3. **Estimate** a homography or PnP pose, convert tile pixels to lat/lon.
4. **Gate** against the filter prediction and inlier count.

What the papers report about failure: WildNav's failures cluster over low-texture and
changed terrain ([paper](../../catalog/resources/wildnav-gnss-free-uav-localization-2022.md));
low-altitude oblique views are much harder than nadir
([AnyVisLoc benchmark](../../catalog/resources/anyvisloc-uav-localization-benchmark-2025.md));
altitude changes strongly affect retrieval accuracy
([SUES-200](../../catalog/resources/sues-200-benchmark-2022.md)). Night operation is possible
with thermal-to-RGB matching ([thermal geo-localization](../../catalog/resources/thermal-geolocalization-iros-2023.md),
[STHN](../../catalog/resources/sthn-thermal-homography-2024.md)).

Reference imagery: Sentinel-2 via public STAC APIs needs no key
([STAC spec](../../catalog/resources/stac-spec.md)); see chapter 7.

## Terrain-relative navigation

Measure terrain height under the vehicle (radar or laser altimeter minus barometric
altitude), collect a profile along the track, and correlate it with a DEM. This is the
TERCOM idea. It works over rough terrain and fails over flat ground and water, where every
position looks the same. A free global DEM is the 30 m Copernicus GLO-30 on AWS
([Copernicus DEM](../../catalog/resources/copernicus-dem-aws.md)); remember the geoid vs
ellipsoid height difference ([GeographicLib](../../catalog/resources/geographiclib-docs.md)).
Vision-based terrain-aided localization for aircraft is the camera variant
([Navon webinar](../../catalog/resources/ion-webinar-navon.md)).

## Magnetic anomaly navigation (MagNav)

The Earth's crust has a spatially varying magnetic anomaly field, mapped by survey flights.
A magnetometer reading compared against the anomaly map gives position. It is passive and
cannot be jammed by RF. The hard part is not matching but **compensation**: the aircraft's
own magnetic field swamps the signal. The scalar reading mixes core field, crustal anomaly
and platform field; Tolles-Lawson is the classical compensation baseline, and physics plus
ML beat either alone in the AFRL/MIT challenge
([challenge paper](../../catalog/resources/afrl-magnav-challenge-2020.md),
[challenge site](../../catalog/resources/magnav-challenge-site.md)). The method's flight-test
basis is AFIT's dissertation work
([Canciani 2016](../../catalog/resources/canciani-afit-magnetic-anomaly-dissertation-2016.md)).
A 2025 field-trial paper reports quantum-magnetometer MagNav outperforming a strategic-grade
INS in airborne and ground trials
([Q-CTRL 2025](../../catalog/resources/qctrl-quantum-assured-magnav-2025.md)); DARPA's RoQS
targets platform noise as the barrier
([RoQS](../../catalog/resources/darpa-roqs-2024.md)). Map coverage and resolution limit where
it works.

## Celestial navigation

A camera that sees stars plus a catalogue gives attitude (a star tracker solves
"lost-in-space" identification, [tetra3 docs](../../catalog/resources/tetra3-docs.md)).
Position additionally needs an accurate local vertical and time. Daytime and low-altitude
use is limited by sky brightness and clouds. Sky polarization offers a heading reference
under clear sky ([OpenSky polarization simulator](../../catalog/resources/opensky-sky-polarization-simulator-2024.md)).
GAO lists celestial among DoD's alternative PNT families
([GAO-21-320SP](../../catalog/resources/gao-21-320sp-gps-alternatives.md)).

## Signals of opportunity (SoOP) and radio ranging

Use signals never designed for navigation: LEO broadband constellations, cellular LTE/5G,
broadcast, or your own beacons.

- **LEO Doppler.** A LEO satellite moves fast, so its Doppler shift encodes geometry, as the
  old TRANSIT system used. With many satellites in view, Doppler-only positioning is
  geometrically viable ([Psiaki, TRANSIT on steroids](../../catalog/resources/psiaki-transit-on-steroids-2021.md)).

  ```
  f_D,i = -(1/lambda) * d/dt || r_sat_i(t) - r_user || + clock drift term
  ```
- **Starlink without cooperation.** Researchers track Starlink downlinks without operator
  support ([Kassas first results](../../catalog/resources/kassas-starlink-first-results-2022.md)),
  partly by reverse-engineering the OFDM signal structure
  ([Humphreys 2023](../../catalog/resources/humphreys-2023-starlink-signal-structure.md)).
  Carrier-phase positioning results are reported at metre level with known altitude
  ([Kassas 2022](../../catalog/resources/kassas-2022-starlink-carrier-phase.md)). Ephemeris
  error is a dominant limitation.
- **Cellular** signals are viable in cities ([LTE receiver webinar](../../catalog/resources/ion-webinar-shamaei-kassas.md)).
- **Terrestrial backups**: eLoran fails differently from GNSS, which is its value
  ([DOT demonstration](../../catalog/resources/dot-complementary-pnt-report-2021.md)); R-Mode
  in the jammed Baltic ([39C3 talk](../../catalog/resources/39c3-baltic-jammer-r-mode.md)).
- **Own beacons**: UWB anchors indoors ([Loco Positioning](../../catalog/resources/bitcraze-loco-positioning.md),
  where anchor geometry dominates accuracy) or LoRa ranging for GPS-denied return-to-home
  ([Hyams](../../catalog/resources/hyams-gps-denied-rth-lora-ranging.md)).

## Failure modes under EW

| Technique | Jam/spoof exposure | Main physical failure |
|-----------|-------------------|-----------------------|
| Visual geo-localization | Passive, no RF | Low texture, changed terrain, clouds, night (without thermal), oblique views, stale maps |
| Terrain matching | Altimeter is an emitter | Flat terrain and water; DEM resolution and datum errors |
| MagNav | Passive | Platform interference; map coverage |
| Celestial | Passive | Cloud, daylight, needs accurate vertical and time |
| SoOP / beacons | RF: can be jammed or spoofed like any radio; receivers do not authenticate | Unknown signal structure, ephemeris and clock errors, geometry |

Any absolute fix can be wrong. Treat each as a measurement with a covariance, gate it, and
keep dead reckoning running underneath.

## Learn it

1. [GAO-21-320SP](../../catalog/resources/gao-21-320sp-gps-alternatives.md) - the families and their maturity.
2. [Review on deep learning for UAV absolute visual localization](../../catalog/resources/couturier-review-dl-uav-avl-2024.md) - map of methods and datasets.
3. [WildNav paper](../../catalog/resources/wildnav-gnss-free-uav-localization-2022.md) - a workable visual-GPS baseline.
4. [Photogrammetry I and II (Stachniss)](../../catalog/resources/stachniss-photogrammetry-i-ii.md) - geometry behind image-to-map registration.
5. [hloc coarse-to-fine](../../catalog/resources/hloc-coarse-to-fine-2018.md), then [AnyVisLoc benchmark](../../catalog/resources/anyvisloc-uav-localization-benchmark-2025.md).
6. [MagNav.jl docs](../../catalog/resources/magnav-jl-docs.md) and the [MagNav challenge paper](../../catalog/resources/afrl-magnav-challenge-2020.md).
7. [Survey on LEO SoOP positioning](../../catalog/resources/leo-soop-positioning-survey-2025.md), then [Kassas GRASP seminar](../../catalog/resources/kassas-ad-astra-leo-grasp-2024.md) and [ION webinar: Unveiling Starlink for PNT](../../catalog/resources/ion-webinar-kozhaya.md).
8. [tetra3 docs](../../catalog/resources/tetra3-docs.md) for star tracking.
9. [Canciani dissertation](../../catalog/resources/canciani-afit-magnetic-anomaly-dissertation-2016.md) and [Psiaki TRANSIT on steroids](../../catalog/resources/psiaki-transit-on-steroids-2021.md) for depth.

## Build with it

- [WildNav](../../catalog/repos/tiers__wildnav.md) and its cleaner reimplementation [visual_localization](../../catalog/repos/terbouchehacene__visual_localization.md) - drone frame to satellite tile.
- [GeoAnchor](../../catalog/repos/yusufgunel__geoanchor.md) - VO plus map matching in a particle filter (young project; blueprint value).
- [LightGlue](../../catalog/repos/cvg__lightglue.md), [vismatch](../../catalog/repos/gmberton__vismatch.md), [AnyLoc](../../catalog/repos/anyloc__anyloc.md) - matchers and retrieval.
- [UAV-VisLoc](../../catalog/repos/intellisensing__uav-visloc.md) and [University-1652 baseline](../../catalog/repos/layumi__university1652-baseline.md) - data and baselines.
- [pystac-client](../../catalog/repos/stac-utils__pystac-client.md), [rasterio](../../catalog/repos/rasterio__rasterio.md), [elevation](../../catalog/repos/bopen__elevation.md) - imagery and DEM access.
- [tercom_nav](../../catalog/repos/mzahana__tercom_nav.md) and [python-tercom](../../catalog/repos/alti3__python-tercom.md) - terrain contour matching.
- [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md), [AFIT example data](../../catalog/repos/afit-eeng-magnav__example-data.md), [MAMMAL](../../catalog/repos/powerbroker2__mammal.md) - magnetic navigation.
- [tetra3](../../catalog/repos/esa__tetra3.md) / [cedar-solve](../../catalog/repos/smroid__cedar-solve.md) and [NASA COTS Star Tracker](../../catalog/repos/nasa__cots-star-tracker.md) - star trackers.
- [UT Starlink signal simulator](../../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md), [LEO-SPINE](../../catalog/repos/xyangll__leospine.md), [Starlink LEO-PNT](../../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md) (unverified claims) - LEO SoOP.
- [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md) and [UTIL UWB dataset tools](../../catalog/repos/williamwenda__uwb_tdoa_dataset.md) - UWB ranging.

Samples in this hub: [`samples/visual-geolocalization-lightglue`](../../samples/visual-geolocalization-lightglue/),
[`samples/terrain-relative-nav-pf`](../../samples/terrain-relative-nav-pf/),
[`samples/magnav-quickstart`](../../samples/magnav-quickstart/).

Related concepts: [visual geo-localization](../../catalog/concepts/visual-geolocalization.md),
[terrain navigation](../../catalog/concepts/terrain-nav.md), [magnetic navigation](../../catalog/concepts/magnetic-nav.md),
[celestial navigation](../../catalog/concepts/celestial-nav.md), [signals of opportunity](../../catalog/concepts/signals-of-opportunity.md),
[RF localization](../../catalog/concepts/rf-localization.md).
