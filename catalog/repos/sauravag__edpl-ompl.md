# edpl-ompl

`repo:sauravag/edpl-ompl` - <https://github.com/sauravag/edpl-ompl>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 22 | HTML | ? | 2019-09-18 | False | archived | low |

C++ belief-space motion planning on top of OMPL (FIRM-style roadmaps with feedback controllers and Kalman-filter belief propagation).

**Why it matters:** One of the few open belief-space planners: it plans over the estimator's covariance, not just position.

**Build notes:** No license file (gh api returns none), so all rights reserved: read-only reference, not usable in a product. Last push 2019-09-18. For a hackathon, implement the core idea directly: propagate EKF covariance along candidate routes and pick the route that keeps it under the alert limit.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `belief-space`, `firm`, `ompl`, `uncertainty`

**Domains:** ground, air

## Related

- depends_on: [OMPL - Open Motion Planning Library](../../catalog/repos/ompl__ompl.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Rapidly-exploring Random Belief Trees for Motion Planning Under Uncertainty](../../catalog/resources/bry-roy-rrbt-icra2011.md) (explains)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-09._
