# PX4 draft PR 27884: airspeed fusion for wind estimation in rotary-wing flight

`res:px4-pr-27884-mc-airspeed-wind-fusion` - doc - <https://github.com/PX4/PX4-Autopilot/pull/27884>

**By:** Jonas Perolini - **Year:** 2026 - **Level:** advanced - **Access:** open

Open draft. For VTOLs in multicopter mode, fuses airspeed into wind states only, gated by lateral specific force as a proxy for being aligned with the wind; the author reports the drag-based wind estimator was not precise enough on their VTOL and asks how to know the vehicle is aligned with the wind.

## Key takeaways

- Practitioner evidence that drag-based wind estimation can be too imprecise on real airframes
- Another heuristic gate on when a measurement is informative about wind

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `ekf2`, `wind`, `airspeed`, `vtol`, `pull-request`

## Related

- part_of: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
