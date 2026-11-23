# pyulog

`repo:px4/pyulog` - <https://github.com/PX4/pyulog>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 173 | Python | BSD-3-Clause | 2026-10-27 | False | production | high |

Python parser and command-line tools for PX4 ULog flight logs (to CSV, info, params, messages).

**Why it matters:** The extractor for every PX4 log: ESC RPM, airspeed, wind estimate, actuator outputs and EKF innovations come out as tables for model-aided estimation experiments.

**Build notes:** pip install pyulog; ulog2csv flight.ulg. Pairs with public logs on PX4 Flight Review. Check each log for esc_status and airspeed topics before relying on them.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `ulog`, `px4`, `log-parsing`, `esc-telemetry`

**Domains:** air

## Related

- same_org: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- same_org: [PX4 Flight Review](../../catalog/repos/px4__flight_review.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-23._
