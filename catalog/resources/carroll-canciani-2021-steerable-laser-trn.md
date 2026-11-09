# Terrain-referenced navigation using a steerable-laser measurement sensor

`res:carroll-canciani-2021-steerable-laser-trn` - paper - <https://navi.ion.org/content/68/1/115>

**By:** Jason D. Carroll, Aaron J. Canciani - **Year:** 2021 - **Level:** advanced - **Access:** open

NAVIGATION 68(1):115-134. Steers a gimballed laser rangefinder to the terrain points that maximise the trace of the position Fisher information block, chosen by particle swarm optimisation over pitch and yaw. Reports large CRLB gains over nadir sensing and about half the error in a mountainous simulation; the aircraft path is unchanged. Read via the journal HTML.

## Key takeaways

- 'Where to look' half of active TRN, with a Fisher (local) criterion
- Objective is multimodal in the pointing angles, hence PSO
- Gimbal dynamics ignored; steering uses the estimated, not true, position

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `trn`, `fisher-information`, `crlb`, `lidar`, `sensor-steering`, `afit`

_Indexed by lane(s): innovation-pa-maneuvers_
