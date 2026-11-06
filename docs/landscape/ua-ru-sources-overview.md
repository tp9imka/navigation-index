# Ukrainian- and Russian-language sources: what they add

<!-- about: res:militarnyi-twist-robotics-oscar-visual-nav, res:militarnyi-harxon-crpa-32-element, res:militarnyi-brave1-crpa-test-lab, res:dou-how-reb-works-2025, res:dou-how-shahed-works-2025, res:dou-delta-architecture-interview-2024, res:dou-jammer-hackathon-2024, res:dou-jammer-hackathon-winners-2024, res:dou-lapko-urban-nav-interview-2025, res:devua-vyriy-beacon-navigation-2026, res:devua-24h-gps-free-drone-2024, res:mod-nastup-mashyn-hackathon-2024, res:militarnyi-edth-munich-2025, res:universe-borotba-za-koordynaty-2022, res:kma-boiko-optical-nav-thesis-2025, res:zp-baranov-vo-gps-denied-2024, res:khmnu-berezka-cps-uav-nav-under-ew-2026, res:kpi-spaskyi-uav-control-nav-under-ew-2025, res:lpnu-klushyn-combined-control-under-ew-2025, res:nangu-sporyshev-uav-control-in-jamming-2025, res:habr-gnss-interference-klimenko-2016, res:habr-gps-jammers-spoofing-2015, res:habr-mcu-gps-sdr-2024, res:habr-zed-f9p-rtk-2022, res:habr-rtklib-postprocessing-2014, res:habr-rope-ladder-return-home-2025, res:habr-bee-nav-translation-2026, res:habr-nav-without-gps-overview-2025, res:habr-monocular-quad-nav-2016, res:gosniias-optical-odometry-multicopter-2016, res:bntu-rulko-terrain-nav-deep-features-2025, res:preprints-lazareva-absolute-vi-nav, res:nstu-konovalov-route-planning-few-landmarks-2024, res:bsuir-saad-gps-antispoofing-2022, res:novayagazeta-gnss-interference-europe-2025, res:coex-clover-docs-optical-flow-ru, res:coex-clover-docs-aruco-map-ru, res:coex-copterhack-2023, repo:copterexpress/clover, repo:vohminv/rope-ladder-tracker, repo:t1gr20an06-k/hackathon-blind-flight, repo:solarwarlock/flyingblind_hakaton, repo:kurligin/safe-route, repo:sasha-lobov/orb_slam3_system_local, repo:danamarkova/graduate_work, repo:roosmax/diploma, repo:msemitkin/fit-gps-spoof-fix, repo:c-o-s-t-y-a/ardupilot_ua, repo:citec-spbu/smart-uav-return-gnss-station, repo:geoscan/geoscan_pioneer_max, res:iqarium-polet-vslepuyu-hackathon-2026, res:habr-kodoka-mvio-cpp-2026, res:nure-nextvision-hacklab-2026, res:ztu-kravchuk-uav-nav-without-gps-2025, res:kpi-hehelskyi-avrutov-uav-nav-complex-env-2025, res:lpnu-romaniv-uav-nav-telemetry-thesis-2025, res:ipu-mlsd-dolgov-autonomous-nav-problems-2025, res:itmo-litvinenko-underlying-surface-nav-2025, res:www1-mipt-fasetka-visual-nav-2026, res:spbran-konovalov-swarm-visual-nav-2025, res:www1-kazan-mesh-nav-grey-zone-2026, res:dou-deftech-forecasts-2026, res:militarnyi-lima-quant-anti-crpa-2026, res:militarnyi-kort-orion8-crpa-2026, res:militarnyi-kometa-crpa-components-2026, res:defence-express-sky-map-2026, res:mintsyfra-ai4uav-video-2024, res:leti-kozlovskikh-intro-visual-odometry-2021, res:gma2026-terion-aerial-survey-without-gnss, res:gma2024-artgeo-laser-scanning-without-gnss, res:lektorium-geoscan-autonomous-drones-course, res:bsu-pazhitnykh-uav-nav-diploma-slides, res:nure-tesliuk-vo-uncertain-env-2024, res:habr-mtf02-optical-flow-sensor-2025, res:vcru-zimkov-autonomous-flight-2025, res:habr-evocargo-localization-2026, res:habr-gps-track-spoofing-filtering-2026, res:habr-ruvds-gps-jamming-spoofing-civilians-2024, res:khpi-yeriomina-sotnikov-cens-decision-function-2016, res:drsp-mezentsev-cens-reference-image-2025, repo:rub1kub/where-are-we-barista, repo:danilka88/gag27062026, repo:drones-voronka/drones-backend, repo:eliseyavdeev/hackatoncodereal, repo:radagastttt/terrain-relative-navigation, repo:mikhraly/radioaltimeter_mcu, repo:sviridov-aleksandr/aerial-nav, repo:bolotnaya-glesenb/drone_navigation, repo:rusaub/mvio, repo:daudalbogachiev925/visual-odometry-vio-, repo:sasha-lobov/vinet_airsim_drone, repo:ledesha/gnss-ak_model, repo:v-nav/clover, repo:shamoleg/clover, repo:devmbs/crtclover, repo:korogodin/gnssrec, repo:korogodin/gnssrecbasics2020, repo:korogodin/glnephexercise, repo:daryamalafeeva/srns, repo:weae-g/note-outdoor, repo:foxfollow/stone-navigation-emulation, repo:drapegnik/bsu-science -->

Lane `ua-ru-sources`: 38 resources and 12 repos, all tagged `lang:uk` or `lang:ru`. Every URL resolved at collection time (Nov 2026). Every repo was checked with `gh api repos/<o>/<n>`. Summaries come from the pages, PDFs and READMEs. Nothing was installed or run. Vendor and author performance numbers are passed on as claims. Strike and terminal-guidance content was skipped. One hit about a strike-oriented navigation product was dropped for that reason.

## What this material teaches that English sources mostly don't

**1. EW is layered. GNSS is one target among several.** English material usually treats "GPS-denied" as the whole problem. The Ukrainian explainers split it into the control uplink, the video downlink and GNSS. They also say radio reconnaissance has to come before any jamming ([DOU on EW](../../catalog/resources/dou-how-reb-works-2025.md)). For a navigation team, that means losing GNSS usually comes together with losing the link. Most designs in this set assume both: [Vyriy beacons](../../catalog/resources/devua-vyriy-beacon-navigation-2026.md) work "without GPS or a link", and the [SPbU return-home project](../../catalog/repos/citec-spbu__smart-uav-return-gnss-station.md) states the same requirement.

**2. The anti-jam arms race is public and specific.** Ukrainian reporting gives CRPA element counts going from 4 to 16, 24 and 32 ([Harxon 32-element](../../catalog/resources/militarnyi-harxon-crpa-32-element.md), [Shahed breakdown](../../catalog/resources/dou-how-shahed-works-2025.md)). It also shows a state test lab for domestic anti-jam antennas ([Brave1 CRPA lab](../../catalog/resources/militarnyi-brave1-crpa-test-lab.md)). The defensive conclusion repeats across sources: once threats carry CRPA plus INS plus position-jump filters, GNSS jamming and spoofing lose much of their effect. Counter-UAS then moves to detection and interceptors.

**3. Visual positioning is a fielded product class.** [OSCAR](../../catalog/resources/militarnyi-twist-robotics-oscar-visual-nav.md) is described as feeding map-matched coordinates to the autopilot, with a vendor claim of about 20 m accuracy. That figure is a realistic bar for a hackathon VPS. The academic side shows the structure underneath: tile the GeoTIFF, pre-index keypoints, search only near the last fix, and define what to do when no fix comes ([KMA thesis](../../catalog/resources/kma-boiko-optical-nav-thesis-2025.md)). The thesis also gives a rare honest cost trade-off: SuperPoint+SuperGlue found more matches but ran about 25x slower than ORB.

**4. Route choice counts as a resilience lever.** Two Russian/Belarusian papers plan routes over feature-rich terrain so the visual fix doesn't drop out ([Rulko](../../catalog/resources/bntu-rulko-terrain-nav-deep-features-2025.md), [Konovalov](../../catalog/resources/nstu-konovalov-route-planning-few-landmarks-2024.md)). English VPS work rarely couples the planner to the matcher like this.

**5. Terrestrial substitutes for GNSS.** Ground beacon ranging is in use in Ukraine ([Vyriy](../../catalog/resources/devua-vyriy-beacon-navigation-2026.md)), with no numbers published. A Russian MIPT diploma gives an open, inspectable version: LoRa two-way ranging plus an INS error-state EKF and MSCKF ([Roosmax/Diploma](../../catalog/repos/roosmax__diploma.md)). Urban rangefinder-to-OpenStreetMap matching is a third, cheap variant ([DOU interview](../../catalog/resources/dou-lapko-urban-nav-interview-2025.md)).

**6. Practitioners modify ArduPilot instead of replacing it.** The KPI paper describes ArduPilot changes for link frequency agility alongside INS backup ([KPI](../../catalog/resources/kpi-spaskyi-uav-control-nav-under-ew-2025.md)). The Lviv paper adds deterministic switching between navigation sources and a mixed fiber/radio link ([Lviv Polytechnic](../../catalog/resources/lpnu-klushyn-combined-control-under-ew-2025.md)). A community Ukrainian translation of the ArduPilot docs exists ([ardupilot_ua](../../catalog/repos/c-o-s-t-y-a__ardupilot_ua.md)).

**7. Civilians see spoofing too.** Spoofing spills into everyday life, and the signatures are simple: tracks that teleport to a fixed far-away point, and impossible speeds. [fit-gps-spoof-fix](../../catalog/repos/msemitkin__fit-gps-spoof-fix.md) turns these into detection rules. [Novaya Gazeta Europe](../../catalog/resources/novayagazeta-gnss-interference-europe-2025.md) covers the same effects in European civil aviation.

**8. Hackathon problem statements are concrete.** Ukrainian state and cluster hackathons publish their tracks:
- [Jammer Hackathon](../../catalog/resources/dou-jammer-hackathon-2024.md): drone detection and tracking. Its [winners](../../catalog/resources/dou-jammer-hackathon-winners-2024.md) were mostly detection, direction finding and decision support.
- [Onslaught of Machines](../../catalog/resources/mod-nastup-mashyn-hackathon-2024.md): advanced navigation, resilient comms, coordination of unmanned systems.
- [EDTH Munich](../../catalog/resources/militarnyi-edth-munich-2025.md): underwater navigation, counter-UAS vision, radio reconnaissance. Brave1 says it wants components that integrate fast, not finished systems.

On the Russian side, the 2026 "Полёт вслепую" (Blind flight) hackathon posed TERCOM: DEM plus radar altimeter in NMEA. Two public solutions exist ([GORIZONT](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md), [FlyingBlind](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)). KosmoHackathon 2026 posed GNSS-shadow ground navigation ([safe-route](../../catalog/repos/kurligin__safe-route.md)). If the hackathon brief turns out to be TERCOM-like, these are the closest worked examples.

## Russian-language foundations worth knowing

- Receiver internals and interference: [Klimenko on Habr](../../catalog/resources/habr-gnss-interference-klimenko-2016.md), [MCU GPS SDR](../../catalog/resources/habr-mcu-gps-sdr-2024.md), [early spoofing overview](../../catalog/resources/habr-gps-jammers-spoofing-2015.md).
- Ground truth on a budget: [ZED-F9P RTK](../../catalog/resources/habr-zed-f9p-rtk-2022.md), [RTKLIB post-processing](../../catalog/resources/habr-rtklib-postprocessing-2014.md).
- Indoor GNSS-free stack, Russian docs first: [Clover](../../catalog/repos/copterexpress__clover.md) with its [optical flow](../../catalog/resources/coex-clover-docs-optical-flow-ru.md) and [ArUco map](../../catalog/resources/coex-clover-docs-aruco-map-ru.md) pages. This is the quickest "external pose => PX4 EKF" template here. Also the [CopterHack](../../catalog/resources/coex-copterhack-2023.md) contest.
- Return-home without GNSS: [rope-ladder](../../catalog/repos/vohminv__rope-ladder-tracker.md) ([Habr](../../catalog/resources/habr-rope-ladder-return-home-2025.md)), [Bee-Nav translation](../../catalog/resources/habr-bee-nav-translation-2026.md).
- Institutional research: [GosNIIAS optical odometry](../../catalog/resources/gosniias-optical-odometry-multicopter-2016.md), [absolute VI-nav preprint](../../catalog/resources/preprints-lazareva-absolute-vi-nav.md), [BSUIR anti-spoofing](../../catalog/resources/bsuir-saad-gps-antispoofing-2022.md) (metadata only).

## Ukrainian academic snapshot

These are short, applied papers. They usually set a target spec and report self-measured results on unpublished data:
- [Zaporizhzhia VO](../../catalog/resources/zp-baranov-vo-gps-denied-2024.md): targets +/-5 m at 10 Hz.
- [Khmelnytskyi](../../catalog/resources/khmnu-berezka-cps-uav-nav-under-ew-2026.md): compares LK, Farneback and RAFT optical flow.
- [National Guard Academy survey](../../catalog/resources/nangu-sporyshev-uav-control-in-jamming-2025.md).

Use them for problem framing and requirement numbers, not as benchmarks.

## Caveats

- Much of the Ukrainian material is news or interviews that pass on vendor claims. No independent test data was found for OSCAR, Vyriy or Osiris. Osiris was left out because only an English-language report was found.
- Habr blocked automated reads for one article (rope-ladder), so its author and date aren't verified.
- Most repos here are small, recent and low-star. They're reference implementations of a problem statement, not libraries.
- Telegram channels and YouTube talks weren't captured. Searches didn't surface stable, citable pages for them.

## Round 2 (lane `ua-ru-round2`)

30 resources and 22 repos, all tagged `lang:uk` or `lang:ru`. Same rules as round 1: every repo checked with `gh api`, every URL fetched or seen in a search result, vendor numbers passed on as claims, strike-oriented items skipped (Osiris on Defense Express and the Ruta navigation story were dropped for that reason).

### The "Полёт вслепую" TERCOM hackathon, filled in

The problem statement is the [Krasnodar hackathon page](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (26-28 June 2026, organiser ООО «ИННОКУБ»). It frames the case as civil cargo delivery to remote sites and does not name the sensors. The team READMEs do: a radar-altimeter log (NMEA-0183, later a TXT variant with start point, azimuth, speed and rate), a constant 1500 m MSL altitude and a Copernicus GLO-30 GeoTIFF, with a validation log handed out on the final day and bonus points for speed and noise robustness.

Public solutions now total six:
- [KROT](../../catalog/repos/rub1kub__where-are-we-barista.md): the clearest write-up of the organiser constraints, with C++ and Rust compute cores.
- [Gagarin](../../catalog/repos/danilka88__gag27062026.md): the most engineered. It has NCC+MAD search, ambiguity gates, an ESKF with dead-reckoning fallback, a pre-flight terrain-informativeness check and an onboard timing table. It reports its own failures (wrong-azimuth peaks, errors from about 50 m to 1.5 km by region).
- [drones-backend](../../catalog/repos/drones-voronka__drones-backend.md): a particle-filter TRN behind a full GCS stack.
- [HackatonCODEreal](../../catalog/repos/eliseyavdeev__hackatoncodereal.md): correlation heatmaps over speed and azimuth.
- The two round-1 repos (GORIZONT, FlyingBlind).

Separately, [terrain-relative-navigation](../../catalog/repos/radagastttt__terrain-relative-navigation.md) is a clean particle-filter TRN on Copernicus DEM, and it's the best teaching companion. One more repo, `jenyaqq/blindflight-terrainnav`, exists but holds only a README and licence, so it isn't indexed.

The common lesson: altimeter-only matching is ambiguous over flat or self-similar terrain. Heading is the weak variable. Teams that win credibility grade their own confidence instead of always emitting a fix. For theory, the Ukrainian "correlation-extremal navigation" literature is the same problem under its Soviet-era name: [decision function under perspective distortion](../../catalog/resources/khpi-yeriomina-sotnikov-cens-decision-function-2016.md) and [reference-image choice](../../catalog/resources/drsp-mezentsev-cens-reference-image-2025.md).

### Visual navigation: code and claims

- Open code: [aerial-nav](../../catalog/repos/sviridov-aleksandr__aerial-nav.md) (Siamese retrieval, then LightGlue registration), [MVIO](../../catalog/repos/rusaub__mvio.md) with its [Habr walkthrough](../../catalog/resources/habr-kodoka-mvio-cpp-2026.md), [learned VIO in AirSim](../../catalog/repos/sasha-lobov__vinet_airsim_drone.md), and a [ROS 2 + PX4 + RTAB-Map diploma stack](../../catalog/repos/bolotnaya-glesenb__drone_navigation.md).
- Russian institutional claims with no code: [MIPT Фасетка](../../catalog/resources/www1-mipt-fasetka-visual-nav-2026.md) (about 6 m at 1000 m, off-nadir to 45 degrees), [SPC RAS swarm VPS](../../catalog/resources/spbran-konovalov-swarm-visual-nav-2025.md), [ITMO keypoint matcher](../../catalog/resources/itmo-litvinenko-underlying-surface-nav-2025.md) (2 m, Gazebo only). There's also a [review from IPU RAS MLSD-2025](../../catalog/resources/ipu-mlsd-dolgov-autonomous-nav-problems-2025.md) that names onboard tile storage as a practical limit.
- Ukrainian practitioners in the [DOU 2026 forecast](../../catalog/resources/dou-deftech-forecasts-2026.md) disagree with each other. Some say there's still no compact optical system that fully replaces GNSS. Others say VSLAM + optic flow + inertial passed field tests. Read the vendor videos ([AI4UAV](../../catalog/resources/mintsyfra-ai4uav-video-2024.md)) with that in mind.
- Low-cost hover without GNSS: [MTF02 review](../../catalog/resources/habr-mtf02-optical-flow-sensor-2025.md) and [vc.ru optical flow + rangefinder build](../../catalog/resources/vcru-zimkov-autonomous-flight-2025.md).

### CRPA and defensive EW, round 2

These items continue the round-1 element-count thread:
- [KORT Orion 8](../../catalog/resources/militarnyi-kort-orion8-crpa-2026.md): a Ukrainian 8-channel CRPA integrated with Septentrio receivers.
- [Kometa teardown](../../catalog/resources/militarnyi-kometa-crpa-components-2026.md): a patch array plus an FPGA, 16 to 32 elements.
- [Lima Quant](../../catalog/resources/militarnyi-lima-quant-anti-crpa-2026.md): an interview claim that a CRPA can be defeated regardless of element count. Unverified.

On the C-UAS sensing side, [Sky Map](../../catalog/resources/defence-express-sky-map-2026.md) documents the low-cost acoustic-network + fusion pattern. The [NextVision HackLab](../../catalog/resources/nure-nextvision-hacklab-2026.md) brief is a ready-made detection/tracking problem statement.

### Spoofing seen from the ground

- [Telematics filter rules](../../catalog/resources/habr-gps-track-spoofing-filtering-2026.md): reachability envelopes, frozen-series detection, and an odometer-vs-GPS path ratio with hysteresis.
- [Stone Nav](../../catalog/repos/foxfollow__stone-navigation-emulation.md): route-constrained dead reckoning with user landmark resets.
- [Evocargo](../../catalog/resources/habr-evocargo-localization-2026.md): localization integrity on autonomous trucks, including truck jammers near toll sites.

### Academic and teaching material

- Ukrainian 2024-2025 surveys: [Zhytomyr Polytechnic](../../catalog/resources/ztu-kravchuk-uav-nav-without-gps-2025.md), [KPI gyroscopic systems](../../catalog/resources/kpi-hehelskyi-avrutov-uav-nav-complex-env-2025.md), [Lviv Polytechnic thesis with simulated jamming](../../catalog/resources/lpnu-romaniv-uav-nav-telemetry-thesis-2025.md), [NURE VO](../../catalog/resources/nure-tesliuk-vo-uncertain-env-2024.md). These are reviews and student work with self-reported results.
- Russian GNSS teaching code from MPEI: [receiver handbook](../../catalog/repos/korogodin__gnssrec.md), [course labs](../../catalog/repos/korogodin__gnssrecbasics2020.md) and [GLONASS ephemeris](../../catalog/repos/korogodin__glnephexercise.md).
- Free courses and talks: [Lektorium/Geoscan course](../../catalog/resources/lektorium-geoscan-autonomous-drones-course.md), [LETI VO seminar](../../catalog/resources/leti-kozlovskikh-intro-visual-odometry-2021.md).

### Gaps after round 2

- **Brave1 hackathon winners on navigation:** none found. Public Brave1 results are about EW, detection and AI guidance trials, and the guidance trials are out of scope.
- **KhAI and NAU theses on GNSS-denied navigation:** none surfaced through search. Their repositories need direct browsing.
- **CopterHack 2024-2025:** the pages aren't in the Clover docs repo, and the 2024 URL now 404s. Only the 2022 V-NAV and 2023 TPU_2 / radio-beacon entries could be traced.
- **YouTube conference talks:** summaries rely on the video descriptions. No transcripts were read.
- **Defense Express:** its navigation coverage is mostly about strike systems, so only Sky Map was kept.
