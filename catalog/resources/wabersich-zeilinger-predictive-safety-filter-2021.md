# A predictive safety filter for learning-based control of constrained nonlinear dynamical systems

`res:wabersich-zeilinger-predictive-safety-filter-2021` - paper - <https://arxiv.org/abs/1812.05506>

**By:** Kim P. Wabersich, Melanie N. Zeilinger - **Year:** 2021 - **Level:** advanced - **Access:** open

MPC-style filter that receives any proposed input, for example from an RL policy, and changes it only when needed to keep a safe backup plan feasible. Handles state- and input-dependent model uncertainty. Automatica 129, 2021, doi 10.1016/j.automatica.2021.109597.

## Key takeaways

- Theory for 'any planner plus a filter'
- Heavier than a CBF-QP; needs an MPC solve

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `predictive-safety-filter`, `mpc`, `learning-based-control`

_Indexed by lane(s): close-area-innovation_
