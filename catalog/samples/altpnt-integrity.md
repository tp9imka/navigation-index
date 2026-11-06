# Sample: Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram

`sample:altpnt-integrity` - code and walkthrough in [samples/altpnt-integrity](../../samples/altpnt-integrity/)

A stdlib-only simulated UAV flight with INS, VIO-like velocity, intermittent visual-geolocalization fixes (repetitive-texture outliers, map-misregistration bias, dropouts over water), optional coarse MagNav-like fixes and a GNSS that is jammed and then spoofed. An 8-state EKF with chi-square innovation gating feeds a solution-separation bank that detects, excludes or (with only two sources) alerts and resolves by dead-reckoning consistency, computes horizontal protection levels against an alert limit, and reports MI/HMI, availability, time-to-alert and an ASCII/SVG Stanford diagram. A monitor-off negative control shows the misleading-information events the monitor removes.

**Verification:** ran with python3.14.7 stdlib on 2026-11-06: default run, --magnav, --no-gnss, --al-sweep, 20-seed Monte Carlo for 8 configurations, CSV and SVG writers (SVG rendered with macOS qlmanage and inspected); 15 unit tests pass (python3 -m unittest), and the detection tests were confirmed to fail with detection disabled. Synthetic data only; no real flight log or indexed repo was run.

**Concepts:** [Assured / resilient PNT](../concepts/assured-pnt.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Visual(-inertial) odometry](../concepts/vio.md), [Jamming and spoofing](../concepts/gnss-interference.md)

**Tags:** `integrity`, `protection-level`, `alert-limit`, `raim`, `araim`, `solution-separation`, `fde`, `chi-square`, `innovation-gate`, `stanford-diagram`, `time-to-alert`, `spoofing`, `ekf`, `stdlib`

## Related

- explains: [MAAST for ARAIM](../repos/stanford-gps-lab__maast_for_araim_2.md)
- explains: [RAIM (MATLAB)](../repos/michaelbeechan__raim.md)
- explains: [FilterPy](../repos/rlabbe__filterpy.md)
- explains: [GTSAM](../repos/borglab__gtsam.md)
- explains: [UASTHN](../repos/arplaboratory__uasthn.md)

_Indexed by lane(s): samples_
