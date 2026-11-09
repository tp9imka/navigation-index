# Neural-Fly

`repo:aerorobotics/neural-fly` - <https://github.com/aerorobotics/neural-fly>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 226 | Jupyter Notebook | ? | 2022-05-21 | False | research-prototype | low |

Training notebook and flight data for Neural-Fly, which learns a wind-invariant representation of quadrotor aerodynamic residual force and adapts it online. Data includes position, velocity, attitude, thrust setpoint, PWM and the computed residual force at several fan-array wind speeds.

**Why it matters:** Real flight logs at labelled wind speeds with motor commands, useful to test how a drag/propulsion model degrades as wind rises.

**Hackathon notes:** No license file; README states personal and educational use only, written permission needed for further use. Fine for an offline wind-sensitivity plot, not for anything shipped.

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `wind`, `aerodynamic-residual`, `meta-learning`, `px4`

**Domains:** air

## Related

- alternative_to: [VID-Dataset](../../catalog/repos/zju-fast-lab__vid-dataset.md)

## Referenced by

- [Neural-Fly enables rapid learning for agile flight in strong winds](../../catalog/resources/oconnell-2022-neural-fly.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
