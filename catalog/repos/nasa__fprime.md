# F Prime (F')

`repo:nasa/fprime` - <https://github.com/nasa/fprime>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 11,882 | C++ | Apache-2.0 | 2026-11-15 | False | production | low |

JPL's component-based flight software framework: typed ports, a modelling language (FPP) and generated C++ glue, flown on the Mars Helicopter. Runs on Linux, RTOSes and microcontrollers.

**Why it matters:** Shows what flight-grade structure looks like (static allocation, explicit interfaces, telemetry/command dictionaries). A nav module written as an F' component is easier to argue about than a ROS node.

**Build notes:** Too heavy to adopt in 48 h. Cite it on the path-to-product slide as the target structure, and borrow its patterns (no dynamic allocation after init, rate groups).

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `flight-software`, `jpl`, `c++`, `component-architecture`, `fpp`

**Domains:** air, space

## Related

- alternative_to: [NASA Core Flight System (cFS)](../../catalog/repos/nasa__cfs.md)
- integrates_with: [Ogma](../../catalog/repos/nasa__ogma.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [NASA Core Flight System (cFS)](../../catalog/repos/nasa__cfs.md) (alternative_to)
- [Ogma](../../catalog/repos/nasa__ogma.md) (integrates_with)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
