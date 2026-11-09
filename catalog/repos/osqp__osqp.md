# OSQP

`repo:osqp/osqp` - <https://github.com/osqp/osqp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,223 | C | Apache-2.0 | 2026-01-12 | False | production | high |

Operator-splitting solver for convex quadratic programs, with embedded C code generation and Python bindings.

**Why it matters:** Minimum-snap with fixed segment times and linear MPC are both QPs; OSQP solves them with no license friction.

**Hackathon notes:** License Apache-2.0 (gh api). Last push 2026-01-12. pip install osqp. Write the min-snap QP yourself in ~100 lines of numpy + OSQP when a team wants code it fully owns.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `qp`, `solver`, `embedded`, `python`, `apache-2.0`

**Domains:** multi

## Related

- alternative_to: [mav_trajectory_generation](../../catalog/repos/ethz-asl__mav_trajectory_generation.md)
- alternative_to: [TinyMPC](../../catalog/repos/tinympc__tinympc.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
