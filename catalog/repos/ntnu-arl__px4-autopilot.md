# PX4-Autopilot (NTNU fork, cbf branch)

`repo:ntnu-arl/px4-autopilot` - <https://github.com/ntnu-arl/PX4-Autopilot>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1 | C++ | BSD-3-Clause | 2025-05-06 | False | research-prototype | medium |

NTNU fork of PX4 whose cbf branch holds the actual PX4-CBF code: CBFSafetyFilter in mc_pos_control, a tof_obstacles_chunk uORB message and CBF_* parameters. Branch HEAD has only the analytic single-constraint filter; the FoV-constrained qpOASES QP is in the earlier commit 338fb51f.

**Why it matters:** This is the code the PX4-CBF baseline must be copied from; its defaults and failure behaviour differ from the paper's flight values.

**Build notes:** Fork (gh api fork=true), license BSD-3-Clause per gh api, last push 2025-05-06. Read src/modules/mc_pos_control/PositionControl/CBFSafetyFilter.cpp and multicopter_safety_filter_params.c. CBF_ENABLED defaults to 0. Parameter defaults (eps 0.5, kappa 10, alpha 1, p0 -2, LP gains 0.01) are not the paper's flight values. See docs/research/close-area-nav/05-cbf-baselines-faithful.md.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `control-barrier-function`, `px4`, `safety-filter`, `fork`, `bsd-3`

**Domains:** air

## Related

- fork_of: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- same_org: [PX4-CBF](../../catalog/repos/ntnu-arl__px4-cbf.md)
- same_org: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

_Indexed by lane(s): cbf-baselines_

_GitHub metadata fetched 2026-11-23._
