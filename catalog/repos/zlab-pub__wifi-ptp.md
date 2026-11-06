# Wi-PTP

`repo:zlab-pub/wifi-ptp` - <https://github.com/zlab-pub/wifi-ptp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 73 | C | ? | 2024-07-01 | False | research-prototype | low |

PTP over Wi-Fi: a patched ath9k driver (Linux 4.19) that timestamps in the Wi-Fi hardware path plus an adjusted linuxptp.

**Why it matters:** Time sync between drones or ground nodes over Wi-Fi instead of cable.

**Hackathon notes:** Needs Atheros ath9k cards and a kernel rebuild on an old kernel. Cite the idea; do not plan on building it in 48 h.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `ptp`, `wifi`, `ath9k`, `linuxptp`, `uav`

**Domains:** multi

## Related

- extends: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
