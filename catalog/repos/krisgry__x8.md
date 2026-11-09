# Skywalker X8 simulator

`repo:krisgry/x8` - <https://github.com/krisgry/x8>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 27 | Matlab | ? | 2018-06-14 | False | archived | low |

MATLAB simulator showcasing the Skywalker X8 flying-wing aerodynamic model from Gryte et al. (ICUAS 2018), with a basic autopilot and the coefficients in a .mat file.

**Why it matters:** A published, real-airframe aerodynamic coefficient set: the process model a fixed-wing vehicle-dynamic-model navigator needs.

**Hackathon notes:** No license file; cite the paper. Thrust model is borrowed from the Aerosonde model per the README, so propulsion is not identified. Port the coefficients to Python rather than run MATLAB.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `fixed-wing`, `aerodynamic-model`, `skywalker-x8`, `matlab`

**Domains:** air

## Related

- alternative_to: [JSBSim](../../catalog/repos/jsbsim-team__jsbsim.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [Aerodynamic modeling of the Skywalker X8 Fixed-Wing Unmanned Aerial Vehicle](../../catalog/resources/gryte-2018-skywalker-x8-aerodynamic-model.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
