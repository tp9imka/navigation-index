# NanoMap: Fast, Uncertainty-Aware Proximity Queries with Lazy Search over Local 3D Data

`res:florence-nanomap-2018` - paper - <https://arxiv.org/abs/1802.09076>

**By:** Peter R. Florence, John Carter, Jake Ware, Russ Tedrake - **Year:** 2018 - **Level:** advanced - **Access:** open

Skips global map fusion: keeps recent depth frames with noisy relative poses and answers proximity queries from the most certain view. The planner therefore sees pose uncertainty in obstacle distance. Quadrotor obstacle avoidance up to 10 m/s. ICRA 2018.

## Key takeaways

- Uncertainty-aware obstacle queries in the body frame
- Cheap to apply loop-closure pose updates

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `depth`, `pose-uncertainty`, `quadrotor`

## Related

- has_code: [NanoMap](../../catalog/repos/peteflorence__nanomap_ros.md)

_Indexed by lane(s): close-area-innovation_
