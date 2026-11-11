# Composing Control Barrier Functions for Complex Safety Specifications

`res:molnar-ames-composing-cbf-lcss2023` - paper - <https://doi.org/10.1109/LCSYS.2023.3339719>

**By:** Tamas G. Molnar, Aaron D. Ames - **Year:** 2023 - **Level:** advanced - **Access:** paywalled

Peer-reviewed (IEEE Control Systems Letters 7:3615-3620, per Crossref). Combines many barrier functions into one with a smooth soft-min, the construction PX4-CBF uses with a tanh saturation and a sharpness parameter kappa. Not read: cited here because PX4-CBF builds on it.

## Key takeaways

- Soft-min composition under-approximates the minimum of the individual barriers
- Larger kappa is less conservative
- Not read; metadata from Crossref and the PX4-CBF paper

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `control-barrier-function`, `composite-cbf`, `theory`, `peer-reviewed`

_Indexed by lane(s): cbf-baselines_
