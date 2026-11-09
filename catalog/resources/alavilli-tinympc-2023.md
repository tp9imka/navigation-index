# TinyMPC: Model-Predictive Control on Resource-Constrained Microcontrollers

`res:alavilli-tinympc-2023` - paper - <https://arxiv.org/abs/2310.16985>

**By:** Anoushka Alavilli, Khai Nguyen, Sam Schoedel, Brian Plancher, Zachary Manchester - **Year:** 2023 - **Level:** intermediate - **Access:** open

ADMM-based MPC solver that caches the Riccati structure so each iteration is cheap enough for a microcontroller; demonstrated on a small quadrotor.

## Key takeaways

- Convex (linearised) MPC can run on autopilot-class MCUs
- Useful 'runs on the aircraft' argument for a product pitch
- Repo README cites an ICRA 2024 Best Paper award

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `mpc`, `admm`, `microcontroller`

## Related

- has_code: [TinyMPC](../../catalog/repos/tinympc__tinympc.md)

_Indexed by lane(s): guidance-planning_
