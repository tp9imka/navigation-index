# Drone Security and the Mysterious Case of DJI's DroneID

`res:ndss-2023-dji-droneid` - paper - <https://www.ndss-symposium.org/ndss-paper/drone-security-and-the-mysterious-case-of-djis-droneid/>

**By:** Nico Schiller, et al. (Ruhr University Bochum, CISPA), Merlin Chlosta, Moritz Schloegel, Nils Bars, et al. - **Year:** 2023 - **Level:** advanced - **Access:** open

Security analysis of DJI drones that reverse-engineers the DroneID broadcast and shows it is unencrypted, with an open receiver released.

## Key takeaways

- Passive decoding enables detection and localization of DJI drones
- Security analysis of drone firmware and protocols
- DroneID leaks drone and pilot position in the clear
- Decoding needs SDR captures at high sample rates

## Deep dives

- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `dji`, `droneid`, `ndss`, `sdr`

## Related

- has_code: [DroneSecurity (DJI DroneID receiver)](../../catalog/repos/rub-syssec__dronesecurity.md)
- uses: [samples2djidroneid](../../catalog/repos/anarkiwi__samples2djidroneid.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [DroneSecurity (DJI DroneID receiver)](../../catalog/repos/rub-syssec__dronesecurity.md) (evaluated_on)

_Indexed by lane(s): defense-context, domains-swarm_
