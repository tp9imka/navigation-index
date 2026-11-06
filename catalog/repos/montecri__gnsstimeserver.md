# GNSSTimeServer

`repo:montecri/gnsstimeserver` - <https://github.com/Montecri/GNSSTimeServer>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 242 | C | MIT | 2026-11-01 | False | active-research | medium |

ESP8266/ESP32 stratum-1 time server fed by a GNSS module and a TCXO-backed RTC, serving NTP and RDATE over WiFi or W5500 Ethernet, with a PTPv2 master edition, web dashboard and battery backup.

**Why it matters:** Cheapest portable GNSS-fed time source for a field demo network.

**Hackathon notes:** Bill of materials and firmware in the repo; an ESP32 plus GNSS module with PPS. Accuracy is MCU-class, not NIC hardware timestamping.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `ntp`, `ptp`, `esp32`, `gnss`, `stratum-1`, `diy`

**Domains:** multi

## Related

- alternative_to: [Time Pi](../../catalog/repos/geerlingguy__time-pi.md)
- alternative_to: [SatPulse](../../catalog/repos/jclark__satpulse.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
