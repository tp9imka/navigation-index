# DroneSecurity (DJI DroneID receiver)

`repo:rub-syssec/dronesecurity` - <https://github.com/RUB-SysSec/DroneSecurity>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,333 | Python | AGPL-3.0 | 2023-03-10 | False | research-prototype | medium |

Ruhr University Bochum receiver for DJI DroneID that works live with an SDR or offline on captures, released with their NDSS 2023 security analysis.

**Why it matters:** Shows how passive decoding of drone telemetry supports detection and localization of DJI aircraft, a common C-UAS need.

**Hackathon notes:** Requires a wideband SDR (e.g. USRP/BladeRF) and recorded or live captures; sample captures ease offline work.

## Deep dives

- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `dji`, `droneid`, `sdr`, `ndss`, `usrp`

**Domains:** air

## Related

- evaluated_on: [Drone Security and the Mysterious Case of DJI's DroneID](../../catalog/resources/ndss-2023-dji-droneid.md)
- alternative_to: [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md) (alternative_to)
- [Drone Security and the Mysterious Case of DJI's DroneID](../../catalog/resources/ndss-2023-dji-droneid.md) (has_code)

_Indexed by lane(s): defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
