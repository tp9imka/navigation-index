# Fisher Information Field: an Efficient and Differentiable Map for Perception-aware Planning

`res:zhang-scaramuzza-fisher-information-field-2020` - paper - <https://arxiv.org/abs/2008.03324>

**By:** Zichao Zhang, Davide Scaramuzza - **Year:** 2020 - **Level:** advanced - **Access:** open

Precomputes a voxel map of visual-localisation information so a planner can score any pose quickly and differentiably, instead of reprojecting all landmarks. Shown with RRT* and trajectory optimisation.

## Key takeaways

- A localisability map turns 'stay localisable' into an ordinary planning cost
- Precomputation moves the expensive part out of the planning loop
- Same idea works on a 2D grid of terrain or texture informativeness

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `perception-aware`, `localisability`, `fisher-information`

## Related

- has_code: [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md)

## Referenced by

- [01. Flyable maneuvers that separate competing location hypotheses](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md) (mentions)

_Indexed by lane(s): guidance-planning_
