# H1: move to distinguish competing location hypotheses

<!-- about: sample:navigation-innovation-lab, sample:vpr-large-area, res:agarwal-2015-nongaussian-global-localization, res:deng-sentis-2026-kidnapped-uav, res:wakulicz-2026-reduced-belief-seminar -->

Status: mechanism demonstrated synthetically; proposed improvement over the
information-gain baseline NOT demonstrated. Not a claim of new active localization.

## Failure and hypothesis

Several places can look alike. More texture does not necessarily distinguish them.
A short change in viewpoint could reject competing location hypotheses sooner than
continuing toward the goal. Hypothesis: a finite-action, cost-aware discriminator
can preserve that benefit with lower movement cost than generic information gain.

## Closest work and proposed difference

- [Agarwal, Tamjidi and Chakravorty](https://arxiv.org/abs/1511.04634): receding-horizon
  motion disambiguates multimodal location beliefs; demonstrated on a ground robot.
- [Deng and Sentis, ION GNSS+ 2026](https://www.ion.org/publications/abstract.cfm?articleID=20744):
  aerial blind-start and recovery using cross-domain imagery and multiple hypotheses.
  The public abstract describes convergence as distinctive observations appear;
  it does not establish that an active motion policy is absent from the full paper.
- [Wakulicz seminar](https://robotics.sydney.edu.au/acfr-seminar-reduced-latent-belief-spaces-for-active-perception-in-robotics/):
  reduced belief representations motivate a small hypothesis/action space. Abstract
  read; talk not watched; this POC does not implement her particular method.

The proposed difference is a low-compute aerial action rule penalizing departure
from forward progress while separating visual alternatives. Aircraft feasibility,
real cross-view predictions, and robustness to map error remain unimplemented.

## POC boundary and algorithm

Inputs: probabilities for three locations plus an unknown mode, a scalar descriptor
map for each candidate, local displacement, and a shared feasible action set.
The world chooses a hidden candidate and noisy observations; the policy cannot see it.

Use three-point Gaussian quadrature to estimate expected entropy reduction for five
local motions. Score `information_gain - lambda * lost_forward_progress`. Apply the
same intersection-of-map-regions constraint to every competitor. Update the belief
with the observed descriptor; accept above 0.98, reject/abstain when unknown dominates
or the 24-observation budget expires. Unknown uses a broad Cauchy likelihood.

This is a synthetic 2D descriptor world: no images, terrain, velocity/acceleration,
camera FoV, energy, obstacle sensing, or 6-DoF aircraft dynamics. The constraints
only model candidate-map corridor membership. Quadrature is approximate. Repeated
observations have independent modeled noise, which real imagery need not have.

## Baselines and falsification

Passive forward motion, a texture-seeking policy, expected information gain, the
proposed cost-aware variant, and an ablation without unknown rejection. Conventional
competitors share the same observation noise and action constraints. Tune lambda on
nominal development seeds only; keep indistinguishable/missing/shifted maps as stress.

Reject the proposed contribution if it reduces to ordinary information gain or does
not improve its cost/success trade-off. A reduction in distance accompanied by more
incorrect accepted fixes is not an unqualified improvement.

## Measured result and decision

On 100 held-out seeds per scenario, tuning selected **lambda=0**: the candidate is
identical to the conventional information-gain policy. Nominal average distance is
3.11 synthetic metres versus 13.11 passive, with 99% versus 100% correct acceptance.
Under map shift, the candidate falsely accepts **72/100** runs versus 0/100 passive
(passive abstains in 37). Under the deliberately obvious missing-truth condition,
unknown rejection abstains in all 100; removing it falsely accepts all 100.

Source: [complete measurements and intervals](../../samples/navigation-innovation-lab/results/report.md).
Zero observed failures is not a zero-risk bound. The missing-truth case is an easy
outlier, not proof against plausible unseen locations.

Decision: retain the failure example and standard baseline; do not pitch this as a
novel robust planner. Next research: jointly marginalize map/descriptor nuisance
parameters, examine data-association-aware planning, and compare to it on unseen
maps. Next engineering: branchable image observations and an aircraft trajectory
feasibility layer. A replay of one fixed flight cannot validate chosen movements.
