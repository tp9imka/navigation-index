# WFB-ng

`repo:svpcom/wfb-ng` - <https://github.com/svpcom/wfb-ng>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,564 | Python | GPL-3.0 | 2026-10-19 | False | production | medium |

Long-range packet radio link over raw Wi-Fi injection with FEC, carrying video, MAVLink and IP tunnels.

**Why it matters:** Unidirectional broadcast-style link with FEC is more robust to interference than plain Wi-Fi; useful for EW-resilient telemetry experiments.

**Hackathon notes:** Install on Linux with compatible RTL8812AU/EU cards; key pairs per link.

**Concepts:** [Electronic warfare resilience](../concepts/ew-resilience.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `wifibroadcast`, `fec`, `raw-wifi`, `telemetry`

**Domains:** air, ground

## Related

- alternative_to: [OpenHD](../repos/openhd__openhd.md)

## Referenced by

- [OpenHD](../repos/openhd__openhd.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
