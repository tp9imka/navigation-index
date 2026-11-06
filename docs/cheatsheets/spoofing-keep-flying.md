# Cheat sheet: spoofing detection, keep flying

Briefs like "detect GNSS spoofing on a vehicle and keep navigating", "assured PNT", "trust /
integrity", "fixed-wing 20-30 km through spoofing". Multicopter and fixed-wing. Decoder rows
4, 20, 27. On a ship: [maritime-ais](maritime-ais.md). Receiver-only monitoring with no vehicle:
[jammer-ew-map](jammer-ew-map.md).

## 1. What judges likely want (30 s)

The moment that sells: the spoof starts, the stock EKF follows it, your monitor fires, the
vehicle switches source and keeps its track. Judges want time to detect, false alarms, and
deviation with vs without the monitor, plus honesty about the slow drag you still miss.

## 2. The demo in 24-48 h

ArduCopter SITL survey, coherent 1 m/s GPS drag, companion monitor (solution separation +
velocity test against real geoloc), EKF3 switch to ExternalNav, dashboard replay. Fixed-wing:
the same monitor on a 27.6 km ArduPlane route.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [golden-demo](../../samples/golden-demo/) | ran | docker + venv (`pymavlink==2.4.50`) | `run.sh` builds the ArduPilot image if missing (~8.5 min, 1.85 GB); v2 ~8 min, Monte Carlo 20 min | `python3 -m venv .venv && .venv/bin/pip install pymavlink==2.4.50`, `PYTHON=.venv/bin/python ./run.sh --v2` |
| [golden-demo-fixedwing](../../samples/golden-demo-fixedwing/) | ran | docker + same venv | plane image 40 s on top of the copter image; ~5 min wall (4 flights at speedup 5) | `PYTHON=.venv/bin/python ./run.sh` |
| [autopilot-spoof-response](../../samples/autopilot-spoof-response/) | ran | docker + venv | 45 flights ~35 min in 5 lanes | `python3 spoof_sweep.py --python .venv/bin/python` |
| [multi-source-fde](../../samples/multi-source-fde/) | ran | venv | VPAIR 0.86 GB + two-source terrain ~120 MB; 164 s for 10 seeds | `.venv/bin/python run_fde.py --data ../relative-nav-benchmark/data/vpair` |

PX4: [golden-demo-px4](../../samples/golden-demo-px4/) `./run.sh` (~9 min, image ~26 min first
time). Onboard-only recipes: [autopilot-resilient-configs](../../samples/autopilot-resilient-configs/)
(156 flights, ~100 min).

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Platform (copter / plane / PX4)? Attack types named? ADR-001 | Demo script: stock EKF run first, then monitor run |
| Nav | Read the monitor in golden-demo; pick thresholds to keep | Run `run.sh --v2` and the `SPOOF=none` control |
| Platform | Build SITL image, venv | Fixed-wing or PX4 variant if the brief says so |
| Viz (4-5) | Dashboard replay from golden-demo | Deviation with vs without monitor on one plot |
| Pitch (5) | Threat model: position vs coherent drag, step, jam-then-spoof | Read [autopilot-gnss-fault-handling](../autopilot-gnss-fault-handling.md) for the "why" slide |

## 4. Numbers you can cite

- Coherent 1 m/s drag: time to detect median 2.8 s; deviation median 7.4 m with the monitor
  vs 75 m without. **SITL** + replayed real geoloc, 4 flights per cell.
- Stock EKFs alone: every PX4 / ArduPilot config believed 96-110 % of a coherent drag; no flag
  at 1 m/s or below with default gates. **SITL**, 30 flights, 1 per cell.
- Fixed-wing, 27.6 km: max cross-track 28-35 m with the monitor (day fixes) vs 749-751 m
  without; EKF3 `GPS_GLITCHING` 0 reports in 16 flights. **SITL**; fixes are statistical draws
  from rates measured on real data.

## 5. Top traps

1. Slow drags are absorbed before any test fires: 0.05-0.5 m/s never alarmed in
   gnss-ins-ekf-outage (synthetic); a coherent drag needs an external reference (VO, airspeed,
   a parked receiver). Show the drag you miss.
2. Chi-square against real geoloc false-alarmed in 4 of 4 no-spoof flights (3-5 m registration
   bias); golden-demo v2 acts on SS + velocity test only. SITL GPS has no horizontal noise, so
   the pre-attack margin is flattering.
3. Fixed-wing: set `AHRS_OPTIONS` bit 0 or DCM falls back to the spoofed GPS; ExternalNav NE
   must use ArduPilot's spherical `LATLON_TO_M` (34 m off at 11 km otherwise); Plane AUTO keeps
   flying on whatever it believes. PX4 `HIL_GPS` cannot carry a spoof flag.

## 6. Stretch goal

Exclude, not just detect: [multi-source-fde](../../samples/multi-source-fde/) excluded a 2 m/s
GNSS drag in 10/10 runs and cut error max from 279 m to 21 m, 0 HMI (mixed: real VPAIR flight,
simulated GNSS and TRN). Or catch 0.3 m/s: no onboard config did; only the external companion
monitor did (PX4, 44-51 s, SITL).

## 7. Links

- Decoder: [rows 4, 20, 27](../problem-statement-decoder.md#the-table); evidence:
  [section 1](../evidence-matrix.md#1-gnss-spoof-detection-on-a-vehicle),
  [section 3](../evidence-matrix.md#3-integrity-metrics-protection-level-misleading-information).
- Cards: [ArduPilot](../integration-cards/ardupilot__ardupilot.md),
  [pymavlink](../integration-cards/ardupilot__pymavlink.md),
  [MAVProxy](../integration-cards/ardupilot__mavproxy.md),
  [PX4](../integration-cards/px4__px4-autopilot.md),
  [gnss_lib_py](../integration-cards/stanford-navlab__gnss_lib_py.md),
  [robot_localization](../integration-cards/cra-ros-pkg__robot_localization.md),
  [GTSAM](../integration-cards/borglab__gtsam.md).
- Datasets: [Jammertest](../dataset-cards/jammertest-data.md), [TEXBAT](../dataset-cards/texbat.md),
  [GSDC](../dataset-cards/gsdc.md), [VPAIR](../dataset-cards/vpair.md).
- Guides: [autopilot-gnss-fault-handling](../autopilot-gnss-fault-handling.md),
  [integrity-monitoring](../integrity-monitoring.md).
