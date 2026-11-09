# PX4-CBF

`repo:ntnu-arl/px4-cbf` - <https://github.com/ntnu-arl/PX4-CBF>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? |  | ? | ? | ? | active-research | high |

Documentation and setup for a CBF safety filter inside the PX4 velocity loop that minimally changes the acceleration setpoint using onboard range data; the code lives in an NTNU PX4 fork.

**Why it matters:** The product-shaped close-area safety filter: already in PX4, range-only, tested on VOXL2 Mini.

**Hackathon notes:** License BSD-3-Clause (gh api), last push 2025-10-16. Needs NTNU's PX4, mavlink and mavros forks. README says the FoV-constrained qpOASES variant crashes on PixRacer Pro; the analytic unconstrained case is the safe one. For 48h, re-implement the composite CBF in Python and cite this as the deploy path.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `control-barrier-function`, `px4`, `safety-filter`, `bsd-3`

**Domains:** air

## Related

- extends: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- same_org: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

## Referenced by

- [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md) (same_org)
- [Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions](../../catalog/resources/misyats-px4-cbf-icuas2025.md) (has_code)

_Indexed by lane(s): close-area-innovation_
