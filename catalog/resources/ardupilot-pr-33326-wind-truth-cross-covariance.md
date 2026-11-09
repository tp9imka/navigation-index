# ArduPilot PR 33326: zero wind cross-covariances when treating wind as truth

`res:ardupilot-pr-33326-wind-truth-cross-covariance` - doc - <https://github.com/ArduPilot/ardupilot/pull/33326>

**By:** Peter Barker - **Year:** 2026 - **Level:** advanced - **Access:** open

Merged to master 2026-06-09. When EKF3 treats wind as truth it zeroed wind variances but left wind-velocity cross-covariances, making the covariance non-positive-definite and occasionally tripping bad_airspeed during no-airspeed dead reckoning (a years-long flaky autotest). The fix zeroes variances and cross-covariances together; reported 200/200 passing samples after the change.

## Key takeaways

- Freezing a state by zeroing only its variance is a real defect pattern; consider-state handling must zero the cross terms too
- Not in Copter-4.6.3 (checked in source)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `ekf3`, `wind`, `covariance`, `dead-reckoning`, `pull-request`

## Related

- part_of: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- explains: [ArduPilot EKF3 drag fusion and wind-state gating (source, Copter-4.6.3)](../../catalog/resources/ardupilot-ekf3-drag-wind-source-copter-4-6-3.md)

## Referenced by

- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)

_Indexed by lane(s): innovation-pa-aero-adaptation_
