# Seed-0 tuning log for st_astar and astar_vo (synthetic)

All runs: seed 0 (tuning seed), 50 `random` layouts, people at 0.5 and 1.0 m/s, the
`run_moving.run_one` harness through `run_predict.fly`. Seed 1 was not run until the constants
below were fixed. Counts are reached / collision / stuck / timeout out of 50, transcribed from the
console of an ad-hoc sweep script that is not kept in the repo (it built each arm with
`planners_st.SpaceTimeAStar(**kw)` or `vo.VOGate(**kw)` and called `run_predict.fly`). Rerun one
row by passing the same keyword arguments.

Round 1, before the turn-around hedge existed (person_margin / vo_margin 0.15, no reach term):
st_astar 49 / 1 / 0 / 0 at 0.5 m/s and 46 / 4 / 0 / 0 at 1.0 m/s; astar_vo 50 / 0 / 0 / 0 and
47 / 3 / 0 / 0. Traces of three st_astar collisions (layouts 15, 20, 27 at 1.0 m/s) showed the
person reversing at a segment end towards the vehicle while the alpha-beta velocity was still
turning over. That is why `reach_s` (turn-around hedge) and the peak-held speed `s_peak` were
added to `predict.py`.

An intermediate hedge used the current tracked speed instead of the peak-held one (st_astar
reach_s 0.5 and 1.0 at margin 0.15, reach_s 0.5 at margin 0.3; astar_vo reach_s 0.5 and 1.0). It
left 2-5 collisions out of 50 at 1.0 m/s in each of those configurations, because the tracked speed dips
towards 0 during a U-turn, exactly when the hedge is needed. It was replaced by the peak-held speed.

Round 2 and 3, with the hedge using the peak-held speed:

| arm | reach_s s | margin m | 0.5 m/s | 1.0 m/s |
|---|---|---|---|---|
| st_astar | 0.0 | 0.15 | 49 / 1 / 0 / 0 | 46 / 4 / 0 / 0 |
| st_astar | 0.5 | 0.15 | 50 / 0 / 0 / 0 | 47 / 3 / 0 / 0 |
| st_astar | 1.0 | 0.15 | 50 / 0 / 0 / 0 | 47 / 3 / 0 / 0 |
| st_astar | 0.5 | 0.3 | 50 / 0 / 0 / 0 | 49 / 1 / 0 / 0 |
| st_astar | 1.0 | 0.3 | 50 / 0 / 0 / 0 | 48 / 2 / 0 / 0 |
| st_astar | 0.5 | 0.45 | 50 / 0 / 0 / 0 | 49 / 1 / 0 / 0 |
| st_astar | 1.0 | 0.45 | 50 / 0 / 0 / 0 | 49 / 1 / 0 / 0 |
| astar_vo | 0.0 | 0.15 | 50 / 0 / 0 / 0 | 47 / 3 / 0 / 0 |
| astar_vo | 0.5 | 0.15 | 50 / 0 / 0 / 0 | 45 / 5 / 0 / 0 |
| astar_vo | 1.0 | 0.15 | 50 / 0 / 0 / 0 | 49 / 1 / 0 / 0 |
| astar_vo | 1.0 | 0.3 | 50 / 0 / 0 / 0 | 50 / 0 / 0 / 0 |
| astar_vo | 1.5 | 0.15 | 50 / 0 / 0 / 0 | 49 / 0 / 1 / 0 |
| astar_vo | 1.5 | 0.3 | 50 / 0 / 0 / 0 | 50 / 0 / 0 / 0 |

Picked: st_astar reach_s 0.5, person_margin 0.3 (the smaller margin among the 1-collision
rows); astar_vo reach_s 1.0, vo_margin 0.3 (the smaller reach among the 0-collision rows). These
are the defaults in `planners_st.py` and `vo.py`, and the seed-0 rows of
[predict_0_1.md](predict_0_1.md) are these configurations. Counting the intermediate hedge, 10
st_astar and 8 astar_vo configurations were tried on seed 0, so the seed-0 rows are optimistic;
seed 1 is the held-out check.
