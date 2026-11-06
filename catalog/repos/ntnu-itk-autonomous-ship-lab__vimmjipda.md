# VIMMJIPDA tracker interface

`repo:ntnu-itk-autonomous-ship-lab/vimmjipda` - <https://github.com/ntnu-itk-autonomous-ship-lab/vimmjipda>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Python | MIT | 2025-12-04 | False | research-prototype | medium |

Interface that runs the VIMMJIPDA multi-target tracker (visibility, interacting multiple models, JIPDA) inside the NTNU colav-simulator; open-sourced November 2025.

**Why it matters:** A maritime-grade multi-target tracker connected to a collision avoidance loop, closing the sense-track-avoid chain.

**Hackathon notes:** Install with uv alongside colav-simulator; the VIMMJIPDA core tracker code is vendored in vimmjipda/code (also published on Code Ocean).

**Concepts:** [Tracking and data association](../../catalog/concepts/target-tracking.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md)

**Tags:** `jipda`, `imm`, `multi-target-tracking`, `radar`, `ntnu`

**Domains:** maritime

## Related

- extends: [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md)
- alternative_to: [Stone Soup](../../catalog/repos/dstl__stone-soup.md)

## Referenced by

- [Stone Soup](../../catalog/repos/dstl__stone-soup.md) (alternative_to)
- [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) (integrates_with)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
