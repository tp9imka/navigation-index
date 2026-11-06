# oscillatord

`repo:orolia2s/oscillatord` - <https://github.com/Orolia2s/oscillatord>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 25 | C | GPL-2.0 | 2026-06-23 | False | production | low |

Daemon that disciplines the oscillator on the Orolia (Safran) Atomic Reference Time Card from a PPS reference and exposes monitoring.

**Why it matters:** Real disciplining code for a miniature atomic clock on a time card, to compare with toy GPSDO loops.

**Hackathon notes:** Needs the hardware; read the disciplining code for the loop design.

**Concepts:** [Timing and time transfer](../concepts/timing.md)

**Tags:** `gpsdo`, `disciplining`, `atomic-clock`, `time-card`

**Domains:** multi

## Related

- integrates_with: [OCP Time Card](../repos/time-appliances-project__time-card.md)
- integrates_with: [Meta Time libraries](../repos/meta__time.md)

## Referenced by

- [Meta Time libraries](../repos/meta__time.md) (integrates_with)
- [OCP Time Card](../repos/time-appliances-project__time-card.md) (integrates_with)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
