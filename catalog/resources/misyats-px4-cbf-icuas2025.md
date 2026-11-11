# Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions

`res:misyats-px4-cbf-icuas2025` - paper - <https://arxiv.org/abs/2504.15850>

**By:** Nazar Misyats, Marvin Harms, Morten Nissov, Martin Jacquet, Kostas Alexis - **Year:** 2025 - **Level:** advanced - **Access:** open

Composite control barrier function built only from onboard range measurements, inserted in the PX4 position and velocity loop as a minimal change to the acceleration setpoint. Does not need consistent localization or mapping. Accepted at ICUAS 2025 per the arXiv comment.

## Key takeaways

- Product-shaped safety filter already inside PX4
- Strongest baseline for a close-area safety filter
- Abstract gives no numbers

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `control-barrier-function`, `px4`, `safety-filter`, `range-sensor`

## Related

- has_code: [PX4-CBF](../../catalog/repos/ntnu-arl__px4-cbf.md)
- has_code: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

## Referenced by

- [Close-area talk scaffold: A to B through obstacles](../../templates/presenting/close-area-story.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Safe Quadrotor Navigation using Composite Control Barrier Functions](../../catalog/resources/harms-composite-cbf-icra2025.md) (same_author)
- [Secure Safety Filter: Towards Safe Flight Control under Sensor Attacks](../../catalog/resources/tan-2025-secure-safety-filter.md) (cites)

_Indexed by lane(s): close-area-innovation_
