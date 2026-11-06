# GNSS-denied navigation: products and companies

<!-- about: res:auterion-skynode-visual-navigation, res:shield-ai-hivemind, res:helsing-hx2-navigation, res:qctrl-ironstone-opal, res:sandboxaq-aqnav, res:xona-pulsar-leo-pnt, res:trustpoint-leo-pnt, res:iridium-pnt-stl-asic, res:honeywell-vision-aided-navigation, res:honeywell-hguide-o480, res:advanced-navigation-boreas, res:inertial-labs-vins, res:safran-versapnt, res:sbg-new-ellipse-firmware, res:vectornav-stl-aided-ins, res:spirent-gss7000-pntx, res:safran-skydel-gsg8, res:infinidome-gpsdome, res:twist-robotics-oscar, res:blue-arrow-visual-nav, res:theseus-visual-navigation-system, res:spleenlab-visionairy, res:uavos-navai, res:septentrio-aim-plus, res:novatel-gajt-710ml -->

What judges from industry already know. Every performance figure below is a **vendor claim**
or press report unless it says otherwise. Nothing here was tested by us. Sources were found via
web search on 2026-11-06; several vendor and GPS World pages block scripted fetches (HTTP 403),
so for those only the search snippet was read.

"Open alternatives" names repos in this index that attack the same problem. They are not
equivalent in grade, certification or maturity.

## Visual navigation (camera vs map, VIO)

| Vendor / product | What it does | Public claims (vendor/press) | Source | Open alternatives |
|---|---|---|---|---|
| Auterion - Skynode S, Auterion Visual Navigation | PX4-derived OS + mission computer; camera-based position source for jammed GNSS | Detects jamming/spoofing and drops GNSS (Jan 2024); used in Ukraine; named in DIU Artemis completion (Oct 2025). No accuracy numbers | [Defense Post](https://thedefensepost.com/2024/07/01/auterion-drone-bypass-jamming/), [Auterion Artemis](https://auterion.com/auterion-successfully-completes-artemis-program-to-deliver-long-range-deep-strike-drone/) | `repo:px4/px4-autopilot`, `repo:tiers/wildnav`, `repo:anyloc/anyloc` |
| Shield AI - Hivemind | Onboard autonomy with multi-sensor state estimation (visual, EO/IR, inertial) | CTO interview: operates GNSS- and comms-denied. No numbers | [Inside Unmanned Systems](https://insideunmannedsystems.com/the-hivemind-working-toward-resilient-intelligent-teams/) | `repo:rpng/open_vins`, `repo:nvidia-isaac/cuvslam`, `repo:borglab/gtsam` |
| Helsing - HX-2 (navigation aspect only) | Onboard map data + landmark recognition | Press: navigates without satellite nav. No accuracy data | [Shephard](https://shephardmedia.com/news/air-warfare/details-revealed-on-new-uas-munition-destined-for-ukraine/) | `repo:uav-avl/benchmark`, `repo:tiers/wildnav` |
| Honeywell - Vision Aided Navigation | Image-to-reference-map correlation, VIS or IR, paired with Honeywell INS; part of an "Alternative Navigation Suite" with MagNav and celestial | "GPS-like" on E170 and AW139 tests (press, no numbers) | [Honeywell](https://aerospace.honeywell.com/us/en/products-and-services/products/navigation-and-sensors/navigation-systems/vision-aided-navigation) | `repo:intellisensing/uav-visloc`, `repo:fabio-sim/lightglue-onnx` |
| Inertial Labs (VIAVI) - VINS, with Maxar Raptor | INS + camera matched to Maxar Precision3D 3D maps | ~35 m horizontal / ~5 m vertical without GNSS (vendor, June 2025) | [Inertial Labs](https://inertiallabs.com/inertial-labs-launches-visual-aided-ins-for-gps-compromised-paths/) | `repo:tiers/wildnav` + `repo:opendronemap/odm` for own maps |
| Spleenlab - VISIONAIRY | Modular perception: VIO, map relocalization, EO/IR and LiDAR SLAM; PX4/ROS integration | Used by Quantum Systems, Blueflite (press). No numbers | [Auterion/Spleenlab](https://auterion.com/safe-autonomous-drone-operations/) | `repo:rpng/open_vins`, `repo:anyloc/anyloc` |
| UAVOS - NavAI | Add-on vision navigation module | Product announcement only | [GPS World](https://www.gpsworld.com/uavos-introduces-navai-vision-based-navigation-module-for-gnss-degraded-uas-operations/) | as above |
| Theseus (US startup, YC) | Camera + IMU + pre-loaded satellite imagery => emits substitute GPS to the autopilot | Integration < 30 min; "six months from a hackathon to a SOCOM sale" (vendor) | [YC launch](https://www.ycombinator.com/launches/Ln6-theseus-gps-denied-navigation-for-drones), [Aviation Week](https://aviationweek.com/aerospace/emerging-technologies/how-trio-engineers-developed-gps-denied-drone-under-500) | `repo:tiers/wildnav`, `repo:thien94/vision_to_mavros`, `repo:osqzss/gps-sdr-sim` (sim only) |
| Twist Robotics - OSCAR (Ukraine) | Landmark recognition => map match => coordinates into autopilot | ">500,000 km flown" by platforms with the module (vendor, Jan 2026) | [Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2026/01/28/8018266) | `repo:uav-avl/benchmark`, `repo:intellisensing/uav-visloc` |
| Blue Arrow (Ukraine, Brave1) | Visual navigation for drones under jamming | Ministerial post, no technical data | [dev.ua](https://dev.ua/en/news/nemozhlyvo-zbyty-z-kursu-ukrainska-blue-arrow-stvoryla-navihatsiiu-dlia-droniv-bez-gps-1749633544) | as above |
| Vermeer (Ukraine) | Optical navigation module (already in index) | see record | `res:militarnyi-vermeer-optical-nav-2025` | as above |

Other Ukrainian names that public reporting attaches to this niche, not separately indexed:
Norda Dynamics, The Fourth Law, ZIR (named by Brave1), PG Robotics "Salamandra" module
([Razom](https://razomua.media/en/news/tekhnolohiyi/lucky-strike-21-ukrayinska-vidpovid-na-frontove-hlushinnya-gps)).
See also `docs/landscape/ua-ru-sources-overview.md` (separate owner).

**Anduril:** no named public navigation product found. Job postings describe vision-based
navigation, terrain contour/map matching, celestial and IMU/EO/IR/radar-altimeter fusion
([example posting](https://job-boards.greenhouse.io/andurilindustries/jobs/5159698007)). Not indexed.
**Palantir:** no navigation product found; skipped.

## Magnetic and quantum navigation

| Vendor / product | What it does | Public claims | Source | Open alternatives |
|---|---|---|---|---|
| Q-CTRL - Ironstone Opal | Quantum magnetometers + software matching crustal anomaly maps | RNP 0.3 in flight; "up to ~46x" (and elsewhere 50x / 94x) lower error than a velocity-aided INS; DO-160 qualified. All vendor | [Q-CTRL case study](https://q-ctrl.com/case-study/q-ctrl-delivering-quantum-advantage-to-airborne-systems), [Quantum Insider](https://thequantuminsider.com/2025/04/14/q-ctrl-overcomes-gps-denial-with-quantum-sensing-reports-quantum-advantage/) | `repo:mit-ai-accelerator/magnav.jl`, `repo:manasp21/magnav.py`, dataset `res:magnav-challenge-site` |
| SandboxAQ - AQNav | Magnetometers + learned compensation + public anomaly maps | RNP 2 over 150+ flight hours on a Baron 58; beat free INS on every >2 h flight; Lumberjack drone test (Sep 2026) published no error numbers | [SandboxAQ](https://www.sandboxaq.com/post/sandboxaq-and-acubed-achieve-remarkable-progress-in-magnetic-navigation), [Quantum Insider](https://thequantuminsider.com/2026/09/09/sandboxaq-tests-gps-free-navigation-on-northrop-grumman-drone/) | same |
| Honeywell - MagNav under DIU TQS | Quantum magnetometer MagNav | Embraer 170 flight without GPS (press) | [DIU TQS](https://www.diu.mil/latest/dius-transition-of-quantum-sensing-tqs-field-testing-to-begin-across-five) | same |
| Infleqtion / BAE / QinetiQ (UK) | Optical atomic clock + cold-atom sensor toward quantum INS | Flown May 2024 (government) | [gov.uk](https://www.gov.uk/government/news/un-jammable-quantum-tech-takes-flight-to-boost-uks-resilience-against-hostile-actors) | no open equivalent (hardware) |

## LEO PNT and signals of opportunity

| Vendor / product | What it does | Public claims | Source | Open alternatives |
|---|---|---|---|---|
| Xona Space Systems - Pulsar | Dedicated authenticated L-band PNT from LEO | Pulsar-0 launched mid-2025; FCC conditional approval; production sats / service 2026-2027 (dates conflict in press) | [SmallSat News](https://smallsatnews.com/2025/07/01/xona-space-systems-has-launched-their-pulsar-0-pnt-satellite/) | `repo:przemyslawpiekarski/starlink-leo-pnt`, `repo:voskavoj/dp`, `res:kassas-starlink-navigation` |
| TrustPoint | C-band LEO PNT | Third demo sat launched June 2025 (vendor) | [Business Wire](https://www.businesswire.com/news/home/20250625377848/en/TrustPoint-Launches-Third-Satellite-and-Successfully-Establishes-First-Contact) | same |
| Iridium - PNT/STL and PNT ASIC | High-power LEO time/location signal; chip for integrators | ASIC unveiled Oct 2025, commercially available Jul 2026; 8x8 mm (press) | [GPS World](https://www.gpsworld.com/iridium-pnt-asic-now-commercially-available-bringing-resilient-gnss-protection-to-devices-worldwide/) | `repo:voskavoj/dp` (Iridium Doppler) |
| VectorNav + NAL Research | STL-aided INS collaboration | Announcement Apr 2025, not a shipped feature | [VectorNav news](https://www.vectornav.com/about/news) | `repo:i2nav-whu/kf-gins` + a SoOP measurement |

## Inertial-centric resilient units

| Vendor / product | What it does | Public claims | Source | Open alternatives |
|---|---|---|---|---|
| Honeywell - HGuide o480 / i700 | Single-card INS with velocity aiding and Septentrio AIM+ receiver; i700 IMU with no-license-required export class | Vendor | [Honeywell PR](https://www.honeywellaerospace.com/us/en/about-us/press-release/2025/05/honeywell-new-single-card-resilient-navigation-system) | `repo:i2nav-whu/kf-gins`, `repo:nmayorov/pyins`, `repo:aceinna/gnss-ins-sim` |
| Advanced Navigation - Boreas + LVS | FOG INS + laser velocity sensor / wheel odometry | ~11.7 m over 65 km jammed (press); <0.1% of distance in mine trial | [Critical Comms](https://www.criticalcomms.com.au/content/transport/article/beating-the-jammers-australian-tech-gives-warfighters-precision-in-gps-blackouts-289326898) | same |
| Safran - VersaPNT, Geonyx | GNSS + IMU + oscillator holdover, jam/spoof detection, NTP/PTP | Vendor | [Safran](https://safran-navigation-timing.com/solution/defense/) | `repo:gitlab.com/gpsd/gpsd`, `repo:gnss-sdr/gnss-sdr` |
| SBG Systems - Ellipse firmware (2025) | Jam/spoof flags, reject/re-enable aiding sensors without filter reset | Vendor | [SBG](https://www.sbg-systems.com/news/introducing-new-ellipse/) | `repo:cra-ros-pkg/robot_localization` |

## Anti-jam antennas and hardened receivers

| Vendor / product | What it does | Public claims | Source | Open alternatives |
|---|---|---|---|---|
| NovAtel - GAJT | CRPA anti-jam antenna (already indexed) | see `res:novatel-gajt-710ml` | indexed | `repo:krakenrf/krakensdr_doa` (direction finding, not nulling) |
| Septentrio - AIM+ | Receiver-level interference mitigation (already indexed) | see `res:septentrio-aim-plus`, `res:septentrio-jammertest-results` | indexed | `repo:gnss-sdr/gnss-sdr`, `repo:algafix/osnma` |
| infiniDome - GPSdome 2 | Retrofit multi-element nulling module for small UAS | "CRPA-like without CRPA cost"; "400%" resilience in trials (vendor) | [GPS World](https://www.gpsworld.com/infinidome-releases-gpsdome-2-dual-band-anti-jamming-technology/) | none full; DIY multi-antenna SDR research only |

## Simulators and test tools

| Vendor / product | What it does | Source | Open alternatives |
|---|---|---|---|
| Spirent - GSS7000, PNT X | Multi-GNSS RF simulator with interference and spoofing scenarios, HIL | [Spirent](https://spirent.com/products/gss6300) | `repo:osqzss/gps-sdr-sim`, `repo:haiyang-wong/osnma-sdr-sim` (cabled / shielded use only, see `docs/export-control-and-ethics.md`) |
| Safran (ex-Orolia) - Skydel / GSG-8 | SDR/GPU simulation engine with jamming, spoofing, CRPA wavefront and LEO options; academic programme | [Safran](https://www.safran-group.com/products-services/skydel-gsg-8-advanced-gnss-simulator) | same |
| Jammertest (Norway) | Open live jamming/spoofing test event | `res:jammertest-norway` | `repo:felixott94/fraunhoferiis_jammertest2025` (data) |

## Reading the table

- Visual map-matching is the most crowded product category, with at least ten vendors and no
  public, comparable accuracy numbers. That gap is real: a neutral benchmark on an open dataset
  (`repo:uav-avl/benchmark`) is something vendors do not publish.
- MagNav vendors all quote RNP levels or INS multipliers, never raw error on a shared dataset.
  The public MagNav challenge data is the only common yardstick.
- LEO PNT is mostly pre-service. Hackathon teams cannot get Xona or TrustPoint signals; they can
  use Starlink/Iridium Doppler as signals of opportunity.
