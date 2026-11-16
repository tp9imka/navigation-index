# Copilot

`repo:copilot-language/copilot` - <https://github.com/Copilot-Language/copilot>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 840 | Haskell | ? | 2026-11-15 | False | active-research | low |

Stream-based runtime-verification language embedded in Haskell. It compiles monitors to constant-time, constant-memory C99 (and Bluespec), so the generated checker can run on a flight controller-class MCU.

**Why it matters:** Bounded-time, no-heap C output is what an embedded safety monitor needs. It is the engine behind Ogma.

**Build notes:** GitHub reports no license; the copilot/LICENSE file in the repo is BSD-3 text. Use through Ogma unless the team already knows Haskell. The generated C can be dropped into a PX4 module or a companion process.

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `runtime-verification`, `c99`, `haskell`, `monitor`, `nasa`, `hard-real-time`

**Domains:** air, space, multi

## Related

- integrates_with: [Ogma](../../catalog/repos/nasa__ogma.md)
- alternative_to: [R2U2](../../catalog/repos/r2u2__r2u2.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Ogma](../../catalog/repos/nasa__ogma.md) (depends_on)
- [R2U2](../../catalog/repos/r2u2__r2u2.md) (alternative_to)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
