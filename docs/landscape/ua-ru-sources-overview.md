# Ukrainian- and Russian-language sources: what they add

<!-- about: res:militarnyi-twist-robotics-oscar-visual-nav, res:militarnyi-harxon-crpa-32-element, res:militarnyi-brave1-crpa-test-lab, res:dou-how-reb-works-2025, res:dou-how-shahed-works-2025, res:dou-delta-architecture-interview-2024, res:dou-jammer-hackathon-2024, res:dou-jammer-hackathon-winners-2024, res:dou-lapko-urban-nav-interview-2025, res:devua-vyriy-beacon-navigation-2026, res:devua-24h-gps-free-drone-2024, res:mod-nastup-mashyn-hackathon-2024, res:militarnyi-edth-munich-2025, res:universe-borotba-za-koordynaty-2022, res:kma-boiko-optical-nav-thesis-2025, res:zp-baranov-vo-gps-denied-2024, res:khmnu-berezka-cps-uav-nav-under-ew-2026, res:kpi-spaskyi-uav-control-nav-under-ew-2025, res:lpnu-klushyn-combined-control-under-ew-2025, res:nangu-sporyshev-uav-control-in-jamming-2025, res:habr-gnss-interference-klimenko-2016, res:habr-gps-jammers-spoofing-2015, res:habr-mcu-gps-sdr-2024, res:habr-zed-f9p-rtk-2022, res:habr-rtklib-postprocessing-2014, res:habr-rope-ladder-return-home-2025, res:habr-bee-nav-translation-2026, res:habr-nav-without-gps-overview-2025, res:habr-monocular-quad-nav-2016, res:gosniias-optical-odometry-multicopter-2016, res:bntu-rulko-terrain-nav-deep-features-2025, res:preprints-lazareva-absolute-vi-nav, res:nstu-konovalov-route-planning-few-landmarks-2024, res:bsuir-saad-gps-antispoofing-2022, res:novayagazeta-gnss-interference-europe-2025, res:coex-clover-docs-optical-flow-ru, res:coex-clover-docs-aruco-map-ru, res:coex-copterhack-2023, repo:copterexpress/clover, repo:vohminv/rope-ladder-tracker, repo:t1gr20an06-k/hackathon-blind-flight, repo:solarwarlock/flyingblind_hakaton, repo:kurligin/safe-route, repo:sasha-lobov/orb_slam3_system_local, repo:danamarkova/graduate_work, repo:roosmax/diploma, repo:msemitkin/fit-gps-spoof-fix, repo:c-o-s-t-y-a/ardupilot_ua, repo:citec-spbu/smart-uav-return-gnss-station, repo:geoscan/geoscan_pioneer_max -->

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
