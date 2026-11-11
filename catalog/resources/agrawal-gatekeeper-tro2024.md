# gatekeeper: Online Safety Verification and Control for Nonlinear Systems in Dynamic Environments

`res:agrawal-gatekeeper-tro2024` - paper - <https://arxiv.org/abs/2211.14361>

**By:** Devansh R. Agrawal, Ruichang Chen, Dimitra Panagou - **Year:** 2024 - **Level:** advanced - **Access:** open

Lightweight check between a planner and a controller: simulate the nominal trajectory to a switch time, then a backup controller such as hover, and commit the safe candidate with the latest switch time. Quadrotor hardware with an online map; 3-10x faster than MPC in simulation per the authors. Peer-reviewed: IEEE T-RO 40:4358-4375, 2024, doi 10.1109/TRO.2024.3454415, plus IROS 2023 pp. 259-266 (Crossref, per docs/research/close-area-nav/05-cbf-baselines-faithful.md).

## Key takeaways

- Planner-agnostic, easy to explain to reviewers
- Needs a backup controller and backup set

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `backup-controller`, `safety-verification`, `quadrotor`, `peer-reviewed`

## Related

- has_code: [gatekeeper](../../catalog/repos/dev10110__gatekeeper.md)

_Indexed by lane(s): close-area-innovation_
