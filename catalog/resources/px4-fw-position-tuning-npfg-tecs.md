# PX4 Fixed-wing Altitude/Position Controller Tuning Guide

`res:px4-fw-position-tuning-npfg-tecs` - doc - <https://docs.px4.io/main/en/config_fw/position_tuning_guide_fixedwing.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intermediate - **Access:** open

Official tuning guide for PX4 fixed-wing outer loops: TECS for altitude and airspeed (FW_T_* parameters) and NPFG lateral path following (NPFG_PERIOD and related parameters).

## Key takeaways

- Tune TECS before NPFG; the guide gives the order
- NPFG period and damping set how hard the aircraft converges to the path
- Year is the page as fetched, not a release date

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `px4`, `fixed-wing`, `tecs`, `npfg`, `tuning`

## Related

- explains: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

_Indexed by lane(s): guidance-planning_
