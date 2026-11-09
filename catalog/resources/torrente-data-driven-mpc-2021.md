# Data-Driven MPC for Quadrotors

`res:torrente-data-driven-mpc-2021` - paper - <https://arxiv.org/abs/2102.05773>

**By:** Guillem Torrente, Elia Kaufmann, Philipp Foehn, Davide Scaramuzza - **Year:** 2021 - **Level:** advanced - **Access:** open

Learns the residual between a nominal quadrotor model and real dynamics with Gaussian processes and uses the corrected model inside acados NMPC, improving tracking at high speed (RA-L 2021).

## Key takeaways

- Physics model + learned residual beats either alone
- Residual mostly captures aerodynamic drag
- Template for a propulsion / aero-aware controller

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `mpc`, `gaussian-process`, `aerodynamics`, `quadrotor`

## Related

- has_code: [Data-Driven MPC for Quadrotors](../../catalog/repos/uzh-rpg__data_driven_mpc.md)
- uses: [acados: a modular open-source framework for fast embedded optimal control](../../catalog/resources/verschueren-acados-2019.md)

_Indexed by lane(s): guidance-planning_
