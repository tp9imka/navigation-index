# Dead Reckoning Failsafe (ArduCopter)

`res:ardupilot-copter-dead-reckoning-failsafe-docs` - doc - <https://ardupilot.org/copter/docs/deadreckoning-failsafe.html>

**By:** ArduPilot Dev Team - **Year:** 2025 - **Level:** intro - **Access:** open

Copter documentation. After GPS loss the vehicle flies normally for about 7-10 s, then starts dead reckoning and switches to RTL, and lands when FS_DR_TIMEOUT (typically 10-30 s) expires. Asks the user to set up wind estimation with EK3_DRAG_BCOEF_X/Y and EK3_DRAG_MCOEF first, but does not explain how they enter dead reckoning.

## Key takeaways

- Stock Copter dead reckoning is scoped to seconds to tens of seconds
- Drag coefficients are hand-set before flight

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `arducopter`, `dead-reckoning`, `failsafe`, `drag`

## Related

- cites: [Windspeed Estimation and Baro Compensation (ArduCopter)](../../catalog/resources/ardupilot-copter-wind-estimation-docs.md)

_Indexed by lane(s): innovation-pa-aero-adaptation_
