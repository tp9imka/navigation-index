# v2e

`repo:sensorsini/v2e` - <https://github.com/SensorsINI/v2e>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 499 | Python | MIT | 2026-04-13 | False | active-research | high |

Converts conventional video into realistic synthetic DVS event streams with sensor noise modeling.

**Why it matters:** Lets you produce event data for training/testing without owning an event camera.

**Hackathon notes:** Not on PyPI: create a conda env, install CUDA PyTorch, then `pip install -e .` from a clone (or use the Colab notebook). Needs a GPU; conversion runs far slower than real time, so test with --stop on a short clip of drone footage first.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `event-camera`, `synthetic-data`, `dvs`

**Domains:** multi

## Related

- alternative_to: [ESIM](../repos/uzh-rpg__rpg_esim.md)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
