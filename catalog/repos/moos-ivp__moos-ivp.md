# MOOS-IvP

`repo:moos-ivp/moos-ivp` - <https://github.com/moos-ivp/moos-ivp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 103 | C++ | NOASSERTION | 2026-10-29 | False | production | high |

Long-running autonomy middleware (MOOS) plus the IvP Helm behaviour-based multi-objective decision engine, used widely for autonomous marine vehicles, including COLREGs-aware collision avoidance behaviours.

**Why it matters:** The academic and navy-adjacent reference for marine vehicle autonomy; much published USV/UUV collision avoidance work is built on it.

**Hackathon notes:** Builds on Linux/macOS with CMake; the bundled alpha and heron missions run in simulation with pMarineViewer. Pair with the MIT 2.680 labs.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [moos-ivp__moos-ivp](../../docs/integration-cards/moos-ivp__moos-ivp.md) (integration-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md)

**Tags:** `moos`, `ivp-helm`, `usv`, `uuv`, `colregs`, `mit`

**Domains:** maritime, underwater

## Related

- extends: [MOOS-IvP COLREGs master's research code](../../catalog/repos/d2snc__moos-ivp-masters.md)
- alternative_to: [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MOOS-IvP COLREGs master's research code](../../catalog/repos/d2snc__moos-ivp-masters.md) (extends)
- [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) (alternative_to)
- [Virtual RobotX (VRX)](../../catalog/repos/osrf__vrx.md) (alternative_to)
- [MIT 2.680 Unmanned Marine Vehicle Autonomy, Sensing and Communications](../../catalog/resources/mit-2680-marine-autonomy.md) (uses)
- [MOOS-IvP documentation wiki](../../catalog/resources/moos-ivp-docs.md) (explains)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
