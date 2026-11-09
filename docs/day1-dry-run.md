# Day-1 dry run: close-area A=>B, one agent, no team (loop-58)

**Next action if you are on Day 1:** read the [blockers table](#blockers) first, then follow the
[runbook](#runbook-as-executed). Copying flight-repo out of the hub needs `ARENA=` and `SAFETY=`
on every `make` call (blocker 2).

What this is: one coding agent followed the hub's Day-1 path from a fresh clone, alone, on
2026-11-09, for a fake brief. Every step was timed with wall clock. Nothing in the hub was fixed;
this page reports what happened.

Input types: every flight number on this page is **synthetic** (simulated layouts, vehicle,
range sensor and estimator). No SITL, no real flight. Wall times are real measurements on this
machine, under heavy load from other agents (see [machine](#machine-and-caveats)).

## Brief and intake answers

Brief: "Fly a small drone autonomously from A to B in an indoor arena with obstacles. Platform and
sensors announced on the day."

Intake card from [day1-close-area-intake.md](day1-close-area-intake.md#1-questions-in-the-order-to-ask).
Only Q6 and Q7 are partly answered by the brief; the rest take the intake default.

| # | Answer | Branch taken |
|---|---|---|
| Q1 drone + SDK | default: PX4-class quad over MAVSDK | `drivers/px4_mavsdk.py` (unrun stub); planner work on the arena |
| Q2 sim / real | default: both, sim first | arena => SITL => real |
| Q3 how B is given | default: offset from A, tolerance 0.3 m | odometry origin at A, decoder row 31 |
| Q4 scoring | default: IMAV-like, completion first | reliability over speed |
| Q5 sensors | default: downward flow + rangefinder, **no obstacle sensor** | intake 3.4 "None" => known-map planning only |
| Q6 indoor / outdoor | brief: indoor; default: no venue positioning | VIO or flow, row 33 |
| Q7 obstacles | brief: obstacles; default: unknown, moved between runs | sensed map + replan |
| Q8 compute | default: ground laptop | 0.7x if scored like IMAV |
| Q9 additions | default: tags allowed, firmware locked | AprilTag at A and B |
| Q10 deliverable | default: live run + deck, best of 2 | demo script + pitch |

Q5 and Q7 defaults together hit the intake's own hard gate: section 3.4 says "Unknown obstacles +
no sensor is a hard gate: ask the organisers again before committing". The intake gives no
default that resolves it (blocker 5). This run continued on the assumption that a range sensor
or a prior map would be announced.

## Total time

| Span | Wall | Source |
|---|---|---|
| Whole run, temp dir created => site checked | 36 min 47 s (15:42:33 => 16:19:20) | temp dir birth time, step clock |
| Of which: getting the clone to finish | 15 min 11 s (15:42:33 => 15:57:44) | clone logs, blocker 1 |
| Of which: decode => site checked | 15 min 15 s (16:04:05 => 16:19:20) | timing script creation time, step clock |
| Commands only (sum of the timed rows below, both site attempts, both arena smokes) | 6 min 51 s (410.89 s) | timing table |

Agent reading and thinking time is the rest. It was not timed per document. Writing this page is
not included.

## Runbook as executed

Hops = files opened to get from the previous step to a working command. Commands ran from the
clone root (`$HUB`) unless shown. `$T` is the temp dir. Raw timings are in the
[timing table](#raw-timings).

### 1. Clone (wall 54.85 s on the attempt that finished; 1 hop: AGENTS.md)

```sh
git clone -q <this checkout> $T/hub < /dev/null
# real 54.85  user 0.26  sys 3.40 ; 3999 files, 66 MB, HEAD 96c1322
```

- Attempt 1 (no stdin redirect) hung past the 120 s tool timeout and the partial clone was removed.
- Attempt 2 in the background (`nohup`) finished, but its timer did not record (zsh
  `$EPOCHREALTIME` unset in that shell).
- Attempt 3 with `< /dev/null` finished in 54.85 s wall for 0.26 s user CPU: the time is waiting,
  not work. A local clone of 66 MB should take seconds; machine load (1-minute load average 87.19 on
  16 cores, measured 5 minutes later) is the likely cause, not verified.

### 2. Decode (wall 1.86 s, 1 hop: AGENTS.md)

```sh
python3 tools/query.py decode "Fly a small drone autonomously from A to B in an indoor arena with obstacles. Platform and sensors announced on the day."
```

```
row 31: Drone A=>B through obstacles in a close area or arena  (score 30.344)
row 33: Indoor drone flight through VIO loss and recovery  (score 17.815)
row 32: Drone flight to a visual goal B: marker, landing pad or tag  (score 11.299)
```

Works. Rows 31 and 33 are the right picks for this brief. Output is 8396 bytes; the row 31 "risk"
field alone is one paragraph of 417 words, so an agent reads it once and moves on.

### 3. Read intake and cheat sheet (2 hops: AGENTS.md => intake, intake => cheat sheet)

| File | Lines | Words |
|---|---|---|
| [day1-close-area-intake.md](day1-close-area-intake.md) | 398 | 4351 |
| [cheatsheets/close-area-a-to-b.md](cheatsheets/close-area-a-to-b.md) | 185 | 1942 |

Both read in full. The intake's section 2 has the two smoke commands; the cheat sheet's section 2
has the same arena command with `--out /tmp/arena`. The intake copy has no `--out`, so as written
it overwrites the committed `samples/close-area-arena/results/straight_random_0.*` (blocker 8).
Not timed separately: reading is agent time inside the 16:04:05 => 16:04:58 window, with decode
(the intake was read once before the clone as well).

### 4. Smoke tests and sample venv (0 extra hops: commands are in intake section 2)

```sh
(cd templates/drone-adapter && python3 -m unittest -v && python3 example_loop.py)        # wall 4.54 s
# Ran 10 tests ... OK ; goal=(5.0, 3.0, 1.0) final_distance_m=0.096 t_s=8.00 collided=False
cd samples/close-area-arena
uv venv .venv && uv pip install --python .venv -r requirements.txt                       # wall 5.89 s
# Using CPython 3.11.15 ; Resolved 12 packages in 1.65s ; numpy 2.4.6, scipy 1.17.1, matplotlib 3.11.2
.venv/bin/python run.py --planner straight --layouts 20 --seed 0 --out $T/arena-out    # wall 75.69 s
# | straight | random | 20 | 40.0 | 0.0 | 60.0 | 0.0 | 16.94 | 0.383 |
# wall 1.5 s for 20 layouts
```

- Both smoke results match the intake's expected output: 10 tests OK, `final_distance_m=0.096`;
  straight reached 40 %, collision 0 %, stuck 60 % (synthetic).
- The uv cache on this machine already held the wheels, so 5.89 s is a warm-cache install, not
  the cold 14.68 s case in [flight-repo](../templates/flight-repo/README.md#brief-to-first-flight).
- The arena run took 75.69 s wall for 1.78 s CPU; the script itself reports 1.5 s. The same
  command again took 9.06 s wall (1.51 s CPU). The first Python start on a fresh venv waits, as
  flight-repo's README already reports (20.89 s and 205.89 s there, cause not found). The intake
  says "about 2 s each" (blocker 3).
- Host `python3` is 3.14.6; uv picked CPython 3.11.15 for the venv. AGENTS.md and the brief say
  3.12 tooling. Nothing broke on either version in this run.

### 5. `make first-flight` in a copy of flight-repo (wall 0.67 s fail, then 39.71 s; 2 hops: flight-repo README, its Makefile)

The README says to clone flight-repo at H+0 as the team repo, so it was copied out of the hub:

```sh
cp -R $HUB/templates/flight-repo $T/team && cd $T/team
make first-flight                                                    # rc=2, 0.67 s
# uv venv ../../samples/close-area-arena/.venv && ...
# error: File not found: `../../samples/close-area-arena/requirements.txt`
```

The failed target still ran `uv venv ../../samples/close-area-arena/.venv`, which created an
empty venv at `/tmp/samples/close-area-arena/.venv`, outside both the team repo and the hub
(removed after the run). The fix was found in the Makefile, not the README:

```sh
make first-flight ARENA=$HUB/samples/close-area-arena SAFETY=$HUB/samples/close-area-safety-filter   # 39.71 s, rc=0
# score input=synthetic adapter=arena:random:0 fault=truth planner=arena:astar_esdf safety=arm:F2 reached=True final_dist_m=0.165 t_s=21.10 collided=False min_clearance_m=0.827 ...
# outcome          reached
# time to goal     19.76 s   (run ends at 19.76 s, 0.299 m from B)
# min clearance    0.8268 m
# wrote results/first_flight_score.json, results/first_flight.png
make test ARENA=... SAFETY=...                                       # 5.62 s: 8 tests OK, arena smoke ok
```

Result matches the committed first flight exactly (19.76 s, 0.8268 m, synthetic). Wall 39.71 s
against the README's warm 4.94 s and 2.48 s; the venv was warm, so this is load. The target also
overwrites the copied `results/first_flight*` files, which is fine in a team copy.

### 6. Pick a planner from the benchmark README (1 hop)

[close-area-benchmark](../samples/close-area-benchmark/README.md) has no "pick this" table; the
pick comes from its "Best planner per family" paragraphs and the reading notes. For this brief
(indoor rooms, obstacles moved between runs, sensor unknown):

- **Pick: `astar_known` (A* + ESDF on a prior map) with F2 under it**, the same stack
  `make first-flight` flies. 100 % reached, 0 % collisions in all 8 families on both presets
  (20 layouts each, seed 0, true pose, synthetic). Needs a map or a first pass of the room, which
  the relocalization headline also needs.
- **Fallback without a map:** `astar_unknown` on a dense sensor (office 95 %, warehouse 55 %,
  ideal preset); on a Crazyflie-like 4-beam sensor `astar_unknown_f2` (office 50 / 5,
  maze 55 / 0). All synthetic, same source.
- **No benchmark row covers the intake's Q5 default** (no obstacle sensor). See blocker 5.

Not run: the planner pick was not re-flown here (the full matrix is about 5.5 min on 14
processes per the README).

### 7. Relocalization demo (venv 0.41 s, run 55.31 s; 2 hops plus a grep)

The relocalize README's Run section lists `experiment.py` and, further down, `run_disambiguate.py`
without the demo's `--out` and query line. The demo command lives in
[demo-script-close-area.md](../templates/demo-script-close-area.md), found with a grep (blocker 4).

```sh
cd samples/close-area-relocalize
uv venv .venv && uv pip install --python .venv -r requirements.txt        # 0.41 s (numpy, scipy from cache)
.venv/bin/python run_disambiguate.py --layouts 100 --seed 1 --arms single,multi,multi_ig --out .venv/demo-out
.venv/bin/python -c "...runs[97]..."                                     # both: 55.31 s wall
```

```
| jump | (f) multi_ig | 100 | 100.0 | 0.0 | 0.0 | 346 | 0 | 2 | 0.4 / 0.4 / 5.0 | 6 | 6 => 6 / 0 / 0 | 2.55 | 0.501 |
wall 42.1 s
single reached [..., (13.0, 0.2, 'accepted', 0.6281), ...]
multi stuck [(2.7, 0.4, 'accepted', 0.0064), (13.0, None, 'open', None)]
multi_ig reached [(2.7, 0.4, 'accepted', 0.0064), (13.0, 1.7, 'accepted', 0.0748)]
```

Works. All six table rows are identical to the committed
[disamb_random_1.md](../samples/close-area-relocalize/results/disamb_random_1.md) (checked with
`diff`), and the run-97 line matches the demo script's expected output (0.6281 m commit for
`single`, `multi` open, `multi_ig` accepted after 1.7 s at 0.0748 m). Synthetic, seed 1. `git
status` in the clone stayed clean: `--out .venv/demo-out` keeps `results/` untouched.

### 8. Three judge-drill answers (1 hop: [judge-drill-close-area.md](../templates/pitch/judge-drill-close-area.md))

Picked the three questions most likely for this brief, where the platform is unknown. Numbers
are from the run in step 7 where marked "re-run", else from the drill page and its sources.

**Q1 "Is this only simulation?"** "Yes, relocalization is simulation only. On held-out seed 1,
100 random layouts per fault, hover plus a disambiguating move reached B in 100 % of dropout and
jump runs, 0 collisions, 0 wrong commits; we re-ran it today and got the same table. The estimator
alone reached 36-64 % on seed 0. Drift is calibrated to real OpenVINS, 1.5 % RPE over 10 m on
UZH-FPV." Labels: 100 % `[synthetic, re-run]`; 36-64 % `[synthetic]`; 1.5 % `[real dataset]`.

**Q6 "What happens on a Crazyflie with 4 beams?"** "Not measured. Our acceptance rule needs 10
returns per scan and a Multi-ranger gives at most 4, so it would hover and never accept. On a
Crazyflie we would accumulate scans over a short yaw sweep. For context, 4 beams drop unknown-map
A* from 95 to 35 % reached in office layouts, in simulation." Labels: relocalization no number;
95 => 35 % `[synthetic]`.

**Q14 "What if the room was never mapped?"** "Then there is nothing to match against and this
method does not apply. We need a floor plan or one first pass of the room. Without either we
hover and land, and that fallback is not measured." Label: no number.

Fit check: the three answers are 66, 54 and 37 words, inside the drill's 50-70 word estimate for
20 s or under it. Not spoken or timed aloud.

### 9. Serve the site, open showcase and playground (2 hops: [site README](../site/README.md), [playground README](../site/playground/README.md))

```sh
python3 -m http.server 8765 --bind 127.0.0.1      # from the clone root; answered on the first poll
node $T/shoot.mjs                                 # own CDP script, headless Chrome 140.0.7339.208, 1280 x 900 viewport
```

- A plain `chrome --headless=new --screenshot --virtual-time-budget=20000` on the showcase wrote a
  PNG but never exited (killed after 180 s). The hub has no showcase screenshot script, and
  `measure_playground.mjs` writes into `site/playground/results/`, so a 71-line CDP script in the
  temp dir did the checks.
- **Showcase** (`?family=office&planner=astar_known&vs=vfh_plus&view=side`): loaded in 4.6 s,
  0 console errors. Counters 923 repos, 399 papers, 58 samples, 81 guides. Replay badges
  "REACHED B" (A* known map) and "STUCK" (VFH+); results grid 15 rows. The hero line still says
  "a safety filter keeps it safe when the drone is wrong about where it is", the headline that
  failed its kill test (blocker 6).
- **Playground, attempt 1** (site_check, wall 134.02 s): Python never got ready. It stalled at
  "step 2 of 4: numpy + scipy wheels ... (6.0 of about 22 MB downloaded)" for 122.5 s, then
  `load failed: Failed to fetch`. The local server logged every request as 200; `curl` fetched the
  14.0 MB scipy wheel from cdn.jsdelivr.net in 0.47 s a minute later. Cause not found (blocker 7).
- **Playground, attempt 2** (site_check2, wall 23.26 s for both pages): "Python ready in 5.5 s
  (22.2 MB downloaded this visit)", 6.15 s by the harness. Run on `random_0`, A* known map, ideal
  sensor, no fault: reached, 19.38 s, min clearance 0.5647 m, path 23.838 m, 0.812 s of Python,
  0 console errors. Same numbers as the playground README's native parity (synthetic).
- Viewport screenshots were taken (showcase replay, showcase results, playground loading,
  playground run) and checked by eye; they lived in the temp dir and were deleted with it.

## Blockers

Status 2026-11-09: blockers 1, 3, 4, 5 and 8 fixed by loop-61; 6 fixed in the wrap-up; 2 and 7 are in loop-59 and loop-63.


| # | Step | File | What broke | Suggested fix |
|---|---|---|---|---|
| 1 | Clone | (agent shell, not the hub) | `git clone` of the local checkout hung past 120 s in the agent's shell; with `< /dev/null` it finished in 54.85 s wall, 0.26 s CPU | Harness issue more than a hub issue. AGENTS.md could say: run long commands with stdin closed or in the background |
| 2 | First flight | [templates/flight-repo/Makefile](../templates/flight-repo/Makefile), [README](../templates/flight-repo/README.md#brief-to-first-flight) | Copied out of the hub (as the README says to do at H+0), `make first-flight` fails in 0.67 s: `ARENA` defaults to `../../samples/close-area-arena`. The failed target first creates a stray venv at `../../samples/close-area-arena/.venv` relative to the copy | Makefile: check `$(ARENA)/requirements.txt` before `uv venv` and print "set ARENA=<hub>/samples/close-area-arena SAFETY=<hub>/samples/close-area-safety-filter". README: show the `ARENA=` / `SAFETY=` form in "Brief to first flight" |
| 3 | Arena smoke | [day1-close-area-intake.md section 2](day1-close-area-intake.md#2-if-we-only-get-3-answers) | "About 2 s each" for the smoke tests; the first run on a fresh venv took 75.69 s wall (1.78 s CPU), the second 9.06 s | Say "first run on a fresh venv can take 1-4 minutes of waiting" next to the 2 s, as flight-repo's README already budgets 4 minutes |
| 4 | Relocalization demo | [samples/close-area-relocalize/README.md](../samples/close-area-relocalize/README.md) | The demo command (`run_disambiguate.py --seed 1 --arms single,multi,multi_ig --out .venv/demo-out` plus the run-97 query) is only in [demo-script-close-area.md](../templates/demo-script-close-area.md); the README's top Run block lists `experiment.py`, which is not the headline arm | Put the demo command first in the README's Run block, or link it from AGENTS.md step 4 next to the relocalize sample |
| 5 | Intake defaults | [day1-close-area-intake.md](day1-close-area-intake.md#1-questions-in-the-order-to-ask) | Q5 default "no obstacle sensor" plus Q7 default "unknown and moved" is the hard gate in section 3.4. With no answers the defaults lead to a stack the page says not to commit to; no benchmark row covers "no sensor" | Change the Q5 default to the most likely small-drone sensor (for example a 4-beam ToF fan, which the arena's `crazyflie` preset models), or name the gate in the Q5 row |
| 6 | Showcase | site/showcase.html line 32 (hero lead) | Hero says the story is "a safety filter keeps it safe when the drone is wrong about where it is". The hub's headline is relocalization after VIO loss; the filter headline failed | Rewrite the lead to the relocalization story (the page is hand-written, not generated) |
| 7 | Playground | [site/playground/README.md](../site/playground/README.md) | First load failed after 122.5 s ("Failed to fetch", 6 of 22 MB) under load; the retry was ready in 6.15 s. Needs cdn.jsdelivr.net; no retry button, no offline path | Add a retry on fetch failure in the worker; state in the README that the playground needs the CDN and fails offline. Test once on venue Wi-Fi |
| 8 | Arena smoke | [day1-close-area-intake.md section 2](day1-close-area-intake.md#2-if-we-only-get-3-answers) | The intake's arena command has no `--out`, so it writes into the sample's committed `results/` (the cheat sheet warns about this and uses `--out /tmp/arena`) | Add `--out /tmp/arena` to the intake command |

Nothing blocked the path for good. With the fixes found in the run (stdin redirect, `ARENA=` and
`SAFETY=`, the demo-script command, a retry), every step produced the hub's published output.

## Raw timings

From `t.sh` (`/usr/bin/time -p`, stdin from `/dev/null`) and a step clock, in the temp dir.
Columns: step, wall s, user s, sys s, exit code, 1-minute load average before => after. User CPU
counts only waited-for children, so it reads low for the multiprocessing relocalize run.

```
clone             54.85   0.26  3.40  rc=0  (attempt 3; attempt 1 hung > 120 s)
decode             1.86   0.07  0.03  rc=0  load=68.21->66.43
adapter_smoke      4.54   0.03  0.01  rc=0  load=93.80->100.62
arena_venv         5.89   0.06  0.16  rc=0  load=109.11->112.62
arena_smoke       75.69   1.78  0.22  rc=0  load=121.88->130.71
arena_smoke_warm   9.06   1.51  0.09  rc=0  load=123.88->128.08
ff_naive           0.67   0.01  0.03  rc=2  load=135.00->135.00
ff_hubpaths       39.71   1.72  0.43  rc=0  load=140.09->143.08
team_test          5.62   0.69  0.22  rc=0  load=136.70->133.12
reloc_venv         0.41   0.03  0.08  rc=0  load=126.87->126.87
reloc_demo        55.31   0.02  0.01  rc=0  load=117.73->86.06
site_check       134.02   0.19  0.06  rc=0  load=68.39->38.67   (playground failed)
site_check2       23.26   0.13  0.03  rc=0  load=42.56->40.70   (both pages ok)
```

Step clock: intake and cheat sheet read by 16:04:58, first flight done 16:09:34, planner picked
16:09:51, relocalization demo done 16:11:06, site done 16:19:20.

## Machine and caveats

- macOS arm64, 16 cores, host Python 3.14.6, uv 0.11.23, Node at /opt/homebrew/bin/node,
  Chrome 140.0.7339.208. Venvs on CPython 3.11.15 (uv's pick).
- The machine ran 6 agent sessions at once: 1-minute load average 38.67 to 143.08 during the run
  on 16 cores. Every wall time here is inflated by that load and is an upper bound, not a
  team-laptop estimate. CPU times are the better guide.
- The uv cache was warm (shared on the machine), so venv times are not cold-cache times.
- One agent, no team: the intake questions were answered by defaults, not by asking anyone.

## Not verified

- No cold-cache venv install; no run on an idle machine; no Linux.
- The planner pick was not re-flown; benchmark numbers are quoted from its README.
- Judge-drill answers were written and word-counted, not spoken or timed.
- Playground attempt 1's failure cause (CDN, load or Chrome) was not found.
- The clone slowness cause was not found.
- Drivers, SITL and anything on a vehicle were out of scope for this path and not touched.
