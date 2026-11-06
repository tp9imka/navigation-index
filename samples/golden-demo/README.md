# Golden demo: GPS drag on a flying ArduCopter, caught and survived

<!-- about: repo:ardupilot/ardupilot, repo:ardupilot/pymavlink, repo:maplibre/maplibre-gl-js, repo:cvg/lightglue, repo:rasterio/rasterio -->

The minute-one demo for judges. An ArduCopter SITL flies an AUTO survey; at t = 25 s its GPS
starts to drift east. A companion process checks GNSS against an independent dead-reckoning +
visual-geolocation reference, raises the alarm, and switches EKF3 to a non-GPS source set. The
contrast run has the same attack and no reaction: the copter believes it is on the survey line
while it really drifts 75 m off it.

Two versions share the same files:

- **v1** (default `./run.sh`): SITL GPS dragged with `SIM_GPS_GLITCH_X/Y` (position only),
  visual geoloc = truth + 1.5 m noise, navapp windowed chi-square detector. Reference output in
  `data/`, numbers below.
- **v2** (`./run.sh --v2`): GPS injected by the companion as MAVLink `GPS_INPUT`, so the drag can
  be coherent (position and velocity together); visual geoloc from real image matching (NAIP 2019
  frame rendered at the SITL truth position, matched against NAIP 2023 with ALIKED + LightGlue);
  solution-separation FDE with a protection level (ported from `samples/altpnt-integrity`); a
  GNSS-velocity vs VIO test; a 52-flight Monte Carlo. Reference output in `data/v2/` and
  `data/mc_summary.json`.

![dashboard at t=100 s](screenshots/golden-t100.jpg)

v1 colours: blue = EKF output with the monitor, white = where that copter really flew. Green =
EKF output without the monitor (it thinks it is on the line), orange = where that copter really
flew. Red dots = spoofed GPS fixes, purple = visual-geoloc fixes. Detection moment:
[t = 36 s](screenshots/golden-t36.jpg). v2 adds a yellow track (the companion's own fused
solution) with the PL ring against a 50 m AL: [v2 at t = 60 s](screenshots/v2-t60.jpg).

## v1 results (ran 2026-11-06, one run each, seed 7)

ArduCopter `Copter-4.6.3` SITL in Docker (`nav-sitl-ardupilot:copter-4.6.3` from
`samples/sitl-docker`), linux/arm64 on Apple Silicon, pymavlink 2.4.50, Python 3.12. Numbers
from `data/summary.json`, produced by `to_navdash.py` from the raw logs.

| | Monitor on | No monitor |
|---|---|---|
| Alarm (windowed chi-square over gate) | t = 34.4 s | same test in shadow mode fired at 34.4 s, no action |
| Time to detect after attack onset | **9.4 s** (spoof offset 9.3 m) | - |
| Response | `MAV_CMD_SET_EKF_SOURCE_SET` 2 at 34.4 s, ACK `MAV_RESULT_ACCEPTED` | none |
| Max cross-track deviation from the planned path after onset (truth) | **7.6 m** | **75.0 m** |
| Cross-track deviation at mission end | 0.5 m | 62.4 m |
| Max EKF horizontal error vs truth | 7.7 m (at 34.3 s, just before the switch) | 88.3 m (at mission end) |
| EKF `GPS_GLITCHING` flag after onset | 0 reports | 0 reports |
| EKF `pos_horiz_variance` max after onset | 1.34 (on ExternalNav, see "Lane switching") | 0.50 (3 of 181 reports > 0.5) |
| Mission (AUTO start to last WP + 5 s) | 117.9 s | 114.9 s |

The no-monitor row is the point: ArduPilot's own EKF never raised `GPS_GLITCHING` and its
normalized position variance touched 0.5 only three times while the vehicle ended 88 m from
where it believed it was. A slow drag stays inside the EKF's innovation gates.

Before the attack the monitor's windowed statistic stayed at 9.9 (monitor run) and 17.8
(baseline) against a gate of 52.4; no epoch was marked suspect before onset. That margin is
flattering: SITL's simulated GPS has no horizontal noise (v2 injects a noisy GPS instead).

## v2 reference run (ran 2026-11-06, one run each, seed 7, speedup 1)

`./run.sh --v2 --update-reference`: injected GPS, coherent 1 m/s drag, replayed real visual
geoloc, `ss+vel`, `--extnav reference`, 150 m AGL. Numbers from `data/v2/summary.json`.

| | Monitor on | No monitor |
|---|---|---|
| First alarm | velocity test at t = 28.0 s (**3.0 s** after onset, offset 3.0 m) | same test in shadow at 28.6 s |
| Other detectors (shadow) | chi2 +19 s, SS +27 s (DR witness blamed GNSS) | chi2 +15.9 s, SS +22 s |
| Response | `MAV_CMD_SET_EKF_SOURCE_SET` 2, ACK `MAV_RESULT_ACCEPTED` | none |
| Max cross-track deviation after onset (truth) | **6.8 m** | **75.0 m** |
| Max EKF horizontal error vs truth | 8.0 m | 93.7 m |
| EKF `GPS_GLITCHING` after onset | 0 reports | 0 reports |
| SS HPL median before onset / AL | 12.8 m / 50 m | 12.8 m / 50 m |
| SS epochs unavailable (PL >= AL) / misleading (error > PL) | 14 / 0 of 120 | 0 / 3 of 117 |
| Visual-geoloc fixes sent / failed (whole flight) | 67 / 52 | 71 / 46 |
| EKF lane switches after the source switch | 0 | - |

## v2 Monte Carlo (ran 2026-11-06, 52 flights)

`python mc.py --lanes 3 --speedup 3 --update-reference`: seeds 1-4 x drag rate 0.3 / 1 / 3 m/s x
spoof position / coherent, each flown twice (monitor acts, baseline shadow), plus 4 no-spoof
flights. All v2 settings: injected GPS, replayed real visual geoloc (1 Hz, 54-64 % fix rate per
group), `--extnav reference`, action detector `ss+vel`, 150 m AGL, onset t = 25 s. **Wall time
1201 s (20 min)** for 52 flights, 3 SITL containers in parallel at `--speedup 3`, 65 s per
flight (median), on a 12-core Apple Silicon host that other jobs kept at load 60-100. All 52
completed the mission (no failsafe). Aggregate: `data/mc_summary.json`; per-flight logs stay
in `runs/mc/`.

Action detector (SS or velocity test, whichever fires first), 4 monitor flights per row; TTD =
first alarm minus onset, 1 s resolution; deviation = truth cross-track from the planned path
after onset:

| Spoof | Rate m/s | TTD s (min / med / max) | missed / FA | Max cross-track dev, monitor (min / med / max) m | Same, no monitor m | EKF `GPS_GLITCHING`, no-monitor runs |
|---|---|---|---|---|---|---|
| position | 0.3 | 40.5 / 45 / 48 | 0 / 0 | 5.4 / 8.4 / 11.1 | 24.5 / 25.7 / 27.2 | 0 of 4 |
| position | 1 | 21 / 22.5 / 24 | 0 / 0 | 16.2 / 17.4 / 18.6 | 75 / 75 / 75 | 0 of 4 |
| position | 3 | 6 / 6.2 / 7 | 0 / 0 | 5.5 / 7.4 / 9.8 | 61 / 64.6 / 66.6 | 4 of 4 |
| coherent | 0.3 | 1 / 37.4 / 46 | 0 / 0 | 6.5 / 11.1 / 29.1 | 27.4 / 28.8 / 29.4 | 0 of 4 |
| coherent | 1 | 2.5 / 2.8 / 4 | 0 / 0 | 6.3 / 7.4 / 10.1 | 75 / 75 / 75 | 0 of 4 |
| coherent | 3 | 0.3 / 1 / 1 | 0 / 0 | 5.7 / 5.8 / 6.3 | 83.6 / 84 / 86.9 | 4 of 4 |

Each detector on its own (8 flights per row: monitor + shadow baseline; a detector's first
alarm before onset counts as a false alarm and gives that flight no TTD):

| Spoof | Rate m/s | chi2 (v1 detector) | SS | vel |
|---|---|---|---|---|
| position | 0.3 | 8/8, median 44-45 s, FA 0 | 8/8, 45-46 s, FA 0 | 0/8 (velocity untouched) |
| position | 1 | 8/8, 15.5-17.5 s, FA 0 | 8/8, 22.5-23.5 s, FA 0 | 0/8 |
| position | 3 | 6/8, 6 s, FA 2 | 8/8, 5.4-6.2 s, FA 0 | 0/8 |
| coherent | 0.3 | 6/8, 35-43 s, FA 2 | 8/8, 37-45 s, FA 0 | 0/8 (0.3 m/s is under its noise) |
| coherent | 1 | 8/8, 16.9 s, FA 0 | 8/8, 23 s, FA 0 | 8/8, 2.8-3.8 s, FA 0 |
| coherent | 3 | 8/8, 5-6.5 s, FA 0 | 8/8, 5-5.2 s, FA 0 | 8/8, 1 s, FA 0 |
| none (4 flights) | - | **FA 4 of 4** | FA 0 | FA 0 |

What this says:

- **The coherent spoof is the hard case for the autopilot, not for this monitor.** ArduPilot's
  EKF raised `GPS_GLITCHING` only at 3 m/s; at 0.3 and 1 m/s it followed both spoof types to
  25-29 m and 75 m (capped by the survey geometry) without a flag. The companion's GNSS-vs-VIO
  velocity test catches a coherent drag of 1 m/s in about 3 s and 3 m/s in about 1 s, because a
  coherent spoofer has to lie about velocity and VIO does not. A position-only drag leaves
  velocity alone, so only the position tests (SS, chi2) see it, slower.
- **Slow drags are slow to catch with real visual geoloc.** At 0.3 m/s the SS alarm needs
  about 45 s (13 m of offset); the 7 m visual-geoloc sigma that keeps false alarms away is what
  sets this. With the simulated 1.5 m geoloc of v1 the chi-square test caught 1 m/s in 9.4 s.
- **v1's chi-square detector is unusable with real geoloc**: 4 of 4 no-spoof flights alarmed.
  Its reference is the visual-geoloc fixes themselves, and their 3-5 m registration bias against
  an unbiased GNSS fills the 10-epoch window. SS (0 of 4) and the velocity test (0 of 4) did not.
- The coherent 0.3 m/s row has one SS alarm 1 s after onset (seed 4): an offset of 0.3 m cannot
  cause that, so treat it as a false alarm that happened to land after onset.
- Max deviation with the monitor stayed 5.4-18.6 m except one coherent 0.3 m/s flight (29.1 m,
  detected late). Position 1 m/s is the worst common case (17 m median): SS needs 22 s there.
- **SS protection level**: median HPL before onset 12.8 m (AL 50 m). After GNSS exclusion the
  remaining branch is dead reckoning and the HPL grows; 801 of 2875 monitor-flight epochs were
  unavailable (PL >= AL or ambiguous). Misleading epochs (SS error > HPL) were 0 in the no-spoof
  flights and appeared during slow undetected drags (e.g. 33-49 over 4 flights at 0.3 m/s): the
  PL does not bound a fault that has not separated the branches yet, which is the textbook
  limit of SS with a 1e-3 missed-detection allocation and two sources.
- EKF lane switches after the source switch: 1 switch in 1 of 24 v2 monitor flights (v1: 4-6
  per flight, see below).


## Run

```sh
cd samples/golden-demo
PYTHON=/path/to/venv/bin/python ./run.sh   # v1: both flights + conversion, ~6 min
./run.sh monitor                            # one flight only (no conversion)
./run.sh --v2                               # v2: coherent 1 m/s drag, replayed real geoloc, SS + PL, ~8 min
SPOOF=position RATE=3 ./run.sh --v2         # other v2 attacks (SPOOF=position|coherent|none)
./run.sh --v2 --live monitor                # v2 with live ALIKED+LightGlue matching in the loop
./run.sh --update-reference                 # v1, and refresh the committed data/
./run.sh --v2 --update-reference            # v2, and refresh the committed data/v2/
python mc.py                                # Monte Carlo, 52 flights, 20 min here (3 lanes, speedup 3)
python mc.py --experiment lanes --seeds 1 2 # EKF lane-switch experiment (speedup 1)
python vgeo_real.py table                   # rebuild data/vgeo_table.json (~29 min CPU here)
./screenshot.sh 100                         # optional, needs Chrome + Node 22+; DATA=data/v2 for v2
python3 -m unittest -v test_to_navdash test_golden_v2   # 17 tests, no SITL
```

**Outputs go to `runs/` (git-ignored) by default**: raw logs `runs/{v1,v2}-{monitor,baseline}.raw.jsonl`,
dashboard input `runs/navdash-v1/` or `runs/navdash-v2/`, Monte Carlo `runs/mc/`. The committed
reference (`data/`, `data/v2/`, `data/mc_summary.json`) only changes with `--update-reference`.

Requirements: `PYTHON` needs `pymavlink` (`python3 -m venv .venv && .venv/bin/pip install
pymavlink==2.4.50`) for every mode. The unit tests run on plain `python3`: `test_golden_v2.py` guards
the `companion.py` import (which needs pymavlink) and skips the 2 tests that use it (17 tests, 2
skipped without pymavlink). `--live` and `vgeo_real.py table` need
the `samples/geoloc-license-clean` requirements (torch, LightGlue, OpenCV, rasterio) and its
data (`python ../geoloc-license-clean/download_data.py`; two NAIP GeoTIFFs, 94 MB + 27 MB).
The replay mode only needs the committed `data/vgeo_table.json` (39 KB), stdlib.

`run.sh` builds the SITL image from `../sitl-docker` if it is missing, starts a fresh container
`golden-sitl` per flight with SERIAL1 on `127.0.0.1:15766` (`PORT=`, `NAME=` override), and
removes it at the end. `mc.py` names its containers `golden2-mc<k>` on ports 15790+ (`--port0`,
`--prefix`). v2 starts SITL at `SITL_HOME=41.301800,-81.751397` (Aukerman Park, Ohio), inside the
NAIP window; the replay refuses to run if the EKF origin is more than 50 m from the table home.

Replay in the dashboard:

```sh
cd ../..                                   # repo root
python3 -m http.server 8000
# v1: http://localhost:8000/templates/demo-dashboard/index.html?manifest=../../samples/golden-demo/data/manifest.json
# v2: http://localhost:8000/templates/demo-dashboard/index.html?manifest=../../samples/golden-demo/data/v2/manifest.json
```

Add `&t=34&follow=0` to open at the alarm. The dashboard is `templates/demo-dashboard`, unchanged.

## What happens, step by step

1. **SITL** boots with `copter.parm` plus `golden.parm` (v2 adds `inject.parm`, `v2.parm`) via
   `docker cp` + `--defaults a,b,...`, because macOS Docker Desktop does not share `/tmp`. Source
   set 1 = GPS + compass + baro; set 2 = ExternalNav position (`EK3_SRC2_POSXY=6`, `POSZ=1` baro,
   `YAW=1` compass), `VISO_TYPE=1` (MAVLink). v1: `EK3_SRC2_VELXY=0`. v2: `EK3_SRC2_VELXY=6`
   (VIO velocity as `VISION_SPEED_ESTIMATE`), `GPS1_TYPE=14` (MAVLink GPS), `WPNAV_SPEED_UP=500`.
2. **Companion** (`companion.py`, pymavlink) requests the streams it logs, gets the EKF origin
   with `MAV_CMD_REQUEST_MESSAGE` (`GPS_GLOBAL_ORIGIN`) and uploads the mission. Its clock is the
   autopilot's `time_boot_ms`, so SITL `--speedup` works; every injected message is stamped in
   sim time (v1 used host wall clock; `--stamp host` reproduces that).
3. **GNSS.** v1: SITL's own simulated GPS. v2: `GPS_INPUT` at 10 Hz built from SITL truth
   (`SIMSTATE`, `SIM_STATE`) + 0.5 m white + 1.0 m Gauss-Markov (30 s) noise per axis, 0.1 m/s
   velocity noise, `time_week_ms` from sim time so `AP_GPS_MAV` jitter correction works. 5 Hz
   failed `GPS 1: not healthy` under host load: AP_GPS wants an average frame gap under 215 ms.
4. **Alt-PNT stream from boot**: visual-geoloc fixes go out as `VISION_POSITION_ESTIMATE` in the
   EKF origin's NED frame, from before takeoff, so ExternalNav is aligned before anyone needs it.
   - v1 `--vgeo sim`: truth + 1.5 m Gaussian, 5 Hz.
   - v2 `--vgeo replay`: 1 Hz, from `data/vgeo_table.json` (see "Real visual geoloc").
   - v2 `--vgeo live`: in-loop matching in a worker thread; each fix is carried forward to
     "now" with VIO before sending, because a match takes seconds.
   - v2 `--extnav reference`: after AUTO starts, ExternalNav gets the companion's GNSS-free
     reference (VIO dead reckoning + visual-geoloc fixes) at 5 Hz with its sigma as covariance,
     instead of raw fixes. Why: see "ExternalNav starvation".
5. **Flight**: GUIDED, arm, takeoff (v1 30 m, v2 150 m AGL), AUTO. Survey: 400 m north, 150 m
   east, 400 m south at 10 m/s. t = 0 is AUTO entry.
6. **Attack** from t = 25 s, toward 090 deg, cap 150 m. v1: `SIM_GPS_GLITCH_X/Y` written every
   0.5 s; in Copter-4.6.3 (`libraries/SITL/SIM_GPS.cpp`) the glitch is added to lat/lon after the
   lag model and velocity is untouched (`SIM_GPS_VERR` is `VERR * rand_float()`, random, not a
   drag; no 4.6 parameter drags velocity). v2: the offset goes into `GPS_INPUT`; `--spoof
   position` leaves velocity at truth, `--spoof coherent` adds the drag rate to velocity too.
7. **Monitors**, every 1 s, all running in every flight (one of them drives the action):
   - `chi2` (v1): navapp `DeadReckoningFilter` on VIO velocity (truth + 0.1 m/s noise +
     (0.05, -0.03) m/s bias) updated with visual-geoloc fixes; navapp `ChiSquareMonitor` tests the
     GNSS innovation, 10-epoch window, false-alarm 1e-4. GNSS is tested, never fused.
   - `ss` (v2): solution-separation bank (`ss_fde.py`), see below.
   - `vel` (v2): windowed chi-square on GNSS velocity (`GPS_RAW_INT` vel/cog) minus VIO velocity,
     sigma 0.18 m/s, variance inflated by (|a| x 0.4 s)^2 because `GPS_RAW_INT` velocity lags
     the VIO sample in turns (the first test flight false-alarmed at the end of the first
     acceleration without it).
8. **Response**: on the first alarm of the chosen detector (`--detector chi2|ss|ss+vel`),
   `MAV_CMD_SET_EKF_SOURCE_SET` (42007) param1 = 2. If SS probation later re-admits GNSS (the
   other source was blamed), the companion switches back to set 1. Baseline mode runs everything
   in shadow and never acts.
9. **Conversion**: `to_navdash.py` writes `navdash/1` tracks, events, a zone and `summary.json`.

## Solution separation and protection level (v2)

`ss_fde.py` ports `Monitor` from `samples/altpnt-integrity/altpnt_integrity.py` (separations,
detection, exclusion, probation, re-admission, rewind, HPL) and imports its constants
(`P_FA` 1e-5, `P_MD` 1e-3, `IR_FF` 1e-7, hold 30 s, probation 45 s, lookback 30 s) and `mat` /
`q_inv` unchanged. Differences, all in the module docstring:

- 4-state filter `[e, n, b_ve, b_vn]` propagated with VIO velocity (the companion has no IMU
  stream), instead of the 8-state INS error model.
- Two monitored absolute sources (GNSS, visual geoloc). With both active a separation fault is
  detectable but not identifiable from the bank. First try: VIO dead reckoning replayed from a
  30 s old snapshot as a third witness; if exactly one source fails a chi-square test against it,
  exclude that one. Otherwise the altpnt path: alert (unavailable), drop both, probation, blame.
  In practice the witness was rarely decisive (30 s of DR is wide), so most detections went
  through the ambiguous alert and a GNSS blame about 45 s later.
- 3 consecutive chi-square gate rejections exclude a source. A 3 m/s drag is gated by every
  filter in the bank, so the separation never grows and plain SS never fires; the unit test
  `test_fast_drag_is_excluded_by_persistent_gating` pins this.
- `HPL = max(K_ff sigma_main, max_j(T_j + K_md sigma_j))`. The dashboard's PL ring is this HPL
  around the companion solution (`ss-monitor.jsonl`, primary), not around ArduPilot's EKF,
  which reports no metric accuracy. AL = 50 m (the altpnt-integrity default).
- After GNSS is excluded, the remaining "fault in visual geoloc" branch is pure dead reckoning,
  so its covariance and the HPL grow with time: one absolute source cannot bound its own fault.
  The dashboard shows the PL ring turning red (PL > AL) well before the copter is in trouble.

## Real visual geoloc (v2)

`vgeo_real.py` renders a 640 x 480 nadir frame (85 deg HFOV, 150 m AGL => 0.43 m/px) from the
**2019** NAIP orthophoto (0.6 m, October) at a given position and yaw, applies the photometric
changes of `geoloc-license-clean/synth_frames.py`, and localizes it with
`geoloc-license-clean/geoloc.py` (ALIKED + LightGlue + MAGSAC, unchanged) against the **2023**
NAIP orthophoto (0.3 m, May): prior 20 m off, search radius 60 m, heading noise 3 deg. The
camera is assumed gimbal-stabilised (no tilt).

Probes before choosing the geometry (12, 8, 10, 12 random frames, CPU): cross-season matching at
80 m and 120 m AGL with 70 deg HFOV gave **0 fixes**; same-season (render and match on 2023) at
80 m gave 6/6 at 0.15-0.29 m, so the rendering is right and the epoch gap is what fails;
200 m / 70 deg gave 6/8 (ALIKED), 2/8 (DISK), 1/8 (SIFT). The demo uses 150 m / 85 deg, a
similar footprint.

`data/vgeo_table.json`: 425 nodes on a 20 m grid over the flight area (+ room for a 120 m west
drift), one real match each, 1716 s wall (3.6 s per frame median, 12-core Apple Silicon under
heavy load from other jobs). **246 / 425 fixes (58 %)**; error median 3.3 m, p90 5.6 m, max
9.9 m; the residual is a consistent ~3.2 m east, -0.7 m north offset (registration difference
between the two NAIP epochs, not matcher noise); a band at roughly 140-280 m north has almost
no fixes (field / tree texture that does not survive the season change). Replay draws each fix
from one of the four surrounding nodes with bilinear weights, so failure zones and the bias keep
their spatial structure. The fixes are real matches; their timing and per-frame variability are
not (one frame per node).

**Live mode, one flight** (`./run.sh --live monitor`, coherent 1 m/s, seed 7, speedup 1,
ran 2026-11-06 next to another SITL): the worker matched one frame every ~3.5 s (median match
3.5 s on CPU), 23 of 34 attempts after AUTO gave a fix (68 %), fix error vs truth at send time
median 4.5 m, max 12.9 m (after carrying each fix forward with VIO over its 3.5 s latency).
The velocity test fired 3.0 s after onset, EKF switched to set 2, mission completed, max
cross-track deviation 7.8 m. SS fired at 27 s after onset, chi2 at 16 s. One flight, not a
statistic; the log stays in `runs/` (not committed).

## ExternalNav starvation (v2 finding)

With raw replayed fixes sent as ExternalNav (`--extnav fixes`, VISO noise 2 m), **4 of 4**
monitor flights of a first Monte Carlo pass detected the spoof, switched to set 2, and then hit
`EKF Failsafe: changed to LAND Mode` at t = 87-90 s, on the return leg over the no-fix band
(about 10 s without a fix; EKF variances were low, the flags dropped absolute horizontal
position). VIO velocity was being fused (`EK3_SRC2_VELXY=6`). Sending the companion's GNSS-free
reference instead (`--extnav reference`: VIO dead reckoning + fixes, continuous at 5 Hz, sigma
as covariance) completed both test flights and is the v2 default. Raw logs of the failing pass
are not committed; the numbers are from `runs/` of that pass.

The real-imagery fixes also caused a **pre-onset false alarm** with the visual-geoloc sigma at
5 m (chi-square at t = 20 s, SS ambiguous alert at 24 s, onset 25 s): the 4-5 m map-registration
bias pulled the reference away from an unbiased GNSS. v2 uses 7 m (overbounding p90 5.6 m),
which costs detection time; see the Monte Carlo.

## EKF lane switching after the source switch (v1 caveat, investigated)

v1 saw `EKF3 lane switch 0/1` every 10-20 s while on ExternalNav. In 4.6.3
(`AP_NavEKF3.cpp`, `UpdateFilter` core selection) a lane switches when the primary's error
score (`0.5 * (velTestRatio + posTestRatio)`, `errorScore()` in `AP_NavEKF3_Outputs.cpp`)
exceeds 1, or another lane's accumulated relative error is better by `EK3_ERR_THRESH`; a lane
must have been non-primary for 10 s, which sets the 10-20 s rhythm. So the switches are a
symptom of high position test ratios on ExternalNav, not a cause.

Experiment (`mc.py --experiment lanes`, v1 flight, chi-square, 1 m/s position drag, speedup 1,
seeds 1 and 2, lane switches after the source switch / EKF reports with pos variance > 0.5):

| Config | seed 1 | seed 2 |
|---|---|---|
| A: v1 exactly (host wall-clock timestamps) | 6 / 101 | 4 / 80 |
| B: sim-time timestamps | 5 / 86 | 5 / 95 |
| C: B + VIO velocity to the EKF (`EK3_SRC2_VELXY=6`) | 4 / 78 | 4 / 94 |
| D: B at 150 m AGL | 6 / 88 | 6 / 94 |
| E: B with GPS injected as `GPS_INPUT` (same position drag) | **0 / 2** | **0 / 1** |
| F: E + the v1 `PARAM_SET` traffic (zero glitch) | **0 / 0** | **0 / 0** |

Timestamps, VIO velocity, altitude and the 2 Hz `PARAM_SET` stream are ruled out. The
oscillation only appears when SITL's own simulated GPS is the GPS, even though source set 2 does
not use GPS for horizontal position. I did not find the mechanism in the EKF3 source; the v1
median EKF error after the switch stayed 0.1-3.4 m, so it is noisy, not divergent. v2 uses the
injected GPS: 1 lane switch in 1 of its 24 Monte Carlo monitor flights.

## Files

| File | What |
|---|---|
| `run.sh` | one command: two flights, logs, conversion (`--v2`, `--live`, `--update-reference`) |
| `golden.parm`, `inject.parm`, `v2.parm` | EKF3 source sets, `VISO_TYPE=1`; MAVLink GPS; VIO velocity + climb rate |
| `companion.py` | MAVLink companion: logging, mission, GPS injection, attack, alt-PNT stream, monitors, response |
| `ss_fde.py` | solution-separation FDE + HPL (ported from altpnt-integrity) and the velocity test |
| `vgeo_real.py` | frame renderer + real matcher (live worker, `table` builder); needs torch |
| `vgeo_replay.py` | stdlib replay of `data/vgeo_table.json` |
| `mc.py` | Monte Carlo and lane experiment runner, parallel SITL containers, aggregation |
| `to_navdash.py` | raw logs => `navdash/1` tracks, `manifest.json`, `zones.geojson`, `summary.json` |
| `test_to_navdash.py`, `test_golden_v2.py` | 17 tests: geometry, converter, SS/PL, velocity test, spoof model, replay, detections |
| `screenshot.sh`, `screenshot.mjs` | headless Chrome capture over the DevTools protocol |
| `data/` | v1 reference run (dashboard input) |
| `data/v2/` | v2 reference run (dashboard input, includes `ss-monitor.jsonl` with `pl_m`) |
| `data/vgeo_table.json`, `data/mc_summary.json` | real-match table; Monte Carlo aggregate |
| `runs/` | everything a run writes, git-ignored |

Reused unchanged: `templates/project-repo/src/navapp`, `templates/demo-dashboard`,
`samples/sitl-docker` (image), `samples/altpnt-integrity` (imported: constants, `mat`, `q_inv`),
`samples/geoloc-license-clean` (imported: `geoloc.Localizer`, `OrthoMap`, `synth_frames.photometric`).

## Dashboard tracks

| Track | Role | Source |
|---|---|---|
| `truth.jsonl` | truth | monitor run `SIMSTATE`; carries the ground-truth `attack_onset` event |
| `truth-baseline.jsonl` | truth (2nd) | baseline run `SIMSTATE` |
| `ss-monitor.jsonl` (v2) | fused, primary | companion SS main solution, `pl_m` = HPL, AL 50 m; health `unavailable` when PL >= AL or ambiguous |
| `ekf-monitor.jsonl` | fused (primary in v1) | monitor run `GLOBAL_POSITION_INT`; v1 health/alarm from the chi-square verdict; `source_switched` event |
| `ekf-baseline.jsonl` | fused | baseline run `GLOBAL_POSITION_INT` |
| `gnss.jsonl` | gnss | monitor run `GPS_RAW_INT` (spoofed) |
| `vgeo.jsonl` | altpnt | the visual-geoloc fixes (simulated in v1, replayed real matches in v2) |

v1 shows **95% radius "not stated" and PL "n/a"** on purpose: ArduPilot reports no horizontal
accuracy in metres for its fused solution (`EKF_STATUS_REPORT` variances are normalized test
ratios). v2's PL belongs to the companion's solution and is labelled so. The spoofing zone is a
circle around the flight area, not an emitter footprint.

## Limits and honest caveats

- **VIO is an oracle with noise** in both versions: truth velocity + white noise + constant
  bias. It is the anchor of every detector here; a real VIO with scale error, dropouts over
  water or texture-poor ground would weaken all of them.
- **v2 visual geoloc is real matching on synthetic frames**: rendered from a real orthophoto of
  a different year/season, nadir, no lens model, no terrain relief, no motion blur. Replay uses
  one match per 20 m node. Live mode attempted one match every ~3.5 s on this CPU.
- **v1 SITL GPS has no horizontal noise** (`SIM_GPS_NOISE` only moves altitude in 4.6.3). v2's
  injected noise model is a guess, not fitted to a receiver.
- **The Monte Carlo is small**: 4 seeds per cell, replayed vgeo, speedup 3, one host under heavy
  load. Distributions are reported as min / median / max (p90 only for the visual geoloc error), not
  confidence intervals.
- **TTD resolution is 1 s** (monitor epoch); times are sim time.
- The detection threshold choices (windows, sigmas, AL) are mine for this demo, not tuned to any
  standard.
- Not tested: amd64, ArduPilot 4.7+ (there the glitch param is `SIM_GPS1_GLTCH`, per
  `samples/ardupilot-ekf3-source-switch`), `ODOMETRY` instead of `VISION_POSITION_ESTIMATE`, the
  LOITER / RTL response, live mode inside the Monte Carlo (too slow on CPU).

## Extending it in a hackathon

- Swap the VIO oracle for a real VIO (`samples/vio-to-mavlink-bridge`) and feed its velocity to
  the monitors; it is the weakest assumption here.
- Model the visual-geoloc map bias as a state (estimate it while GNSS is trusted) instead of
  overbounding it with a 7 m sigma; that should buy back detection time.
- Response variants: `self.set_mode("RTL")` or `"LOITER"` next to the source switch; or move the
  decision onboard with the Lua examples named in `samples/ardupilot-ekf3-source-switch`.
- Harder attacks: a step, `SIM_GPS_JAM=1`, or a spoof that also drags altitude.

## Pitfalls hit while building it

- Host ports 15760-15763 were taken by another SITL on this machine; the default is 15766.
- Cross-track deviation hides drag along the current leg. The survey runs north/south so the
  eastward drag is cross-track on the long legs. Report both metrics.
- `chrome --headless --screenshot --virtual-time-budget` hung on the MapLibre page for over
  2 min; driving Chrome over the DevTools protocol (`screenshot.mjs`) takes 13 s.
- v2: `GPS_INPUT` at 5 Hz => `GPS 1: not healthy`, arming refused (fixed with 10 Hz).
- v2: SS with a sub-filter per source never fires on a fast drag, because every filter gates the
  step (fixed with the 3-consecutive-gate exclusion).
- v2: a first version of the DR witness skipped the current epoch's VIO step (10 m at 10 m/s)
  and always came out ambiguous; caught by reading the separation log, fixed, unit-tested.
