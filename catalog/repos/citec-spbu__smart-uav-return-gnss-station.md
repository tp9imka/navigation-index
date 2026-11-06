# Smart-UAV-Return-GNSS-Station

`repo:citec-spbu/smart-uav-return-gnss-station` - <https://github.com/citec-spbu/Smart-UAV-Return-GNSS-Station>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3 | C | ? | 2024-06-01 | False | research-prototype | low |

Student project from SPbU (CITEC) on returning a UAV to its launch point when both GNSS and the ground-station link are lost, targeting a RockPi 4 companion computer. Description in Russian; README is minimal and points to an external Notion board.

**Why it matters:** Same problem statement as many Ukrainian field requirements (lost link + lost GNSS => come home), from the Russian academic side.

**Hackathon notes:** Sparse docs; read the C sources directly. Reference value only.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Electronic warfare resilience](../concepts/ew-resilience.md)

**Tags:** `lang:ru`, `return-to-home`, `rockpi`, `student`

**Domains:** air

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
