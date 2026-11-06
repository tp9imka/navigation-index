# Marginalized Particle Filter for Accurate and Reliable Terrain-Aided Navigation

`res:nordlund-gustafsson-2009-mpf-terrain-aided-navigation` - paper - <https://doi.org/10.1109/TAES.2009.5310306>

**By:** Per-Johan Nordlund, Fredrik Gustafsson - **Year:** 2009 - **Level:** advanced - **Access:** paywalled

IEEE TAES 45(4) paper integrating INS and terrain-aided positioning in one marginalized (Rao-Blackwellized) particle filter: particles for the nonlinear part, Kalman filters for the conditionally linear part, plus a jointly estimated discrete mode. Simulations reach near Cramer-Rao accuracy. Open copy in Linkoping's DiVA.

## Key takeaways

- Joint INS + TAP design instead of a separate TRN fix
- Marginalized PF keeps the particle count manageable
- Handles multimodal terrain via a mode variable

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `terrain-aided-navigation`, `marginalized-particle-filter`, `rao-blackwellized`

## Related

- same_author: [Terrain navigation using Bayesian statistics](../../catalog/resources/bergman-ljung-gustafsson-1999-terrain-navigation-bayesian.md)

_Indexed by lane(s): backlog_
