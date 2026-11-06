# Threat model: TODO project name

Fill at H+0 to H+2, freeze at H+14. Every "not mitigated" row is a line on the limits slide.
Background: [playbook 2.1](../docs/hackathon-playbook.md#21-threat-model-gnss-denial-and-deception),
[NISTIR 8323](../catalog/resources/nist-ir-8323-pnt-profile.md) (GNSS as untrusted input),
[DHS Resilient PNT Conformance Framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md).

## 1. System under consideration

- Platform: TODO (small UAS / fixed-wing / UGV / USV / UUV / dismounted / timing node)
- Mission phase covered: TODO (cruise, loiter, return-to-home, docking...)
- Nav sources: TODO (GNSS L1/L5, IMU grade, odometry, camera, baro, mag, radio ranging)
- Outputs and consumers: TODO (autopilot via MAVLink, TAK via CoT, operator UI, log)
- Alert limit: TODO m horizontal. Time to alert: TODO s. These define "usable".

## 2. Assets

| Asset | Why it matters |
|---|---|
| Position / velocity estimate | Wrong position => wrong route, airspace or collision |
| Time | Wrong time => logs, crypto, network sync break |
| Integrity flag | A missed alarm is worse than no flag |
| Datalink (C2, telemetry, video) | Loss removes the operator from the loop |
| Reference data (maps, DEM, imagery, anomaly maps) | Stale data corrupts the "independent" source |

## 3. Threats

Mark each row: M = mitigated, D = detected only, N = not addressed, X = out of scope.

| # | Threat | Mechanism | Symptom we would see | Our detector / response | Status | Evidence (test, run file) |
|---|---|---|---|---|---|---|
| T1 | GNSS jamming | Noise raises floor, receiver loses lock | C/N0 drop on all SVs, AGC change, fix lost | TODO | | |
| T2 | GNSS spoofing, sudden | Counterfeit signal captures receiver, jump | Position/time step, residuals spike | TODO | | |
| T3 | GNSS spoofing, slow drag-off | Offset grows below single-epoch gates | Fix stays "good"; INS slowly agrees with spoofer | TODO (windowed test, independent velocity) | | |
| T4 | Meaconing | Real signals rebroadcast with delay | Consistent but offset position and clock | TODO | | |
| T5 | Time push | Spoofer shifts receiver clock | PPS step vs holdover clock | TODO | | |
| T6 | After-effects | Corrupted state persists after GNSS returns | Clocks, logs, terrain warnings stay wrong | TODO (re-validate on recovery) | | |
| T7 | Datalink jamming | C2 / telemetry RF denied | Link loss, rising packet loss, RSSI changes | TODO (failsafe, store-and-forward) | | |
| T8 | Datalink spoofing / injection | Forged commands or telemetry | Unexpected mode changes, duplicate sysids | TODO (MAVLink2 signing, allowlist) | | |
| T9 | Sensor spoofing - camera | Dazzle, decoys, adversarial patterns | Matcher confidence collapses or jumps | TODO | | |
| T10 | Sensor spoofing - magnetometer / baro | Local fields, pressure manipulation | Heading or altitude inconsistent with others | TODO | | |
| T11 | Map staleness | Season, construction, destroyed landmarks | Low match scores, consistent bias | TODO (score gating, map date in output) | | |
| T12 | Collateral spoofing | Own-side protection hits our consumer devices | Phones and COTS receivers wrong | TODO | | |

## 4. Assumptions

State them so judges can attack them, not discover them.

- A1: First fix at start-up is trusted (true in the shipped skeleton: `DeadReckoningFilter.predict`).
- A2: IMU / odometry is not attacked and its bias is bounded by TODO m/s.
- A3: Attacker has no physical or software access to the vehicle.
- A4: Reference data is no older than TODO.
- A5: TODO

## 5. What we mitigate and what we do not

| We mitigate | We do not (and why) |
|---|---|
| TODO | TODO, e.g. "coordinated spoof of GNSS and camera - needs a third independent source" |
| | Attacks on the autopilot firmware - out of scope for 48h |
| | Military signals (M-code, P(Y)) - not public, not touched |

## 6. Test evidence

| Threat | Test condition (synthetic / SITL / dataset / bench) | Run file | Result |
|---|---|---|---|
| T3 | Synthetic drag-off 1.5 m/s, seed 7 | `runs/spoof.jsonl` | from `make eval`, not retyped |

Untested rows say "not tested". Real-signal tests use cabled or shielded setups only
([export control and ethics](../docs/export-control-and-ethics.md#3-gnss-signal-simulation-and-rf-transmission)).
