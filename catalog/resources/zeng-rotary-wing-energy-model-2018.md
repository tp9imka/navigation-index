# Energy Minimization for Wireless Communication with Rotary-Wing UAV

`res:zeng-rotary-wing-energy-model-2018` - paper - <https://arxiv.org/abs/1804.02238>

**By:** Yong Zeng, Jie Xu, Rui Zhang - **Year:** 2018 - **Level:** intermediate - **Access:** open

Derives a closed-form propulsion power model for rotary-wing UAVs as a function of forward speed (blade profile, induced and parasite terms), then uses it to optimise trajectories. The power model is widely reused outside the comms context.

## Key takeaways

- Power vs speed is U-shaped: hover is not the cheapest state per second, and there is a max-range speed
- Closed form, so it drops straight into a route cost
- Parameters need a real airframe; defaults in the paper are illustrative

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `energy-model`, `rotary-wing`, `propulsion-power`

## Related

- uses: [AeroSandbox](../../catalog/repos/peterdsharpe__aerosandbox.md)

_Indexed by lane(s): guidance-planning_
