# 08. Crazyflie sensing limits: what the planner and safety filter can rely on

Research note, 2026-11-09. Question: if the first-day platform is a Crazyflie 2.x with
the Multi-ranger and Flow v2 decks, what can it sense, what can it not sense, and what sensor
settings should the [close-area arena](../../../samples/close-area-arena/README.md) use so that
sim results transfer?

Nothing was flown or run for this note. Numbers are the sources' own claims, labelled by source
type and by who measured them. Geometry numbers (section 4) are derived from the 27 deg cone
with the formulas shown; they are not measurements. Platform table for context:
[02 section 2](02-sims-platforms-competitions.md).

Source labels: **[datasheet]** chip vendor, or a vendor-figure reproduction where named;
**[docs]** Bitcraze product pages and tutorials; **[code]** crazyflie-firmware master, read
via `gh api` on 2026-11-09 (latest commit `e828ed2`, 2026-11-04); **[forum]** Bitcraze forum or
GitHub issues; **[paper]** papers, with venue status.

## 1. Bottom line

- **The Multi-ranger sees 30 % of the horizontal circle.** Four 27 deg cones at 0, 90, 180,
  270 deg cover 4 x 27 = 108 of 360 deg. The four 63 deg wedges centred on the diagonals are
  blind. At 1.5 m a blind wedge is 1.57 m wide, so a whole table can sit in it unseen.
- **Obstacles you pass close to drop out of view.** An obstacle at lateral offset y from the
  flight line leaves the front cone when it is 4.16 y ahead and enters the side cone only at
  0.24 y. At y = 0.15 m (the arena vehicle radius) it is unseen for the last 0.62 m. A
  memoryless range barrier loses it exactly when it matters.
- **Glass is invisible and dark surfaces are weak.** Real flights by ETH Zurich with one
  forward VL53L1 crashed 10 of 10 times; most crashes were undetected glass doors
  ([BatDeck, arXiv 2412.10048](https://arxiv.org/abs/2412.10048) [paper, preprint]).
- **Range depends on light.** Long mode, which the Multi-ranger uses by default, drops from about
  3.6 m in the dark to about 0.73 m in strong ambient light (ST figures, see section 2.2).
- **Rate is 10 Hz.** The firmware polls all five sensors every 100 ms [code].
- **The Flow deck needs a textured, matte, lit floor** and holds height only between 0.2 m and
  3.0 m in hover mode [docs]. No published drift-per-metre number was found.
- **Consequence for the hub headline** ([README](README.md)): on a Crazyflie, "what the drone
  cannot see" is most bearings plus every glass surface. The map and protection-level half of
  the filter does most of the work, and the range half needs a short memory. **Since measured
  (synthetic):** the protection-level margin did not beat a fixed 0.2 m bound
  ([safety-filter Part e](../../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic));
  a 3 s scan memory cut DWA collisions on a 4-ray fan from 52 % to 18 % (random) and 58 % to 20 %
  (narrow_gap) ([dwa-bug](../../../samples/close-area-planner-dwa-bug/README.md#results-ran-2026-11-09-apple-m3-max-macos-2662-cpython-31210-numpy-254-scipy-1181)).

## 2. Multi-ranger deck

### 2.1 Hardware and firmware

| Item | Value | Source |
|---|---|---|
| Sensors | 5 x ST VL53L1x ToF: front, back, left, right, up | [docs] [product page](https://www.bitcraze.io/products/multi-ranger-deck/) |
| Down sensor | None on this deck. Height comes from the Flow deck VL53L1x | [docs] |
| Claimed range | "up to 4 meters within a few millimeters (depending on surface and light conditions)" | [docs] product page |
| Deck mass | 2.3 g, 35 x 35 x 5 mm, mounts on top | [docs] product page |
| Built-in avoidance | None. "The deck provides sensor data only" | [docs] product page |
| Field of view per beam | 27 deg full cone (16 x 16 SPAD array, all SPADs enabled). Can be narrowed to about 15 deg with a smaller region of interest | [datasheet] via [Pololu carrier page](https://www.pololu.com/product/3415), which quotes ST |
| Minimum range | 4 cm; closer targets are detected but not accurate | [datasheet] via Pololu |
| Emitter | 940 nm Class 1 VCSEL, eye safe | [datasheet] via Pololu |
| Distance mode used | LONG. `vl53l1xInit` only calls `VL53L1_DataInit` and `VL53L1_StaticInit`; the vendored ST API's `StaticInit` sets `VL53L1_DISTANCEMODE_LONG` and preset `LOWPOWER_AUTONOMOUS` | [code] `src/drivers/src/vl53l1x.c`, `src/lib/vl53l1/core/src/vl53l1_api.c` |
| Timing budget | Not set by the driver; left at the ST preset default. Value not traced | [code] |
| Update rate | 10 Hz. `mrTask` waits `M2T(100)` then reads front, back, up, left, right in turn | [code] `src/deck/drivers/src/multiranger.c` |
| Invalid reading | Readings whose range status fails `filterMask` (default: only `RANGE_VALID` passes) are written as 32767 mm, that is 32.767 m | [code] `multiranger.c` |
| Log names | `range.front`, `range.back`, `range.left`, `range.right`, `range.up` | [forum] [t=4448](https://forum.bitcraze.io/viewtopic.php?t=4448) (Bitcraze staff reply) |

### 2.2 Range by surface and light

The ST datasheet table was not read as text: the PDF uses embedded fonts that stdlib tools could
not extract. The figures below are ST's numbers as reproduced by two secondary pages.

| Mode | Dark | Strong ambient light | Max rate | Source |
|---|---|---|---|---|
| Short | about 136 cm | about 135 cm | 50 Hz | [datasheet] figures reproduced by [espboards](https://www.espboards.dev/sensors/vl53l1x/); rate from Pololu |
| Medium | about 290 cm | about 76 cm | 30 Hz | same |
| Long (Multi-ranger default) | about 360 cm | about 73 cm | 30 Hz | same |

- The 4 m figure needs long mode, a long timing budget, dark conditions and a white target
  (espboards paraphrasing ST; SparkFun's driver notes say 4 m in the dark with a 200 ms budget,
  [hookup guide](https://learn.sparkfun.com/tutorials/qwiic-distance-sensor-vl53l1x-hookup-guide/all)).
- Ranging error: about +-20 to 25 mm depending on mode and ambient light ([datasheet] via
  espboards).
- Surface reflectance changes maximum range but not the time-of-flight principle (Pololu). The
  grey-target (lower reflectance) rows of the ST table were not recovered. **Not verified.**

### 2.3 Noise

- Bitcraze's own noise model for the same chip, used for the Flow deck height sensor in medium
  mode with a 25 ms budget, is std = 0.0025 (1 + exp(k (d - 2.5))) m with k = ln(80) / 1.5,
  fitted through 2.5 mm at 2.5 m and 0.2 m at 4.0 m [code] `zranger2.c`. Evaluated: 2.5 mm up
  to 1.5 m, 3.1 mm at 2.0 m, 5.0 mm at 2.5 m, 13 mm at 3.0 m, 49 mm at 3.5 m, 0.20 m at 4.0 m.
  Who measured it and how is not stated in the code. It applies to a downward sensor over a
  floor, not to the Multi-ranger's long mode.
- Readings jump at object edges because the sensor integrates over its cone ([forum] t=4448,
  Bitcraze staff). The Flow deck tutorial says the sensor reports the closest detection in the
  cone [docs].

### 2.4 Known failure surfaces

| Surface | What happens | Evidence | Measured by |
|---|---|---|---|
| Glass doors, transparent walls | Not detected. Most of 10 crashes in 10 forward-VL53L1 flights were glass doors; mean 4 m flown, 9 s | [paper] BatDeck, arXiv 2412.10048, section VI-C (preprint) | ETH Zurich / Bologna, real office flights, single forward VL53L1 on a Multi-ranger reduced to one sensor, 33 Hz, their own avoidance algorithm |
| Black or absorptive objects | Hard to detect | [paper] BatDeck VI-C, qualitative | same |
| Narrow objects (chair legs, poles) | Missed where the object fills little of the cone (chair edge example) | [paper] BatDeck Fig. 7 text, qualitative | same |
| Mirrors and glass near the deck | Lighthouse positioning also needs "no glass or mirrors" | [docs] [positioning overview](https://www.bitcraze.io/documentation/system/positioning/) | Bitcraze |
| Sporadic bad readings across sensors | Reported by one user on two decks; Bitcraze suspected a power or connector fault | [forum] t=4448 | one user, unresolved |

No published minimum detectable pole diameter was found. **Not verified.**

## 3. Flow deck v2

| Item | Value | Source |
|---|---|---|
| Flow sensor | PixArt PMW3901 ("works best on matt surfaces") | [docs] [product page](https://www.bitcraze.io/products/flow-deck-v2/) |
| PMW3901 specs | Working range 80 mm to infinity, 42 deg field of view, max 7.4 rad/s, needs > 60 lux | [datasheet] figures as listed by [CubePilot HereFlow docs](https://docs.cubepilot.org/user-guides/flow-senor/here-flow) (same chip); PixArt datasheet not read |
| Height sensor | VL53L1x, driver `bcZRanger2`, MEDIUM mode, 25 ms timing budget, 40 Hz loop; readings at or above 5 m are dropped as outliers | [code] `zranger2.c`, `flowdeck_v1v2.c` |
| Flow rate | Flow task reads the sensor after `vTaskDelay(10)` at a 1000 Hz tick, so up to 100 Hz | [code] `flowdeck_v1v2.c`, `FreeRTOSConfig.h` |
| Flow noise in the EKF | Fixed std 2.0 (flow units) by default; an adaptive model from shutter time, fitted by Bitcraze over low and high texture, is off by default | [code] `flowdeck_v1v2.c` |
| Flow outlier gate | Frames with a pixel delta of 100 or more are dropped; flow is only fused when the sensor reports motion | [code] |
| EKF model | 35 px across 42 deg; height clamped to at least 0.1 m inside the flow model | [code] `kalman_core/mm_flow.c` |
| Hover height | 0.2 m to 3.0 m in the client's hover mode (1.0 m for Flow deck v1) | [docs] [getting started](https://www.bitcraze.io/documentation/tutorials/getting-started-with-flow-deck/) |
| Low limit | "Kind of blind below 8 cm", so take-off is open loop until flow starts | [forum] [t=5082](https://forum.bitcraze.io/viewtopic.php?t=5082), Bitcraze staff |
| High limit | No recommended limit; depends on texture, light and floor. Theoretical limit is the ToF range | [forum] [t=4532](https://forum.bitcraze.io/viewtopic.php?t=4532), Bitcraze staff. 2 m "works fine on wood floor" ([forum] [t=3231](https://forum.bitcraze.io/viewtopic.php?t=3231)) |
| Mass | 1.6 g, mounts under the Crazyflie | [docs] |

Floor and lighting failure cases, all from Bitcraze's
[flow deck limitations post](https://www.bitcraze.io/2023/11/go-with-the-flow-relative-positioning-with-the-flow-deck/)
[docs, blog] unless marked:

- Plain single-colour floor (no texture).
- Black areas; at start-up the position estimate diverges. Reproduced on black patches of a
  black-white rubber mat: x/y diverge while the drone sits on the black part
  ([forum] [crazyflie-firmware issue 617](https://github.com/bitcraze/crazyflie-firmware/issues/617),
  user report; Bitcraze advised resetting the estimator just before take-off).
- Low light. Shiny floors, and infrared scattering for the height sensor.
- Flying over its own shadow.
- Frequent yaw: flow caused by yaw is not separated from translation, so the drone drifts.
- Near walls or over obstacles: the height cone reports the closest return (the wall or the box
  top), and the flow model assumes a flat floor [docs, getting started]. Flying over a box reads
  as a sudden height drop.
- Flow resolution is 1/10 pixel, which is coarse at greater height ([paper] BatDeck VII-A).

Drift: Bitcraze calls the Flow deck relative positioning by dead reckoning, so error grows
without bound [docs]. **No published drift-per-metre or drift-per-minute figure for the Flow
deck was found.** BatDeck reports velocity MSE for Flow deck v2 against motion capture on a
table and a carpet (their Table III), but the table values were not in the text extract and
were not read.

## 4. AI deck, Lighthouse and Loco positioning (short)

- **AI deck 1.1**: GAP8 (8+1 core RISC-V), Himax HM01B0 320 x 320 greyscale camera, ESP32
  WiFi, 4.4 g. Needs a JTAG programmer to flash the GAP8; no built-in function for the camera
  [docs] [product page](https://www.bitcraze.io/products/ai-deck/). It adds no positioning by
  itself.
- **Lighthouse**: Bitcraze rates it mm-class accuracy over at most 8 x 8 x 3 m, line of sight, no
  glass or mirrors, up to 4 base stations [docs] positioning overview. Measured against Qualisys
  mocap by Bitcraze and collaborators (Taffanel et al., ICRA 2021 workshop,
  [arXiv 2104.11523](https://arxiv.org/abs/2104.11523) [paper]): mean and median error 2-4 cm,
  flight outliers about 5 cm, up to 18 cm when moved fast near the edge of coverage. The same
  paper's conclusion says about 1 cm on average; the two statements disagree and were not
  resolved. Hub record: `res:taffanel-2021-lighthouse-positioning-accuracy`.
- **Loco (UWB)**: Bitcraze rates it dm-class [docs]. Bitcraze's own static test with six
  anchors in two-way ranging ([accuracy page](https://www.bitcraze.io/documentation/system/positioning/accuracy-loco/))
  shows x/y errors of 0.03-0.16 m, z errors up to 0.44 m for points below the anchor volume,
  std 0.5-2 cm, and one point with 0.237 m mean 3D error. Raw ranges read 0.22-0.40 m short,
  which Bitcraze attributes to antenna delay. Bitcraze says these are indications, not a
  specification. Hub record: `res:bitcraze-lps-precision-wiki` (archived copy of the same data).

## 5. Obstacle classes a 4-beam horizontal ranger cannot sense

Geometry for a 27 deg full cone (half angle 13.5 deg) per beam. Cone width at range r is
2 r tan 13.5 deg = 0.48 r. A blind wedge spans 90 - 27 = 63 deg; its chord at range r is
2 r sin 31.5 deg = 1.045 r. Recompute with:
`python3 -c "import math;h=math.radians(13.5);print([(r,2*r*math.tan(h),2*r*math.sin(math.radians(31.5)),r*math.tan(h)) for r in (0.5,1.5)])"`

| r | Cone width per beam | Blind wedge chord | Largest round obstacle hidden on a diagonal (radius) | Vertical band seen (+- around flight height) |
|---|---|---|---|---|
| 0.5 m | 0.24 m | 0.52 m | 0.26 m | +-0.12 m |
| 1.5 m | 0.72 m | 1.57 m | 0.78 m | +-0.36 m |

Top view, body frame, front up. `#` = sensed cone, `.` = blind wedge. Rings at 0.5 m and 1.5 m:

```
                         front 0 deg
              .  .  .  .   ####   .  .  .  .
          .   .  .  .  .    ##    .  .  .  .   .
       .  blind 63 deg  .   ##   .  blind 63 deg  .
          .  (diag 45)   .  ##  .   (diag 315)  .
   left  ##########.......[CF].......##########  right
   90 deg           .  .  . ## .  .  .            270 deg
          .   blind  .  .   ##   .  .  blind  .
       .  .  .  .  .  .     ##      .  .  .  .  .
              .  .  .  .   ####   .  .  .  .
                          back 180 deg

   at 0.5 m: each # cone 0.24 m wide, each . wedge 0.52 m across
   at 1.5 m: each # cone 0.72 m wide, each . wedge 1.57 m across
   up beam: one 27 deg cone straight up. Down: Flow deck ToF only (sees the floor or a box top)
```

Unsensed classes, most dangerous first:

1. **Transparent and mirror surfaces** (glass doors, acrylic panels). Invisible at any bearing
   ([paper] BatDeck). Fine-mesh safety nets: **not verified**.
2. **Diagonals.** Anything in the four 63 deg wedges. Flying diagonally puts the direction of
   travel in a blind wedge: with velocity at 45 deg no beam looks where the drone is going.
3. **Grazing obstacles that leave the cone.** For lateral offset y, an obstacle is blind for
   forward distance between y tan 13.5 deg and y / tan 13.5 deg: 0.04-0.62 m at y = 0.15 m,
   0.05-0.83 m at y = 0.2 m, 0.07-1.25 m at y = 0.3 m. Derived geometry, not measured.
4. **Below and above the band.** A low bar or table edge whose top is more than 0.12 m below
   flight height is not in the front cone at 0.5 m. Overhangs are seen only directly above (up
   beam). Boxes below are seen only by the height sensor, which then corrupts height and flow
   scaling (section 3).
5. **Thin objects** (poles, cables, chair legs): missed when they fill little of the cone
   ([paper] BatDeck, qualitative). No minimum diameter is published.
6. **Dark, absorptive surfaces** at long range, and anything beyond about 0.73 m in strong light
   (long mode figure, section 2.2).

What this does to the planner and safety filter:

- A memoryless body-frame range barrier (PX4-CBF style, [05](05-cbf-baselines-faithful.md))
  only constrains motion along the four beam axes. Either keep a short-memory local map built
  from past returns and odometry, or restrict commanded velocity to beam axes. The memory window
  must carry the odometry drift as extra margin.
- Yawing to scan the blind wedges costs Flow deck drift (section 3). Prefer translating along
  beam axes over yawing.
- Glass, low bars and thin poles can only be handled by the map half of the filter (known
  obstacles from whoever set the task, or a map built under better sensing). That is the protection
  level half of the hub headline. Since measured (synthetic): for map-only obstacles a fixed
  0.2 m bound did as well as the protection level, and the headline failed
  ([research decision](../README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).
- Speed cap from range and rate, using the arena vehicle (a <= 3 m/s^2, radius 0.15 m) and one
  100 ms sensor period as latency: v^2 / (2 a) + 0.1 v <= R - 0.15. With R = 0.73 m that gives
  1.59 m/s; with R = 3.0 m the arena's own 2 m/s cap binds. Derived, synthetic vehicle model.

## 6. Proposed arena settings: "crazyflie" sensor preset

`RangeFan` ([sensors.py](../../../samples/close-area-arena/sensors.py)) takes `n_beams`, `fov`
(spread of beam centres), `max_range`, `noise_std`, `dropout`. With `fov = 2 pi` and
`n_beams = 4` its spacing gives beams at -180, -90, 0 and 90 deg, which matches the Multi-ranger
horizontal layout. Each beam is one ideal ray; there is no per-beam cone or material model yet
(see Driver edits). Current default for comparison: 72 beams, 360 deg, 6 m, 0.02 m, 2 %.
**Built since:** the arena's `presets.py` and `sensors_cone.py` now consume the rows marked "not
supported yet" below (27 deg cone, 0.04 m minimum range, glass and mirror invisible, dark-surface
range). Glass-family collisions with the crazyflie preset were 90 % (freest_beam) and 100 % (A*
unknown map), synthetic
([sensor realism](../../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic)).

| Field | crazyflie (nominal indoor) | crazyflie_bright | crazyflie_ideal | Basis |
|---|---|---|---|---|
| `n_beams` | 4 | 4 | 4 | [docs] 4 horizontal VL53L1x (up beam not modelled in 2.5D) |
| `fov` (beam spread) | 2 pi | 2 pi | 2 pi | Beams 90 deg apart |
| `max_range` m | 3.0 | 0.73 | 3.6 | 3.6 = long mode dark, ST figure; 0.73 = long mode strong light, ST figure; 3.0 = **proposal**, a margin below 3.6 for non-white arena surfaces and room light, not measured |
| `noise_std` m | 0.02 | 0.02 | 0.0025 | 0.02 from ST +-20-25 mm ranging error; 0.0025 = Bitcraze down-ranger model below 1.5 m (different mode) |
| `dropout` | 0.05 | 0.10 | 0.0 | **Proposal.** No published dropout rate; picked above the 0.02 default because cone-edge jumps and status rejections are reported [forum]. 0.10 for bright light is a guess |
| beam cone deg (not supported yet) | 27 | 27 | 27 | [datasheet] |
| `min_range` m (not supported yet) | 0.04 | 0.04 | 0.04 | [datasheet] via Pololu |
| rate Hz | 10 | 10 | 10 | [code] `multiranger.c`; arena `plan_hz` is already 10 |
| glass and mirror obstacles (not supported yet) | always `inf` | always `inf` | always `inf` | [paper] BatDeck |
| dark obstacles (not supported yet) | `inf` beyond 1.0 m | `inf` beyond 0.5 m | seen | **Proposal**, no number published |

Paste-ready for `run.py` `DEFAULTS["sensor"]` or a preset dict:

```python
import math

SENSOR_PRESETS = {
    # Crazyflie Multi-ranger, horizontal beams only (front, left, back, right).
    "crazyflie":        {"n_beams": 4, "fov": 2 * math.pi, "max_range": 3.0,  "noise_std": 0.02,   "dropout": 0.05},
    "crazyflie_bright": {"n_beams": 4, "fov": 2 * math.pi, "max_range": 0.73, "noise_std": 0.02,   "dropout": 0.10},
    "crazyflie_ideal":  {"n_beams": 4, "fov": 2 * math.pi, "max_range": 3.6,  "noise_std": 0.0025, "dropout": 0.0},
}
# Not yet consumed by RangeFan; for a later sensor-model change.
CRAZYFLIE_EXTRA = {"beam_cone": math.radians(27), "min_range": 0.04, "rate_hz": 10,
                   "invisible_materials": ("glass", "mirror"), "dark_max_range": 1.0}
```

Other arena settings that follow from the platform, all proposals:

- Area: 8 x 8 m if Lighthouse is the position source (Bitcraze's stated maximum), instead of
  20 x 20 m.
- Vehicle radius 0.15 m and z = 1.0 m sit inside the Flow deck hover range (0.2-3.0 m).
- Add an obstacle family with glass panels on the A-B line and thin poles of 0.02-0.05 m, so
  the cost of the unsensed classes shows up in the scorer.

## 7. Not verified

Reconciled 2026-11-09: every bullet below is still open. The arena now simulates the
section 6 preset, which tests the planners against this doc's model, not the model against a
real deck.

- The ST VL53L1X datasheet table itself (read through espboards and Pololu); the grey-target
  rows; the Multi-ranger timing budget under the `LOWPOWER_AUTONOMOUS` preset.
- The PMW3901 datasheet (figures via CubePilot's page for the same chip).
- Any Flow deck drift number; BatDeck Table III values.
- Minimum detectable pole diameter and real dropout rates for the Multi-ranger.
- Whether fine-mesh nets are seen by the VL53L1x.
- Section 5 and 6 geometry and speed caps are derived, not flown. Simulated since with these
  values: on 4 beams, unknown-map A* reached 35 % in office (25 % collisions) and 0 % in
  warehouse (50 % collisions), 20 layouts per cell, synthetic
  ([benchmark crazyflie preset](../../../samples/close-area-benchmark/README.md#preset-crazyflie)).

## Ask on the first day

Which decks are fitted (Multi-ranger, Flow v2, AI deck, Lighthouse or Loco); floor texture and
lighting; any glass, mesh or thin poles in the arena; whether obstacle positions are given.
