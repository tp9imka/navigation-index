# Precision Landing

`res:px4-precision-landing-docs` - doc - <https://docs.px4.io/main/en/advanced_features/precland.html>

**By:** PX4 Dev Team - **Year:** 2026 - **Level:** intermediate - **Access:** open

PX4 guide to landing on a marked target from IR-LOCK or a companion computer sending MAVLink LANDING_TARGET (local NED). Covers the landing_target_estimator, opportunistic vs required modes, and parameters such as PLD_HACC_RAD (default 0.2 m) and PLD_BTOUT (default 5 s).

## Key takeaways

- A ready path for 'B is a marker': companion detects the tag, PX4 does the terminal approach
- Required mode searches and retries if the target is not seen
- The page says a valid global position is needed: check before relying on it indoors

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `precision-landing`, `landing-target`, `fiducial`, `px4`

## Related

- explains: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [vision_landing](../../catalog/repos/goodrobots__vision_landing.md)

## Referenced by

- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [AprilTag goal B: detection envelope vs range and view angle, and a tag-relative final approach](../../catalog/samples/fiducial-goal-apriltag.md) (explains)

_Indexed by lane(s): close-area-localization_
