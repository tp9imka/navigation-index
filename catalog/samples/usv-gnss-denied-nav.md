# Sample: USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund

`sample:usv-gnss-denied-nav` - code and walkthrough in [samples/usv-gnss-denied-nav](../../samples/usv-gnss-denied-nav/)

A simulated USV runs a 19.6 km transit over real geography (Lillgrund => Drogden channel => Copenhagen approach) built from OpenStreetMap coastline, Oresund bridge, wind turbines and seamarks, with 75 min of real Danish Maritime Authority AIS traffic as radar targets. Compass + bottom-track speed log dead reckoning, a 720-azimuth marine radar ray-cast with clutter, incidence-dependent detection and ship occlusion, likelihood-field + point-to-line ICP matching of returns to the chart (with degenerate, ambiguous and few-return checks), a 4-state EKF that also calibrates compass bias from matched heading, and a monitor (solution separation + 30 s GNSS-vs-radar/DR mean test, exclusion only when the GNSS-free filter has recent radar fixes). Over 5 seeds a slow GNSS drag (0.003 m/s^2 to 0.6 m/s) is excluded 125-131 s after onset near the coast at a 23-26 m offset (max error 10-25 m vs 1391-1395 m for GNSS+DR and for a single filter with radar but only innovation gates); onset in open water is caught at 202-250 s (max 71-102 m); a 1.5 km radar range makes it fail (175-1024 m). Zero false alarms in 25 runs. Writes navdash/1 JSONL for templates/demo-dashboard and own-ship CoT via the mavlink-to-tak-cot builder; README maps the pieces onto OpenCPN/radar_pi, Signal K, colav-simulator and MOOS-IvP.

**Verification:** Ran 2026-11-06 on macOS with python 3.14.7 stdlib: 15 unit tests pass and three negative controls (detection off, degeneracy check off, isolation rule off) each make the targeted test fail; run.py for 5 scenarios x 4 configurations x 5 seeds, numbers in the README come from example_output/summary_5seeds.*; plot.py with matplotlib 3.11.2 (python 3.13.15); example_output/spoof-coastal loaded in templates/demo-dashboard in headless Chrome (metrics panel read). Fixtures built from Overpass (OSM) and a locally downloaded DMA AIS file for 2026-10-20. Not done: real radar data, S-57 ENC input, CoT in a TAK client, running any of the linked maritime stacks. Sensors, radar and attacks are simulated; the simulated world equals the OSM chart apart from buoy offsets, so radar fix errors are optimistic.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [dma-ais](../../docs/dataset-cards/dma-ais.md) (dataset-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Radar navigation and odometry](../../catalog/concepts/radar-nav.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `usv`, `marine-radar`, `radar-chart-matching`, `icp`, `likelihood-field`, `dead-reckoning`, `dvl`, `compass-bias`, `spoofing`, `jamming`, `solution-separation`, `fde`, `integrity`, `openstreetmap`, `overpass`, `danish-maritime-authority`, `ais`, `oresund`, `copenhagen`, `navdash`, `cot`, `tak`, `stdlib`

## Related

- explains: [OpenCPN](../../catalog/repos/opencpn__opencpn.md)
- explains: [OpenCPN radar_pi](../../catalog/repos/opencpn-radar-pi__radar_pi.md)
- explains: [Signal K Server](../../catalog/repos/signalk__signalk-server.md)
- explains: [signalk-to-nmea0183](../../catalog/repos/signalk__signalk-to-nmea0183.md)
- explains: [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md)
- explains: [MOOS-IvP](../../catalog/repos/moos-ivp__moos-ivp.md)
- explains: [CFEAR Radarodometry](../../catalog/repos/dan11003__cfear_radarodometry.md)
- explains: [Pohang Canal Dataset: A Multimodal Maritime Dataset for Autonomous Navigation in Restricted Waters](../../catalog/resources/pohang-canal-dataset-2023.md)
- explains: [R-Mode Baltic and R-Mode Baltic 2](../../catalog/resources/dlr-r-mode-baltic.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Danish Maritime Authority historical AIS data](../../catalog/resources/dma-historical-ais.md) (dataset_for)
- [OpenStreetMap data via the Overpass API](../../catalog/resources/openstreetmap-overpass-api.md) (dataset_for)

_Indexed by lane(s): samples_
