# Closing the Loop on Runtime Monitors with Fallback-Safe MPC

`res:sinha-fallback-safe-mpc-cdc2023` - paper - <https://arxiv.org/abs/2309.08603>

**By:** Rohan Sinha, Edward Schmerling, Marco Pavone - **Year:** 2023 - **Level:** advanced - **Access:** open

Robust MPC that uses perception estimates while keeping a fallback plan that does not depend on perception, paired with a runtime monitor calibrated by conformal prediction. When the monitor fires, the fallback runs. Aircraft taxiing sim and a simulated quadrotor that slows and descends. CDC 2023.

## Key takeaways

- Monitor => slow down, with a calibrated alarm
- Perception errors were simulated

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `runtime-monitor`, `conformal-prediction`, `fallback`, `mpc`

_Indexed by lane(s): close-area-innovation_
