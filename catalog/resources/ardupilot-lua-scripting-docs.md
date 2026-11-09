# ArduPilot Lua Scripts

`res:ardupilot-lua-scripting-docs` - doc - <https://ardupilot.org/dev/docs/common-lua-scripts.html>

**By:** ArduPilot - **Year:** 2026 - **Level:** intermediate - **Access:** open

How to run Lua scripts on the ArduPilot flight controller: board requirements, heap sizing, script sandboxing and time slicing, and checksum gating for arming. Used for on-FC monitors such as automatic EKF source switching.

## Key takeaways

- Needs at least 2 MB flash and 80 kB memory; not available on F4 boards
- Scripts are not guaranteed to run on a reliable schedule
- SCR_LD_CHECKSUM / SCR_RUN_CHECKSUM can block arming if scripts differ from expected
- ahrs-source.lua in the repo switches GPS / ExtNav / optical flow by innovation votes

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `ardupilot`, `lua`, `scripting`, `ekf-source`, `monitor`

## Related

- has_code: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [EKF Source Selection and Switching](../../catalog/resources/ardupilot-ekf3-sources.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
