# Drone Security and the Mysterious Case of DJI's DroneID

`res:ndss-2023-dji-droneid` - paper - <https://www.ndss-symposium.org/ndss-paper/drone-security-and-the-mysterious-case-of-djis-droneid/>

**By:** Nico Schiller, et al. (Ruhr University Bochum, CISPA) - **Year:** 2023 - **Level:** advanced - **Access:** open

Reverse-engineers DJI's DroneID broadcast, shows it is unencrypted, and builds an SDR receiver that decodes drone and pilot positions.

## Key takeaways

- Passive decoding enables detection and localization of DJI drones
- Security analysis of drone firmware and protocols

**Concepts:** [Counter-UAS and drone detection](../concepts/counter-uas.md), [RF localization and direction finding](../concepts/rf-localization.md)

**Tags:** `dji`, `droneid`, `ndss`, `sdr`

## Related

- has_code: [DroneSecurity (DJI DroneID receiver)](../repos/rub-syssec__dronesecurity.md)

## Referenced by

- [DroneSecurity (DJI DroneID receiver)](../repos/rub-syssec__dronesecurity.md) (evaluated_on)

_Indexed by lane(s): defense-context_
