# Landscape: what judges already know

<!-- about: res:auterion-skynode-visual-navigation, res:theseus-visual-navigation-system, res:twist-robotics-oscar, res:qctrl-ironstone-opal, res:sandboxaq-aqnav, res:xona-pulsar-leo-pnt, res:iridium-pnt-stl-asic, res:honeywell-vision-aided-navigation, res:inertial-labs-vins, res:infinidome-gpsdome, res:uk-dasa-emp-pnt-problem-statement-2024, res:eudis-defence-hackathon-2026, res:brave-nato-unite-2026, res:diu-tqs-program -->

Commercial products, funded programmes and 2025-2026 trends in GNSS-denied navigation, so a
hackathon team can place its idea against what is already sold or funded.

| File | Contents |
|---|---|
| [gnss-denied-nav-products.md](gnss-denied-nav-products.md) | ~30 vendors by category: visual, magnetic/quantum, LEO PNT, inertial, anti-jam, simulators. Vendor claims labelled, open alternatives from this index |
| [programs-and-challenges.md](programs-and-challenges.md) | DARPA, DIU, AFRL/MIT, NATO DIANA, EDF, ESA NAVISP, UK DASA, Brave1, EUDIS and other hackathons, with their problem statements |
| [trends-2025-2026.md](trends-2025-2026.md) | Fiber-optic drones, commodity visual nav, LEO PNT launches, quantum flight tests, OSNMA service, national backups |
| ua-ru-sources-overview.md | Ukrainian and Russian-language sources (separate owner) |

Index records: `data/resources/landscape.json` (kinds `product`, `company`, `program`, tag `landscape`).
Query: `python3 tools/query.py search "landscape magnetic"`.

Caveats: found by web search on 2026-11-06. Most performance numbers are vendor claims that no
independent party has published. Some vendor pages block scripted fetches, so for those only
search snippets were read. Nothing here was run or tested.

## What is commoditized

Judges from industry, funders or the military will treat these as solved or for sale:

1. **Camera-to-satellite-map position fix for small drones.** At least ten vendors (Auterion,
   Theseus, Twist Robotics, Vermeer, Blue Arrow, Spleenlab, UAVOS, Honeywell, Inertial Labs/Maxar,
   Helsing). One of them (Theseus) began at a 2024 hackathon. A plain "match the frame to Google
   satellite tiles" demo is the default entry, not a differentiator.
2. **VIO / visual odometry for drift reduction.** Open source (`repo:rpng/open_vins`,
   `repo:nvidia-isaac/cuvslam`) and built into PX4/ArduPilot integration paths.
3. **GNSS + tactical IMU + velocity aid in one unit**, with jamming/spoofing flags (Honeywell
   HGuide o480, SBG Ellipse firmware, Safran VersaPNT, Advanced Navigation Boreas).
4. **Receiver-level anti-jam and CRPA modules** (NovAtel GAJT, Septentrio AIM+, infiniDome).
5. **Lab GNSS jamming/spoofing simulation** (Spirent, Safran Skydel).
6. **Authenticated nav data**: Galileo OSNMA is a free operational service since July 2025.

## Where a hackathon team can still add something

Ordered by how reachable they are in 24-48 h with the open tools in this index.

1. **Integrity, not accuracy.** No vendor publishes how its visual or magnetic fix fails. A
   monitor that flags a wrong visual match or a spoofed GNSS fix before the filter accepts it,
   with a measured false-alarm/missed-detection rate on recorded data, matches the DASA ask
   ("AI for spoofing detection and multi-source fusion") and is rare in demos.
   Building blocks: `repo:gnss-sdr/gnss-sdr`, `repo:algafix/osnma`, `repo:s7am1na/gnss-spoofing-dataset`,
   `repo:cra-ros-pkg/robot_localization`, `repo:borglab/gtsam`.
2. **Honest numbers on open data.** Vendors quote RNP levels and "x times better than INS".
   Showing error vs distance on a public benchmark (`repo:uav-avl/benchmark`,
   `res:magnav-challenge-site`, `repo:hmf21/aerialvl`) with failure cases is something judges
   cannot get from a brochure.
3. **The hard conditions vendors skip in marketing:** night/thermal imagery
   (`repo:arplaboratory/satellite-thermal-geo-localization`), low altitude, snow/season change,
   water and featureless fields, map staleness. Pick one and measure it.
4. **Fusion of cheap heterogeneous sources** under a small-UAS budget: visual fix + baro + IMU +
   Starlink/Iridium Doppler or radio beacons, with a switch-over policy. Every problem statement
   (DASA, EDF 2024, Brave1/NATO) says "multi-sensor", but most products sell one modality.
5. **Drop-in integration path.** Feed the estimate to PX4/ArduPilot as an external position or as
   a substitute GNSS message (`repo:thien94/vision_to_mavros`, `repo:mavlink/mavros`) and show it
   in SITL. Funders ask for "plug-in replacement for COTS"; a working SITL loop beats slides.
6. **Detect-and-warn for others.** A crowd or fleet-level GNSS interference map from drone or
   phone logs (`repo:univaasadigieco/vaara`, `repo:felixott94/fraunhoferiis_jammertest2025`) fits
   the UK GNSS-warning and Jammertest themes and needs no special hardware.

## What to avoid

- Claiming accuracy you did not measure; judges know vendor numbers are unverified and will
  ask how you measured yours.
- Anything that depends on quantum sensors, FOG IMUs or LEO PNT signals you cannot access. Use
  the software problem with public data instead.
- Live GNSS signal transmission. Simulation goes into a cable or shielded box only; see
  `docs/export-control-and-ethics.md`.
- Pitches framed around targeting or terminal guidance: out of scope for this index and for
  most dual-use funding lines (Brave1/NATO joint funding is non-lethal only).
