# Diploma: LoRa local navigation system (MIPT 2026)

`repo:roosmax/diploma` - <https://github.com/Roosmax/Diploma>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | MIT | 2026-07-22 | False | research-prototype | high |

MIPT (FAKT) 2026 diploma: local navigation for a UAV under GNSS suppression, correcting a strapdown INS with LoRa two-way-ranging (TWR) distances to ground beacons. Python code includes INS mechanization, an error-state EKF, a tightly coupled MSCKF variant, least-squares triangulation, an IMU simulator and parameter studies; thesis and slides are in Russian (.docx/.pptx).

**Why it matters:** Open, inspectable version of the 'ground beacons instead of satellites' approach that Ukrainian vendors also describe publicly (see Vyriy beacon navigation).

**Hackathon notes:** Pure Python simulation, no hardware needed; good basis for a beacon-ranging + INS demo. No README; read Code/main.py and the thesis.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [RF localization and direction finding](../concepts/rf-localization.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `lang:ru`, `lora`, `twr`, `beacons`, `eskf`, `thesis`

**Domains:** air

## Referenced by

- [Vyriy створила маякову навігацію для дронів, яка працює без GPS і зв’язку](../resources/devua-vyriy-beacon-navigation-2026.md) (explains)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
