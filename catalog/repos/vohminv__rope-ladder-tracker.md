# rope-ladder-tracker

`repo:vohminv/rope-ladder-tracker` - <https://github.com/VohminV/rope-ladder-tracker>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | ? | 2025-08-14 | False | research-prototype | medium |

Python/OpenCV return-to-home for a quadcopter with a downward camera and no GPS. Instead of integrating optical flow, it stores keyframes ('rungs') on the way out and, on the way back, matches the nearest rung and truncates history, sending the residual offset to the controller. README and the companion Habr article are in Russian.

**Why it matters:** A small, readable alternative to drift-prone flow integration for the specific job of getting home when GNSS is gone; the same idea as teach-and-repeat.

**Hackathon notes:** Pure Python + OpenCV, runs on a laptop against recorded downward video. Integration with a flight controller is left to the user (README sends offsets; no MAVLink bridge verified). Good seed for a 'return home under jamming' demo.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `lang:ru`, `optical-flow`, `return-to-home`, `teach-and-repeat`, `opencv`

**Domains:** air

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Как я научил квадрокоптер возвращаться домой без GPS: алгоритм «верёвочной лестницы»](../../catalog/resources/habr-rope-ladder-return-home-2025.md) (has_code)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
