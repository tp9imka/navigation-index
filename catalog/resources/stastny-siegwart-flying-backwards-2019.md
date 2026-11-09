# On Flying Backwards: Preventing Run-away of Small, Low-speed, Fixed-wing UAVs in Strong Winds

`res:stastny-siegwart-flying-backwards-2019` - paper - <https://arxiv.org/abs/1908.01381>

**By:** Thomas Stastny, Roland Siegwart - **Year:** 2019 - **Level:** advanced - **Access:** open

Nonlinear lateral path-following guidance for fixed-wing UAVs that uses online wind estimates and adjusts the airspeed reference when wind approaches or exceeds airspeed. Flight-tested in strong mountain winds. This line of work underlies PX4's NPFG.

## Key takeaways

- Path following must handle wind faster than airspeed explicitly
- Wind estimate is a guidance input, so estimator quality matters to guidance
- Link between this paper and PX4 NPFG is from the author overlap and PX4 docs naming, not checked line by line

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `fixed-wing`, `path-following`, `wind`, `npfg`

## Related

- has_code: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

_Indexed by lane(s): guidance-planning_
