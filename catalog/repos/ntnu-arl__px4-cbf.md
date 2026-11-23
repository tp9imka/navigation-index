# PX4-CBF

`repo:ntnu-arl/px4-cbf` - <https://github.com/ntnu-arl/PX4-CBF>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 14 |  | BSD-3-Clause | 2025-10-16 | False | active-research | high |

Documentation and setup for a CBF safety filter inside the PX4 position controller that minimally changes the acceleration setpoint using onboard range data. The code lives on the ntnu-arl/PX4-Autopilot fork, branch cbf.

**Why it matters:** The product-shaped close-area safety filter: already in PX4, range-only, tested on VOXL2 Mini.

**Build notes:** License BSD-3-Clause (gh api), last push 2025-10-16. Needs NTNU's PX4, mavlink and mavros forks. Fork branch cbf (HEAD e7ef0c61, 2025-02-12) ships only the closed-form single-constraint filter, with no FoV constraint; the paper's FoV-constrained qpOASES QP is in the earlier commit 338fb51f. README says the FoV variant crashes on PixRacer Pro. PX4 parameter defaults (CBF_EPSILON 0.5, CBF_KAPPA 10, CBF_ALPHA 1, CBF_POLE0 -2, CBF_ENABLED 0) differ from the paper's flight values (Table II: eps 0.7, kappa 70, alpha 2, p0 -2.5); use Table II, which matches composite_cbf. For 48h, re-implement in Python and run both arms (shipped closed form and FoV QP); see docs/research/close-area-nav/05-cbf-baselines-faithful.md.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `control-barrier-function`, `px4`, `safety-filter`, `bsd-3`

**Domains:** air

## Related

- extends: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- same_org: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

## Referenced by

- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area talk scaffold: A to B through obstacles](../../templates/presenting/close-area-story.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md) (same_org)
- [PX4-Autopilot (NTNU fork, cbf branch)](../../catalog/repos/ntnu-arl__px4-autopilot.md) (same_org)
- [Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions](../../catalog/resources/misyats-px4-cbf-icuas2025.md) (has_code)

_Indexed by lane(s): close-area-innovation_

_GitHub metadata fetched 2026-11-23._
