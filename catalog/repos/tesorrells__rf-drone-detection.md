# RF-Drone-Detection (Georgia Tech)

`repo:tesorrells/rf-drone-detection` - <https://github.com/tesorrells/RF-Drone-Detection>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 226 | Python | ? | 2025-05-21 | False | research-prototype | medium |

Georgia Tech student project on passive RF drone detection: a wifi_monitor.py script that flags DJI MAC OUI prefixes via airodump-ng, plus hackrf_sweep and GNU Radio experiment tools.

**Why it matters:** Shows a cheap passive RF detection path for drones that use Wi-Fi links.

**Hackathon notes:** Needs root and a monitor-mode Wi-Fi adapter (tested on 2.4 GHz only, Ubuntu 18.04). It only matches two DJI OUI prefixes, so it misses non-Wi-Fi links and is trivially spoofed. No licence file.

**Concepts:** [Counter-UAS and drone detection](../concepts/counter-uas.md), [RF localization and direction finding](../concepts/rf-localization.md)

**Tags:** `passive-rf`, `wifi`, `drone-detection`

**Domains:** air

## Related

- alternative_to: [DroneRF](../repos/al-sad__dronerf.md)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
