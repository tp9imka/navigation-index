# Non-Gaussian Belief Space Planning: Correctness and Complexity

`res:platt-2012-non-gaussian-belief-space-planning` - paper - <https://people.csail.mit.edu/tlp/pdf/2012/ICRA12_1775_FI.pdf>

**By:** Robert Platt, Leslie Kaelbling, Tomas Lozano-Perez, Russ Tedrake - **Year:** 2012 - **Level:** advanced - **Access:** open

ICRA 2012. Plans actions under the system dynamics so the predicted observations of the most likely state differ as much as possible from those of a few other belief samples, then re-plans as the belief changes. Proves eventual localization under stated conditions with as few as two samples. Demo is a planar arm with one range laser. Full text read.

## Key takeaways

- Cost = sum over samples of exp(-squared distance between predicted observation sequences)
- Dynamics enter as hard constraints x_{t+1} = f(x_t, u_t): the template for flyable maneuvers
- Guarantee needs an exact Bayes filter and a planner that finds low-cost plans
- Closest mechanism to 'pick the maneuver that separates hypotheses'

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `belief-space-planning`, `hypothesis-separation`, `non-gaussian`, `receding-horizon`, `icra`

## Related

- cites: [Rapidly-exploring Random Belief Trees for Motion Planning Under Uncertainty](../../catalog/resources/bry-roy-rrbt-icra2011.md)

_Indexed by lane(s): innovation-pa-maneuvers_
