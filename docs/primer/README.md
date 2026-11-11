# Navigation primer

Use this when a navigation term, sensor or failure mode is new to you and you need the plain
explanation plus the repos to build with. It does not tell you what to build: for a full
brief start at the decoder's [full-brief routing table](../problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages),
and for the close-area A to B task at [close-area-nav](../research/close-area-nav/README.md).

A field guide to navigation and PNT (positioning, navigation and timing) for software
engineers joining a defense-flavoured hackathon. Each chapter explains one cluster of
the hub in plain language, names the ways it fails under electronic warfare (EW), and
ends with two lists:

- **Learn it** - resources from this index in reading order, intro => advanced.
- **Build with it** - the repos from this index you are most likely to ship with.

Every link inside the chapters points at a generated catalog page (`../../catalog/...`),
which in turn links to the upstream source. Numbers (accuracy, drift, cost) appear only where a cited
source states them; otherwise the chapter says what drives the error instead of
inventing a figure.

## Chapters

| Page | Use it when | You get |
|---|---|---|
| 1. [PNT fundamentals](01-pnt-fundamentals.md) | you do anything here | Frames (the top source of hackathon bugs), uncertainty, consistency and integrity, assured PNT vocabulary, timing |
| 2. [GNSS and its threats](02-gnss-and-threats.md) | you parse receiver data, detect jamming or spoofing, use RTK/PPP or OSNMA | How GNSS works, precision modes, threats, safe handling of interference data |
| 3. [Inertial navigation and sensor fusion](03-inertial-and-fusion.md) | you write or tune a Kalman filter or factor graph, or fuse GNSS with an IMU | INS, the Kalman filter in five lines, GNSS/INS coupling, filters vs factor graphs, learned inertial odometry |
| 4. [Vision, LiDAR and radar odometry](04-vision-lidar-radar-odometry.md) | you navigate relative to the surroundings (VIO, SLAM, LiDAR, radar) | Odometry vs SLAM vs relocalization, VIO, LiDAR and radar odometry, place recognition and matching |
| 5. [Absolute alternative PNT](05-absolute-alt-pnt.md) | you need an absolute fix without GNSS | Map matching: image-to-map, terrain, magnetic, celestial, signals of opportunity and radio ranging |
| 6. [Autopilots and C2](06-autopilots-and-c2.md) | you feed a position into PX4/ArduPilot, talk MAVLink or push tracks to TAK | The two open autopilots, getting your position in, source switching, C2 links, CoT/TAK, counter-UAS detection |
| 7. [Maps, geodesy and planning](07-maps-geodesy-planning.md) | you convert coordinates, load DEMs and imagery, or plan paths or missions | Geodesy you need, free map data, display, planning, multi-agent |
| 8. [Maritime, underwater and ground](08-maritime-underwater-ground.md) | you work off the drone: ships, AIS, ROVs, DVL, ground robots, dismounted users | One section per domain, including dismounted and indoor |
| 9. [Evaluation and datasets](09-evaluation-and-datasets.md) | you must prove your system works | Metrics, datasets by scenario, simulators, resilience test design, what competitions reward |

Every chapter also has a "Failure modes under EW" section and ends with "Learn it" and "Build
with it".

## Suggested order

- **Close-area A=>B team (likely first-day task):** 1 => 4 => 6 => 7 => 9, then
  [close-area-nav](../research/close-area-nav/README.md) and
  [samples/close-area-arena](../../samples/close-area-arena/README.md).
- **Air-domain alt-nav team (long range):** 1 => 3 => 2 => 5 => 4 => 6 => 9.
- **Interference-monitoring / OSINT team:** 1 => 2 => 7 => 6 (TAK part) => 9.
- **Ground or maritime robot team:** 1 => 3 => 4 => 8 => 7 => 9.

## Read alongside

- [Learning paths](../learning-paths.md) - 1-day, 1-week and 1-month study tracks.
- [Export control and ethics](../export-control-and-ethics.md) - read before you touch GNSS
  signal generation, RF transmission, flight tests or defense end uses.
- [INDEX.md](../../INDEX.md) - concept tree and high-fit repos.
- `python3 tools/query.py concept concept:<id>` - full listing for any concept.

## Scope

The hub covers navigation, localization, PNT resilience, autonomy, situational awareness,
defensive EW and counter-UAS detection. Weapon terminal guidance, targeting and offensive
payloads are out of scope, and this primer does not cover them.
