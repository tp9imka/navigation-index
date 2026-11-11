# Path to product: from a nav algorithm to something that flies

<!-- about: repo:px4/px4-autopilot, repo:ardupilot/ardupilot, repo:nasa/ogma, repo:act3-ace/run-time-assurance, res:astm-f3269-21-rta, res:faa-ac-20-115d-do-178c, res:easa-ai-concept-paper-issue-2 -->

Some briefs say the winning team may take its solution towards real-world implementation. After
this page you can say where your algorithm runs, how it talks to the autopilot, what timing
it needs, which standards it would meet on the way to an aircraft, and how you ship a novel
estimator next to a certified baseline without betting the aircraft on it.

What this page does not repeat:

- Which stacks run on a laptop today and their limits: [practical-readiness.md](practical-readiness.md).
- Licenses of learned weights (SuperPoint, DINOv2, MASt3R...): [model-weights-licenses.md](model-weights-licenses.md).
- GNSS fault handling inside PX4 / ArduPilot: [autopilot-gnss-fault-handling.md](autopilot-gnss-fault-handling.md).
- Protection levels and solution separation: [integrity-monitoring.md](integrity-monitoring.md).
- Export control: [export-control-and-ethics.md](export-control-and-ethics.md).

Every number below has a source. "Vendor" means the number comes from the company selling the
hardware. "Not found" means I looked and did not find a published number. Read on 2026-11-09.

## 1. Onboard compute: what fits where

Two boxes on almost every small or medium UAV:

- **Flight controller (FC)**: a microcontroller running the autopilot and its EKF. Hard
  real-time, small memory, no images.
- **Companion computer**: a Linux SoC that runs cameras, VIO, matching and neural networks,
  and sends a position or odometry estimate to the FC.

| Platform | Compute (source) | Nav workloads that fit | Cited latency / power | Source |
|---|---|---|---|---|
| Pixhawk 6X (FMUv6X) | STM32H753 Cortex-M7 480 MHz, 2 MB flash, 1 MB RAM | PX4 EKF2, fusing external vision / aux global position; small runtime monitors | EKF2 prediction period default 10000 us => 100 Hz (`EKF2_PREDICT_US`). External vision expected at 30-50 Hz | [Pixhawk 6X docs](../catalog/resources/px4-pixhawk-6x-docs.md), PX4 `src/modules/ekf2/module.yaml`, [PX4 external position estimation](../catalog/resources/px4-external-position-estimation.md) |
| CubeOrange+ | STM32H757 Cortex-M7 400 MHz, 2 MB flash, 1 MB RAM (PX4 docs page) | ArduPilot EKF3 with source switching; Lua monitors | ArduPilot ExtNav needs >= 4 Hz; Lua needs >= 2 MB flash and 80 kB memory | [PX4 Cube Orange+ page](https://docs.px4.io/main/en/flight_controller/cubepilot_cube_orangeplus.html), [ArduPilot non-GPS position](../catalog/resources/ardupilot-dev-mavlink-nongps-position.md), [Lua scripts](../catalog/resources/ardupilot-lua-scripting-docs.md) |
| Raspberry Pi 5 | 4x Cortex-A76 2.4 GHz, CPU only (plus optional Hailo add-on) | CPU VIO (ROVIO-class filters), CNN-backbone VPR at a few Hz, classic feature matching | ncnn, 4 threads: ResNet-50 46.21 ms avg, MobileNetV2 10.52 ms, ViT 611.65 ms. Power not measured | [ncnn](../catalog/repos/tencent__ncnn.md) `benchmark/README.md`, [Hailo examples](../catalog/repos/hailo-ai__hailo-rpi5-examples.md) |
| Jetson Orin Nano Super 8GB | 67 sparse / 33 dense INT8 TOPS, 7 / 15 / 25 W modes (vendor) | GPU VIO (cuVSLAM), stereo depth, learned matching / VPR with TensorRT | cuVSLAM Mono-Depth 424x240: 31 ms avg, about 30% frames dropped (25 W). Stereo disparity 1080p graph: 19 ms at 30 Hz. ESS DNN stereo 576p: 30 ms (vendor) | [cuVSLAM paper](../catalog/resources/cuvslam-2025.md) App. B, [Isaac ROS performance](../catalog/resources/isaac-ros-performance-summary.md), [Orin Nano Super blog](../catalog/resources/nvidia-orin-nano-super-blog.md) |
| Jetson AGX Orin (upper bound for reference) | 64 GB module | Everything above with headroom | cuVSLAM per-frame track: stereo 1.8 ms, stereo-inertial 3.8 ms, mono 2.7 ms (768x480). Stereo disparity graph 1080p 9.3 ms (vendor) | [cuVSLAM paper](../catalog/resources/cuvslam-2025.md) Table 1, [Isaac ROS performance](../catalog/resources/isaac-ros-performance-summary.md) |
| Jetson Orin NX 8/16GB | Between Nano and AGX (vendor) | Same as Nano with more headroom | Not found: no Orin NX nav latency in cuVSLAM paper or Isaac ROS tables | - |
| ModalAI VOXL 2 (Qualcomm QRB5165) | 8 cores up to 3.091 GHz, 15 TOPS NPU, 16 g, PX4 on the DSP (vendor) | FC + companion in one: VIO (ModalAI QVIO, OpenVINS server), INT8 NPU inference | Not found: no third-party VIO or matcher latency published for QRB5165 | [VOXL 2 docs](../catalog/resources/px4-modalai-voxl-2-docs.md), [voxl-open-vins-server](https://gitlab.com/voxl-public/voxl-sdk/services/voxl-open-vins-server) |
| Qualcomm RB5 / Flight RB5 | Same QRB5165 SoC as VOXL 2 | As VOXL 2 | Not found for QRB5165. Nearby proxies on Qualcomm AI Hub: SuperPoint 640x480 on QCS8550 16.13 ms float (QNN); on RB3 Gen 2 (QCS6490) W8A8 TFLite 580.219 ms with 40 of 156 layers on CPU (vendor) | [AI Hub SuperPoint](../catalog/resources/qualcomm-ai-hub-superpoint.md), [ai-hub-models](../catalog/repos/qualcomm__ai-hub-models.md) |
| Older Jetsons (TX2, Xavier NX) | - | VIO only | Only qualitative: ROVIO lowest CPU on every board; others used more than one core; Kimera highest memory | [Jeon et al. 2021](../catalog/resources/jeon-2021-vio-jetson-benchmark.md) |

How to read it:

- **The FC never sees an image.** Its job is the EKF and the failsafes. Your algorithm runs on
  the companion and hands the FC a measurement.
- **CPU-only boards run filters, not transformers.** On a Pi 5 a ViT forward pass took
  611.65 ms in the ncnn benchmark. A DINOv2-based VPR will be sub-Hz there. A ResNet-class
  backbone at about 46 ms is a few Hz once you add pre- and post-processing.
- **Jetson numbers are vendor numbers.** Reproduce one on your board with
  [TensorRT](../catalog/repos/nvidia__tensorrt.md) `trtexec` and
  [jetson-stats](../catalog/repos/rbonghi__jetson_stats.md) before quoting it. Quote mean and
  p99 latency plus watts in the power mode you used.
- **Qualcomm NPUs reward INT8 work.** The 580 ms RB3 Gen 2 SuperPoint result is what CPU
  fallback looks like. Quantize with [AIMET](../catalog/repos/qualcomm__aimet.md) and check
  that every layer lands on the NPU.
- Measure your own number and say "measured on X, power mode Y". One measured row beats the
  whole table above.

## 2. Integration patterns

### 2.1 Four ways in

| Pattern | Where your code runs | Interface | Good for | Watch out for |
|---|---|---|---|---|
| A. FC module | Inside PX4 (uORB module) or ArduPilot (library) | uORB topics / AP library calls | Small, deterministic logic: monitors, a 1-state filter | MCU budget; ArduPilot is GPLv3 (section 5); you now own FC certification scope |
| B. FC Lua (ArduPilot) | Lua VM on the FC | ArduPilot scripting API | Source switching, monitors, glue | "Scripts are not guaranteed to be run on a reliable schedule" ([Lua docs](../catalog/resources/ardupilot-lua-scripting-docs.md)) |
| C. Companion => MAVLink | Companion computer | `ODOMETRY`, `VISION_POSITION_ESTIMATE` | Works with both autopilots, any language | Timestamps and delay tuning; MAVLink link bandwidth |
| D. Companion => PX4 via uXRCE-DDS | Companion with ROS 2 | `/fmu/in/vehicle_visual_odometry`, `/fmu/in/aux_global_position`, custom modes | ROS 2 teams on PX4; geolocalization fixes | `px4_msgs` must match firmware; DDS unauthenticated, keep the link isolated |

Concrete entry points:

- **Relative odometry (VIO, VO, optical flow-like)** => PX4 `vehicle_visual_odometry`
  (MAVLink `ODOMETRY` with `MAV_FRAME_LOCAL_FRD`, or `VISION_POSITION_ESTIMATE`) at 30-50 Hz
  ([PX4](../catalog/resources/px4-external-position-estimation.md)). ArduPilot: `ODOMETRY`
  preferred, at 4 Hz or more, `EK3_SRC1_POSXY = 6` (ExternalNav)
  ([ArduPilot](../catalog/resources/ardupilot-dev-mavlink-nongps-position.md),
  [EKF sources](../catalog/resources/ardupilot-ekf3-sources.md)).
- **Absolute fixes (visual geolocalization, terrain matching, magnetic map matching)** =>
  PX4 aux global position: `AuxGlobalPosition` has a `source` field (vision, terrain,
  magnetic, pseudolites, LEO) and EKF2 fuses up to 4 instances via `EKF2_AGP*_` parameters.
  Horizontal only; vertical is reserved
  ([msg doc](../catalog/resources/px4-aux-global-position-msg.md)). On v1.16 / v1.17 the same
  DDS topic exists with type `VehicleGlobalPosition`; the dedicated message is on main.
  This is the best-shaped hook in either autopilot for an alt-PNT fix. On ArduPilot's
  non-GPS page the absolute-position options, `GPS_INPUT` and
  `GLOBAL_VISION_POSITION_ESTIMATE`, are both marked "not recommended"; teams usually feed
  ExtNav instead.
- **Your own flight mode** (for example "hold position on vision only") =>
  [PX4 ROS 2 Control Interface](../catalog/resources/px4-ros2-control-interface-docs.md) with
  [px4-ros2-interface-lib](../catalog/repos/auterion__px4-ros2-interface-lib.md). Modes sit
  inside PX4's failsafe state machine and arming checks. Parts are still experimental.
- **Plumbing**: [uXRCE-DDS docs](../catalog/resources/px4-uxrce-dds-docs.md),
  [Micro XRCE-DDS Agent](../catalog/repos/eprosima__micro-xrce-dds-agent.md),
  [px4_msgs](../catalog/repos/px4__px4_msgs.md), [MAVROS](../catalog/repos/mavlink__mavros.md),
  [MAVSDK](../catalog/repos/mavlink__mavsdk.md),
  [mavlink-router](../catalog/repos/mavlink-router__mavlink-router.md),
  [ardupilot_ros](../catalog/repos/ardupilot__ardupilot_ros.md).

### 2.2 Time sync

The estimator needs the time the photo was taken, not the time the message arrived.

1. **Hardware first.** Trigger the camera from the FC camera-trigger output or from a sync
   board like [VersaVIS](../catalog/repos/ethz-asl__versavis.md), and stamp the exposure
   midpoint.
2. **Clock alignment.** PX4's DDS client syncs timestamps by default (`UXRCE_DDS_SYNCT`).
   MAVLink has `TIMESYNC`. On the companion, keep the system clock disciplined
   (see [timing-resilience.md](timing-resilience.md)).
3. **Delay parameter.** PX4: `EKF2_EV_DELAY`, "the difference between the timestamp of the
   measurement and the 'actual' capture time". It can be 0 only with correct capture
   timestamps and timesync. Tune it to the value that gives the lowest innovations in dynamic
   manoeuvres. ArduPilot: `VISO_DELAY_MS`, 0-250 ms, default 10 (from `AP_VisualOdom.cpp`).
   PX4's `EKF2_DELAY_MAX` (default 200 ms) must be at least the largest sensor delay.
4. **Measure the pipeline.** [ros2_tracing](../catalog/repos/ros2__ros2_tracing.md) gives
   per-callback latency. Report p50 and p99, not the mean.

### 2.3 Latency budget template

Fill this with your own measurements. The rows are the template; there are no numbers in it
on purpose.

```
camera exposure + readout     ____ ms   (sensor datasheet)
transfer to companion         ____ ms   (USB / MIPI / Ethernet)
pre-processing                ____ ms
inference / matching          ____ ms   (trtexec / benchncnn, p99)
local estimator (VIO / PF)    ____ ms
publish => FC (MAVLink / DDS) ____ ms
-------------------------------------
total capture => FC            ____ ms   => set EKF2_EV_DELAY / VISO_DELAY_MS
rate delivered                 ____ Hz   (PX4 wants 30-50 Hz odometry; ArduPilot >= 4 Hz)
```

Rule of thumb from the docs above: a delayed but correctly timestamped measurement is fine
(the EKF runs on a delayed horizon). A wrongly timestamped one is not.

### 2.4 Determinism

- Keep the estimator thread apart from image I/O and logging. Lock memory, pin the thread,
  give it a real-time priority: [ros2-realtime-examples](../catalog/repos/ros-realtime__ros2-realtime-examples.md).
  Compare executor settings with the [reference-system](../catalog/repos/ros-realtime__reference-system.md) method.
- Fix input sizes and engine builds. TensorRT engines are tied to GPU and TensorRT version;
  build on the target.
- No allocation after init in anything that might move to the FC. That is how
  [F Prime](../catalog/repos/nasa__fprime.md) and [cFS](../catalog/repos/nasa__cfs.md) code
  is written, and it is what a reviewer will ask about.

## 3. Certification and assurance map, in plain language

You will not certify anything in a hackathon. You can show you know which documents apply and
which architecture keeps the certification cost down.

| Document | What it is | When it applies to a nav function | Access |
|---|---|---|---|
| DO-178C / ED-12C ([AC 20-115D](../catalog/resources/faa-ac-20-115d-do-178c.md)) | Software development assurance. Levels A-E by worst failure condition | Any flight software. Your nav code's level follows from the hazard its failure can cause | Standard paywalled; AC free |
| DO-254 / ED-80 ([AC 20-152A](../catalog/resources/faa-ac-20-152a-do-254.md)) | Airborne electronic hardware assurance (FPGA, ASIC, boards) | When the function moves into custom hardware; complex COTS SoCs need extra evidence (FAA Order 8110.105B) | Standard paywalled; AC free |
| [DO-160G](../catalog/resources/rtca-do-160g.md) | Environmental and EMI qualification of the box | Companion computer and sensors in the aircraft | Paywalled |
| [DO-334](../catalog/resources/rtca-do-334-ahrs-mops.md) | MOPS for strapdown AHRS | Closest RTCA performance standard to an inertial fallback | Paywalled |
| DO-229 (SBAS) and DO-316 (GPS/ABAS) | GNSS receiver MOPS | The GNSS side of a hybrid; context for integrity terms. Titles from general knowledge, not read for this page | Paywalled |
| ARP4754A / ARP4761 | System development and safety assessment | Produces the failure conditions that set DO-178C / DO-254 levels; cited by F3269 | Paywalled |
| [ASTM F3269-21](../catalog/resources/astm-f3269-21-rta.md) | Run-time assurance practice for UAS | The pattern for shipping a complex or learned nav function next to an assured fallback (section 4). Free explanation: [Nagarajan et al. 2021](../catalog/resources/nagarajan-2021-astm-f3269-scitech.md) | Paywalled |
| [STANAG 4703](../catalog/resources/nato-stanag-4703-aep-83.md) / STANAG 4671 | NATO airworthiness codes: light UAS up to 150 kg / fixed-wing 150-20,000 kg | Military customers map a product to these or a national equivalent | 4703 2014 text public; current Ed 3 not read |
| [EASA SORA 2.5](../catalog/resources/easa-ed-decision-2025-018-r-sora-2-5.md) | Risk assessment for "specific" category drone operations | Civil operations in Europe: authorises an operation rather than type-certifying the aircraft | Free |
| [EASA AI Concept Paper Issue 2](../catalog/resources/easa-ai-concept-paper-issue-2.md) | Guidance for Level 1 and 2 ML: learning assurance, explainability | Any learned component (VPR backbone, matcher, learned inertial model) | Free |
| [ED-324 / ARP6983](../catalog/resources/eurocae-wg-114-ed-324-arp6983.md) | Joint EUROCAE / SAE process standard for ML | Draft; WG target 31 Dec 2026. Say "aligned with the draft", not "compliant" | Not published |

What this means for a team:

- **Assurance cost follows authority.** A function that can steer the aircraft into terrain gets
  a high software level. A function that only offers a measurement to a monitored EKF can sit
  lower if the monitor and fallback carry the safety argument. That is the whole point of
  F3269.
- **ML has no finished standard.** Point to the EASA concept paper and the ED-324 draft, show
  you track data provenance (see [model-weights-licenses.md](model-weights-licenses.md)), and
  keep the learned part behind a monitor.
- **Civil vs military.** Civil drones in Europe go through SORA for the operation. A defense
  customer will use military airworthiness codes (STANAG 4671 / 4703 or national). Do not
  claim a path you have not checked with the customer.

## 4. Runtime assurance: ship the new algorithm next to a trusted baseline

The pattern (Simplex, [Sha 2001](../catalog/resources/sha-2001-simplex.md); formalised for UAS
in [ASTM F3269](../catalog/resources/astm-f3269-21-rta.md)): run the high-performance,
hard-to-verify function, watch it with a simple verified monitor, and switch to a simple
verified fallback before it can cause harm.

```
                 sensors (IMU, baro, mag, GNSS, camera)
                         |                     |
                         v                     v
   +------------------------------+   +------------------------------+
   | COMPLEX FUNCTION (new)       |   | BASELINE (assured)           |
   | your VPR / terrain / VIO     |   | EKF2 / EKF3: IMU + baro + mag|
   | on companion computer        |   | (+ GNSS when trusted)        |
   +---------------+--------------+   +---------------+--------------+
                   | candidate fix                    | reference
                   v                                  v
           +--------------------------------------------------+
           | SAFETY MONITOR (simple, on FC or isolated core)  |
           | - innovation vs EKF within gate?                 |
           | - jump vs INS-propagated position plausible?     |
           | - message fresh? covariance sane?                |
           +-------------------------+------------------------+
                                     | ok / not ok
                                     v
           +--------------------------------------------------+
           | RTA SWITCH: fuse candidate  OR  drop it          |
           | recovery: INS dead-reckoning => loiter / RTL /   |
           | land per autopilot failsafe                      |
           +--------------------------------------------------+
```

How each box maps to existing pieces:

- **Baseline**: PX4 EKF2 or ArduPilot EKF3, unchanged. Their own innovation gates already
  reject gross outliers.
- **Switch, ArduPilot**: EKF source sets (`EK3_SRCn_*`) switched by the stock
  `libraries/AP_Scripting/examples/ahrs-source.lua`, which votes between GPS, ExtNav and
  optical flow using GPS speed accuracy and ExtNav innovation thresholds over about 2 s.
- **Switch, PX4**: per-source enable bits (`EKF2_EV_CTRL`, `EKF2_AGP*_CTRL`) or, in flight,
  the MAVLink command `VEHICLE_CMD_ESTIMATOR_SENSOR_ENABLE` (named in the `EKF2_SENS_EN`
  parameter description on PX4 main).
- **Monitor code**: generate it from requirements with
  [FRET](../catalog/repos/nasa-sw-vnv__fret.md) => [Ogma](../catalog/repos/nasa__ogma.md) =>
  [Copilot](../catalog/repos/copilot-language__copilot.md) C99, or write temporal properties
  for [R2U2](../catalog/repos/r2u2__r2u2.md). For the switch logic itself, read
  [AFRL run-time-assurance](../catalog/repos/act3-ace__run-time-assurance.md) (explicit /
  implicit Simplex and ASIF) and [SOTER on ROS](../catalog/repos/drona-org__soteronros.md).
- **Learned parts**: [Black-Box Simplex](../catalog/resources/mehmood-2022-black-box-simplex.md)
  shows the pattern still works when neither controller is verified offline.
  [alpha-beta-CROWN](../catalog/repos/verified-intelligence__alpha-beta-crown.md) can bound a
  small network, not a ViT backbone.
- **Fault handling already in the autopilots**:
  [autopilot-gnss-fault-handling.md](autopilot-gnss-fault-handling.md). Integrity math for
  the monitor: [integrity-monitoring.md](integrity-monitoring.md).

Rules that keep the argument honest:

1. The monitor is simpler than the thing it monitors. If it needs a neural network, it is not
   a monitor.
2. The monitor runs at the baseline's assurance level and on a separate execution context
   (FC, or an isolated core), so the complex function cannot starve it.
3. The fallback must work without the complex function: show an IMU-only or IMU + baro + mag
   run and its drift over the time it takes to reach a safe state.
4. Log every switch with the reason. That log is your evidence.

A demo reviewers will remember: replay a flight log where GNSS is spoofed, show the new nav
function being accepted, then rejected by the monitor when it drifts, and the EKF falling back
without a position jump.

## 5. License traps for a shipped product

Weights and training data: [model-weights-licenses.md](model-weights-licenses.md). This
section covers the rest.

| Item | License (source) | Trap | What to do |
|---|---|---|---|
| ArduPilot firmware | GPLv3 ([ArduPilot license page](../catalog/resources/ardupilot-gplv3-license-page.md)) | Code compiled into the firmware is a derivative work: shipping it means shipping source and keeping upgrade rights | Keep the proprietary algorithm on the companion. ArduPilot's page says closed code on a companion is fine |
| ArduPilot Lua scripts | Not addressed on the license page | Whether a script loaded at runtime is a derivative work is not settled there | Treat scripts as source you will publish, or ask a lawyer |
| PX4 | BSD-3 for flight stack and middleware ([PX4 licenses](https://docs.px4.io/main/en/contribute/licenses.html)) | Permissive, but submodules vary: GitHub reports NOASSERTION for `sbgECom`, `libtomcrypt`, `Monocypher`. NuttX is Apache-2.0 | Run a license audit over `.gitmodules` before shipping a binary |
| Pixhawk hardware designs | CC-BY-SA 3.0 (PX4 licenses page) | A board derived from the open design must be shared alike | Buy FMUs, or design your own from scratch |
| MAVLink | XML and generated C library MIT; generator LGPLv3 ([MAVLink license](../catalog/resources/mavlink-license.md)) | None for generated headers | Fine in closed companion code |
| Jetson software | TensorRT OSS parts Apache-2.0; core runtime ships with JetPack under NVIDIA's terms (not re-read here) | Redistribution of the runtime in your image | Read the JetPack license before building a product image |
| Dev tools | jetson-stats is AGPL-3.0 | AGPL in a shipped image | Bench tool only |
| Government code | AFRL run-time-assurance: "This software is government owned" | No explicit grant | Learn from it, reimplement |
| No-license repos | SOTER on ROS has no license file | No grant at all | Read only |
| Training data | KITTI: CC BY-NC-SA 3.0 (cvlibs.net) | NonCommercial + ShareAlike on a shipped model is a risk | Train shipped models on CC BY / CC0 / own data; keep a provenance record |

Not legal advice. "Product" here includes a sponsor demo that leaves your hands.

## 6. The "path to product" slide

Adapt these 6 bullets. Replace every bracket with your measured value or delete the bullet.

- **Runs on**: [board, power mode]. Measured [N] ms p99 per frame at [W] W, [Hz] output. FC
  unchanged: stock [PX4 vX / ArduPilot vX].
- **Integrates through standard interfaces**: [ODOMETRY / aux_global_position / ExtNav] into
  the stock EKF, timestamps at capture, delay [D] ms measured and set in
  [EKF2_EV_DELAY / VISO_DELAY_MS].
- **Ships behind a runtime-assurance monitor** (ASTM F3269 pattern): innovation gate,
  plausibility vs INS, freshness. On failure the stock EKF drops the source and the
  autopilot failsafe takes over. Demo: [spoofing replay, switch at t = X s].
- **Certification path**: monitor and fallback carry the safety argument (DO-178C level set
  by ARP4761-style hazard analysis); the novel function stays advisory. Civil: SORA 2.5.
  Military: STANAG 4703 / 4671 or national code.
- **ML assurance**: learned parts follow EASA AI Concept Paper Issue 2 learning-assurance
  themes; data provenance recorded; aligned with the ED-324 / ARP6983 draft.
- **License-clean**: proprietary code on the companion; permissive dependencies only
  (BSD / MIT / Apache); weights and data per the project's license matrix.
- **Next 90 days**: [HIL on target board], [flight test in a GNSS-denied range], [hazard
  analysis + requirements in FRET].

## 7. What I could not verify

- Orin NX, RB5 / VOXL 2 nav-workload latency: no published number found.
- Jeon et al. 2021 CPU and memory values are in a figure only; not transcribed.
- STANAG 4671 text: the public French archive link timed out; facts here come from search
  summaries and the 4703 document.
- DO-229, DO-316, ARP4754A, ARP4761: named from general knowledge, not opened.
- DO-160H publication status after its planned March 2026 date.
- ED-324 / ARP6983 release: target date only.
- Raspberry Pi 5 power under a nav workload: not measured.
