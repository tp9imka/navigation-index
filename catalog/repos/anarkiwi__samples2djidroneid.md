# samples2djidroneid

`repo:anarkiwi/samples2djidroneid` - <https://github.com/anarkiwi/samples2djidroneid>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 37 | Python | Apache-2.0 | 2026-10-27 | False | active-research | medium |

Decodes DJI DroneID (OcuSync 2.0) frames from SDR I/Q recordings, building on proto17's reverse engineering and Kismet.

**Why it matters:** Recovers DJI drone and pilot location telemetry from RF, filling the gap for drones without standard Remote ID.

**Build notes:** Needs high-rate I/Q captures; decoding is slow with interference.

## Deep dives

- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `dji`, `droneid`, `ocusync`, `sdr`

**Domains:** air

## Related

- extends: [dji_droneid](../../catalog/repos/proto17__dji_droneid.md)
- alternative_to: [DroneSecurity (DJI DroneID receiver)](../../catalog/repos/rub-syssec__dronesecurity.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [DragonSync](../../catalog/repos/alphafox02__dragonsync.md) (integrates_with)
- [dji_droneid](../../catalog/repos/proto17__dji_droneid.md) (alternative_to)
- [DroneSecurity (DJI DroneID receiver)](../../catalog/repos/rub-syssec__dronesecurity.md) (alternative_to)
- [Drone Security and the Mysterious Case of DJI's DroneID](../../catalog/resources/ndss-2023-dji-droneid.md) (uses)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-16._
