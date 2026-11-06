# Navigation primer

A field guide to navigation and PNT (positioning, navigation and timing) for software
engineers joining a defense-flavoured hackathon. Each chapter explains one cluster of
the hub in plain language, names the ways it fails under electronic warfare (EW), and
ends with two lists:

- **Learn it** - resources from this index in reading order, intro => advanced.
- **Build with it** - the repos from this index you are most likely to ship with.

Every link points at a generated catalog page (`../../catalog/...`), which in turn links
to the upstream source. Numbers (accuracy, drift, cost) appear only where a cited
source states them; otherwise the chapter says what drives the error instead of
inventing a figure.

## Chapters

| # | Chapter | Read it if you are going to... |
|---|---------|--------------------------------|
| 1 | [PNT fundamentals](01-pnt-fundamentals.md) | do anything here. Frames, state, uncertainty, integrity, timing, assured PNT vocabulary. |
| 2 | [GNSS and its threats](02-gnss-and-threats.md) | parse receiver data, detect jamming or spoofing, use RTK/PPP, OSNMA. |
| 3 | [Inertial navigation and sensor fusion](03-inertial-and-fusion.md) | write or tune a Kalman filter or factor graph, fuse GNSS with an IMU. |
| 4 | [Vision, LiDAR and radar odometry](04-vision-lidar-radar-odometry.md) | navigate relative to the surroundings: VIO, SLAM, LiDAR and radar odometry. |
| 5 | [Absolute alternative PNT](05-absolute-alt-pnt.md) | get an absolute fix without GNSS: image-to-map, terrain, magnetic, celestial, signals of opportunity. |
| 6 | [Autopilots and C2](06-autopilots-and-c2.md) | feed a position into PX4/ArduPilot, talk MAVLink, push tracks to TAK. |
| 7 | [Maps, geodesy and planning](07-maps-geodesy-planning.md) | convert coordinates, load DEMs and imagery, plan paths or missions. |
| 8 | [Maritime, underwater and ground](08-maritime-underwater-ground.md) | work off the drone: ships, AIS, ROVs, DVL, ground robots, dismounted users. |
| 9 | [Evaluation and datasets](09-evaluation-and-datasets.md) | prove your system works: metrics, datasets, simulators, test events. |

## Suggested order

- **Air-domain alt-nav team (most common):** 1 => 3 => 2 => 5 => 4 => 6 => 9.
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
