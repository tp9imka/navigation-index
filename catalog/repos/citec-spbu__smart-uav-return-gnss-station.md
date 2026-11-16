# Smart-UAV-Return-GNSS-Station

`repo:citec-spbu/smart-uav-return-gnss-station` - <https://github.com/citec-spbu/Smart-UAV-Return-GNSS-Station>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 3 | C | ? | 2024-06-01 | False | research-prototype | low |

Student project from SPbU (CITEC) on returning a UAV to its launch point when both GNSS and the ground-station link are lost, targeting a RockPi 4 companion computer. Description in Russian; README is minimal and points to an external Notion board.

**Why it matters:** Same problem statement as many Ukrainian field requirements (lost link + lost GNSS => come home), from the Russian academic side.

**Build notes:** Sparse docs; read the C sources directly. Reference value only.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `lang:ru`, `return-to-home`, `rockpi`, `student`

**Domains:** air

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Landscape: what reviewers already know](../../docs/landscape/README.md) (mentions)
- [Sources in Ukrainian and Russian](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-16._
