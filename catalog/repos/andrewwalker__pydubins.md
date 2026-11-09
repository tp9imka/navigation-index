# pydubins

`repo:andrewwalker/pydubins` - <https://github.com/AndrewWalker/pydubins>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 79 | C | MIT | 2025-08-17 | False | production | high |

Python wrapper around the C Dubins-Curves library: shortest paths for a vehicle with a minimum turn radius, plus sampling along the path.

**Why it matters:** Minimum-radius 2D paths are the building block of fixed-wing route planning and loiter / re-fix manoeuvres.

**Hackathon notes:** License MIT (gh api). Last push 2025-08-17. Builds a C extension on install; if no compiler, the closed-form Dubins words are short enough to write in numpy. 2D only and no wind: use EDuPlane when wind or climb limits matter.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `dubins`, `fixed-wing`, `python`, `mit`

**Domains:** air, maritime

## Related

- alternative_to: [EDuPlane (Extended Dubins Airplane)](../../catalog/repos/dlr-ft__eduplane.md)
- alternative_to: [mavsim_public (Small Unmanned Aircraft)](../../catalog/repos/byu-magicc__mavsim_public.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [01. Flyable maneuvers that separate competing location hypotheses](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md) (mentions)
- [mavsim_public (Small Unmanned Aircraft)](../../catalog/repos/byu-magicc__mavsim_public.md) (alternative_to)
- [EDuPlane (Extended Dubins Airplane)](../../catalog/repos/dlr-ft__eduplane.md) (extends)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
