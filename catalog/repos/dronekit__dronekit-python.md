# DroneKit-Python

`repo:dronekit/dronekit-python` - <https://github.com/dronekit/dronekit-python>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,955 | Python | Apache-2.0 | 2024-05-30 | False | archived | low |

Older high-level Python API for MAVLink vehicles, built on pymavlink; maintenance has slowed (last push 2024).

**Why it matters:** Many tutorials still use it; fine for simple ArduPilot scripts but prefer pymavlink or MAVSDK for new work.

**Hackathon notes:** The PyPI release 2.9.2 (2019) fails to import on Python 3.10+ (it uses collections.MutableMapping); pin Python 3.9 or install from GitHub master, which has the fix. Better to avoid for new work.

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `python`, `legacy`

**Domains:** air

## Related

- depends_on: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)
- alternative_to: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [pymavlink](../../catalog/repos/ardupilot__pymavlink.md) (depends_on)
- [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
