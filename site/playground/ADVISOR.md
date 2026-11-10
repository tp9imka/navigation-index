# Playground Advisor: which planner to pick for this world

A panel for the [arena playground](index.html). When a preset world is loaded it shows, for that
family and the selected sensor, how every benchmarked planner did: reached, collision and stuck %,
median time to B, and a bar. It recommends one planner that needs a prior map and one that does not,
with a one-line reason and a "Use this" button. An (i) next to every planner, sensor preset, VIO fault
and the F2 filter explains it in 2-4 plain lines with numbers. Standalone test page:
[advisor-demo.html](advisor-demo.html).

Everything shown is **synthetic**: simulated layouts, vehicle, sensors and VIO, scored on truth. No
number in the panel is a flight or SITL result.

## Key result

Ivan's observation holds in the benchmark. On office and maze, only 2 of the 10 map-free planners
(straight excluded) reach B in at least 50 % of layouts with the ideal sensor (`astar_unknown`,
`dstar_lite`). With the Crazyflie sensor only 1 of 10 does (`astar_unknown_f2`: office 50 % reached
/ 5 % collision, maze 55 % / 0 %). The three prior-map planners reach 100 % with 0 % collision in
both families on both sensors. Source: [data/advisor.json](data/advisor.json), built from
[matrix_0.json](../../samples/close-area-benchmark/results/matrix_0.json) (20 layouts per cell,
seed 0, true pose).

Two playground-specific traps the panel shows:

- **Run time limit.** Since loop-73b the playground uses the benchmark's limit: 120 s on maze and
  warehouse (worker.js `max_time_for` = bench.py `LONG_FAMILIES`), 60 s elsewhere. Before, it stopped
  every run at 60 s, and the table printed "N % by 60 s" under cells that reached B later (on maze with
  the Crazyflie sensor, `astar_unknown_f2` reached 55 % in 120 s and 0 % within 60 s). That note now
  shows only where the playground limit is shorter than the benchmark cell's, which no preset family is.
- **Unknown-map A* in the playground is the shipped one.** Its map starts 2.5 m behind A. The
  benchmark moved the map corner to the area corner. Ideal sensor, office: 15 % (shipped) vs 95 %
  (benchmark) reached ([prior_check_0.md](../../samples/close-area-benchmark/results/prior_check_0.md)).

## Check (ran 2026-11-09, headless Chrome 140, Apple M3 Max)

`node site/playground/results/advisor-check.mjs` (from the repo root, no npm packages, no network
needed for the demo page) opens the demo page and the real playground, and prints a JSON report.
Result: all checks pass (`pass` field), including:

- The cards equal the winners in advisor.json. When the winner is not a playground option yet
  (`astar_mpc`), the card shows a tied planner the page offers (`astar_known`) and names the winner.
- "Use this" (map-free, maze x crazyflie) calls `onPick("astar_unknown", {filter: "F2"})`.
- Header clicks sort the table both ways. The (i) popover opens on a real mouse click, shows
  What / Needs / Good at / Fails and the benchmark lines, and Escape closes it.
- Custom world drawn from empty: "No benchmark for custom worlds", no table. Edited from maze with
  `crazyflie_bright`: maze table with the nearest sensor (`crazyflie`) and a note.
- Dark theme follows `prefers-color-scheme`. At 390 px the panel fits the viewport; the table
  scrolls inside its own box and the popover stays on screen.
- The wiring below, injected into the unchanged playground page: the panel follows `PG.loadPreset`
  and the Config A sensor select, "Use this" sets Config A planner and filter, and adding an obstacle
  switches to the custom-world note.

Screenshots (viewport only): [maze x crazyflie](results/advisor-maze-crazyflie.png),
[planner popover](results/advisor-popover.png), [custom world](results/advisor-custom.png),
[warehouse dark, weak pick](results/advisor-warehouse-dark.png),
[phone 390 px](results/advisor-phone-390.png), [phone popover](results/advisor-phone-390-popover.png),
[inside the playground](results/advisor-in-playground.png).

Not checked: Safari and Firefox, touch input on a real phone, screen readers beyond the ARIA
attributes, and the wiring against loop-62's edited index.html / playground.js (it was injected into
the version in this checkout).

## How the data is built

```sh
python3 site/playground/data/build_advisor.py     # stdlib, < 1 s, writes data/advisor.json (about 111 kB)
```

- **Cells.** Per family x preset x planner it recomputes `reached`, `collision`, `stuck`, `timeout`
  (%), `median_time_s` (over runs that reached B), `median_clearance_m` (over all runs), `n`, `seed`,
  `collisions_by_material` and `max_time_s` from the 4,480 per-run rows of matrix_0.json, and exits
  non-zero if any value differs from the matrix's own `summary`. All 224 cells match. Maze and
  warehouse cells got `reached_within_60s` while the playground stopped every run at 60 s; since
  loop-73b the playground limit equals the benchmark's (120 s there), so no cell has it.
- **Recommendation.** Rule: highest reached %, then lowest collision %, then lowest median time.
  Ranked separately for planners that need a prior map (`astar_known`, `informed_rrt_star`,
  `astar_mpc`) and those that do not. Ties on reached and collision are listed. A map-free winner
  under 50 % reached or at 20 % collision or more is flagged "weak", with the safest map-free option
  (lowest collision, then highest reached). That happens on narrow_gap, warehouse and glass_office
  with the Crazyflie sensor.
- **Option docs.** Planner, sensor, VIO fault and filter texts are written in the script with
  numbers from the sample READMEs (each doc lists its `src`). Generated per family: each planner's
  "in the benchmark" lines, the sensor impact (best map-free planner and how many reach 80 % with
  under 10 % collision), F2 impact (`astar_unknown` vs `astar_unknown_f2`, with glass hits), and the
  VIO dropout / jump impact on A* known map from
  [reloc_matrix_refs.md](../../samples/close-area-relocalize/results/reloc_matrix_refs.md)
  (seeds 2-4, 90 runs per cell, 7 families; forest not run there).
- **Ids.** `playground_to_bench` maps the playground's option ids to benchmark rows: `apf` =>
  `apf_escape`, the other 5 map to the same name. Each benchmark row has `playground: {planner,
  filter}`; `astar_unknown_f2` => planner `astar_unknown` + filter `F2`. Rows with
  `in_playground_now: false` (`informed_rrt_star`, `astar_mpc`, `dwa`, `dwa_mem`, `bug2`,
  `tangent_bug`, `dstar_lite`) get a "new" tag and assume loop-62 adds them under the benchmark name.
  If loop-62 uses other ids, add them to `PG_TO_BENCH` / `BENCH_TO_PG` and rebuild. Not in the
  benchmark: preset `crazyflie_bright` (shown as `crazyflie`, nearest), every VIO fault (the matrix
  uses the true pose), and F2 on any planner other than `astar_unknown`.

## API

```js
const adv = Advisor.mount(container, {
  getFamily,     // () => "maze" | { custom: true, from: "maze" | null }
  getPreset,     // () => "ideal" | "crazyflie" | "crazyflie_bright"
  onPick,        // (plannerId, { planner, filter, bench }) => void
  getAvailable,  // optional: () => planner option ids the page offers; others get no button
  pollMs,        // optional, default 400: re-render when getFamily / getPreset / getAvailable change
  dataUrl,       // optional, default data/advisor.json next to advisor.js
});
adv.refresh();   // force a re-render; adv.destroy() removes the panel
```

## Wiring (for the driver; loop-62 owns index.html and playground.js)

**index.html**, 3 additions:

1. In `<head>`, after the `playground.css` link:
   ```html
   <link rel="stylesheet" href="advisor.css?v=20261109">
   ```
2. In `<head>`, before the `playground.js` script tag (both are `defer`, so this order makes
   `window.Advisor` exist when playground.js runs):
   ```html
   <script defer src="advisor.js?v=20261109"></script>
   ```
3. In `<main>`, right after the closing `</div>` of `<div class="pg-grid">`:
   ```html
   <div id="advisorBox"></div>
   ```

**playground.js**, one block at the end of the file, after `window.PG = {...};`. It uses `S`, `$`
and `setCfg` from playground.js. A world counts as a benchmark family only while it is an unedited
preset (`S.pristine`); an edited preset or an opened file shows the custom note with its family.

<!-- wire-js -->
```js
// Advisor panel (advisor.js, loop-65): benchmark success rates per planner for the loaded preset family.
if (window.Advisor) window.PG_ADVISOR = Advisor.mount($("#advisorBox"), {
  getFamily: () => (S.pristine && S.presetName && S.doc.family !== "custom") ? S.doc.family
    : { custom: true, from: S.doc && S.doc.family !== "custom" ? S.doc.family : null },
  getPreset: () => $("#A_preset").value,
  getAvailable: () => Array.from($("#A_planner").options).filter(o => !o.disabled).map(o => o.value),
  onPick: (planner, cfg) => { setCfg(0, { planner, filter: cfg.filter }); $("#cfgA").scrollIntoView({ block: "nearest" }); },
});
```

The panel polls every 400 ms, so no other playground.js line needs to change. If loop-62 renames
the `#A_preset` / `#A_planner` selects or `setCfg`, adjust the three lines above. If share links
should carry the pick, `onPick` is the place to update them.
