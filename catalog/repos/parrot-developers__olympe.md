# Olympe

`repo:parrot-developers/olympe` - <https://github.com/Parrot-Developers/olympe>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 96 | Python | BSD-3-Clause | 2026-10-15 | False | production | low |

Parrot's Python controller library for ANAFI drones and the Sphinx simulator, using the Arsdk messages (moveBy, moveTo, piloting, camera).

**Why it matters:** The SDK path if the event platform is a Parrot ANAFI. Same code drives Sphinx and the real drone.

**Build notes:** BSD-3-Clause. PyPI ships only a manylinux x86_64 wheel (parrot-olympe 8.5.0), and Sphinx needs Ubuntu x64 plus an NVIDIA GPU, so neither runs on an Apple Silicon Mac. Only useful if an x86 Linux GPU box is provided.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `parrot`, `anafi`, `sphinx`, `python`, `bsd-3-clause`

**Domains:** air

## Referenced by

- [Sphinx system requirements](../../catalog/resources/parrot-sphinx-system-requirements.md) (part_of)

_Indexed by lane(s): close-area-sims_

_GitHub metadata fetched 2026-11-16._
