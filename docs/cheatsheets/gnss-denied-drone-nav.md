# Cheat sheet: GNSS-denied drone navigation

Briefs like "navigate a small drone 10 km without GPS", "bring it home after jamming",
"drop-in GNSS replacement for a COTS autopilot", "how long can we fly after GNSS loss".
Decoder rows 1, 2, 20, 26. Fixed-wing over 20 km: see also
[terrain-night-celestial](terrain-night-celestial.md) and
[spoofing-keep-flying](spoofing-keep-flying.md).

## 1. What judges likely want (30 s)

They have seen camera-to-satellite matching from vendors and other teams. They reward an
error-vs-distance curve on open data, a gate that refuses bad visual fixes before the filter,
and the estimate going into a stock autopilot through a message it already reads. Say where it
breaks (map age, night, water).

## 2. The demo in 24-48 h

One real flight, end to end: nadir VO => retrieval => LightGlue fixes => gated EKF, scored per
km. Then the same estimate into SITL as ExternalNav.

| Sample | Status | Deps | Setup / download | First commands (from `samples/<name>/`) |
|---|---|---|---|---|
| [e2e-visual-nav-vpair](../../samples/e2e-visual-nav-vpair/) | ran | venv, Python 3.12 pins | VPAIR sample 0.86 GB (shared with relative-nav-benchmark); front end ~4 min per pass on M2 MPS, fusion 16 s | `../relative-nav-benchmark/fetch_data.sh aerial`, `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`, `.venv/bin/python run_fusion.py --data ../relative-nav-benchmark/data/vpair` |
| [golden-demo](../../samples/golden-demo/) | ran | docker + venv (`pymavlink==2.4.50`) | ArduPilot SITL image ~8.5 min build, 1.85 GB; v2 run ~8 min | `PYTHON=.venv/bin/python ./run.sh --v2` |
| [ardupilot-ekf3-source-switch](../../samples/ardupilot-ekf3-source-switch/) | ran | docker + pymavlink | same SITL image; ~100 s flight | `python3 source_switch.py --connect tcp:127.0.0.1:5762 --setup && python3 source_switch.py --connect tcp:127.0.0.1:5762` |
| [vpr-large-area](../../samples/vpr-large-area/) | ran | venv, Python 3.12 | NAIP download 6-25 min per vintage, DB build ~9 min | `.venv/bin/python download_data.py && .venv/bin/python run_vpr.py --skip-real` |

PX4 instead: [golden-demo-px4](../../samples/golden-demo-px4/) `./run.sh` (PX4 image ~26 min
the first time). Holdover-budget brief (row 26): [gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage/)
`python3 ekf_outage.py` (stdlib, under 1 s, synthetic).

## 3. First 2 hours (3-5 people)

| Who | 0:00-1:00 | 1:00-2:00 |
|---|---|---|
| Lead | Decode, confirm distance / platform / map provided, ADR-001 | Repo from [project-repo](../../templates/project-repo/), demo script |
| Nav | Start VPAIR fetch, venv for e2e | `run_fusion.py` green; read the gate code |
| Platform | Build SITL image (golden-demo `run.sh` builds it) | `source_switch.py --setup` and one flight |
| Viz (4-5) | TAK or dashboard with synthetic track | Error-vs-km plot from e2e results |
| Pitch (5) | Threat model, licences (ALIKED not SuperPoint) | Eval plan: VO-only baseline vs gated fixes |

## 4. Numbers you can cite

- VO only RMS 156 m over 8.53 km => strict-gated fixes RMS 4.8 m, 149 of 188 frames fixed,
  0 false fused. **Real** flight (VPAIR), 1 flight; map and truth share a source.
- Map age: retrieval R@10 within 100 m 0.98 on the same imagery, 0.48-0.73 across a 2-8 year
  gap. **Synthetic** queries cut from real NAIP, 150 per row.
- GPS cut without a source switch: EKF coasts ~6 s, then failsafe LAND. **SITL** (Copter
  4.6.3), 1 flight.

## 5. Top traps

1. A loose match gate without the filter gate fused 15 false fixes and drove RMS to 12 km.
   Keep the chi-square gate on.
2. Real frames are much harder than synthetic: the vpr chain fixed 1 of 23 real 2016 eBee frames,
   geoloc-license-clean 1 of 5. Do not promise the synthetic fix rate.
3. Autopilot traps: PX4 v1.17.0 has no `GPS_INPUT` handler and `failure gps off` gets no ACK
   ([upstream finding 8](../upstream-findings.md#8-px4-v1170-sih-gps-failure-injection-gets-no-ack));
   ArduPilot 4.6 `SIM_GPS_DISABLE` vs 4.7 `SIM_GPS1_ENABLE`; ENU vs NED. SuperPoint weights are
   non-commercial; FAISS + torch in one process abort on macOS arm64.

## 6. Stretch goal

Add a second absolute source so the protection level becomes usable:
[two-source-integrity-vpair](../../samples/two-source-integrity-vpair/) took availability at
AL 50 m from 1.6 % (visual fixes alone) to 84.4 % with a LiDAR-heightmap TRN, 0 HMI (mixed:
real flight, simulated TRN sensor, best-case shared DSM). Or cut the GCS link at the same time
as GNSS and show a defined onboard behaviour.

## 7. Links

- Decoder: [rows 1, 2, 20, 26](../problem-statement-decoder.md#the-table); evidence:
  [section 4](../evidence-matrix.md#4-absolute-alt-pnt-position-error),
  [section 5](../evidence-matrix.md#5-relative-navigation-and-drift-without-gnss).
- Cards: [OpenVINS](../integration-cards/rpng__open_vins.md),
  [LightGlue](../integration-cards/cvg__lightglue.md), [AnyLoc](../integration-cards/anyloc__anyloc.md),
  [ArduPilot](../integration-cards/ardupilot__ardupilot.md),
  [pymavlink](../integration-cards/ardupilot__pymavlink.md),
  [MAVProxy](../integration-cards/ardupilot__mavproxy.md),
  [px4-ros2-interface-lib](../integration-cards/auterion__px4-ros2-interface-lib.md),
  [evo](../integration-cards/michaelgrupp__evo.md).
- Datasets: [VPAIR](../dataset-cards/vpair.md), [UAV-VisLoc](../dataset-cards/uav-visloc.md),
  [AerialVL](../dataset-cards/aerialvl.md), [NAIP](../dataset-cards/naip-planetary-computer.md),
  [UZH-FPV](../dataset-cards/uzh-fpv.md).
- Guide: [autopilot-gnss-fault-handling](../autopilot-gnss-fault-handling.md).
